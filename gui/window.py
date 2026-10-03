from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget, QSplitter, QPushButton
from PySide6.QtCore import Qt, QThread, Signal, Slot, QObject

from message_area import MessageArea
from text_area import TextArea
from ticket_area import TicketArea
from sidebar import Sidebar
from settings import SettingsWindow
from src.chat_manager import ChatManager
from src.database import get_connection

class ChatWorker(QObject):
    finished = Signal(tuple)
    error = Signal(tuple)

    def __init__(self, chat_manager):
        super().__init__()
        self.chat_manager = chat_manager

    @Slot(tuple)
    def process(self, data):
        text, session_id = data
        try:
            response = self.chat_manager.process_message(text, session_id=session_id)
            resolved_id = session_id if session_id is not None else self.chat_manager.current_session_id
            self.finished.emit((response, resolved_id))
        except Exception as e:
            resolved_id = session_id if session_id is not None else self.chat_manager.current_session_id
            self.error.emit((str(e), resolved_id))


class MainWindow(QMainWindow):
    # Signal to trigger the worker
    request_process = Signal(tuple)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BetAssist")
        self.resize(1100, 700)
        self.is_processing = False

        self.chat_manager = ChatManager()

        # Setup Thread and Worker
        self.worker_thread = QThread()
        self.chat_worker = ChatWorker(self.chat_manager)
        self.chat_worker.moveToThread(self.worker_thread)

        # Connect Worker signals to UI slots
        self.chat_worker.finished.connect(self.on_chat_finished)
        self.chat_worker.error.connect(self.on_chat_error)

        # Connect request signal to worker process slot
        self.request_process.connect(self.chat_worker.process)
        self.worker_thread.start()

        # GUI
        main_container = QWidget()
        self.setCentralWidget(main_container)

        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)

        # Left: Sidebar
        self.sidebar = Sidebar()
        self.sidebar.session_selected.connect(self.handle_session_selected)
        self.sidebar.new_chat_requested.connect(self.handle_new_chat)
        self.sidebar.settings_requested.connect(self.handle_settings_requested)
        self.sidebar.session_deleted.connect(self.handle_session_deleted)
        self.splitter.addWidget(self.sidebar)

        # Middle: Chat Area
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chatContainer")
        chat_layout = QVBoxLayout(self.chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        self.message_area = MessageArea()
        self.text_area = TextArea()

        chat_layout.addWidget(self.message_area, 9)
        chat_layout.addWidget(self.text_area, 1)

        self.text_area.message_sent.connect(self.handle_message_sent)
        self.splitter.addWidget(self.chat_container)

        # Right: Ticket Bar
        self.ticket_container = QWidget()
        self.ticket_container.setObjectName("ticketContainer")
        ticket_layout = QVBoxLayout(self.ticket_container)
        ticket_layout.setContentsMargins(0, 0, 0, 0)
        self.ticket_area = TicketArea()
        ticket_layout.addWidget(self.ticket_area)

        self.splitter.addWidget(self.ticket_container)
        self.splitter.setCollapsible(0, False) # Sidebar
        self.splitter.setCollapsible(2, False) # Tickets
        self.splitter.setSizes([250, 600, 250])

        main_layout.addWidget(self.splitter)

        # Collapse buttons
        self.ticket_collapse_btn = QPushButton("◧", main_container)
        self.ticket_collapse_btn.setObjectName("ticketCollapseBtn")
        self.ticket_collapse_btn.setFixedSize(36, 36)
        self.ticket_collapse_btn.clicked.connect(self.toggle_ticket_area)
        self.ticket_collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ticket_collapse_btn.setToolTip("Show / hide ticket panel")

        self.update_button_positions()
        self.refresh_sidebar()

    def update_button_positions(self):
        margin = 18
        # Ticket button is on the right
        self.ticket_collapse_btn.move(self.centralWidget().width() - self.ticket_collapse_btn.width() - margin, margin)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_button_positions()

    def toggle_ticket_area(self):
        visible = self.ticket_container.isVisible()
        self.ticket_container.setVisible(not visible)

    def toggle_sidebar(self):
        # This is now handled by Sidebar.toggle_compact, but we can call it from here if needed
        # However, the button is now inside the sidebar, so we don't need this method anymore.
        pass

    def closeEvent(self, event):
        """Ensure background threads are shut down safely before the app closes."""
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)

    def handle_message_sent(self, text):
        # 1. Display user message immediately
        self.message_area.add_message(text, sender="User")
        # 2. Disable the send button
        self.text_area.set_enabled(False)
        if self.chat_manager.current_session_id is None:
            self.chat_manager.clear_session(create_new=True)
            self.refresh_sidebar()
        # 3. Trigger the background worker with current session ID
        # We pass the ID now so the worker knows where to save the response
        # even if the user switches chats while waiting.
        self.request_process.emit((text, self.chat_manager.current_session_id))

    @Slot(tuple)
    def on_chat_finished(self, data):
        response, session_id = data
        # Only append the response to the GUI if the session that requested it is still active
        # Handle the case where current_session_id might have been updated by the worker
        if session_id == self.chat_manager.current_session_id:
            # 1. Sync the internal ChatManager state from DB to ensure consistency
            self.chat_manager.load_session(session_id)

            # 2. Display assistant response
            self.message_area.add_message(response, sender="Assistant")
            # 3. Re-enable the send button
            self.text_area.set_enabled(True)
            self.refresh_sidebar()
        else:
            # The user has switched chats. We don't show the message here,
            # but it is already saved in the database by the ChatManager.
            self.text_area.set_enabled(True)

    @Slot(tuple)
    def on_chat_error(self, data):
        error_msg, session_id = data
        # Only display the error in the GUI if the session is still active
        if session_id == self.chat_manager.current_session_id:
            # 1. Display the error message
            self.message_area.add_message(f"Error: {error_msg}", sender="Assistant")
            # 2. Re-enable the send button
            self.text_area.set_enabled(True)
        else:
            self.text_area.set_enabled(True)

    def handle_session_selected(self, session_id):
        # Avoid reloading the same session if it's already active
        if session_id == self.chat_manager.current_session_id:
            return

        if self.chat_manager.load_session(session_id):
            # Clear message area
            # IMPORTANT: We must avoid deleting widgets while other events might be accessing them.
            # Using deleteLater() is correct, but we should ensure we are not doing this
            # in a way that clashes with rapid state changes.

            self.message_area.clear_messages()

            # Repopulate messages
            for msg in self.chat_manager.conversation:
                sender = "User" if msg.startswith("User: ") else "Assistant"
                text = msg.split(": ", 1)[1]
                self.message_area.add_message(text, sender=sender)

    def handle_new_chat(self):
        # Do not create a new DB session immediately when clicking "New Chat".
        # Only reset the local state.
        self.chat_manager.clear_session(create_new=False)
        self.message_area.clear_messages()
        self.refresh_sidebar()

    def handle_settings_requested(self):
        # We use a local variable instead of self.settings_win to avoid
        # holding a reference to a window that might have been deleted by Qt.
        settings_win = SettingsWindow(self)
        # Crucial: Tell Qt to explicitly delete the C++ object when the window closes,
        # preventing memory leaks and 'invalid pointer' crashes during rapid toggling.
        settings_win.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        settings_win.show()

    def handle_session_deleted(self, session_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

        # If the deleted session was the active one, clear the chat area
        if self.chat_manager.current_session_id == session_id:
            # Reset state without creating a new DB entry
            self.chat_manager.clear_session(create_new=False)
            self.message_area.clear_messages()

        self.refresh_sidebar()

    def refresh_sidebar(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM chat_sessions ORDER BY updated_at DESC")
        sessions = cur.fetchall()
        conn.close()
        self.sidebar.update_history(sessions, self.chat_manager.current_session_id)

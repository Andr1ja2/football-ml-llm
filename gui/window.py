from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget, QSplitter, QPushButton
from PySide6.QtCore import Qt, QThread, Signal, Slot, QObject

from message_area import MessageArea
from text_area import TextArea
from ticket_area import TicketArea
from src.chat_manager import ChatManager


class ChatWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, chat_manager):
        super().__init__()
        self.chat_manager = chat_manager

    @Slot(str)
    def process(self, text):
        try:
            response = self.chat_manager.process_message(text)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    # Signal to trigger the worker
    request_process = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Football Chat Application")
        self.resize(800, 600)

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
        self.splitter = QSplitter(Qt.Horizontal)

        # Left: Chat Area
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)

        self.message_area = MessageArea()
        self.text_area = TextArea()

        chat_layout.addWidget(self.message_area, 9)
        chat_layout.addWidget(self.text_area, 1)

        self.text_area.message_sent.connect(self.handle_message_sent)

        self.splitter.addWidget(chat_container)

        # Right: Ticket Bar
        self.ticket_container = QWidget()
        ticket_layout = QVBoxLayout(self.ticket_container)

        self.ticket_area = TicketArea()
        

        ticket_layout.addWidget(self.ticket_area)

        self.splitter.addWidget(self.ticket_container)
        self.splitter.setCollapsible(1, False)
        self.splitter.setSizes([200,50])
        main_layout.addWidget(self.splitter)

        # Collapse button
        self.collapse_button = QPushButton("🗐", main_container)
        self.collapse_button.setFixedSize(35, 35)
        self.collapse_button.clicked.connect(self.toggle_ticket_area)
        self.collapse_button.raise_()
        self.collapse_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(40, 40, 40, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 60, 0.5)
            }   
        """)
        self.collapse_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.update_button_position()

    def update_button_position(self):
        margin = 18

        x = self.centralWidget().width() - self.collapse_button.width() - margin
        y = margin

        self.collapse_button.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        splitter_width = self.splitter.width()

        min_width = max(200, int(splitter_width * 0.15))
        max_width = int(splitter_width * 0.45)

        self.ticket_container.setMinimumWidth(min_width)
        self.ticket_container.setMaximumWidth(max_width)

        self.update_button_position()

    def toggle_ticket_area(self):
        visible = self.ticket_container.isVisible()

        self.ticket_container.setVisible(not visible)

        if (visible):
            self.message_area.layout.setContentsMargins(0, 0, 45, 0)
        else:
            self.message_area.layout.setContentsMargins(0, 0, 0, 0)

    def handle_message_sent(self, text):
        # 1. Display user message immediately
        self.message_area.add_message(text, sender="User")

        # 2. Disable the send button
        self.text_area.set_enabled(False)

        # 3. Trigger the background worker
        self.request_process.emit(text)

    @Slot(str)
    def on_chat_finished(self, response):
        # 1. Display assistant response
        self.message_area.add_message(response, sender="Mistral")

        # 2. Re-enable the send button
        self.text_area.set_enabled(True)

    @Slot(str)
    def on_chat_error(self, error_msg):
        # 1. Display the error message
        self.message_area.add_message(f"Error: {error_msg}", sender="Mistral")

        # 2. Re-enable the send button
        self.text_area.set_enabled(True)

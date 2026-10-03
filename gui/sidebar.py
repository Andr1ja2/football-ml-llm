from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

class Sidebar(QWidget):
    session_selected = Signal(int)
    new_chat_requested = Signal()
    settings_requested = Signal()
    session_deleted = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_compact = False
        self.setFixedWidth(250)

        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                color: #cccccc;
                border-right: 1px solid #333333;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: none;
                padding: 8px;
                border-radius: 4px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background-color: #37373d;
                color: white;
            }
            QListWidget {
                border: none;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Top Header Area
        self.header_layout = QVBoxLayout()

        # Define buttons
        self.new_chat_btn = QPushButton("+ New Chat")
        self.new_chat_btn.clicked.connect(lambda: self.new_chat_requested.emit())

        self.collapse_btn = QPushButton("⬅")
        self.collapse_btn.setFixedSize(30, 30)
        self.collapse_btn.clicked.connect(self.toggle_compact)

        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.clicked.connect(lambda: self.settings_requested.emit())

        # Initial layout state
        self.history_list = QListWidget()
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_list.setFixedWidth(230) # Default expanded width minus margins
        self.history_list.itemClicked.connect(self.on_item_clicked)

        self.set_compact_state()
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.history_list)

        # Bottom: Settings Button
        self.layout.addWidget(self.settings_btn)

    def toggle_compact(self):
        self.is_compact = not self.is_compact
        self.set_compact_state()
        # Request a sidebar refresh from the main window to sync the current session ID
        main_window = self.window()
        if hasattr(main_window, 'refresh_sidebar'):
            main_window.refresh_sidebar()


    def set_compact_state(self):
        # We must clear and rebuild the layout because we are switching
        # between a vertical stack (compact) and a horizontal row (expanded).
        while self.header_layout.count():
            item = self.header_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                while item.layout().count():
                    layout_item = item.layout().takeAt(0)
                    if layout_item.widget():
                        layout_item.widget().setParent(None)

        if self.is_compact:
            self.setFixedWidth(50)
            self.new_chat_btn.setText("+")
            self.settings_btn.setText("⚙")
            self.collapse_btn.setText("➡")

            # Fixed sizes for compact mode to ensure buttons are perfectly square
            self.new_chat_btn.setFixedSize(30, 30)
            self.collapse_btn.setFixedSize(30, 30)
            self.settings_btn.setFixedSize(30, 30)

            # Stacked vertically: Collapse on top, then New Chat
            self.header_layout.addWidget(self.collapse_btn)
            self.header_layout.addWidget(self.new_chat_btn)
            self.history_list.setFixedWidth(30)
        else:
            self.setFixedWidth(250)
            self.new_chat_btn.setText("+ New Chat")
            self.settings_btn.setText("⚙ Settings")
            self.collapse_btn.setText("⬅")

            # Reset sizes for expanded mode so the New Chat button can grow
            self.new_chat_btn.setMinimumWidth(0)
            self.new_chat_btn.setMaximumWidth(16777215)
            self.collapse_btn.setFixedSize(30, 30)
            self.settings_btn.setMinimumWidth(0)
            self.settings_btn.setMaximumWidth(16777215)

            # Row layout: [New Chat (Expanding)] [Stretch] [Collapse (Fixed)]
            top_row = QHBoxLayout()
            top_row.addWidget(self.new_chat_btn)
            top_row.addStretch()
            top_row.addWidget(self.collapse_btn)
            self.header_layout.addLayout(top_row)
            self.history_list.setFixedWidth(230)

        self.refresh_history_display()

    def on_item_clicked(self, item):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if session_id is not None:
            # Keep highlight state in sync when the list is rebuilt (e.g. compact toggle)
            self._current_session_id = session_id
            self.session_selected.emit(session_id)

    def contextMenuEvent(self, event):
        # Map the event position from Sidebar coordinates to QListWidget coordinates
        list_pos = self.history_list.mapFromParent(event.pos())
        index = self.history_list.indexAt(list_pos)

        if index.isValid():
            item = self.history_list.item(index.row())
            session_id = item.data(Qt.ItemDataRole.UserRole)
            session_title = item.text()

            from PySide6.QtWidgets import QMenu, QMessageBox
            menu = QMenu(self)
            delete_action = menu.addAction("Delete Chat")

            action = menu.exec(event.globalPos())
            if action == delete_action:
                # Show confirmation dialog
                confirm = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete '{session_title}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if confirm == QMessageBox.StandardButton.Yes:
                    self.session_deleted.emit(session_id)

    def update_history(self, sessions, current_session_id=None):
        self._last_sessions = sessions
        self._current_session_id = current_session_id
        self.refresh_history_display()

    def refresh_history_display(self):
        if not hasattr(self, '_last_sessions'):
            return

        self.history_list.clear()
        active_id = getattr(self, '_current_session_id', None)
        selected_row = None
        for session_id, title in self._last_sessions:
            display_text = "●" if self.is_compact else title
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, session_id)
            if self.is_compact:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Highlight the currently active session
            row = self.history_list.count()
            self.history_list.addItem(item)
            if session_id == active_id:
                selected_row = row

        if selected_row is not None:
            self.history_list.setCurrentRow(selected_row)

        # Ensure the selection is visually updated
        self.history_list.update()


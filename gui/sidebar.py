from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel,
)
from PySide6.QtCore import Signal, Qt

class Sidebar(QWidget):
    session_selected = Signal(int)
    new_chat_requested = Signal()
    settings_requested = Signal()
    session_deleted = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.is_compact = False
        self.setFixedWidth(250)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 16, 14, 16)
        self.layout.setSpacing(12)

        self.brand_block = QWidget()
        brand_layout = QVBoxLayout(self.brand_block)
        brand_layout.setContentsMargins(4, 0, 0, 4)
        brand_layout.setSpacing(2)

        self.brand_title = QLabel("BetAssist")
        self.brand_title.setObjectName("sidebarBrand")
        self.brand_tagline = QLabel("Betting analyst")
        self.brand_tagline.setObjectName("sidebarTagline")
        brand_layout.addWidget(self.brand_title)
        brand_layout.addWidget(self.brand_tagline)

        # Top Header Area
        self.header_layout = QVBoxLayout()

        # Define buttons
        self.new_chat_btn = QPushButton("+ New Chat")
        self.new_chat_btn.setObjectName("sidebarNewChat")
        self.new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_chat_btn.clicked.connect(lambda: self.new_chat_requested.emit())

        self.collapse_btn = QPushButton("‹")
        self.collapse_btn.setObjectName("sidebarIconBtn")
        self.collapse_btn.setFixedSize(34, 34)
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.clicked.connect(self.toggle_compact)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setObjectName("sidebarSettings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(lambda: self.settings_requested.emit())

        self.history_label = QLabel("RECENT")
        self.history_label.setObjectName("sidebarSectionLabel")

        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_list.setFixedWidth(222)
        self.history_list.itemClicked.connect(self.on_item_clicked)

        self.set_compact_state()
        self.layout.addWidget(self.brand_block)
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.history_label)
        self.layout.addWidget(self.history_list, 1)

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
            self.setFixedWidth(56)
            self.brand_block.setVisible(False)
            self.history_label.setVisible(False)
            self.new_chat_btn.setText("+")
            self.settings_btn.setText("⚙")
            self.collapse_btn.setText("›")

            self.new_chat_btn.setFixedSize(34, 34)
            self.collapse_btn.setFixedSize(34, 34)
            self.settings_btn.setFixedSize(34, 34)
            self.new_chat_btn.setObjectName("sidebarIconBtn")
            self.settings_btn.setObjectName("sidebarIconBtn")

            self.header_layout.addWidget(self.collapse_btn)
            self.header_layout.addWidget(self.new_chat_btn)
            self.history_list.setFixedWidth(28)
        else:
            self.setFixedWidth(250)
            self.brand_block.setVisible(True)
            self.history_label.setVisible(True)
            self.new_chat_btn.setText("+ New Chat")
            self.settings_btn.setText("⚙ Settings")
            self.collapse_btn.setText("‹")

            self.new_chat_btn.setObjectName("sidebarNewChat")
            self.settings_btn.setObjectName("sidebarSettings")

            self.new_chat_btn.setMinimumSize(0, 0)
            self.new_chat_btn.setMaximumSize(16777215, 16777215)
            self.collapse_btn.setFixedSize(34, 34)
            self.settings_btn.setMinimumSize(0, 0)
            self.settings_btn.setMaximumSize(16777215, 16777215)

            # Row layout: [New Chat (Expanding)] [Stretch] [Collapse (Fixed)]
            top_row = QHBoxLayout()
            top_row.setSpacing(8)
            top_row.addWidget(self.new_chat_btn)
            top_row.addStretch()
            top_row.addWidget(self.collapse_btn)
            self.header_layout.addLayout(top_row)
            self.history_list.setFixedWidth(222)

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
                if session_id == active_id:
                    item.setForeground(Qt.GlobalColor.green)

            # Highlight the currently active session
            row = self.history_list.count()
            self.history_list.addItem(item)
            if session_id == active_id:
                selected_row = row

        if selected_row is not None:
            self.history_list.setCurrentRow(selected_row)

        # Ensure the selection is visually updated
        self.history_list.update()

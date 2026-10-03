from PySide6.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QWidget, QLabel
from PySide6.QtCore import Qt, QTimer

from message import Message


class MessageArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("messageArea")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.scrollArea = QScrollArea()
        self.scrollArea.setObjectName("messageScroll")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)

        self.content = QWidget()
        self.content.setObjectName("messageContent")

        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(28, 24, 28, 24)
        self.layout.setSpacing(14)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.empty_state = QWidget()
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(8)

        empty_title = QLabel("Start a conversation")
        empty_title.setObjectName("chatEmptyTitle")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_hint = QLabel(
            "Ask for ticket ideas, edge analysis, or chat about today's fixtures."
        )
        empty_hint.setObjectName("chatEmptyHint")
        empty_hint.setWordWrap(True)
        empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_hint.setMaximumWidth(420)

        empty_layout.addStretch()
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_hint)
        empty_layout.addStretch()

        self.layout.addWidget(self.empty_state)

        self.scrollArea.setWidget(self.content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scrollArea)

    def _hide_empty_state(self):
        self.empty_state.setVisible(False)

    def clear_messages(self):
        i = 0
        while i < self.layout.count():
            item = self.layout.itemAt(i)
            widget = item.widget() if item else None
            if widget is self.empty_state:
                i += 1
                continue
            if widget:
                self.layout.takeAt(i)
                widget.deleteLater()
            else:
                i += 1
        self.show_empty_state()

    def add_message(self, text, sender="User"):
        self._hide_empty_state()

        role_label = "YOU" if sender == "User" else "ANALYST"
        message = Message(role_label, text, sender=sender)
        self.layout.addWidget(message)
        QTimer.singleShot(0, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        bar = self.scrollArea.verticalScrollBar()
        bar.setValue(bar.maximum())

    def show_empty_state(self):
        if self.layout.indexOf(self.empty_state) < 0:
            self.layout.insertWidget(0, self.empty_state)
        self.empty_state.setVisible(True)

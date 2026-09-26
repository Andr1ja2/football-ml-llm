from PySide6.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QWidget
from PySide6.QtCore import Qt

from message import Message


class MessageArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.Box)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)

        self.content = QWidget()

        self.layout = QVBoxLayout(self.content)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scrollArea.setWidget(self.content)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scrollArea)

    def add_message(self, text, sender="User"):
        label = "𖨆 User" if sender == "User" else "모 Agent"
        message = Message(label, text)
        self.layout.addWidget(message)
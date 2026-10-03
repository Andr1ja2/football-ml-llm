from PySide6.QtWidgets import QFrame, QPushButton, QTextEdit, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent

# Allow sending message via "Enter" key but keep new line key as "Shift + Enter"
class TextBox(QTextEdit):
    enter_pressed = Signal()

    def keyPressEvent(self, event: QKeyEvent):
        if (event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
            self.enter_pressed.emit()
            return

        super().keyPressEvent(event)

class TextArea(QFrame):
    message_sent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("textArea")
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 8, 20, 8)
        layout.setSpacing(12)

        self.textBox = TextBox()
        self.textBox.setObjectName("composerInput")
        self.textBox.setMinimumHeight(60)
        self.textBox.setMaximumHeight(90)
        self.textBox.setPlaceholderText("Message the analyst…  (Enter to send, Shift+Enter for new line)")

        self.sendButton = QPushButton("➤ Send")
        self.sendButton.setObjectName("composerSend")
        self.sendButton.setMinimumHeight(60)
        self.sendButton.setMaximumHeight(90)
        self.sendButton.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding
        )
        self.sendButton.clicked.connect(self.send_message)
        self.textBox.enter_pressed.connect(self.send_message)
        self.sendButton.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.textBox, 1)
        layout.addWidget(self.sendButton)

    def send_message(self):
        text = self.textBox.toPlainText().strip()

        if not text:
            return

        self.message_sent.emit(text)
        self.textBox.clear()

    def set_enabled(self, enabled: bool):
        self.sendButton.setEnabled(enabled)
        self.textBox.setEnabled(enabled)

from PySide6.QtWidgets import QFrame, QPushButton, QTextEdit, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTextEdit

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

        self.setFrameShape(QFrame.Shape.Box)

        layout = QHBoxLayout(self) 

        self.textBox = TextBox()
        self.sendButton = QPushButton('Send')
        self.sendButton.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.sendButton.clicked.connect(self.send_message)
        self.textBox.enter_pressed.connect(self.send_message)
        self.sendButton.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.textBox, 9)
        layout.addWidget(self.sendButton, 1)

    def send_message(self):
        text = self.textBox.toPlainText().strip()

        if not text:
            return

        self.message_sent.emit(text)
        self.textBox.clear()

    def set_enabled(self, enabled: bool):
        self.sendButton.setEnabled(enabled)


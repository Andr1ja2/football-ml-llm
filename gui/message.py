from PySide6.QtWidgets import QFrame, QVBoxLayout, QTextEdit, QLabel, QSizePolicy
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

# Class allows text to resize based on the needed hight and allowed width
class MessageTextEdit(QTextEdit):
    def __init__(self, text="", parent=None):
        super().__init__(parent)

        self.setPlainText(text)
        self.setReadOnly(True)

        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.setSizeAdjustPolicy(
            QTextEdit.SizeAdjustPolicy.AdjustIgnored
        )

        QTimer.singleShot(0, self.update_height)

    def update_height(self):
        document_height = self.document().documentLayout().documentSize().height()
        margins = self.contentsMargins()

        self.setFixedHeight(
            int(document_height)
            + margins.top()
            + margins.bottom()
            + 8
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_height)


class Message(QFrame):
    def __init__(self, user, text, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.Box)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum
        )

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.user = QLabel(user)

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.user.setFont(font)

        self.text = MessageTextEdit(text)

        self.layout.addWidget(self.user)
        self.layout.addWidget(self.text)
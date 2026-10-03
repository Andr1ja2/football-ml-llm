from PySide6.QtWidgets import QFrame, QVBoxLayout, QTextEdit, QLabel, QSizePolicy
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

# Class allows text to resize based on the needed hight and allowed width
class MessageTextEdit(QTextEdit):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setObjectName("messageBody")

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
        # Guard against race conditions where this timer fires after the widget is destroyed
        if not self.document() or not self.document().documentLayout():
            return

        try:
            document_height = self.document().documentLayout().documentSize().height()
            margins = self.contentsMargins()

            self.setFixedHeight(
                int(document_height)
                + margins.top()
                + margins.bottom()
                + 8
            )
        except (AttributeError, RuntimeError):
            # Catch cases where C++ objects are deleted while the Python call is in progress
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_height)


class Message(QFrame):
    def __init__(self, user, text, sender="User", parent=None):
        super().__init__(parent)

        is_user = sender == "User"
        self.setObjectName("messageUser" if is_user else "messageAssistant")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum
        )

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 12)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.user = QLabel(user)
        self.user.setObjectName("messageRoleUser" if is_user else "messageRoleAssistant")

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.user.setFont(font)

        self.text = MessageTextEdit(text)

        self.layout.addWidget(self.user)
        self.layout.addWidget(self.text)

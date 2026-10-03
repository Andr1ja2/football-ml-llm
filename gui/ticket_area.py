from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt


class TicketArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ticketArea")
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 22, 20, 20)
        layout.setSpacing(16)

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        title = QLabel("TICKET SLIP")
        title.setObjectName("ticketPanelTitle")

        subtitle = QLabel("Generated selections appear here")
        subtitle.setObjectName("ticketPanelSubtitle")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

        empty_card = QFrame()
        empty_card.setObjectName("ticketEmptyCard")
        card_layout = QVBoxLayout(empty_card)
        card_layout.setContentsMargins(16, 24, 16, 24)

        empty_text = QLabel(
            "No active ticket yet.\n\n"
            "Request a combo from the chat and leg details will show in this panel."
        )
        empty_text.setObjectName("ticketEmptyText")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text.setWordWrap(True)

        card_layout.addWidget(empty_text)
        layout.addWidget(empty_card)
        layout.addStretch()

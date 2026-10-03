from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt

class TicketReceipt(QFrame):
    def __init__(self, ticket_data, index, parent=None):
        super().__init__(parent)
        self.setObjectName("ticketReceipt")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QLabel(f"TICKET #{index + 1}")
        header.setObjectName("ticketReceiptHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setWordWrap(True)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(header)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setLineWidth(1)
        line.setStyleSheet("background-color: #2a3544;")
        layout.addWidget(line)

        # Legs
        for leg in ticket_data["legs"]:
            leg_widget = QWidget()
            leg_layout = QHBoxLayout(leg_widget)
            leg_layout.setContentsMargins(0, 4, 0, 4)

            match_label = QLabel(leg["match"])
            match_label.setObjectName("ticketLegMatch")
            match_label.setWordWrap(True)
            # Let match label take as much space as possible
            match_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            outcome_label = QLabel(f"{leg['outcome']} ({leg['odds']}x)")
            outcome_label.setObjectName("ticketLegOutcome")
            outcome_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            # Allow the outcome to shrink but stay visible
            outcome_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

            leg_layout.addWidget(match_label, 1)
            leg_layout.addWidget(outcome_label)
            layout.addWidget(leg_widget)

        # Divider
        layout.addWidget(line)

        # Footer
        footer_layout = QHBoxLayout()
        odds_label = QLabel(f"Total Odds: {ticket_data['combo_odds']:.2f}")
        odds_label.setObjectName("ticketReceiptFooter")
        odds_label.setWordWrap(True)
        odds_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        ev_label = QLabel(f"EV: {ticket_data['expected_value']:.2%}")
        ev_label.setObjectName("ticketReceiptFooter")
        ev_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        ev_label.setWordWrap(True)
        ev_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        footer_layout.addWidget(odds_label, 1)
        footer_layout.addWidget(ev_label)
        layout.addLayout(footer_layout)


class TicketArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ticketArea")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 22, 20, 20)
        self.main_layout.setSpacing(16)

        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        title = QLabel("TICKET SLIP")
        title.setObjectName("ticketPanelTitle")
        title.setWordWrap(True)

        subtitle = QLabel("Generated selections appear here")
        subtitle.setObjectName("ticketPanelSubtitle")
        subtitle.setWordWrap(True)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.main_layout.addWidget(header)

        # Scroll Area for Tickets
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.container = QWidget()
        self.container.setObjectName("ticketContainer")
        self.ticket_layout = QVBoxLayout(self.container)
        self.ticket_layout.setContentsMargins(0, 0, 0, 0)
        self.ticket_layout.setSpacing(12)
        self.ticket_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        # Empty State
        self.empty_card = QFrame()
        self.empty_card.setObjectName("ticketEmptyCard")
        card_layout = QVBoxLayout(self.empty_card)
        card_layout.setContentsMargins(16, 24, 16, 24)

        empty_text = QLabel(
            "No active ticket yet.\n\n"
            "Request a combo from the chat and leg details will show in this panel."
        )
        empty_text.setObjectName("ticketEmptyText")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text.setWordWrap(True)

        card_layout.addWidget(empty_text)
        self.ticket_layout.addWidget(self.empty_card)

        self.tickets_count = 0

    def add_ticket(self, ticket_data):
        # Remove empty card on first ticket
        if self.tickets_count == 0:
            # We don't delete the card, we just hide it or keep it in a way
            # that doesn't trigger C++ deletion if we want to reuse it.
            # But the safest way in Qt is to just not remove it if we aren't sure.
            # Instead, let's just hide it.
            if self.empty_card:
                self.empty_card.hide()

        receipt = TicketReceipt(ticket_data, self.tickets_count)
        # Insert the new ticket at the top (index 0) of the layout
        self.ticket_layout.insertWidget(0, receipt)
        self.tickets_count += 1

    def clear_tickets(self):
        """Removes all ticket receipts and restores the empty state."""
        # Remove all widgets from the ticket layout
        while self.ticket_layout.count() > 0:
            item = self.ticket_layout.takeAt(0)
            widget = item.widget()
            if widget:
                if widget != self.empty_card:
                    widget.deleteLater()
                else:
                    # If we encounter the empty card, we have it in hand.
                    # We can just keep it.
                    pass

        self.tickets_count = 0

        # Restore empty card
        if self.empty_card:
            self.empty_card.show()
            # In Qt, if takeAt(0) removed the empty_card, we must add it back.
            # Since we just cleared the layout, we just add it.
            self.ticket_layout.addWidget(self.empty_card)

    def load_tickets(self, tickets_list):
        """Clears the current area and loads a list of tickets."""
        self.clear_tickets()
        for ticket in tickets_list:
            self.add_ticket(ticket)

"""Central theme tokens and Qt stylesheets for the application."""

# —— Palette: ——
BG_BASE = "#0a0e14"
BG_ELEVATED = "#111820"
BG_SURFACE = "#171f2a"
BG_HOVER = "#1e2836"
BG_INPUT = "#121922"

BORDER = "#2a3544"
BORDER_FOCUS = "#3dd68c"

TEXT_PRIMARY = "#e8eef4"
TEXT_SECONDARY = "#8fa3b8"
TEXT_MUTED = "#5c6f82"

ACCENT = "#3dd68c"
ACCENT_HOVER = "#56e89d"
ACCENT_PRESSED = "#2eb872"
ACCENT_MUTED = "#1a3d2e"

USER_ACCENT = "#58a6ff"
USER_BG = "#152238"
AGENT_BG = "#171f2a"

DANGER = "#f07178"
WARNING = "#e3b341"

RADIUS_SM = "6px"
RADIUS_MD = "10px"
RADIUS_LG = "14px"

FONT_FAMILY = '"Segoe UI", "SF Pro Text", "Ubuntu", "Cantarell", sans-serif'
FONT_MONO = '"Cascadia Code", "SF Mono", "Consolas", monospace'


def app_stylesheet() -> str:
    return f"""
    * {{
        font-family: {FONT_FAMILY};
    }}

    QMainWindow, QDialog {{
        background-color: {BG_BASE};
        color: {TEXT_PRIMARY};
    }}

    QWidget#chatContainer {{
        background-color: {BG_BASE};
    }}

    QWidget#ticketContainer {{
        background-color: {BG_ELEVATED};
        border-left: 1px solid {BORDER};
    }}

    /* —— Splitter —— */
    QSplitter::handle {{
        background-color: {BORDER};
        width: 1px;
    }}
    QSplitter::handle:hover {{
        background-color: {ACCENT_MUTED};
    }}

    /* —— Scroll bars —— */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 4px 2px 4px 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BG_HOVER};
        border-radius: 5px;
        min-height: 32px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {BORDER};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        height: 0;
    }}

    /* —— Sidebar —— */
    QWidget#sidebar {{
        background-color: {BG_ELEVATED};
        border-right: 1px solid {BORDER};
    }}
    QLabel#sidebarBrand {{
        color: {TEXT_PRIMARY};
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    QLabel#sidebarTagline {{
        color: {TEXT_MUTED};
        font-size: 11px;
        font-weight: 500;
    }}
    QLabel#sidebarSectionLabel {{
        color: {TEXT_MUTED};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.12em;
        padding: 4px 4px 0 4px;
    }}
    QPushButton#sidebarNewChat {{
        background-color: {ACCENT_MUTED};
        color: {ACCENT};
        border: 1px solid #2a5c44;
        border-radius: {RADIUS_MD};
        padding: 10px 14px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton#sidebarNewChat:hover {{
        background-color: #234a38;
        border-color: {ACCENT};
        color: {ACCENT_HOVER};
    }}
    QPushButton#sidebarNewChat:pressed {{
        background-color: #1a3d2e;dark sports-terminal (pitch green accent) 
    }}
    QPushButton#sidebarIconBtn {{
        background-color: {BG_SURFACE};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_SM};
        padding: 0;
        font-size: 14px;
    }}
    QPushButton#sidebarIconBtn:hover {{
        background-color: {BG_HOVER};
        color: {TEXT_PRIMARY};
        border-color: #3d4d61;
    }}
    QPushButton#sidebarSettings {{
        background-color: transparent;
        color: {TEXT_SECONDARY};
        border: 1px solid transparent;
        border-radius: {RADIUS_MD};
        padding: 10px 14px;
        font-size: 13px;
        text-align: left;
    }}
    QPushButton#sidebarSettings:hover {{
        background-color: {BG_HOVER};
        color: {TEXT_PRIMARY};
        border-color: {BORDER};
    }}
    QListWidget#historyList {{
        background-color: transparent;
        border: none;
        outline: none;
        padding: 4px 0;
    }}
    QListWidget#historyList::item {{
        color: {TEXT_SECONDARY};
        padding: 10px 12px;
        border-radius: {RADIUS_SM};
        margin: 2px 0;
        border-left: 3px solid transparent;
    }}
    QListWidget#historyList::item:hover {{
        background-color: {BG_HOVER};
        color: {TEXT_PRIMARY};
    }}
    QListWidget#historyList::item:selected {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border-left: 3px solid {ACCENT};
    }}

    /* —— Message area —— */
    QFrame#messageArea {{
        background-color: {BG_BASE};
        border: none;
    }}
    QScrollArea#messageScroll {{
        background-color: transparent;
        border: none;
    }}
    QWidget#messageContent {{
        background-color: transparent;
    }}
    QLabel#chatEmptyTitle {{
        color: {TEXT_SECONDARY};
        font-size: 18px;
        font-weight: 600;
    }}
    QLabel#chatEmptyHint {{
        color: {TEXT_MUTED};
        font-size: 13px;
    }}

    QFrame#messageUser {{
        background-color: {USER_BG};
        border: 1px solid #243552;
        border-radius: {RADIUS_LG};
        border-top-right-radius: 4px;
    }}
    QFrame#messageAssistant {{
        background-color: {AGENT_BG};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_LG};
        border-top-left-radius: 4px;
    }}
    QLabel#messageRoleUser {{
        color: {USER_ACCENT};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
    }}
    QLabel#messageRoleAssistant {{
        color: {ACCENT};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
    }}
    QTextEdit#messageBody {{
        background-color: transparent;
        color: {TEXT_PRIMARY};
        border: none;
        font-size: 14px;
        line-height: 1.45;
        selection-background-color: {ACCENT_MUTED};
        selection-color: {TEXT_PRIMARY};
    }}

    /* —— Composer —— */
    QFrame#textArea {{
        background-color: {BG_ELEVATED};
        border: none;
        border-top: 1px solid {BORDER};
    }}
    QTextEdit#composerInput {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_LG};
        padding: 12px 16px;
        font-size: 14px;
        selection-background-color: {ACCENT_MUTED};
    }}
    QTextEdit#composerInput:focus {{
        border-color: {BORDER_FOCUS};
    }}
    QPushButton#composerSend {{
        background-color: {ACCENT};
        color: #062a1a;
        border: none;
        border-radius: {RADIUS_LG};
        font-weight: 700;
        font-size: 15px;
        padding: 0 20px;
        min-width: 88px;
    }}
    QPushButton#composerSend:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton#composerSend:pressed {{
        background-color: {ACCENT_PRESSED};
    }}
    QPushButton#composerSend:disabled {{
        background-color: {BG_HOVER};
        color: {TEXT_MUTED};
    }}

    QPushButton#ticketCollapseBtn {{
        background-color: {BG_SURFACE};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: 18px;
        font-size: 15px;
    }}
    QPushButton#ticketCollapseBtn:hover {{
        background-color: {BG_HOVER};
        color: {ACCENT};
        border-color: #3d4d61;
    }}

    /* —— Ticket panel —— */
    QFrame#ticketArea {{
        background-color: transparent;
        border: none;
    }}
    QFrame#ticketReceipt {{
        background-color: {BG_SURFACE};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_MD};
    }}
    QLabel#ticketReceiptHeader {{
        color: {ACCENT};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
    }}
    QLabel#ticketLegMatch {{
        color: {TEXT_SECONDARY};
        font-size: 12px;
    }}
    QLabel#ticketLegOutcome {{
        color: {TEXT_PRIMARY};
        font-size: 12px;
        font-weight: 600;
    }}
    QLabel#ticketReceiptFooter {{
        color: {TEXT_MUTED};
        font-size: 11px;
        font-weight: 600;
    }}
    QLabel#ticketPanelTitle {{
        color: {TEXT_PRIMARY};
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.06em;
    }}

    QLabel#ticketPanelSubtitle {{
        color: {TEXT_MUTED};
        font-size: 11px;
    }}
    QFrame#ticketEmptyCard {{
        background-color: {BG_SURFACE};
        border: 1px dashed {BORDER};
        border-radius: {RADIUS_MD};
    }}
    QLabel#ticketEmptyText {{
        color: {TEXT_MUTED};
        font-size: 12px;
    }}

    /* —— Settings —— */
    QDialog#settingsDialog {{
        background-color: {BG_ELEVATED};
    }}
    QLabel#settingsTitle {{
        font-size: 20px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
    }}
    QLabel#settingsSubtitle {{
        font-size: 12px;
        color: {TEXT_MUTED};
        margin-bottom: 8px;
    }}
    QLabel#settingsSectionTitle {{
        font-size: 14px;
        font-weight: 600;
        color: {TEXT_PRIMARY};
        margin-top: 4px;
    }}
    QLabel#settingsLlmStatus {{
        font-size: 11px;
        color: {TEXT_MUTED};
    }}
    QComboBox#llmModelCombo {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_SM};
        padding: 6px 10px;
        min-height: 28px;
    }}
    QComboBox#llmModelCombo:focus {{
        border-color: {BORDER_FOCUS};
    }}
    QComboBox#llmModelCombo:disabled {{
        color: {TEXT_MUTED};
    }}
    QPushButton#settingsRefreshModels {{
        min-height: 28px;
        padding: 6px 12px;
    }}
    QLabel {{
        color: {TEXT_SECONDARY};
        font-size: 13px;
    }}
    QDoubleSpinBox, QSpinBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_SM};
        padding: 6px 10px;
        min-height: 28px;
    }}
    QDoubleSpinBox:focus, QSpinBox:focus {{
        border-color: {BORDER_FOCUS};
    }}
    QDoubleSpinBox::up-button, QSpinBox::up-button,
    QDoubleSpinBox::down-button, QSpinBox::down-button {{
        background-color: {BG_HOVER};
        border: none;
        width: 18px;
    }}
    QPushButton#settingsSave {{
        background-color: {ACCENT};
        color: #062a1a;
        border: none;
        border-radius: {RADIUS_SM};
        padding: 8px 20px;
        font-weight: 700;
    }}
    QPushButton#settingsSave:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton#settingsCancel, QPushButton#settingsRestore {{
        background-color: {BG_SURFACE};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_SM};
        padding: 8px 16px;
        font-weight: 600;
    }}
    QPushButton#settingsCancel:hover, QPushButton#settingsRestore:hover {{
        background-color: {BG_HOVER};
        color: {TEXT_PRIMARY};
    }}

    QMenu {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_SM};
        padding: 4px;
    }}
    QMenu::item {{
        padding: 8px 24px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {BG_HOVER};
    }}

    QMessageBox {{
        background-color: {BG_ELEVATED};
    }}
    QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
    }}
    QMessageBox QPushButton {{
        background-color: {BG_SURFACE};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: {RADIUS_SM};
        padding: 6px 16px;
        min-width: 72px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {BG_HOVER};
    }}
    """


def apply_app_style(app) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(app_stylesheet())

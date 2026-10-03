from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
import sys
import os

# Add project root and src directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'src'))

from window import MainWindow
from styles import apply_app_style


app = QApplication(sys.argv)
app.setApplicationName("BetAssist")
app.setApplicationDisplayName("BetAssist")

font = QFont()
font.setFamilies(["Segoe UI", "SF Pro Text", "Ubuntu", "Cantarell", "sans-serif"])
font.setPointSize(10)
app.setFont(font)

apply_app_style(app)

window = MainWindow()
window.show()
sys.exit(app.exec())

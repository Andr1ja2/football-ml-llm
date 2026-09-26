from PySide6.QtWidgets import QApplication
import sys
import os

# Add project root and src directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'src'))

from window import MainWindow


app = QApplication()
window = MainWindow()
window.show()
app.exec()
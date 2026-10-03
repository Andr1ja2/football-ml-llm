from PySide6.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from src.live_config import settings_manager

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Settings")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Dynamic generation of fields based on settings.json
        self.inputs = {}

        # We only want to edit the threshold constants
        editable_keys = [
            "MIN_EDGE_1X2_HOME",
            "MIN_EDGE_BTTS",
            "MIN_MODEL_PROB_BTTS",
            "MIN_EDGE_OU25",
            "MIN_MODEL_PROB_OU25",
            "MAX_LEGS"
        ]

        for key in editable_keys:
            current_val = settings_manager.get(key, 0.0)
            if key == "MAX_LEGS":
                spin = QSpinBox() # Use integer spinbox for legs
                spin.setRange(1, 10)
                spin.setValue(int(current_val))
            else:
                spin = QDoubleSpinBox()
                spin.setRange(0.0, 1.0)
                spin.setSingleStep(0.01)
                spin.setValue(float(current_val))
            form.addRow(key.replace("_", " ").title(), spin)
            self.inputs[key] = spin

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        self.restore_btn = QPushButton("Restore Defaults")
        self.restore_btn.clicked.connect(self.restore_defaults)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.restore_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def save_settings(self):
        for key, spin in self.inputs.items():
            settings_manager.set(key, spin.value())

        settings_manager.save_settings()
        self.accept()

    def restore_defaults(self):
        settings_manager.restore_defaults()
        # Update the UI to reflect the restored defaults
        for key, spin in self.inputs.items():
            spin.setValue(float(settings_manager.get(key, 0.0)))


from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QComboBox,
)
from PySide6.QtCore import Qt
from src.live_config import settings_manager, DEFAULT_SETTINGS
from src.llm_client import get_installed_models

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle("Settings")
        self.setFixedSize(440, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        title = QLabel("Settings")
        title.setObjectName("settingsTitle")
        subtitle = QLabel(
            "Choose a local Ollama model and tune edge and probability cutoffs "
            "used when building tickets."
        )
        subtitle.setObjectName("settingsSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

        llm_header = QLabel("LLM")
        llm_header.setObjectName("settingsSectionTitle")
        layout.addWidget(llm_header)

        llm_form = QFormLayout()
        llm_form.setSpacing(14)
        llm_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        llm_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        model_row = QHBoxLayout()
        model_row.setSpacing(8)
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("llmModelCombo")
        self.refresh_models_btn = QPushButton("Refresh")
        self.refresh_models_btn.setObjectName("settingsRefreshModels")
        self.refresh_models_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_models_btn.clicked.connect(self.refresh_model_list)
        model_row.addWidget(self.model_combo, stretch=1)
        model_row.addWidget(self.refresh_models_btn)
        llm_form.addRow("Model", model_row)

        self.llm_status_label = QLabel()
        self.llm_status_label.setObjectName("settingsLlmStatus")
        self.llm_status_label.setWordWrap(True)
        llm_form.addRow("", self.llm_status_label)

        layout.addLayout(llm_form)

        thresholds_header = QLabel("Model thresholds")
        thresholds_header.setObjectName("settingsSectionTitle")
        layout.addWidget(thresholds_header)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        # Dynamic generation of fields based on settings.json
        self.inputs = {}

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
            label = QLabel(key.replace("_", " ").title())
            if key == "MAX_LEGS":
                spin = QSpinBox()
                spin.setRange(1, 10)
                spin.setValue(int(current_val))
            else:
                spin = QDoubleSpinBox()
                spin.setRange(0.0, 1.0)
                spin.setSingleStep(0.01)
                spin.setDecimals(3)
                spin.setValue(float(current_val))
            form.addRow(label, spin)
            self.inputs[key] = spin

        layout.addLayout(form)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.restore_btn = QPushButton("Restore defaults")
        self.restore_btn.setObjectName("settingsRestore")
        self.restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restore_btn.clicked.connect(self.restore_defaults)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("settingsSave")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_settings)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("settingsCancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.restore_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        self.refresh_model_list()

    def _saved_model_name(self) -> str:
        return (settings_manager.get("LLM_MODEL") or "").strip()

    def _update_llm_status(self, server_online: bool, models: list[str]) -> None:
        saved = self._saved_model_name()
        if server_online:
            if saved and saved not in models:
                self.llm_status_label.setText(
                    f"Saved model \"{saved}\" is not in the list returned by Ollama "
                    "(it may have been removed). You can still keep it if it remains on disk."
                )
            elif saved:
                self.llm_status_label.setText(f"Using saved model: {saved}")
            else:
                self.llm_status_label.setText(
                    "Select a model you installed in Ollama, then save."
                )
        else:
            if saved:
                self.llm_status_label.setText(
                    f"Ollama server unreachable. Saved model: {saved}"
                )
            else:
                self.llm_status_label.setText(
                    "Ollama server unreachable. Start Ollama and refresh to choose a model."
                )

    def refresh_model_list(self) -> None:
        previous = self.model_combo.currentData() or self.model_combo.currentText()
        if previous in ("", "Server unreachable"):
            previous = self._saved_model_name()

        models = get_installed_models()
        self.model_combo.clear()

        if not models:
            self.model_combo.addItem("Server unreachable", "")
            self.model_combo.setEnabled(False)
            self._update_llm_status(server_online=False, models=[])
            return

        self.model_combo.setEnabled(True)
        saved = self._saved_model_name()
        if saved and saved not in models:
            models = [saved, *models]

        for name in models:
            self.model_combo.addItem(name, name)

        target = previous if previous in models else saved
        if target:
            idx = self.model_combo.findData(target)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.setCurrentIndex(-1)

        self._update_llm_status(server_online=True, models=models)

    def _selected_model_for_save(self) -> str:
        if not self.model_combo.isEnabled():
            return self._saved_model_name()
        data = self.model_combo.currentData()
        if data:
            return str(data).strip()
        return ""

    def save_settings(self):
        for key, spin in self.inputs.items():
            settings_manager.set(key, spin.value())

        settings_manager.set("LLM_MODEL", self._selected_model_for_save())

        settings_manager.save_settings()
        self.accept()

    def restore_defaults(self):
        # Update UI to reflect restored defaults while keeping saved model unchanged
        saved_model = settings_manager.get("LLM_MODEL", DEFAULT_SETTINGS["LLM_MODEL"])
        settings_manager.restore_defaults()
        settings_manager.set("LLM_MODEL", saved_model)
        settings_manager.save_settings()

        for key, spin in self.inputs.items():
            if key == "MAX_LEGS":
                spin.setValue(int(settings_manager.get(key, 0)))
            else:
                spin.setValue(float(settings_manager.get(key, 0.0)))

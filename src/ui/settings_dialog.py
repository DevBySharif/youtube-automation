"""
settings_dialog.py
Settings dialog for configuring user preferences.

Configurable options:
  - Default Voice
  - Default Speed
  - Default Whisper Model
  - Keep Temp Files (TTL)
  - Auto-open Output Folder on finish
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSlider, QCheckBox, QPushButton,
    QGroupBox, QFormLayout, QDialogButtonBox,
)
from PySide6.QtCore import Qt, QSettings

from config import VOICES, WHISPER_MODELS, DEFAULT_VOICE, DEFAULT_SPEED, DEFAULT_WHISPER_MODEL


class SettingsDialog(QDialog):
    """Preferences and settings dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences & Settings")
        self.setMinimumWidth(440)
        self._settings = QSettings("TimestampAnalyzer", "App")

        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        # ── Pipeline Defaults Group ───────────────────────────────────────────
        pipe_group = QGroupBox("Pipeline Defaults")
        pipe_layout = QFormLayout(pipe_group)
        pipe_layout.setSpacing(12)

        self.voice_combo = QComboBox()
        for v_id, v_label in VOICES:
            self.voice_combo.addItem(v_label, userData=v_id)
        pipe_layout.addRow("Default Voice:", self.voice_combo)

        speed_row = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(8)
        self.speed_slider.setMaximum(12)
        self.speed_label = QLabel("1.0×")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(f"{v/10.0:.1f}×"))
        speed_row.addWidget(self.speed_slider, stretch=1)
        speed_row.addWidget(self.speed_label)
        pipe_layout.addRow("Default Speed:", speed_row)

        self.model_combo = QComboBox()
        for m_id, m_label in WHISPER_MODELS:
            self.model_combo.addItem(m_label, userData=m_id)
        pipe_layout.addRow("Whisper Model:", self.model_combo)

        layout.addWidget(pipe_group)

        # ── Application Behavior Group ────────────────────────────────────────
        app_group = QGroupBox("Application Behavior")
        app_layout = QVBoxLayout(app_group)
        app_layout.setSpacing(10)

        self.auto_open_cb = QCheckBox("Auto-open output folder when generation finishes")
        app_layout.addWidget(self.auto_open_cb)

        self.keep_temp_cb = QCheckBox("Keep temporary run folders for 24 hours (automatic cleanup)")
        app_layout.addWidget(self.keep_temp_cb)

        layout.addWidget(app_group)

        # ── Dialog Buttons ───────────────────────────────────────────────────
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._save_values)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _load_values(self) -> None:
        voice = self._settings.value("voice", DEFAULT_VOICE)
        speed = float(self._settings.value("speed", DEFAULT_SPEED))
        model = self._settings.value("whisper_model", DEFAULT_WHISPER_MODEL)
        auto_open = self._settings.value("auto_open_folder", "true") == "true"
        keep_temp = self._settings.value("keep_temp_files", "true") == "true"

        for i in range(self.voice_combo.count()):
            if self.voice_combo.itemData(i) == voice:
                self.voice_combo.setCurrentIndex(i)
                break

        self.speed_slider.setValue(round(speed * 10))

        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == model:
                self.model_combo.setCurrentIndex(i)
                break

        self.auto_open_cb.setChecked(auto_open)
        self.keep_temp_cb.setChecked(keep_temp)

    def _save_values(self) -> None:
        self._settings.setValue("voice", self.voice_combo.currentData())
        self._settings.setValue("speed", self.speed_slider.value() / 10.0)
        self._settings.setValue("whisper_model", self.model_combo.currentData())
        self._settings.setValue("auto_open_folder", "true" if self.auto_open_cb.isChecked() else "false")
        self._settings.setValue("keep_temp_files", "true" if self.keep_temp_cb.isChecked() else "false")
        self.accept()

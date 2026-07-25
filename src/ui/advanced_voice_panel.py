"""
advanced_voice_panel.py
Collapsible Advanced Voice Controls Panel featuring:
  • Stability (0-100)
  • Expressiveness (0-100)
  • Clarity (0-100)
  • Energy (0-100)
  • Pitch (-20 to +20 semitones)
  • Volume Gain (-12 dB to +12 dB)
  • Sentence Pause (0 to 1500 ms)
  • Word Pause (0 to 500 ms)
  • Paragraph Pause (0 to 3000 ms)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QFrame, QSpinBox, QDoubleSpinBox,
)
from PySide6.QtCore import Qt, Signal
from voice_engine.narration_modes import AdvancedVoiceSettings


class AdvancedVoicePanel(QFrame):
    """Collapsible panel for advanced voice & timing parameters."""

    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._is_collapsed: bool = True
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 10, 14, 10)
        main_layout.setSpacing(10)

        # Header button to toggle collapse
        self.toggle_btn = QPushButton("⚙️  Advanced Voice Controls  ▼")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9EFF00;
                font-weight: 700;
                font-size: 9pt;
                text-align: left;
                padding: 4px 0;
            }
            QPushButton:hover {
                color: #B8FF3B;
            }
        """)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        main_layout.addWidget(self.toggle_btn)

        # Container Widget for controls
        self.content_widget = QWidget()
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(10)

        # 1. Stability Slider (0-100)
        layout.addLayout(self._create_slider_row("Stability", 0, 100, 75, "%", "stability_slider", "stability_val"))

        # 2. Expressiveness Slider (0-100)
        layout.addLayout(self._create_slider_row("Expressiveness", 0, 100, 80, "%", "expressiveness_slider", "expressiveness_val"))

        # 3. Clarity Slider (0-100)
        layout.addLayout(self._create_slider_row("Clarity", 0, 100, 85, "%", "clarity_slider", "clarity_val"))

        # 4. Energy Slider (0-100)
        layout.addLayout(self._create_slider_row("Energy", 0, 100, 75, "%", "energy_slider", "energy_val"))

        # 5. Pitch Slider (-20 to +20 semitones)
        layout.addLayout(self._create_slider_row("Pitch", -20, 20, 0, " st", "pitch_slider", "pitch_val"))

        # 6. Volume Gain (-12 to +12 dB)
        layout.addLayout(self._create_slider_row("Volume Gain", -12, 12, 0, " dB", "vol_slider", "vol_val"))

        # 7. Sentence Pause (0 to 1500 ms)
        layout.addLayout(self._create_slider_row("Sentence Pause", 0, 1500, 600, " ms", "sentence_pause_slider", "sentence_pause_val"))

        # 8. Word Pause (0 to 500 ms)
        layout.addLayout(self._create_slider_row("Word Pause", 0, 500, 150, " ms", "word_pause_slider", "word_pause_val"))

        # 9. Paragraph Pause (0 to 3000 ms)
        layout.addLayout(self._create_slider_row("Paragraph Pause", 0, 3000, 1200, " ms", "para_pause_slider", "para_pause_val"))

        main_layout.addWidget(self.content_widget)
        self.content_widget.hide()  # Start collapsed by default

    def toggle_collapse(self) -> None:
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self.content_widget.hide()
            self.toggle_btn.setText("⚙️  Advanced Voice Controls  ▼")
        else:
            self.content_widget.show()
            self.toggle_btn.setText("⚙️  Advanced Voice Controls  ▲")

    def _create_slider_row(
        self, label_text: str, min_val: int, max_val: int, default_val: int, suffix: str, slider_attr: str, val_attr: str
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 8.5pt; color: #F5F5F5;")
        row.addWidget(lbl, stretch=1)

        val_lbl = QLabel(f"{default_val}{suffix}")
        val_lbl.setStyleSheet("font-size: 8.5pt; font-weight: 700; color: #9EFF00;")
        setattr(self, val_attr, val_lbl)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setFixedWidth(130)
        setattr(self, slider_attr, slider)

        def update_val(v: int):
            val_lbl.setText(f"{v}{suffix}")
            self.settings_changed.emit()

        slider.valueChanged.connect(update_val)

        row.addWidget(slider)
        row.addWidget(val_lbl)
        return row

    def get_settings(self) -> AdvancedVoiceSettings:
        return AdvancedVoiceSettings(
            speed=1.0,
            stability=self.stability_slider.value(),
            expressiveness=self.expressiveness_slider.value(),
            clarity=self.clarity_slider.value(),
            energy=self.energy_slider.value(),
            pitch_semitones=self.pitch_slider.value(),
            volume_gain_db=float(self.vol_slider.value()),
            sentence_pause_ms=self.sentence_pause_slider.value(),
            word_pause_ms=self.word_pause_slider.value(),
            paragraph_pause_ms=self.para_pause_slider.value(),
        )

    def apply_profile_dict(self, prof: dict) -> None:
        """Apply parameters from a narration profile."""
        if "stability" in prof:
            self.stability_slider.setValue(prof["stability"])
        if "expressiveness" in prof:
            self.expressiveness_slider.setValue(prof["expressiveness"])
        if "clarity" in prof:
            self.clarity_slider.setValue(prof["clarity"])
        if "energy" in prof:
            self.energy_slider.setValue(prof["energy"])
        if "pitch_semitones" in prof:
            self.pitch_slider.setValue(prof["pitch_semitones"])
        if "sentence_pause_ms" in prof:
            self.sentence_pause_slider.setValue(prof["sentence_pause_ms"])
        if "word_pause_ms" in prof:
            self.word_pause_slider.setValue(prof["word_pause_ms"])
        if "paragraph_pause_ms" in prof:
            self.para_pause_slider.setValue(prof["paragraph_pause_ms"])

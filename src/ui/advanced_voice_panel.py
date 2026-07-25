"""
advanced_voice_panel.py
Collapsible Advanced Voice Controls Panel featuring:
  • Grouped Sections: Speech & Tone, Expression & Emotion, Timing & Pauses
  • Double-click slider reset to defaults
  • Numeric Spinboxes & Wheel Support
  • Tooltips & Accessibility
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QFrame, QSpinBox,
)
from PySide6.QtCore import Qt, Signal
from voice_engine.narration_modes import AdvancedVoiceSettings


class ResetSlider(QSlider):
    """Custom slider supporting double-click reset to default value."""

    def __init__(self, orientation, default_val: int, parent=None):
        super().__init__(orientation, parent)
        self.default_val = default_val

    def mouseDoubleClickEvent(self, event):
        self.setValue(self.default_val)
        super().mouseDoubleClickEvent(event)


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
        layout.setSpacing(8)

        # ── SECTION 1: SPEECH & TONE ─────────────────────────────────────────
        layout.addWidget(self._create_section_header("SPEECH & TONE"))
        layout.addLayout(self._create_slider_row("Pitch", -20, 20, 0, " st", "pitch_slider", "pitch_spin", "Pitch shift in semitones"))
        layout.addLayout(self._create_slider_row("Volume Gain", -12, 12, 0, " dB", "vol_slider", "vol_spin", "Volume boost or attenuation in dB"))

        # ── SECTION 2: EXPRESSION & EMOTION ───────────────────────────────
        layout.addWidget(self._create_section_header("EXPRESSION & EMOTION"))
        layout.addLayout(self._create_slider_row("Stability", 0, 100, 75, "%", "stability_slider", "stability_spin", "Voice consistency across sentences"))
        layout.addLayout(self._create_slider_row("Expressiveness", 0, 100, 80, "%", "expressiveness_slider", "expressiveness_spin", "Emotional variation and inflection"))
        layout.addLayout(self._create_slider_row("Clarity", 0, 100, 85, "%", "clarity_slider", "clarity_spin", "Phoneme sharpness and detail"))
        layout.addLayout(self._create_slider_row("Energy", 0, 100, 75, "%", "energy_slider", "energy_spin", "Vocal projection and dynamics"))

        # ── SECTION 3: TIMING & PAUSES ─────────────────────────────────────
        layout.addWidget(self._create_section_header("TIMING & PAUSES"))
        layout.addLayout(self._create_slider_row("Sentence Pause", 0, 1500, 600, " ms", "sentence_pause_slider", "sentence_pause_spin", "Pause duration after full stops"))
        layout.addLayout(self._create_slider_row("Word Pause", 0, 500, 150, " ms", "word_pause_slider", "word_pause_spin", "Pause duration between spoken words"))
        layout.addLayout(self._create_slider_row("Paragraph Pause", 0, 3000, 1200, " ms", "para_pause_slider", "para_pause_spin", "Pause duration between paragraphs"))

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

    def _create_section_header(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 7.5pt; font-weight: 700; color: #9E9E9E; letter-spacing: 1px; margin-top: 6px;")
        return lbl

    def _create_slider_row(
        self, label_text: str, min_val: int, max_val: int, default_val: int, suffix: str, slider_attr: str, spin_attr: str, tooltip: str
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 8.5pt; color: #F5F5F5;")
        lbl.setToolTip(tooltip + " (Double-click slider to reset)")
        row.addWidget(lbl, stretch=1)

        slider = ResetSlider(Qt.Orientation.Horizontal, default_val)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setFixedWidth(110)
        slider.setToolTip(f"{tooltip}\nDouble-click to reset ({default_val}{suffix})")
        setattr(self, slider_attr, slider)

        spin = QSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setValue(default_val)
        spin.setSuffix(suffix)
        spin.setFixedWidth(75)
        setattr(self, spin_attr, spin)

        # Sync slider & spinbox
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        slider.valueChanged.connect(lambda: self.settings_changed.emit())

        row.addWidget(slider)
        row.addWidget(spin)
        return row

    def get_settings(self) -> AdvancedVoiceSettings:
        return AdvancedVoiceSettings(
            speed=1.0,
            stability=self.stability_spin.value(),
            expressiveness=self.expressiveness_spin.value(),
            clarity=self.clarity_spin.value(),
            energy=self.energy_spin.value(),
            pitch_semitones=self.pitch_spin.value(),
            volume_gain_db=float(self.vol_spin.value()),
            sentence_pause_ms=self.sentence_pause_spin.value(),
            word_pause_ms=self.word_pause_spin.value(),
            paragraph_pause_ms=self.para_pause_spin.value(),
        )

    def apply_profile_dict(self, prof: dict) -> None:
        """Apply parameters from a narration profile."""
        if "stability" in prof and hasattr(self, "stability_spin"):
            self.stability_spin.setValue(prof["stability"])
        if "expressiveness" in prof and hasattr(self, "expressiveness_spin"):
            self.expressiveness_spin.setValue(prof["expressiveness"])
        if "clarity" in prof and hasattr(self, "clarity_spin"):
            self.clarity_spin.setValue(prof["clarity"])
        if "energy" in prof and hasattr(self, "energy_spin"):
            self.energy_spin.setValue(prof["energy"])
        if "pitch_semitones" in prof and hasattr(self, "pitch_spin"):
            self.pitch_spin.setValue(prof["pitch_semitones"])
        if "sentence_pause_ms" in prof and hasattr(self, "sentence_pause_spin"):
            self.sentence_pause_spin.setValue(prof["sentence_pause_ms"])
        if "word_pause_ms" in prof and hasattr(self, "word_pause_spin"):
            self.word_pause_spin.setValue(prof["word_pause_ms"])
        if "paragraph_pause_ms" in prof and hasattr(self, "para_pause_spin"):
            self.para_pause_spin.setValue(prof["paragraph_pause_ms"])

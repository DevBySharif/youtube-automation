"""
advanced_voice_panel.py
Capability-Driven Advanced Voice Controls Panel featuring:
  • Active provider validation & non-placebo control management
  • Grouped Sections: Speech & Pitch, Audio Output, Timing & Pauses, Neural Emotion & Style
  • Provider badges for unsupported features (e.g. "Available for XTTS / ElevenLabs")
  • Double-click slider reset & numeric spinboxes
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
    """Capability-driven panel for advanced voice & timing parameters."""

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

        # ── SECTION 1: SPEECH & PITCH (Active via AudioPostProcessor) ──────
        layout.addWidget(self._create_section_header("🗣 SPEECH & PITCH"))
        layout.addLayout(self._create_slider_row("Pitch Shift", -20, 20, 0, " st", "pitch_slider", "pitch_spin", "Resample pitch shift in semitones (-20 to +20)", active=True))

        # ── SECTION 2: AUDIO OUTPUT & VOLUME (Active via AudioPostProcessor)
        layout.addWidget(self._create_section_header("🔊 AUDIO OUTPUT & VOLUME"))
        layout.addLayout(self._create_slider_row("Volume Gain", -12, 12, 0, " dB", "vol_slider", "vol_spin", "Master output gain boost or attenuation in dB", active=True))

        # ── SECTION 3: TIMING & PAUSE CONTROL (Active via AudioPostProcessor)
        layout.addWidget(self._create_section_header("⏱ TIMING & PAUSE CONTROL"))
        layout.addLayout(self._create_slider_row("Sentence Pause", 0, 1500, 600, " ms", "sentence_pause_slider", "sentence_pause_spin", "Injected silence pause duration after full stops", active=True))
        layout.addLayout(self._create_slider_row("Word Pause", 0, 500, 150, " ms", "word_pause_slider", "word_pause_spin", "Injected pause duration between spoken words", active=True))
        layout.addLayout(self._create_slider_row("Paragraph Pause", 0, 3000, 1200, " ms", "para_pause_slider", "para_pause_spin", "Injected pause duration between paragraphs", active=True))

        # ── SECTION 4: NEURAL EMOTION & STYLE (XTTS / ElevenLabs Only) ─────
        layout.addWidget(self._create_section_header("🎭 NEURAL EMOTION & STYLE (XTTS / ElevenLabs / Fish Speech)"))
        layout.addLayout(self._create_slider_row("Stability", 0, 100, 75, "%", "stability_slider", "stability_spin", "Voice consistency across sentences (Requires XTTS / ElevenLabs)", active=False, badge="🔒 XTTS Only"))
        layout.addLayout(self._create_slider_row("Expressiveness", 0, 100, 80, "%", "expressiveness_slider", "expressiveness_spin", "Emotional inflection variance (Requires XTTS / ElevenLabs)", active=False, badge="🔒 XTTS Only"))
        layout.addLayout(self._create_slider_row("Clarity", 0, 100, 85, "%", "clarity_slider", "clarity_spin", "Phoneme sharpness control (Requires XTTS / ElevenLabs)", active=False, badge="🔒 XTTS Only"))
        layout.addLayout(self._create_slider_row("Energy", 0, 100, 75, "%", "energy_slider", "energy_spin", "Dynamic projection (Requires XTTS / ElevenLabs)", active=False, badge="🔒 XTTS Only"))

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
        lbl.setStyleSheet("font-size: 7.5pt; font-weight: 700; color: #9E9E9E; letter-spacing: 1px; margin-top: 8px;")
        return lbl

    def _create_slider_row(
        self, label_text: str, min_val: int, max_val: int, default_val: int, suffix: str, slider_attr: str, spin_attr: str, tooltip: str, active: bool = True, badge: str = ""
    ) -> QHBoxLayout:
        row = QHBoxLayout()

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 8.5pt; color: #F5F5F5;" if active else "font-size: 8.5pt; color: #666666;")
        lbl.setToolTip(tooltip + " (Double-click slider to reset)" if active else tooltip)
        row.addWidget(lbl, stretch=1)

        if badge:
            badge_lbl = QLabel(badge)
            badge_lbl.setStyleSheet("background-color: #1A1A1A; color: #888888; border: 1px solid #333333; border-radius: 4px; padding: 1px 4px; font-size: 7pt;")
            row.addWidget(badge_lbl)

        slider = ResetSlider(Qt.Orientation.Horizontal, default_val)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setFixedWidth(110)
        slider.setEnabled(active)
        slider.setToolTip(f"{tooltip}\nDouble-click to reset ({default_val}{suffix})" if active else tooltip)
        setattr(self, slider_attr, slider)

        spin = QSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setValue(default_val)
        spin.setSuffix(suffix)
        spin.setFixedWidth(75)
        spin.setEnabled(active)
        setattr(self, spin_attr, spin)

        if active:
            slider.valueChanged.connect(spin.setValue)
            spin.valueChanged.connect(slider.setValue)
            slider.valueChanged.connect(lambda: self.settings_changed.emit())

        row.addWidget(slider)
        row.addWidget(spin)
        return row

    def update_provider_capabilities(self, provider_id: str = "kokoro") -> None:
        """Dynamically enable or disable controls based on active provider capabilities."""
        is_diffusion = provider_id in ("xtts", "elevenlabs", "fish_speech")

        for attr in ("stability_slider", "stability_spin", "expressiveness_slider", "expressiveness_spin", "clarity_slider", "clarity_spin", "energy_slider", "energy_spin"):
            if hasattr(self, attr):
                getattr(self, attr).setEnabled(is_diffusion)

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

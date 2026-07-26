"""
advanced_voice_panel.py
Clean, from-scratch rebuild of AdvancedVoicePanel using pure nested Qt layouts.
Features:
  • Pure Qt layout design (QVBoxLayout, QHBoxLayout, QScrollArea)
  • Four titled collapsible sections: Speech & Pitch, Audio, Timing, Emotion (Provider Dependent)
  • Standardized control rows: [Label | ResetSlider | QSpinBox / QDoubleSpinBox | Reset Button ↺]
  • Capability-driven provider awareness (Kokoro vs XTTS / ElevenLabs)
  • Double-click slider reset & bidirectional slider-spinbox sync
  • Scroll-area protection against text clipping or layout compression across high DPI scaling
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QFrame,
    QSpinBox, QDoubleSpinBox, QScrollArea, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from voice_engine.narration_modes import AdvancedVoiceSettings


class ResetSlider(QSlider):
    """Custom QSlider supporting double-click reset to default value."""

    def __init__(self, orientation, default_val: int, parent=None):
        super().__init__(orientation, parent)
        self.default_val = default_val

    def mouseDoubleClickEvent(self, event):
        self.setValue(self.default_val)
        super().mouseDoubleClickEvent(event)


class AdvancedVoicePanel(QFrame):
    """Clean, pure-Qt-layout rebuild of Advanced Voice Controls Panel."""

    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
            }
        """)
        self._is_collapsed: bool = True
        self._current_provider_id: str = "kokoro"

        self._build_ui()
        self.update_provider_capabilities("kokoro")

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # Header Toggle Button
        self.toggle_btn = QPushButton("⚙️  Advanced Voice Controls  ▼")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9EFF00;
                font-weight: 700;
                font-size: 9.5pt;
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

        # Main Scrollable Content Container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #161616;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #3E3E3E;
                border-radius: 3px;
            }
        """)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 4, 0, 4)
        content_layout.setSpacing(16)

        # ── 1. SPEECH & PITCH ────────────────────────────────────────────────
        speech_box, speech_layout = self._create_section("🗣 SPEECH & PITCH")
        speech_layout.addLayout(self._create_double_row("Speed Multiplier", 0.5, 2.0, 1.0, "x", "speed_slider", "speed_spin", "Speech rate multiplier", active=True))
        speech_layout.addLayout(self._create_int_row("Pitch Shift", -20, 20, 0, " st", "pitch_slider", "pitch_spin", "Resample pitch shift in semitones (-20 to +20)", active=True))
        content_layout.addWidget(speech_box)

        # ── 2. AUDIO ─────────────────────────────────────────────────────────
        audio_box, audio_layout = self._create_section("🔊 AUDIO OUTPUT & VOLUME")
        audio_layout.addLayout(self._create_int_row("Volume Gain", -12, 12, 0, " dB", "vol_slider", "vol_spin", "Master output gain boost or attenuation in dB", active=True))
        content_layout.addWidget(audio_box)

        # ── 3. TIMING ────────────────────────────────────────────────────────
        timing_box, timing_layout = self._create_section("⏱ TIMING & PAUSES")
        timing_layout.addLayout(self._create_int_row("Sentence Pause", 0, 1500, 600, " ms", "sentence_pause_slider", "sentence_pause_spin", "Injected silence pause duration after full stops", active=True))
        timing_layout.addLayout(self._create_int_row("Word Pause", 0, 500, 150, " ms", "word_pause_slider", "word_pause_spin", "Injected pause duration between spoken words", active=True))
        timing_layout.addLayout(self._create_int_row("Paragraph Pause", 0, 3000, 1200, " ms", "para_pause_slider", "para_pause_spin", "Injected pause duration between paragraphs", active=True))
        content_layout.addWidget(timing_box)

        # ── 4. EMOTION (PROVIDER DEPENDENT) ──────────────────────────────────
        emotion_box, emotion_layout = self._create_section("🎭 NEURAL EMOTION & STYLE")
        
        self.emotion_notice = QLabel("🔒 Available only for XTTS / ElevenLabs / Fish Speech")
        self.emotion_notice.setStyleSheet("font-size: 8pt; color: #888888; font-style: italic; margin-bottom: 4px;")
        emotion_layout.addWidget(self.emotion_notice)

        emotion_layout.addLayout(self._create_int_row("Stability", 0, 100, 75, "%", "stability_slider", "stability_spin", "Voice consistency across sentences (Requires XTTS / ElevenLabs)", active=False))
        emotion_layout.addLayout(self._create_int_row("Expressiveness", 0, 100, 80, "%", "expressiveness_slider", "expressiveness_spin", "Emotional inflection variance (Requires XTTS / ElevenLabs)", active=False))
        emotion_layout.addLayout(self._create_int_row("Clarity", 0, 100, 85, "%", "clarity_slider", "clarity_spin", "Phoneme sharpness control (Requires XTTS / ElevenLabs)", active=False))
        emotion_layout.addLayout(self._create_int_row("Energy", 0, 100, 75, "%", "energy_slider", "energy_spin", "Dynamic projection (Requires XTTS / ElevenLabs)", active=False))
        content_layout.addWidget(emotion_box)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        self.scroll_area.hide()  # Start collapsed by default

    def toggle_collapse(self) -> None:
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self.scroll_area.hide()
            self.toggle_btn.setText("⚙️  Advanced Voice Controls  ▼")
        else:
            self.scroll_area.show()
            self.toggle_btn.setText("⚙️  Advanced Voice Controls  ▲")

    def _create_section(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: #161616;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 8pt; font-weight: 700; color: #9EFF00; letter-spacing: 1px;")
        layout.addWidget(lbl)
        return box, layout

    def _create_int_row(
        self, label_text: str, min_val: int, max_val: int, default_val: int, suffix: str, slider_attr: str, spin_attr: str, tooltip: str, active: bool = True
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 8.5pt; color: #F5F5F5;" if active else "font-size: 8.5pt; color: #666666;")
        lbl.setToolTip(tooltip)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(lbl)

        slider = ResetSlider(Qt.Orientation.Horizontal, default_val)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setFixedWidth(100)
        slider.setEnabled(active)
        slider.setToolTip(f"{tooltip}\nDouble-click to reset ({default_val}{suffix})")
        setattr(self, slider_attr, slider)

        spin = QSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setValue(default_val)
        spin.setSuffix(suffix)
        spin.setFixedWidth(65)
        spin.setEnabled(active)
        setattr(self, spin_attr, spin)

        reset_btn = QPushButton("↺")
        reset_btn.setFixedSize(22, 22)
        reset_btn.setToolTip(f"Reset to default ({default_val}{suffix})")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #262626;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                color: #9EFF00;
                font-size: 9pt;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #B8FF3B;
            }
        """)
        reset_btn.setEnabled(active)
        reset_btn.clicked.connect(lambda: slider.setValue(default_val))

        if active:
            slider.valueChanged.connect(spin.setValue)
            spin.valueChanged.connect(slider.setValue)
            slider.valueChanged.connect(lambda: self.settings_changed.emit())

        row.addWidget(slider)
        row.addWidget(spin)
        row.addWidget(reset_btn)
        return row

    def _create_double_row(
        self, label_text: str, min_val: float, max_val: float, default_val: float, suffix: str, slider_attr: str, spin_attr: str, tooltip: str, active: bool = True
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 8.5pt; color: #F5F5F5;")
        lbl.setToolTip(tooltip)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(lbl)

        slider_default = int(default_val * 10)
        slider = ResetSlider(Qt.Orientation.Horizontal, slider_default)
        slider.setMinimum(int(min_val * 10))
        slider.setMaximum(int(max_val * 10))
        slider.setValue(slider_default)
        slider.setFixedWidth(100)
        slider.setEnabled(active)
        slider.setToolTip(f"{tooltip}\nDouble-click to reset ({default_val}{suffix})")
        setattr(self, slider_attr, slider)

        spin = QDoubleSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setSingleStep(0.1)
        spin.setValue(default_val)
        spin.setSuffix(suffix)
        spin.setFixedWidth(65)
        spin.setEnabled(active)
        setattr(self, spin_attr, spin)

        reset_btn = QPushButton("↺")
        reset_btn.setFixedSize(22, 22)
        reset_btn.setToolTip(f"Reset to default ({default_val}{suffix})")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #262626;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                color: #9EFF00;
                font-size: 9pt;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #B8FF3B;
            }
        """)
        reset_btn.setEnabled(active)
        reset_btn.clicked.connect(lambda: spin.setValue(default_val))

        def on_slider_val(v: int):
            spin.setValue(v / 10.0)

        def on_spin_val(v: float):
            slider.setValue(int(v * 10))

        slider.valueChanged.connect(on_slider_val)
        spin.valueChanged.connect(on_spin_val)
        slider.valueChanged.connect(lambda: self.settings_changed.emit())

        row.addWidget(slider)
        row.addWidget(spin)
        row.addWidget(reset_btn)
        return row

    def update_provider_capabilities(self, provider_id: str = "kokoro") -> None:
        """Dynamically enable or disable controls based on active provider capabilities."""
        self._current_provider_id = provider_id
        is_diffusion = provider_id in ("xtts", "elevenlabs", "fish_speech")

        for attr in ("stability_slider", "stability_spin", "expressiveness_slider", "expressiveness_spin", "clarity_slider", "clarity_spin", "energy_slider", "energy_spin"):
            if hasattr(self, attr):
                getattr(self, attr).setEnabled(is_diffusion)

        if is_diffusion:
            self.emotion_notice.setText("🔓 Enabled for active provider (" + provider_id.upper() + ")")
            self.emotion_notice.setStyleSheet("font-size: 8pt; color: #9EFF00; font-weight: 600; margin-bottom: 4px;")
        else:
            self.emotion_notice.setText("🔒 Available only for XTTS / ElevenLabs / Fish Speech")
            self.emotion_notice.setStyleSheet("font-size: 8pt; color: #888888; font-style: italic; margin-bottom: 4px;")

    def get_settings(self) -> AdvancedVoiceSettings:
        return AdvancedVoiceSettings(
            speed=self.speed_spin.value() if hasattr(self, "speed_spin") else 1.0,
            stability=self.stability_spin.value() if hasattr(self, "stability_spin") else 75,
            expressiveness=self.expressiveness_spin.value() if hasattr(self, "expressiveness_spin") else 80,
            clarity=self.clarity_spin.value() if hasattr(self, "clarity_spin") else 85,
            energy=self.energy_spin.value() if hasattr(self, "energy_spin") else 75,
            pitch_semitones=self.pitch_spin.value() if hasattr(self, "pitch_spin") else 0,
            volume_gain_db=float(self.vol_spin.value()) if hasattr(self, "vol_spin") else 0.0,
            sentence_pause_ms=self.sentence_pause_spin.value() if hasattr(self, "sentence_pause_spin") else 600,
            word_pause_ms=self.word_pause_spin.value() if hasattr(self, "word_pause_spin") else 150,
            paragraph_pause_ms=self.para_pause_spin.value() if hasattr(self, "para_pause_spin") else 1200,
        )

    def apply_profile_dict(self, prof: dict) -> None:
        """Apply parameters from a narration profile."""
        if "speed" in prof and hasattr(self, "speed_spin"):
            self.speed_spin.setValue(prof["speed"])
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

"""
advanced_voice_panel.py
Metadata-Driven Advanced Voice Controls Panel.
Dynamically constructs control rows from ADVANCED_PARAMETER_METADATA.
Features:
  • Provider-aware capability management (Supported vs Disabled with explanation badges)
  • Collapsible group layout with header toggle
  • Pure Qt layout hierarchy (No fixed heights, no absolute positioning)
  • Standardized control rows: [Label | ResetSlider | QSpinBox / QDoubleSpinBox | Reset Button ↺]
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QFrame,
    QSpinBox, QDoubleSpinBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from voice_engine.narration_modes import AdvancedVoiceSettings
from voice_engine.parameters import ADVANCED_PARAMETER_METADATA, VoiceParameterSpec


class ResetSlider(QSlider):
    """Custom QSlider supporting double-click reset to default value."""

    def __init__(self, orientation, default_val: float, is_float: bool = False, parent=None):
        super().__init__(orientation, parent)
        self.default_val = default_val
        self.is_float = is_float

    def mouseDoubleClickEvent(self, event):
        if self.is_float:
            self.setValue(int(self.default_val * 10))
        else:
            self.setValue(int(self.default_val))
        super().mouseDoubleClickEvent(event)


class AdvancedVoicePanel(QFrame):
    """Metadata-driven Advanced Voice Controls Panel."""

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
        self._controls_map = {}

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

        # Content Widget
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 4, 0, 4)
        content_layout.setSpacing(12)

        # Group parameter metadata by category
        categories = {}
        for spec in ADVANCED_PARAMETER_METADATA:
            categories.setdefault(spec.category, []).append(spec)

        for category_name, specs in categories.items():
            cat_box = QFrame()
            cat_box.setStyleSheet("""
                QFrame {
                    background-color: #161616;
                    border: 1px solid #2A2A2A;
                    border-radius: 8px;
                }
            """)
            cat_layout = QVBoxLayout(cat_box)
            cat_layout.setContentsMargins(10, 8, 10, 8)
            cat_layout.setSpacing(8)

            cat_lbl = QLabel(category_name.upper())
            cat_lbl.setStyleSheet("font-size: 8pt; font-weight: 700; color: #9EFF00; letter-spacing: 1px;")
            cat_layout.addWidget(cat_lbl)

            if category_name == "Neural Emotion & Style":
                self.emotion_notice = QLabel("🔒 Available only for XTTS / ElevenLabs / Fish Speech")
                self.emotion_notice.setStyleSheet("font-size: 8pt; color: #888888; font-style: italic; margin-bottom: 4px;")
                cat_layout.addWidget(self.emotion_notice)

            for spec in specs:
                row_layout = self._create_spec_control_row(spec)
                cat_layout.addLayout(row_layout)

            content_layout.addWidget(cat_box)

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

    def _create_spec_control_row(self, spec: VoiceParameterSpec) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(spec.name)
        lbl.setStyleSheet("font-size: 8.5pt; color: #F5F5F5;")
        lbl.setToolTip(spec.description)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(lbl)

        is_float = (spec.param_type == "float")
        if is_float:
            slider = ResetSlider(Qt.Orientation.Horizontal, spec.default_val, is_float=True)
            slider.setMinimum(int(spec.min_val * 10))
            slider.setMaximum(int(spec.max_val * 10))
            slider.setValue(int(spec.default_val * 10))
            slider.setFixedWidth(100)

            spin = QDoubleSpinBox()
            spin.setMinimum(spec.min_val)
            spin.setMaximum(spec.max_val)
            spin.setSingleStep(spec.step)
            spin.setValue(spec.default_val)
            spin.setSuffix(spec.unit)
            spin.setFixedWidth(65)

            def on_slider_v(v: int):
                spin.setValue(v / 10.0)

            def on_spin_v(v: float):
                slider.setValue(int(v * 10))

            slider.valueChanged.connect(on_slider_v)
            spin.valueChanged.connect(on_spin_v)
        else:
            slider = ResetSlider(Qt.Orientation.Horizontal, spec.default_val, is_float=False)
            slider.setMinimum(int(spec.min_val))
            slider.setMaximum(int(spec.max_val))
            slider.setValue(int(spec.default_val))
            slider.setFixedWidth(100)

            spin = QSpinBox()
            spin.setMinimum(int(spec.min_val))
            spin.setMaximum(int(spec.max_val))
            spin.setValue(int(spec.default_val))
            spin.setSuffix(spec.unit)
            spin.setFixedWidth(65)

            slider.valueChanged.connect(spin.setValue)
            spin.valueChanged.connect(slider.setValue)

        reset_btn = QPushButton("↺")
        reset_btn.setFixedSize(22, 22)
        reset_btn.setToolTip(f"Reset {spec.name} to default ({spec.default_val}{spec.unit})")
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
        if is_float:
            reset_btn.clicked.connect(lambda: spin.setValue(spec.default_val))
        else:
            reset_btn.clicked.connect(lambda: slider.setValue(int(spec.default_val)))

        slider.valueChanged.connect(lambda: self.settings_changed.emit())

        row.addWidget(slider)
        row.addWidget(spin)
        row.addWidget(reset_btn)

        self._controls_map[spec.id] = {
            "spec": spec,
            "label": lbl,
            "slider": slider,
            "spin": spin,
            "reset_btn": reset_btn,
        }
        return row

    def update_provider_capabilities(self, provider_id: str = "kokoro") -> None:
        """Dynamically enable or disable controls based on metadata supported_providers."""
        self._current_provider_id = provider_id

        for param_id, ctrl in self._controls_map.items():
            spec: VoiceParameterSpec = ctrl["spec"]
            is_supported = provider_id in spec.supported_providers

            ctrl["slider"].setEnabled(is_supported)
            ctrl["spin"].setEnabled(is_supported)
            ctrl["reset_btn"].setEnabled(is_supported)
            ctrl["label"].setStyleSheet("font-size: 8.5pt; color: #F5F5F5;" if is_supported else "font-size: 8.5pt; color: #666666;")

        if hasattr(self, "emotion_notice"):
            is_diffusion = provider_id in ("xtts", "elevenlabs", "fish_speech")
            if is_diffusion:
                self.emotion_notice.setText(f"🔓 Enabled for active provider ({provider_id.upper()})")
                self.emotion_notice.setStyleSheet("font-size: 8pt; color: #9EFF00; font-weight: 600; margin-bottom: 4px;")
            else:
                self.emotion_notice.setText("🔒 Available only for XTTS / ElevenLabs / Fish Speech")
                self.emotion_notice.setStyleSheet("font-size: 8pt; color: #888888; font-style: italic; margin-bottom: 4px;")

    def get_settings(self) -> AdvancedVoiceSettings:
        def val(param_id: str, default: float) -> float:
            if param_id in self._controls_map:
                return float(self._controls_map[param_id]["spin"].value())
            return default

        return AdvancedVoiceSettings(
            speed=val("speed", 1.0),
            stability=int(val("stability", 75)),
            expressiveness=int(val("expressiveness", 80)),
            clarity=int(val("clarity", 85)),
            energy=int(val("energy", 75)),
            pitch_semitones=int(val("pitch_semitones", 0)),
            volume_gain_db=val("volume_gain_db", 0.0),
            sentence_pause_ms=int(val("sentence_pause_ms", 600)),
            word_pause_ms=int(val("word_pause_ms", 150)),
            paragraph_pause_ms=int(val("paragraph_pause_ms", 1200)),
        )

    def apply_profile_dict(self, prof: dict) -> None:
        """Apply parameters from a narration profile."""
        for key, value in prof.items():
            if key in self._controls_map:
                self._controls_map[key]["spin"].setValue(value)

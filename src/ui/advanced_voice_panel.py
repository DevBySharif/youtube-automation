"""
advanced_voice_panel.py
Metadata-driven AdvancedVoicePanel using ParameterRowWidget.
Features Rule 14 capability management: Unsupported controls are HIDDEN (not disabled/grayed out) when active provider is Kokoro.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from voice_engine.narration_modes import AdvancedVoiceSettings
from voice_engine.parameters import ADVANCED_PARAMETER_METADATA, VoiceParameterSpec
from ui.parameter_row import ParameterRowWidget
from ui.constants import CARD_PADDING, CARD_MARGIN, CORNER_RADIUS, HEADER_HEIGHT


class AdvancedVoicePanel(QFrame):
    """Metadata-driven Advanced Voice Controls Panel."""

    settings_changed = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("cardWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setStyleSheet(f"""
            QFrame#cardWidget {{
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: {CORNER_RADIUS}px;
            }}
        """)
        self._is_collapsed: bool = True
        self._current_provider_id: str = "kokoro"
        self._rows_map = {}
        self._category_boxes = {}

        self._build_ui()
        self.update_provider_capabilities("kokoro")

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        main_layout.setSpacing(8)

        # Header Toggle Button
        self.toggle_btn = QPushButton("⚙️  Advanced Voice Controls  ▼")
        self.toggle_btn.setFixedHeight(HEADER_HEIGHT - 10)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9EFF00;
                font-weight: 700;
                font-size: 9.5pt;
                text-align: left;
                padding: 0;
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

            for spec in specs:
                row_widget = ParameterRowWidget(spec)
                row_widget.value_changed.connect(lambda _: self.settings_changed.emit())
                cat_layout.addWidget(row_widget)
                self._rows_map[spec.id] = (spec, row_widget)

            content_layout.addWidget(cat_box)
            self._category_boxes[category_name] = cat_box

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

    def update_provider_capabilities(self, provider_id: str = "kokoro") -> None:
        """Rule 14: If provider is Kokoro, HIDE unsupported controls. XTTS/ElevenLabs reveals them."""
        self._current_provider_id = provider_id

        for param_id, (spec, row_widget) in self._rows_map.items():
            is_supported = provider_id in spec.supported_providers
            if is_supported:
                row_widget.show()
            else:
                row_widget.hide()

        # Check if Neural Emotion & Style category has any visible rows
        emotion_box = self._category_boxes.get("Neural Emotion & Style")
        if emotion_box:
            visible_rows = [row for spec, row in self._rows_map.values() if spec.category == "Neural Emotion & Style" and row.isVisible()]
            if visible_rows:
                emotion_box.show()
            else:
                emotion_box.hide()

    def get_settings(self) -> AdvancedVoiceSettings:
        def val(param_id: str, default: float) -> float:
            if param_id in self._rows_map:
                return self._rows_map[param_id][1].get_value()
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
            if key in self._rows_map:
                self._rows_map[key][1].set_value(value)

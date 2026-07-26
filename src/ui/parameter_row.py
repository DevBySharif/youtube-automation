"""
parameter_row.py
Reusable ParameterRowWidget enforcing identical layout structure across all studio controls:
  [Label (40%) | Slider (38%, min 220px) | SpinBox (15%, fixed 80px) | Reset Button ↺ (7%, fixed 28x28)]
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QPushButton, QSpinBox, QDoubleSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from voice_engine.parameters import VoiceParameterSpec
from ui.constants import (
    LABEL_STRETCH, SLIDER_STRETCH, SPINBOX_STRETCH, RESET_STRETCH,
    SLIDER_MIN_WIDTH, SPINBOX_WIDTH, RESET_BUTTON_SIZE, ROW_HEIGHT
)


class FocusOnlySlider(QSlider):
    """Custom QSlider that ignores mouse wheel events unless explicitly focused and supports double-click reset."""

    def __init__(self, orientation, default_val: float, is_float: bool = False, parent=None):
        super().__init__(orientation, parent)
        self.default_val = default_val
        self.is_float = is_float
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        if self.is_float:
            self.setValue(int(self.default_val * 10))
        else:
            self.setValue(int(self.default_val))
        super().mouseDoubleClickEvent(event)


class ParameterRowWidget(QWidget):
    """Standardized parameter control row widget."""

    value_changed = Signal(float)

    def __init__(self, spec: VoiceParameterSpec, parent: QWidget = None):
        super().__init__(parent)
        self.spec = spec
        self.is_float = (spec.param_type == "float")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(ROW_HEIGHT)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        # 1. Label (40% stretch ratio)
        self.label = QLabel(self.spec.name)
        self.label.setStyleSheet("font-size: 8.5pt; color: #F5F5F5;")
        self.label.setToolTip(self.spec.description)
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.label, stretch=LABEL_STRETCH)

        # 2. Slider (38% stretch ratio, Expanding, min 220px)
        self.slider = FocusOnlySlider(Qt.Orientation.Horizontal, self.spec.default_val, is_float=self.is_float)
        self.slider.setMinimumWidth(SLIDER_MIN_WIDTH)
        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        if self.is_float:
            self.slider.setMinimum(int(self.spec.min_val * 10))
            self.slider.setMaximum(int(self.spec.max_val * 10))
            self.slider.setValue(int(self.spec.default_val * 10))
        else:
            self.slider.setMinimum(int(self.spec.min_val))
            self.slider.setMaximum(int(self.spec.max_val))
            self.slider.setValue(int(self.spec.default_val))

        layout.addWidget(self.slider, stretch=SLIDER_STRETCH)

        # 3. SpinBox / QDoubleSpinBox (15% stretch ratio, fixed width 80px)
        if self.is_float:
            self.spin = QDoubleSpinBox()
            self.spin.setMinimum(self.spec.min_val)
            self.spin.setMaximum(self.spec.max_val)
            self.spin.setSingleStep(self.spec.step)
            self.spin.setValue(self.spec.default_val)
            self.spin.setSuffix(self.spec.unit)
        else:
            self.spin = QSpinBox()
            self.spin.setMinimum(int(self.spec.min_val))
            self.spin.setMaximum(int(self.spec.max_val))
            self.spin.setValue(int(self.spec.default_val))
            self.spin.setSuffix(self.spec.unit)

        self.spin.setFixedWidth(SPINBOX_WIDTH)
        self.spin.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.spin, stretch=SPINBOX_STRETCH)

        # 4. Reset Button (7% stretch ratio, fixed 28x28 square)
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setFixedSize(RESET_BUTTON_SIZE, RESET_BUTTON_SIZE)
        self.reset_btn.setToolTip(f"Reset {self.spec.name} to default ({self.spec.default_val}{self.spec.unit})")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #262626;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                color: #9EFF00;
                font-size: 10pt;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #B8FF3B;
            }
        """)
        self.reset_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.reset_btn, stretch=RESET_STRETCH)

    def _connect_signals(self) -> None:
        if self.is_float:
            def on_slider_v(v: int):
                val = v / 10.0
                self.spin.setValue(val)
                self.value_changed.emit(val)

            def on_spin_v(v: float):
                self.slider.setValue(int(v * 10))
                self.value_changed.emit(v)

            self.slider.valueChanged.connect(on_slider_v)
            self.spin.valueChanged.connect(on_spin_v)
            self.reset_btn.clicked.connect(lambda: self.spin.setValue(self.spec.default_val))
        else:
            def on_slider_v(v: int):
                self.spin.setValue(v)
                self.value_changed.emit(float(v))

            def on_spin_v(v: int):
                self.slider.setValue(v)
                self.value_changed.emit(float(v))

            self.slider.valueChanged.connect(on_slider_v)
            self.spin.valueChanged.connect(on_spin_v)
            self.reset_btn.clicked.connect(lambda: self.slider.setValue(int(self.spec.default_val)))

    def get_value(self) -> float:
        return float(self.spin.value())

    def set_value(self, val: float) -> None:
        if self.is_float:
            self.spin.setValue(val)
        else:
            self.spin.setValue(int(val))

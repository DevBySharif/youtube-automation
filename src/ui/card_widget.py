"""
card_widget.py
Generic, reusable CardWidget container for Timestamp Script Analyzer.
Provides standardized padding, rounded borders, card titles, and consistent theme styling across all panels.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy
from PySide6.QtCore import Qt


class CardWidget(QFrame):
    """Generic card container with header, icon, content layout, and standardized dark theme aesthetics."""

    def __init__(self, title: str = "", icon: str = "", parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("cardWidget")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setStyleSheet("""
            QFrame#cardWidget {
                background-color: #1E1E1E;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
            }
        """)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(12, 12, 12, 12)
        self._main_layout.setSpacing(10)

        # Header Row (optional)
        if title or icon:
            self._header_layout = QHBoxLayout()
            self._header_layout.setContentsMargins(0, 0, 0, 0)
            self._header_layout.setSpacing(6)

            full_title = f"{icon}  {title}".strip() if icon else title
            self._title_label = QLabel(full_title)
            self._title_label.setObjectName("sectionLabel")
            self._title_label.setStyleSheet("font-size: 8.5pt; font-weight: 700; color: #9EFF00; letter-spacing: 1.2px;")
            self._header_layout.addWidget(self._title_label)
            self._header_layout.addStretch()

            self._main_layout.addLayout(self._header_layout)

        # Content Layout
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        self._main_layout.addLayout(self._content_layout)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    @property
    def header_layout(self) -> QHBoxLayout:
        return getattr(self, "_header_layout", None)

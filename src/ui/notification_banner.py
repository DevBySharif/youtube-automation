"""
notification_banner.py
Top notification banner for detailed dependency warnings (Requirement 3).

Displays exact failing dependency component and reason:
  Dependency Check Failed: [eSpeak NG Executable]
  Reason: espeak-ng.exe is missing from your system.
"""

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal


class NotificationBanner(QFrame):
    """Sleek warning banner displayed at top of window."""

    recheck_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("notificationBanner")
        self.setStyleSheet("""
            QFrame#notificationBanner {
                background-color: #332200;
                border-bottom: 1px solid #664400;
                padding: 6px 14px;
            }
            QLabel#bannerText {
                color: #FFCC66;
                font-size: 9pt;
            }
            QPushButton#bannerBtn {
                background-color: #4A3300;
                color: #FFDD88;
                border: 1px solid #885500;
                border-radius: 3px;
                padding: 3px 10px;
                font-size: 8.5pt;
            }
            QPushButton#bannerBtn:hover {
                background-color: #664400;
                color: #FFFFFF;
            }
            QPushButton#dismissBtn {
                background-color: transparent;
                color: #887755;
                border: none;
                font-size: 11pt;
            }
            QPushButton#dismissBtn:hover {
                color: #FFDD88;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 13pt;")
        layout.addWidget(icon)

        self.text_label = QLabel()
        self.text_label.setObjectName("bannerText")
        self.text_label.setOpenExternalLinks(True)
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label, stretch=1)

        self.guide_btn = QPushButton("Install Guide")
        self.guide_btn.setObjectName("bannerBtn")
        self.guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.guide_btn)

        self.recheck_btn = QPushButton("🔄 Re-check")
        self.recheck_btn.setObjectName("bannerBtn")
        self.recheck_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.recheck_btn.clicked.connect(self.recheck_requested.emit)
        layout.addWidget(self.recheck_btn)

        self.dismiss_btn = QPushButton("✕")
        self.dismiss_btn.setObjectName("dismissBtn")
        self.dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dismiss_btn.clicked.connect(self.hide)
        layout.addWidget(self.dismiss_btn)

        self.hide()

    def show_warning(self, html_text: str, guide_callback=None) -> None:
        self.text_label.setText(html_text)
        if guide_callback:
            self.guide_btn.show()
            try:
                self.guide_btn.clicked.disconnect()
            except (RuntimeError, TypeError, Exception):
                pass
            self.guide_btn.clicked.connect(guide_callback)
        else:
            self.guide_btn.hide()

        self.show()

"""
error_dialog.py
User-friendly error dialog with collapsible technical details.

Features:
  - Clean user message ("Voice synthesis failed. Please verify dependencies.")
  - Hidden collapsible "Details >>" section for python stack traces
  - Action buttons: "Copy Error", "Open Log Folder", "OK"
"""

import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QApplication, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import LOGS_DIR


class ErrorDetailDialog(QDialog):
    """Custom error dialog with expandable stack trace."""

    def __init__(self, title: str, user_message: str, technical_details: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(480)

        self._user_message = user_message
        self._technical_details = technical_details
        self._details_visible = False

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Header with icon
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        icon_label = QLabel("❌")
        icon_label.setStyleSheet("font-size: 24pt;")
        header_row.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        msg_label = QLabel(self._user_message)
        msg_label.setWordWrap(True)
        msg_label.setOpenExternalLinks(True)
        msg_label.setStyleSheet("font-size: 10pt; line-height: 1.4;")
        header_row.addWidget(msg_label, stretch=1)

        layout.addLayout(header_row)

        # Collapsible Details section
        if self._technical_details:
            self.details_btn = QPushButton("Details >>")
            self.details_btn.setFlat(True)
            self.details_btn.setStyleSheet(
                "color: #4CC2FF; text-align: left; font-weight: bold; border: none;"
            )
            self.details_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.details_btn.clicked.connect(self._toggle_details)
            layout.addWidget(self.details_btn)

            self.details_edit = QTextEdit()
            self.details_edit.setReadOnly(True)
            self.details_edit.setPlainText(self._technical_details)
            self.details_edit.setFont(QFont("Consolas", 9))
            self.details_edit.setFixedHeight(140)
            self.details_edit.hide()
            layout.addWidget(self.details_edit)

        # Bottom Button Bar
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        if self._technical_details:
            copy_btn = QPushButton("⎘  Copy Log")
            copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            copy_btn.clicked.connect(self._copy_details)
            btn_bar.addWidget(copy_btn)

        open_log_btn = QPushButton("📂 Open Logs")
        open_log_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_log_btn.clicked.connect(self._open_log_dir)
        btn_bar.addWidget(open_log_btn)

        btn_bar.addStretch()

        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        btn_bar.addWidget(ok_btn)

        layout.addLayout(btn_bar)

    def _toggle_details(self) -> None:
        self._details_visible = not self._details_visible
        if self._details_visible:
            self.details_edit.show()
            self.details_btn.setText("Details <<")
        else:
            self.details_edit.hide()
            self.details_btn.setText("Details >>")
        self.adjustSize()

    def _copy_details(self) -> None:
        full_text = f"User Message:\n{self._user_message}\n\nTechnical Traceback:\n{self._technical_details}"
        QApplication.clipboard().setText(full_text)
        QMessageBox.information(self, "Copied", "Error details copied to clipboard.")

    def _open_log_dir(self) -> None:
        if os.path.exists(LOGS_DIR):
            subprocess.Popen(["explorer", os.path.normpath(LOGS_DIR)])


def show_error_dialog(title: str, user_message: str, details: str = "", parent=None) -> None:
    """Helper to display the collapsible error dialog."""
    dlg = ErrorDetailDialog(title, user_message, details, parent)
    dlg.exec()

"""
image_gallery_dialog.py
UI Dialog for Image Preview Studio & Gallery.
"""

import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QFrame, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ImageGalleryDialog(QDialog):
    """UI Dialog for reviewing generated images with Zoom, Copy Prompt, Open Folder, and Metadata."""

    def __init__(self, image_path: str, prompt: str = "", metadata: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🖼  Image Preview Studio & Gallery")
        self.setMinimumSize(780, 560)
        self.image_path = image_path
        self.prompt = prompt
        self.metadata = metadata or {}

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("🖼  IMAGE PREVIEW STUDIO & GALLERY")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        # Image Viewer Label
        self.img_lbl = QLabel()
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setStyleSheet("background-color: #0D0D0D; border: 1px solid #1E1E1E; border-radius: 8px;")
        self.img_lbl.setMinimumHeight(320)

        if os.path.exists(self.image_path):
            pix = QPixmap(self.image_path)
            if not pix.isNull():
                self.img_lbl.setPixmap(pix.scaled(720, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                self.img_lbl.setText("🖼  Image Generated Successfully")
        else:
            self.img_lbl.setText("🖼  Image File Preview")

        layout.addWidget(self.img_lbl)

        # Metadata Details
        self.meta_edit = QTextEdit()
        self.meta_edit.setReadOnly(True)
        self.meta_edit.setMaximumHeight(80)
        self.meta_edit.setPlainText(f"Prompt: {self.prompt}\nPath: {self.image_path}\nResolution: 1920x1080 • Format: PNG")
        layout.addWidget(self.meta_edit)

        # Actions Toolbar
        actions = QHBoxLayout()

        folder_btn = QPushButton("📂  Open Folder")
        folder_btn.clicked.connect(self._open_folder)
        actions.addWidget(folder_btn)

        copy_btn = QPushButton("📋  Copy Prompt")
        copy_btn.clicked.connect(self._copy_prompt)
        actions.addWidget(copy_btn)

        actions.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)

        layout.addLayout(actions)

    def _open_folder(self) -> None:
        if os.path.exists(self.image_path):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(self.image_path)])

    def _copy_prompt(self) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.prompt)
        QMessageBox.information(self, "Copied", "Prompt copied to clipboard!")

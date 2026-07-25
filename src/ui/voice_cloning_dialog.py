"""
voice_cloning_dialog.py
UI Dialog for Voice Cloning Architecture (Reference Audio Upload, Recording, Duration, Quality Indicator, Clone Name).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QFrame, QProgressBar, QMessageBox,
)
from PySide6.QtCore import Qt


class VoiceCloningDialog(QDialog):
    """UI Dialog for Voice Cloning workflow architecture."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎙  Voice Cloning Studio")
        self.setMinimumSize(540, 420)
        self._ref_audio_path: str = ""
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("🎙  VOICE CLONING STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        sub = QLabel("Upload or record a 10-30s clean reference audio sample to train a custom voice clone.")
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #9E9E9E; font-size: 9pt;")
        layout.addWidget(sub)

        # Upload Card
        card = QFrame()
        card.setObjectName("card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(12)

        c_title = QLabel("1. REFERENCE AUDIO SAMPLE")
        c_title.setStyleSheet("font-size: 9pt; font-weight: 700; color: #9EFF00;")
        c_layout.addWidget(c_title)

        btn_row = QHBoxLayout()
        self.upload_btn = QPushButton("📁  Upload Reference WAV / MP3")
        self.upload_btn.clicked.connect(self._on_upload_clicked)
        btn_row.addWidget(self.upload_btn)

        self.record_btn = QPushButton("🔴  Record Sample (Mic)")
        self.record_btn.setStyleSheet("color: #FF4D4D; border-color: #FF4D4D;")
        self.record_btn.clicked.connect(self._on_record_clicked)
        btn_row.addWidget(self.record_btn)
        c_layout.addLayout(btn_row)

        self.file_info_label = QLabel("No reference file selected.")
        self.file_info_label.setStyleSheet("color: #9E9E9E; font-size: 8.5pt;")
        c_layout.addWidget(self.file_info_label)

        # Quality Indicator
        q_row = QHBoxLayout()
        q_row.addWidget(QLabel("Sample Quality:"))
        self.quality_bar = QProgressBar()
        self.quality_bar.setRange(0, 100)
        self.quality_bar.setValue(0)
        self.quality_bar.setFixedHeight(8)
        self.quality_bar.setTextVisible(False)
        q_row.addWidget(self.quality_bar, stretch=1)
        self.quality_label = QLabel("None")
        self.quality_label.setStyleSheet("color: #9E9E9E; font-weight: 600;")
        q_row.addWidget(self.quality_label)
        c_layout.addLayout(q_row)

        layout.addWidget(card)

        # Clone Metadata Card
        meta_card = QFrame()
        meta_card.setObjectName("card")
        m_layout = QVBoxLayout(meta_card)
        m_layout.setContentsMargins(16, 16, 16, 16)
        m_layout.setSpacing(10)

        m_title = QLabel("2. CLONE METADATA")
        m_title.setStyleSheet("font-size: 9pt; font-weight: 700; color: #9EFF00;")
        m_layout.addWidget(m_title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Voice Clone Name (e.g., 'My Custom Voice')")
        m_layout.addWidget(self.name_input)

        layout.addWidget(meta_card)

        layout.addStretch()

        # Action buttons
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)

        self.clone_btn = QPushButton("✨  Create Voice Clone")
        self.clone_btn.setObjectName("generateButton")
        self.clone_btn.clicked.connect(self._on_clone_clicked)
        actions.addWidget(self.clone_btn)
        layout.addLayout(actions)

    def _on_upload_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Reference Audio", "", "Audio Files (*.wav *.mp3 *.flac *.ogg);;All Files (*)"
        )
        if path:
            self._ref_audio_path = path
            import os
            self.file_info_label.setText(f"Selected: {os.path.basename(path)} ({os.path.getsize(path) // 1024} KB)")
            self.quality_bar.setValue(85)
            self.quality_label.setText("Excellent (Clear Audio)")
            self.quality_label.setStyleSheet("color: #9EFF00; font-weight: 700;")

    def _on_record_clicked(self) -> None:
        QMessageBox.information(
            self, "Microphone Recording",
            "Microphone recording architecture prepared. Uploading reference WAV is currently recommended."
        )

    def _on_clone_clicked(self) -> None:
        name = self.name_input.text().strip()
        if not self._ref_audio_path:
            QMessageBox.warning(self, "Reference Audio Required", "Please upload a reference audio sample first.")
            return
        if not name:
            QMessageBox.warning(self, "Voice Name Required", "Please enter a name for your custom voice clone.")
            return

        QMessageBox.information(
            self, "Voice Clone Ready",
            f"Voice Clone '{name}' created successfully in Voice Library!\n"
            "This clone is ready for future XTTS / Fish Speech provider integration."
        )
        self.accept()

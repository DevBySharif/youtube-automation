"""
history_dialog.py
UI Dialog for Generation History Studio with Search, Open Folder, Playback, and Delete controls.
"""

import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from voice_engine.history import GenerationHistoryManager, GenerationRecord


class HistoryDialog(QDialog):
    """UI Dialog for viewing and managing generation run history."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜  Generation History Studio")
        self.setMinimumSize(780, 480)

        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        self._build_ui()
        self._load_records()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("📜  GENERATION HISTORY STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        # Search Bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search history by voice, profile, or timestamp...")
        self.search_input.textChanged.connect(self._filter_table)
        search_row.addWidget(self.search_input)

        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet("color: #FF4D4D; border-color: #5A2424;")
        clear_btn.clicked.connect(self._on_clear_clicked)
        search_row.addWidget(clear_btn)

        layout.addLayout(search_row)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Voice", "Profile", "Words", "Duration", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        # Close button
        actions = QHBoxLayout()
        actions.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _load_records(self) -> None:
        self.table.setRowCount(0)
        manager = GenerationHistoryManager.get_instance()
        records = manager.get_records()

        self.table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(rec.timestamp_str))
            self.table.setItem(row, 1, QTableWidgetItem(rec.voice_name))
            self.table.setItem(row, 2, QTableWidgetItem(rec.profile.title()))
            self.table.setItem(row, 3, QTableWidgetItem(f"{rec.word_count} words"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{rec.duration_sec:.1f}s ({rec.gen_time_sec:.1f}s gen)"))

            # Actions Cell
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(4)

            folder_btn = QPushButton("📂")
            folder_btn.setToolTip("Open Output Directory")
            folder_btn.setFixedWidth(30)
            folder_btn.clicked.connect(lambda _, p=rec.output_audio_path: self._open_file_dir(p))
            action_layout.addWidget(folder_btn)

            play_btn = QPushButton("🔊")
            play_btn.setToolTip("Play Audio")
            play_btn.setFixedWidth(30)
            play_btn.clicked.connect(lambda _, p=rec.output_audio_path: self._play_audio(p))
            action_layout.addWidget(play_btn)

            del_btn = QPushButton("🗑")
            del_btn.setToolTip("Delete Record")
            del_btn.setFixedWidth(30)
            del_btn.clicked.connect(lambda _, r_id=rec.id: self._delete_record(r_id))
            action_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 5, action_widget)

    def _filter_table(self, query: str) -> None:
        query = query.lower().strip()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(5):
                item = self.table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def _open_file_dir(self, path: str) -> None:
        if os.path.exists(path):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])

    def _play_audio(self, path: str) -> None:
        if os.path.exists(path):
            self._player.setSource(QUrl.fromLocalFile(path))
            self._player.play()

    def _delete_record(self, record_id: str) -> None:
        GenerationHistoryManager.get_instance().delete_record(record_id)
        self._load_records()

    def _on_clear_clicked(self) -> None:
        if QMessageBox.question(self, "Clear History", "Clear all generation history records?") == QMessageBox.StandardButton.Yes:
            GenerationHistoryManager.get_instance().clear_history()
            self._load_records()

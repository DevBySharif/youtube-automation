"""
image_history_dialog.py
UI Dialog for Image History Studio.
"""

import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from image_engine.history import ImageHistoryManager


class ImageHistoryDialog(QDialog):
    """UI Dialog for browsing previously generated image history."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜  Image History Studio")
        self.setMinimumSize(820, 480)
        self._build_ui()
        self._load_records()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("📜  IMAGE HISTORY STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        # Search Row
        s_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search image history by prompt, model, or timestamp...")
        self.search_input.textChanged.connect(self._filter_table)
        s_row.addWidget(self.search_input)
        layout.addLayout(s_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Provider", "Model", "Prompt Summary", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _load_records(self) -> None:
        records = ImageHistoryManager.get_instance().get_records()
        self.table.setRowCount(len(records))

        for row, rec in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(rec.timestamp_str))
            self.table.setItem(row, 1, QTableWidgetItem(rec.provider_id.upper()))
            self.table.setItem(row, 2, QTableWidgetItem(rec.model_name))
            self.table.setItem(row, 3, QTableWidgetItem(rec.prompt[:50] + "…"))

            folder_btn = QPushButton("📂")
            folder_btn.setFixedWidth(30)
            folder_btn.clicked.connect(lambda _, p=rec.output_path: self._open_file(p))
            self.table.setCellWidget(row, 4, folder_btn)

    def _filter_table(self, query: str) -> None:
        query = query.lower().strip()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(4):
                item = self.table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def _open_file(self, path: str) -> None:
        if os.path.exists(path):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])

"""
image_plan_dialog.py
UI Dialog for AI Image & Camera Planning Studio Preview.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
)
from PySide6.QtCore import Qt


class ImagePlanDialog(QDialog):
    """UI Dialog for viewing AI-generated image timeline planning metadata."""

    def __init__(self, plan_data: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🖼  AI Image & Camera Planning Studio")
        self.setMinimumSize(850, 520)
        self.plan_data = plan_data
        self._build_ui()
        self._load_table()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("🖼  AI IMAGE & CAMERA PLANNING STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        sub = QLabel("Planned image events, shot framing, camera movement, and structured prompts derived from narration intelligence.")
        sub.setStyleSheet("color: #9E9E9E; font-size: 8.5pt;")
        layout.addWidget(sub)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Img #", "Time Range", "Duration", "Shot & Motion", "Main Subject", "Structured Prompt"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _load_table(self) -> None:
        self.table.setRowCount(len(self.plan_data))
        for row, ev in enumerate(self.plan_data):
            self.table.setItem(row, 0, QTableWidgetItem(f"#{ev.get('image_index', row + 1)}"))
            self.table.setItem(row, 1, QTableWidgetItem(f"{ev.get('start_time', 0.0)}s - {ev.get('end_time', 0.0)}s"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{ev.get('duration', 0.0)}s"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{ev.get('camera_angle', 'Medium')} ({ev.get('camera_movement', 'Hold')})"))
            self.table.setItem(row, 4, QTableWidgetItem(str(ev.get('main_subject', 'Subject'))))
            self.table.setItem(row, 5, QTableWidgetItem(str(ev.get('positive_prompt', ''))))

"""
image_queue_dialog.py
UI Dialog for AI Image Generation Queue & Batch Studio.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QProgressBar,
)
from PySide6.QtCore import Qt
from image_engine.registry import ImageProviderRegistry
from image_engine.queue_manager import ImageBatchScheduler


class ImageQueueDialog(QDialog):
    """UI Dialog for managing AI Image Generation queue and provider selection."""

    def __init__(self, plan_events: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🖼  AI Image Generation Queue Studio")
        self.setMinimumSize(850, 520)
        self.plan_events = plan_events
        self.scheduler = ImageBatchScheduler()

        self._build_ui()
        self._populate_queue()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("🖼  AI IMAGE GENERATION QUEUE STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        # Provider Selector Row
        p_row = QHBoxLayout()
        p_row.addWidget(QLabel("IMAGE PROVIDER:"))
        self.provider_combo = QComboBox()
        for prov in ImageProviderRegistry.get_instance().list_providers():
            self.provider_combo.addItem(prov["name"], userData=prov["id"])
        p_row.addWidget(self.provider_combo, stretch=1)

        run_btn = QPushButton("▶  Generate All Images")
        run_btn.setObjectName("generateButton")
        run_btn.clicked.connect(self._run_batch)
        p_row.addWidget(run_btn)

        layout.addLayout(p_row)

        # Queue Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Task ID", "Scene", "Prompt Summary", "Status", "Progress"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _populate_queue(self) -> None:
        tasks = self.scheduler.populate_queue(self.plan_events, "output/images")
        self.table.setRowCount(len(tasks))

        for row, t in enumerate(tasks):
            self.table.setItem(row, 0, QTableWidgetItem(t.task_id))
            self.table.setItem(row, 1, QTableWidgetItem(f"Scene {t.scene_index}"))
            self.table.setItem(row, 2, QTableWidgetItem(t.prompt[:60] + "…"))
            self.table.setItem(row, 3, QTableWidgetItem(t.status.upper()))
            self.table.setItem(row, 4, QTableWidgetItem(f"{t.progress_pct}%"))

    def _run_batch(self) -> None:
        provider_id = self.provider_combo.currentData()
        self.scheduler.run_all(provider_id)
        self._populate_queue()

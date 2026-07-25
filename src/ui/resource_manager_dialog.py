"""
resource_manager_dialog.py
Resource Manager UI window (Help -> Resource Manager...).

Allows users to inspect local model availability and download missing resources explicitly.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QProgressBar, QMessageBox, QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui  import QColor

from config import APP_NAME
from resource_manager import ResourceManager, ResourceDownloadWorker, ManagedResource


class ResourceManagerDialog(QDialog):
    """Resource Manager dialog for model status & explicit downloading."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} — Resource Manager")
        self.setMinimumSize(720, 420)
        self._worker = None

        self._build_ui()
        self.refresh_resources()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Header with status badge
        header_row = QHBoxLayout()
        header_title = QLabel("<b>Managed Model Resources</b>")
        header_title.setStyleSheet("font-size: 11pt;")
        header_row.addWidget(header_title)

        header_row.addStretch()

        self.status_badge = QLabel("Checking…")
        self.status_badge.setStyleSheet("""
            background-color: #252526;
            border-radius: 4px;
            padding: 3px 10px;
            font-weight: bold;
            font-size: 9.5pt;
        """)
        header_row.addWidget(self.status_badge)
        layout.addLayout(header_row)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Resource Name", "Category", "Est. Size", "Local Status", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_msg_label = QLabel("")
        self.status_msg_label.setStyleSheet("color: #4CC2FF; font-size: 9pt;")
        layout.addWidget(self.status_msg_label)

        # Bottom Button Bar
        btn_bar = QHBoxLayout()

        self.download_all_btn = QPushButton("↓ Download All Missing Resources")
        self.download_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_all_btn.clicked.connect(self._download_all_missing)
        btn_bar.addWidget(self.download_all_btn)

        btn_bar.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_resources)
        btn_bar.addWidget(refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_bar.addWidget(close_btn)

        layout.addLayout(btn_bar)

    def refresh_resources(self) -> None:
        mgr = ResourceManager.get_instance()
        resources = mgr.get_all_resources()

        self.table.setRowCount(len(resources))
        all_ok = True

        for row, res in enumerate(resources):
            # Name
            item_name = QTableWidgetItem(res.name)
            item_name.setToolTip(res.description)
            self.table.setItem(row, 0, item_name)

            # Category
            self.table.setItem(row, 1, QTableWidgetItem(res.category))

            # Size
            self.table.setItem(row, 2, QTableWidgetItem(res.size_str))

            # Status
            status_item = QTableWidgetItem("Installed ✓" if res.is_installed else "Missing ❌")
            if res.is_installed:
                status_item.setForeground(QColor("#6A9153"))
            else:
                status_item.setForeground(QColor("#F14C4C"))
                all_ok = False
            self.table.setItem(row, 3, status_item)

            # Action Button
            action_btn = QPushButton("Downloaded ✓" if res.is_installed else "↓ Download")
            action_btn.setEnabled(not res.is_installed)
            if not res.is_installed:
                action_btn.clicked.connect(lambda _, r_id=res.id: self._download_single(r_id))
            self.table.setCellWidget(row, 4, action_btn)

        if all_ok:
            self.status_badge.setText("🟢  OFFLINE READY")
            self.status_badge.setStyleSheet("background-color: #1E331E; color: #6A9153; border: 1px solid #4E733E; border-radius: 4px; padding: 3px 10px;")
            self.download_all_btn.setEnabled(False)
        else:
            self.status_badge.setText("🟡  RESOURCES MISSING")
            self.status_badge.setStyleSheet("background-color: #332200; color: #FFCC66; border: 1px solid #664400; border-radius: 4px; padding: 3px 10px;")
            self.download_all_btn.setEnabled(True)

    def _download_single(self, resource_id: str) -> None:
        self._start_download([resource_id])

    def _download_all_missing(self) -> None:
        mgr = ResourceManager.get_instance()
        missing = [r.id for r in mgr.get_all_resources() if not r.is_installed]
        if missing:
            self._start_download(missing)

    def _start_download(self, resource_ids: list) -> None:
        self.progress_bar.show()
        self.download_all_btn.setEnabled(False)
        self.status_msg_label.setText("Starting resource download…")

        self._worker = ResourceDownloadWorker(resource_ids, self)
        self._worker.status_changed.connect(self.status_msg_label.setText)
        self._worker.finished.connect(self._on_download_finished)
        self._worker.start()

    def _on_download_finished(self, success: bool, message: str) -> None:
        self.progress_bar.hide()
        self.download_all_btn.setEnabled(True)
        self.status_msg_label.setText("")

        if success:
            QMessageBox.information(self, "Download Complete", message)
        else:
            QMessageBox.critical(self, "Download Failed", message)

        self.refresh_resources()

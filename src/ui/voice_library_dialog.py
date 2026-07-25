"""
voice_library_dialog.py
UI Dialog for Voice Library with Search, Tags, Categories (Favorites, Recent, Downloaded, Custom).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QTabWidget, QWidget, QFrame,
)
from PySide6.QtCore import Qt
from voice_engine.registry import VoiceProviderRegistry


class VoiceLibraryDialog(QDialog):
    """UI Dialog for browsing and managing the Voice Library."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚  Voice Library Studio")
        self.setMinimumSize(680, 520)
        self.selected_voice_id: str = "af_bella"
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("📚  VOICE LIBRARY STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        # Search Bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search voices by name, accent, gender, or tag (e.g. 'Bella', 'Female', 'UK')...")
        self.search_input.textChanged.connect(self._filter_voices)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        # Tabs
        self.tabs = QTabWidget()
        self.all_list = QListWidget()
        self.fav_list = QListWidget()
        self.custom_list = QListWidget()

        self.tabs.addTab(self.all_list, "All Voices")
        self.tabs.addTab(self.fav_list, "⭐ Favorites")
        self.tabs.addTab(self.custom_list, "🎙 Custom & Cloned")

        layout.addWidget(self.tabs, stretch=1)

        self._populate_voices()

        # Action row
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)

        self.select_btn = QPushButton("Select Voice")
        self.select_btn.setObjectName("generateButton")
        self.select_btn.clicked.connect(self._on_select_clicked)
        actions.addWidget(self.select_btn)

        layout.addLayout(actions)

    def _populate_voices(self) -> None:
        self.all_list.clear()
        provider = VoiceProviderRegistry.get_instance().get_provider()
        for v in provider.list_voices():
            item = QListWidgetItem(f"{v.name}  [{v.accent} • {v.gender}]")
            item.setData(Qt.ItemDataRole.UserRole, v.voice_id)
            self.all_list.addItem(item)

    def _filter_voices(self, query: str) -> None:
        query = query.lower().strip()
        for i in range(self.all_list.count()):
            item = self.all_list.item(i)
            item.setHidden(query not in item.text().lower())

    def _on_select_clicked(self) -> None:
        curr = self.all_list.currentItem()
        if curr:
            self.selected_voice_id = curr.data(Qt.ItemDataRole.UserRole)
            self.accept()

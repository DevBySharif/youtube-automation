"""
dictionary_dialog.py
UI Dialog for Custom Pronunciation Dictionary Studio.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
)
from PySide6.QtCore import Qt
from voice_engine.dictionary import PronunciationDictionaryManager


class DictionaryDialog(QDialog):
    """UI Dialog for managing custom pronunciation replacements."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚  Custom Pronunciation Dictionary Studio")
        self.setMinimumSize(580, 420)
        self._build_ui()
        self._load_dictionary()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("📚  PRONUNCIATION DICTIONARY STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        sub = QLabel("Add custom phonetic pronunciations for brand names, acronyms, and technical terms.")
        sub.setStyleSheet("color: #9E9E9E; font-size: 8.5pt;")
        layout.addWidget(sub)

        # Input Row
        inp_row = QHBoxLayout()
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Word (e.g. 'YouTube')")
        inp_row.addWidget(self.word_input, stretch=1)

        self.pron_input = QLineEdit()
        self.pron_input.setPlaceholderText("Spoken Form (e.g. 'Yoo Toob')")
        inp_row.addWidget(self.pron_input, stretch=1)

        add_btn = QPushButton("➕  Add Word")
        add_btn.setObjectName("generateButton")
        add_btn.clicked.connect(self._on_add_clicked)
        inp_row.addWidget(add_btn)

        layout.addLayout(inp_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Word", "Spoken Pronunciation", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        # Close button
        actions = QHBoxLayout()
        actions.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _load_dictionary(self) -> None:
        self.table.setRowCount(0)
        dct = PronunciationDictionaryManager.get_instance().get_dictionary()
        self.table.setRowCount(len(dct))

        for row, (word, pron) in enumerate(dct.items()):
            self.table.setItem(row, 0, QTableWidgetItem(word))
            self.table.setItem(row, 1, QTableWidgetItem(pron))

            del_btn = QPushButton("🗑")
            del_btn.setFixedWidth(30)
            del_btn.clicked.connect(lambda _, w=word: self._delete_word(w))
            self.table.setCellWidget(row, 2, del_btn)

    def _on_add_clicked(self) -> None:
        word = self.word_input.text().strip()
        pron = self.pron_input.text().strip()
        if word and pron:
            PronunciationDictionaryManager.get_instance().add_entry(word, pron)
            self.word_input.clear()
            self.pron_input.clear()
            self._load_dictionary()

    def _delete_word(self, word: str) -> None:
        PronunciationDictionaryManager.get_instance().remove_entry(word)
        self._load_dictionary()

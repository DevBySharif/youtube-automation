"""
script_panel.py
Left panel — voiceover script editor with drag & drop support and live script statistics.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent

_KOKORO_WPM = 130
LARGE_SCRIPT_WORD_THRESHOLD = 3000


class ScriptEditor(QPlainTextEdit):
    """QPlainTextEdit with drag & drop for .txt files."""

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText(
            "Paste your voiceover script here…\n\n"
            "Example:\n"
            "There is a stranger you have never forgotten.\n"
            "Someone you saw once.\n"
            "Maybe on a train.\n\n"
            "Tip: You can also drag & drop a .txt file here."
        )
        font = QFont("Consolas", 10, QFont.Weight.Medium)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(".txt"):
                    event.acceptProposedAction()
                    return
        elif mime.hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                filepath = url.toLocalFile()
                if filepath.lower().endswith(".txt") and os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                            content = fh.read()
                        self.setPlainText(content)
                        self.file_dropped.emit(content)
                        event.acceptProposedAction()
                        return
                    except OSError:
                        pass
        elif mime.hasText():
            self.setPlainText(mime.text())
            event.acceptProposedAction()
        else:
            event.ignore()


class ScriptPanel(QWidget):
    """Left panel containing section label, script editor card, and live stats bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._speed_multiplier = 1.0
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 10, 16)
        layout.setSpacing(12)

        # Main Script Card
        card = QFrame()
        card.setObjectName("card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(12)

        # Header row
        header_row = QHBoxLayout()
        label = QLabel("📝  VOICEOVER SCRIPT")
        label.setObjectName("sectionLabel")
        header_row.addWidget(label)
        header_row.addStretch()
        c_layout.addLayout(header_row)

        self.editor = ScriptEditor()
        c_layout.addWidget(self.editor, stretch=1)

        # Live Stats Toolbar
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("""
            QFrame {
                background-color: #161616;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                padding: 4px 12px;
            }
            QLabel {
                color: #9E9E9E;
                font-size: 8.5pt;
                font-family: Consolas, monospace;
            }
        """)
        stats_layout = QHBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(8, 4, 8, 4)
        stats_layout.setSpacing(14)

        self.words_label = QLabel("Words: 0")
        self.chars_label = QLabel("Chars: 0")
        self.est_label   = QLabel("Est. Audio: 0s")

        stats_layout.addWidget(self.words_label)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.chars_label)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.est_label, stretch=1)

        c_layout.addWidget(self.stats_frame)

        layout.addWidget(card, stretch=1)

    def _connect_signals(self) -> None:
        self.editor.textChanged.connect(self._update_stats)

    def set_speed_multiplier(self, speed: float) -> None:
        self._speed_multiplier = speed
        self._update_stats()

    def _update_stats(self) -> None:
        text = self.get_script()
        words = len(text.split()) if text else 0
        chars = len(text)

        wpm = _KOKORO_WPM * self._speed_multiplier
        total_seconds = int((words / wpm) * 60) if wpm > 0 and words > 0 else 0
        m, s = divmod(total_seconds, 60)
        est_str = f"{m}m {s:02d}s" if m > 0 else f"{s}s"

        self.words_label.setText(f"Words: {words:,}")
        self.chars_label.setText(f"Chars: {chars:,}")
        self.est_label.setText(f"Est. Audio: ~{est_str}")

    def get_script(self) -> str:
        return self.editor.toPlainText().strip()

    def set_script(self, text: str) -> None:
        self.editor.setPlainText(text)
        self._update_stats()

    def is_empty(self) -> bool:
        return not self.editor.toPlainText().strip()

    def word_count(self) -> int:
        return len(self.get_script().split())

    def estimated_minutes(self, speed: float = 1.0) -> float:
        wpm = _KOKORO_WPM * speed
        return self.word_count() / wpm if wpm > 0 else 0.0

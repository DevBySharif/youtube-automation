"""
output_tabs.py
Bottom tabbed panel:
  Tab 1 — Timestamp Script  (read-only editor, Copy, Save, Open Folder)
  Tab 2 — Voiceover         (embedded player, Export WAV, Open Folder)

Summary Banner:
  Displays output file summary upon successful generation.
"""

import os
import subprocess

from PySide6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QFileDialog, QApplication,
    QLabel, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ui.audio_player import AudioPlayerWidget


def _open_folder(path: str) -> None:
    """Open folder in Windows Explorer."""
    if os.path.isdir(path):
        subprocess.Popen(["explorer", os.path.normpath(path)])
    elif os.path.isfile(path):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])


class SummaryFooter(QFrame):
    """Output summary banner with Lime Green theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #162410;
                border: 1px solid #9EFF00;
                border-radius: 8px;
                padding: 6px 12px;
            }
            QLabel {
                color: #9EFF00;
                font-size: 8.5pt;
                font-weight: 600;
                font-family: Consolas, monospace;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        self.label = QLabel("Generated: voice.wav + timestamp_script.txt")
        layout.addWidget(self.label)
        self.hide()

    def show_summary(self, audio_size_mb: float, word_count: int, scene_count: int) -> None:
        self.label.setText(
            f"✓ Generated Output: voice.wav ({audio_size_mb:.1f} MB)  |  "
            f"timestamp_script.txt ({word_count} words, {scene_count} scenes)"
        )
        self.show()


class TimestampTab(QWidget):
    """Tab 1 — Timestamp script display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._run_dir: str = ""
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText(
            "✨  READY TO GENERATE\n\n"
            "Paste your script on the left and click ▶ Generate Narration.\n\n"
            "You will receive:\n"
            "  ✓ High Quality Neural Voiceover (.wav)\n"
            "  ✓ Synchronized Word & Sentence Timestamps\n"
            "  ✓ SRT, VTT, and ASS Subtitle Files\n"
            "  ✓ AI Image Timeline & Scene Concept Plans\n"
            "  ✓ Master Video Automation JSON"
        )
        font = QFont("Consolas", 10.5)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit, stretch=1)

        # Output Summary Banner
        self.summary_footer = SummaryFooter()
        layout.addWidget(self.summary_footer)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.open_folder_btn = QPushButton("📂  Open Folder")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.setToolTip("Generate a script first to enable output folder")
        self.open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_btn.clicked.connect(lambda: _open_folder(self._run_dir))
        btn_row.addWidget(self.open_folder_btn)

        btn_row.addStretch()

        self.copy_btn = QPushButton("⎘  Copy")
        self.copy_btn.setEnabled(False)
        self.copy_btn.setToolTip("Generate script first to enable copy")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_row.addWidget(self.copy_btn)

        self.save_btn = QPushButton("↓  Save…")
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip("Generate script first to enable save")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_to_file)
        btn_row.addWidget(self.save_btn)

        layout.addLayout(btn_row)

    def _copy_to_clipboard(self) -> None:
        text = self.text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            original = self.copy_btn.text()
            self.copy_btn.setText("✓  Copied!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText(original))

    def _save_to_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Timestamp Script",
            "timestamp_script.txt",
            "Text Files (*.txt);;All Files (*)",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(self.text_edit.toPlainText())
            except OSError as exc:
                QMessageBox.critical(self, "Save Failed", str(exc))

    def set_script(self, text: str, run_dir: str = "", audio_path: str = "") -> None:
        self.text_edit.setPlainText(text)
        has_content = bool(text.strip())

        self.copy_btn.setEnabled(has_content)
        self.copy_btn.setToolTip("" if has_content else "Generate script first to enable copy")

        self.save_btn.setEnabled(has_content)
        self.save_btn.setToolTip("" if has_content else "Generate script first to enable save")

        self._run_dir = run_dir
        has_dir = bool(run_dir) and os.path.isdir(run_dir)
        self.open_folder_btn.setEnabled(has_dir)
        self.open_folder_btn.setToolTip("" if has_dir else "Generate script first to enable output folder")

        if has_content and audio_path and os.path.isfile(audio_path):
            audio_size = os.path.getsize(audio_path) / (1024 * 1024)
            words = len(text.split())
            scenes = text.count("[")
            self.summary_footer.show_summary(audio_size, words, scenes)
        else:
            self.summary_footer.hide()

    def clear(self) -> None:
        self.text_edit.clear()
        self.summary_footer.hide()
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(False)
        self._run_dir = ""


class AudioTab(QWidget):
    """Tab 2 — Embedded audio player (Voiceover)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._audio_path: str = ""
        self._run_dir:    str = ""
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(16)

        layout.addStretch()
        self.player = AudioPlayerWidget()
        layout.addWidget(self.player)
        layout.addStretch()

        btn_row = QHBoxLayout()

        self.open_folder_btn = QPushButton("📂  Open Folder")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.setToolTip("Generate voiceover first to enable output folder")
        self.open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_btn.clicked.connect(lambda: _open_folder(self._run_dir))
        btn_row.addWidget(self.open_folder_btn)

        btn_row.addStretch()

        self.export_btn = QPushButton("↓  Export WAV…")
        self.export_btn.setEnabled(False)
        self.export_btn.setToolTip("Generate voiceover first to export WAV")
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self._export_audio)
        btn_row.addWidget(self.export_btn)

        layout.addLayout(btn_row)

    def _export_audio(self) -> None:
        if not self._audio_path:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Voiceover",
            "voiceover.wav",
            "WAV Audio (*.wav);;All Files (*)",
        )
        if path:
            import shutil
            try:
                shutil.copy2(self._audio_path, path)
            except OSError as exc:
                QMessageBox.critical(self, "Export Failed", str(exc))

    def load_audio(self, audio_path: str, run_dir: str = "", auto_play: bool = False) -> None:
        self._audio_path = audio_path
        self._run_dir    = run_dir
        self.player.load(audio_path)

        has_audio = bool(audio_path) and os.path.isfile(audio_path)
        self.export_btn.setEnabled(has_audio)
        self.export_btn.setToolTip("" if has_audio else "Generate voiceover first to export WAV")

        has_dir = bool(run_dir) and os.path.isdir(run_dir)
        self.open_folder_btn.setEnabled(has_dir)
        self.open_folder_btn.setToolTip("" if has_dir else "Generate voiceover first to enable output folder")

        if auto_play and has_audio:
            self.player.play()

    def stop_playback(self) -> None:
        self.player.stop_playback()

    def clear(self) -> None:
        self.player.stop_playback()
        self._audio_path = ""
        self._run_dir    = ""
        self.export_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(False)


class OutputTabs(QTabWidget):
    """Bottom tabbed output panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timestamp_tab = TimestampTab()
        self.audio_tab     = AudioTab()

        self.addTab(self.timestamp_tab, "📜 Timestamp Script")
        self.addTab(self.audio_tab,     "🔊 Voiceover Audio")

    def display_results(
        self,
        timestamp_script: str,
        audio_path:       str,
        run_dir:          str = "",
        auto_open_folder: bool = False,
    ) -> None:
        self.audio_tab.stop_playback()
        self.timestamp_tab.set_script(timestamp_script, run_dir=run_dir, audio_path=audio_path)
        self.audio_tab.load_audio(audio_path, run_dir=run_dir, auto_play=False)
        self.setCurrentIndex(0)

        if auto_open_folder and run_dir and os.path.isdir(run_dir):
            _open_folder(run_dir)

    def display_partial(self, audio_path: str, run_dir: str = "") -> None:
        self.audio_tab.stop_playback()
        self.audio_tab.load_audio(audio_path, run_dir=run_dir, auto_play=False)
        self.setCurrentIndex(1)

    def clear(self) -> None:
        self.timestamp_tab.clear()
        self.audio_tab.clear()

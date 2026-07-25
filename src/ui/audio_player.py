"""
audio_player.py
Embedded audio player widget using QMediaPlayer + QAudioOutput with:
  • Play / Pause / Replay controls
  • Playback speed selector (0.75x to 2.0x)
  • Seek slider & time labels
  • Reveal file in explorer button
"""

import os
import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl, QTimer


def _format_time(ms: int) -> str:
    """Convert milliseconds to MM:SS string."""
    s = max(0, ms // 1000)
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"


class AudioPlayerWidget(QWidget):
    """
    Self-contained polished audio player.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path: str = ""
        self._slider_dragging = False

        # ── Qt Multimedia ────────────────────────────────────────────
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        # ── Seek-bar update timer ────────────────────────────────────
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._update_seek_bar)

        self._build_ui()
        self._connect_media_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Filename label
        self.filename_label = QLabel("No audio loaded")
        self.filename_label.setStyleSheet("color: #9E9E9E; font-size: 8.5pt;")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.filename_label)

        # Seek bar
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setEnabled(False)
        layout.addWidget(self.seek_slider)

        # Controls row
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("playButton")
        self.play_btn.setEnabled(False)
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        controls.addWidget(self.play_btn)

        self.replay_btn = QPushButton("🔁")
        self.replay_btn.setEnabled(False)
        self.replay_btn.setFixedSize(32, 32)
        self.replay_btn.setToolTip("Replay from start")
        self.replay_btn.clicked.connect(self._replay)
        controls.addWidget(self.replay_btn)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #9EFF00; font-weight: 700; font-size: 8.5pt;")
        controls.addWidget(self.time_label)

        controls.addStretch()

        # Speed selector
        controls.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentIndexChanged.connect(self._change_speed)
        controls.addWidget(self.speed_combo)

        # Reveal Folder Button
        self.folder_btn = QPushButton("📂 Reveal File")
        self.folder_btn.setEnabled(False)
        self.folder_btn.clicked.connect(self._open_folder)
        controls.addWidget(self.folder_btn)

        layout.addLayout(controls)

    def _connect_media_signals(self) -> None:
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.errorOccurred.connect(self._on_error)

        self.play_btn.clicked.connect(self._toggle_playback)
        self.seek_slider.sliderPressed.connect(self._on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self._on_slider_released)
        self.seek_slider.sliderMoved.connect(self._on_slider_moved)

    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.play_btn.setText("⏸" if playing else "▶")
        if playing:
            self._timer.start()
        else:
            self._timer.stop()

    def _on_duration_changed(self, duration_ms: int) -> None:
        self.seek_slider.setRange(0, duration_ms)
        self.seek_slider.setEnabled(duration_ms > 0)
        total = _format_time(duration_ms)
        cur = _format_time(self.player.position())
        self.time_label.setText(f"{cur} / {total}")

    def _on_position_changed(self, position_ms: int) -> None:
        if not self._slider_dragging:
            self.seek_slider.setValue(position_ms)
        total = _format_time(self.player.duration())
        self.time_label.setText(f"{_format_time(position_ms)} / {total}")

    def _on_error(self, error, error_string: str) -> None:
        self.filename_label.setText(f"Playback error: {error_string}")

    def _update_seek_bar(self) -> None:
        if not self._slider_dragging:
            self.seek_slider.setValue(self.player.position())

    def _toggle_playback(self) -> None:
        state = self.player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _replay(self) -> None:
        self.player.setPosition(0)
        self.player.play()

    def _change_speed(self) -> None:
        txt = self.speed_combo.currentText().replace("x", "")
        try:
            sp = float(txt)
            self.player.setPlaybackRate(sp)
        except Exception:
            pass

    def _open_folder(self) -> None:
        if os.path.exists(self._current_path):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(self._current_path)])

    def _on_slider_pressed(self) -> None:
        self._slider_dragging = True
        self._timer.stop()

    def _on_slider_released(self) -> None:
        self.player.setPosition(self.seek_slider.value())
        self._slider_dragging = False
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._timer.start()

    def _on_slider_moved(self, value: int) -> None:
        total = _format_time(self.player.duration())
        self.time_label.setText(f"{_format_time(value)} / {total}")

    def load(self, audio_path: str) -> None:
        """Load a WAV file. Stops any current playback first."""
        self.stop_playback()
        self._current_path = audio_path
        self.player.setSource(QUrl.fromLocalFile(audio_path))
        self.play_btn.setEnabled(True)
        self.replay_btn.setEnabled(True)
        self.folder_btn.setEnabled(True)
        filename = os.path.basename(audio_path)
        self.filename_label.setText(f"🎵  {filename}")
        self.filename_label.setStyleSheet("color: #F5F5F5; font-size: 8.5pt; font-weight: 700;")

    def stop_playback(self) -> None:
        """Stop current playback before loading new audio."""
        self.player.stop()
        self._timer.stop()

    def get_current_path(self) -> str:
        return self._current_path

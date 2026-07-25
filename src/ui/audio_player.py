"""
audio_player.py
Embedded audio player widget using QMediaPlayer + QAudioOutput.

Controls:
  - Play / Pause toggle button
  - Seek slider (updates every 250ms via QTimer)
  - Current time / total duration label
  - Filename display

The player and audio_output are stored as instance attributes to prevent
garbage collection before playback finishes.
"""

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QSizePolicy,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore       import Qt, QUrl, QTimer


def _format_time(ms: int) -> str:
    """Convert milliseconds to MM:SS string."""
    s     = max(0, ms // 1000)
    m, s  = divmod(s, 60)
    return f"{m:02d}:{s:02d}"


class AudioPlayerWidget(QWidget):
    """
    Self-contained audio player.
    Call load(path) to load a WAV file.
    Call stop_playback() before loading a new file.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_path: str = ""
        self._slider_dragging   = False

        # ── Qt Multimedia ────────────────────────────────────────────
        self.player       = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        # ── Seek-bar update timer ────────────────────────────────────
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._update_seek_bar)

        self._build_ui()
        self._connect_media_signals()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Filename label
        self.filename_label = QLabel("No audio loaded")
        self.filename_label.setStyleSheet("color: #808080; font-size: 9pt;")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.filename_label)

        # Seek bar
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setEnabled(False)
        layout.addWidget(self.seek_slider)

        # Controls row
        controls = QHBoxLayout()
        controls.setSpacing(12)

        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("playButton")
        self.play_btn.setEnabled(False)
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        controls.addWidget(self.play_btn)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        controls.addWidget(self.time_label)

        controls.addStretch()
        layout.addLayout(controls)

    # ── Media Signals ─────────────────────────────────────────────────────────

    def _connect_media_signals(self) -> None:
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.errorOccurred.connect(self._on_error)

        self.play_btn.clicked.connect(self._toggle_playback)
        self.seek_slider.sliderPressed.connect(self._on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self._on_slider_released)
        self.seek_slider.sliderMoved.connect(self._on_slider_moved)

    # ── Slots ─────────────────────────────────────────────────────────────────

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
        cur   = _format_time(self.player.position())
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

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self, audio_path: str) -> None:
        """Load a WAV file. Stops any current playback first."""
        self.stop_playback()
        self._current_path = audio_path
        self.player.setSource(QUrl.fromLocalFile(audio_path))
        self.play_btn.setEnabled(True)
        filename = os.path.basename(audio_path)
        self.filename_label.setText(filename)
        self.filename_label.setStyleSheet("color: #D4D4D4; font-size: 9pt;")

    def stop_playback(self) -> None:
        """Stop current playback before loading new audio."""
        self.player.stop()
        self._timer.stop()

    def get_current_path(self) -> str:
        return self._current_path

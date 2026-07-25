"""
controls_panel.py
Professional Voice Engine controls panel featuring:
  • Provider Selector Architecture
  • 15 AI Narration Profiles (Documentary, YouTube Explainer, Storytelling, Motivation, Finance, History, etc.)
  • Collapsible Advanced Voice Settings Panel (Stability, Expressiveness, Clarity, Energy, Pitch, Gain, Pauses)
  • Quality Profile Selector (Draft, Standard, High, Studio, Lossless)
  • Generation History Studio shortcut
  • Voice Library & Voice Cloning Studio shortcuts
  • Async Kokoro Voice Preview with Caching
"""

import os
import time
import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QSlider, QPushButton, QProgressBar, QSpacerItem, QSizePolicy, QFrame,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from config import VOICES, WHISPER_MODELS, DEFAULT_VOICE, DEFAULT_SPEED, DEFAULT_WHISPER_MODEL, TEMP_DIR
from voice_engine.registry import VoiceProviderRegistry
from voice_engine.capabilities import QUALITY_PROFILES, QualityProfile
from voice_engine.narration_modes import (
    NarrationMode, NARRATION_MODE_LABELS, NARRATION_MODE_PROFILES,
    HumanizationSettings, AdvancedVoiceSettings
)
from voice_engine.favorites import VoiceFavoritesManager
from ui.voice_cloning_dialog import VoiceCloningDialog
from ui.voice_library_dialog import VoiceLibraryDialog
from ui.advanced_voice_panel import AdvancedVoicePanel
from ui.history_dialog import HistoryDialog

log = logging.getLogger(__name__)


# ── Asynchronous Voice Preview Worker ──────────────────────────────────────────

class VoicePreviewWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, voice: str, speed: float, parent=None):
        super().__init__(parent)
        self.voice = voice
        self.speed = speed
        self.preview_text = "Hello! This is a preview of the selected voice."

    def run(self) -> None:
        out_dir = os.path.join(TEMP_DIR, "preview")
        os.makedirs(out_dir, exist_ok=True)
        tmp_path = os.path.join(out_dir, f"preview_{self.voice}.wav")

        try:
            # Check preview cache first for instant playback
            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                self.finished.emit(True, tmp_path)
                return

            provider = VoiceProviderRegistry.get_instance().get_provider()
            res_path = provider.generate_preview(
                voice_id=self.voice,
                output_path=tmp_path,
                text=self.preview_text,
                speed=self.speed,
            )
            if res_path and os.path.exists(res_path):
                self.finished.emit(True, res_path)
            else:
                self.finished.emit(False, "Preview audio generation failed.")
        except Exception as exc:
            log.warning("Voice preview generation failed: %s", exc)
            self.finished.emit(False, str(exc))


class ControlsPanel(QWidget):
    """
    Professional Voice Engine panel with Provider Matrix, 15 Narration Profiles,
    Collapsible Advanced Voice Settings, Quality Profiles, and History Studio.
    """

    generate_requested = Signal(str, float, str)
    cancel_requested   = Signal()
    speed_changed      = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stage_message: str   = "Ready"
        self._elapsed_start: float = 0.0
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.setInterval(1000)
        self._elapsed_timer.timeout.connect(self._tick_elapsed)

        # Audio Preview Player
        self._preview_worker: Optional[VoicePreviewWorker] = None
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.9)
        self._player.playbackStateChanged.connect(self._on_preview_state_changed)
        self._current_preview_wav: str = ""

        self._build_ui()
        self._connect_signals()
        self._update_voice_metadata()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 14, 14, 14)
        layout.setSpacing(12)

        # Tabbed Control Studio
        self.control_tabs = QTabWidget()

        # ── TAB 1: VOICE & SPEECH STUDIO ──────────────────────────────────────
        self.tab_core = QWidget()
        core_layout = QVBoxLayout(self.tab_core)
        core_layout.setContentsMargins(6, 10, 6, 6)
        core_layout.setSpacing(10)

        # Provider & Profile Card
        provider_card = QFrame()
        provider_card.setObjectName("card")
        p_layout = QVBoxLayout(provider_card)
        p_layout.setContentsMargins(12, 10, 12, 10)
        p_layout.setSpacing(8)

        # Provider Selector
        p_row = QHBoxLayout()
        p_label = QLabel("PROVIDER")
        p_label.setObjectName("sectionLabel")
        p_row.addWidget(p_label)

        self.provider_combo = QComboBox()
        for prov in VoiceProviderRegistry.get_instance().list_providers():
            label = prov["name"] if prov["available"] else f"{prov['name']} (Plug-in)"
            self.provider_combo.addItem(label, userData=prov["id"])
        p_row.addWidget(self.provider_combo, stretch=1)
        p_layout.addLayout(p_row)

        # 15 AI Narration Profiles
        n_row = QHBoxLayout()
        n_label = QLabel("PROFILE")
        n_label.setObjectName("sectionLabel")
        n_row.addWidget(n_label)

        self.narration_combo = QComboBox()
        for mode in NarrationMode:
            label = NARRATION_MODE_LABELS[mode]
            self.narration_combo.addItem(label, userData=mode.value)
        n_row.addWidget(self.narration_combo, stretch=1)
        p_layout.addLayout(n_row)

        core_layout.addWidget(provider_card)

        # Voice Card
        voice_card = QFrame()
        voice_card.setObjectName("card")
        card_layout = QVBoxLayout(voice_card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)

        # Header Row & Shortcuts
        card_header = QHBoxLayout()
        card_title = QLabel("🎙  VOICE & SPEECH")
        card_title.setObjectName("sectionLabel")
        card_header.addWidget(card_title)
        card_header.addStretch()

        self.fav_btn = QPushButton("⭐")
        self.fav_btn.setFixedWidth(28)
        self.fav_btn.setToolTip("Favorite Voice")
        self.fav_btn.clicked.connect(self._toggle_favorite)
        card_header.addWidget(self.fav_btn)

        self.library_btn = QPushButton("📚 Library")
        self.library_btn.setStyleSheet("padding: 3px 6px; font-size: 8pt;")
        self.library_btn.clicked.connect(self._open_voice_library)
        card_header.addWidget(self.library_btn)

        self.dict_btn = QPushButton("📖 Dict")
        self.dict_btn.setStyleSheet("padding: 3px 6px; font-size: 8pt;")
        self.dict_btn.setToolTip("Custom Pronunciation Dictionary Studio")
        self.dict_btn.clicked.connect(self._open_dictionary_studio)
        card_header.addWidget(self.dict_btn)

        self.clone_btn = QPushButton("🎙 Clone")
        self.clone_btn.setStyleSheet("padding: 3px 6px; font-size: 8pt;")
        self.clone_btn.clicked.connect(self._open_voice_cloning)
        card_header.addWidget(self.clone_btn)
        card_layout.addLayout(card_header)

        # Voice Dropdown
        self.voice_combo = QComboBox()
        for voice_id, voice_label in VOICES:
            self.voice_combo.addItem(voice_label, userData=voice_id)
        card_layout.addWidget(self.voice_combo)

        # Metadata & Badges Row
        meta_row = QHBoxLayout()
        self.meta_lang_label = QLabel("Language: English (US)")
        self.meta_lang_label.setObjectName("subTextLabel")
        meta_row.addWidget(self.meta_lang_label)
        meta_row.addStretch()

        badge_lbl = QLabel("Offline • Neural • 24kHz")
        badge_lbl.setStyleSheet("background-color: #1E1E1E; color: #9EFF00; border: 1px solid #9EFF00; border-radius: 4px; padding: 2px 6px; font-size: 7.5pt; font-weight: 700;")
        meta_row.addWidget(badge_lbl)
        card_layout.addLayout(meta_row)

        # Speed Header & Slider
        speed_header = QHBoxLayout()
        speed_title = QLabel("Speed")
        speed_title.setStyleSheet("font-size: 8.5pt; font-weight: 600; color: #F5F5F5;")
        speed_header.addWidget(speed_title)
        self.speed_label = QLabel(f"{DEFAULT_SPEED:.1f}×")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.speed_label.setStyleSheet("color: #9EFF00; font-weight: 700; font-size: 9pt;")
        speed_header.addWidget(self.speed_label)
        card_layout.addLayout(speed_header)

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("0.5×"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(5)
        self.speed_slider.setMaximum(20)
        self.speed_slider.setValue(10)
        self.speed_slider.setTickInterval(1)
        speed_row.addWidget(self.speed_slider, stretch=1)
        speed_row.addWidget(QLabel("2.0×"))
        card_layout.addLayout(speed_row)

        # Preview Button
        self.preview_btn = QPushButton("▶  Preview Voice")
        self.preview_btn.setObjectName("previewButton")
        self.preview_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.preview_btn.clicked.connect(self._start_voice_preview)
        card_layout.addWidget(self.preview_btn)

        core_layout.addWidget(voice_card)

        # Collapsible Advanced Voice Settings Panel
        self.adv_panel = AdvancedVoicePanel()
        core_layout.addWidget(self.adv_panel)

        # Whisper Alignment Card
        model_card = QFrame()
        model_card.setObjectName("card")
        m_layout = QVBoxLayout(model_card)
        m_layout.setContentsMargins(12, 8, 12, 8)
        m_layout.setSpacing(6)

        m_title = QLabel("⚡  WHISPER ALIGNMENT MODEL")
        m_title.setObjectName("sectionLabel")
        m_layout.addWidget(m_title)

        self.model_combo = QComboBox()
        for model_id, model_label in WHISPER_MODELS:
            self.model_combo.addItem(model_label, userData=model_id)
        self._set_combo_by_data(self.model_combo, DEFAULT_WHISPER_MODEL)
        m_layout.addWidget(self.model_combo)

        core_layout.addWidget(model_card)
        self.control_tabs.addTab(self.tab_core, "Voice Studio")

        # ── TAB 2: QUALITY & POST-PROCESSING ──────────────────────────────────
        self.tab_fx = QWidget()
        fx_layout = QVBoxLayout(self.tab_fx)
        fx_layout.setContentsMargins(8, 10, 8, 8)
        fx_layout.setSpacing(10)

        q_card = QFrame()
        q_card.setObjectName("card")
        qc_layout = QVBoxLayout(q_card)
        qc_layout.setContentsMargins(12, 12, 12, 12)
        qc_layout.setSpacing(8)

        qc_title = QLabel("🎚  VOICE QUALITY PROFILE")
        qc_title.setObjectName("sectionLabel")
        qc_layout.addWidget(qc_title)

        self.quality_combo = QComboBox()
        for qp in QualityProfile:
            prof = QUALITY_PROFILES[qp]
            self.quality_combo.addItem(f"{prof.name} — {prof.description}", userData=qp.value)
        self.quality_combo.setCurrentIndex(3)  # Studio 48 kHz / -14 LUFS default
        qc_layout.addWidget(self.quality_combo)

        # Audio FX Filters
        fx_title = QLabel("✨  HUMANIZATION & AUDIO FX")
        fx_title.setObjectName("sectionLabel")
        qc_layout.addWidget(fx_title)

        self.chk_natural_pauses = QCheckBox("Natural Sentence Pauses")
        self.chk_natural_pauses.setChecked(True)
        qc_layout.addWidget(self.chk_natural_pauses)

        self.chk_micro_pauses = QCheckBox("Random Micro Pauses")
        self.chk_micro_pauses.setChecked(True)
        qc_layout.addWidget(self.chk_micro_pauses)

        self.chk_breathing = QCheckBox("Sentence Breathing Effects")
        self.chk_breathing.setChecked(True)
        qc_layout.addWidget(self.chk_breathing)

        self.chk_lufs = QCheckBox("Loudness Normalization (-14 LUFS YouTube)")
        self.chk_lufs.setChecked(True)
        qc_layout.addWidget(self.chk_lufs)

        self.chk_limiter = QCheckBox("Brickwall Limiter (-1.0 dB)")
        self.chk_limiter.setChecked(True)
        qc_layout.addWidget(self.chk_limiter)

        fx_layout.addWidget(q_card)

        # History Studio Button
        self.history_btn = QPushButton("📜  Open Generation History Studio…")
        self.history_btn.clicked.connect(self._open_history_studio)
        fx_layout.addWidget(self.history_btn)

        fx_layout.addStretch()
        self.control_tabs.addTab(self.tab_fx, "Quality & History")

        layout.addWidget(self.control_tabs)

        # ── Generate Button ───────────────────────────────────────────────────
        self.generate_btn = QPushButton("▶  Generate")
        self.generate_btn.setObjectName("generateButton")
        self.generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.generate_btn)

        # ── Cancel Button ─────────────────────────────────────────────────────
        self.cancel_btn = QPushButton("✕  Cancel Generation")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.hide()
        layout.addWidget(self.cancel_btn)

        # ── Status Display ────────────────────────────────────────────────────
        self.status_label = QLabel("🟢  Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # ── Elapsed Time ──────────────────────────────────────────────────────
        self.elapsed_label = QLabel("")
        self.elapsed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.elapsed_label.setStyleSheet("color: #9E9E9E; font-size: 8.5pt; font-family: Consolas, monospace;")
        layout.addWidget(self.elapsed_label)

        # ── Progress Bar ──────────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        layout.addStretch()

    def _connect_signals(self) -> None:
        self.voice_combo.currentIndexChanged.connect(self._update_voice_metadata)
        self.narration_combo.currentIndexChanged.connect(self._on_narration_mode_changed)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)

    def _update_voice_metadata(self) -> None:
        voice_id = self.voice_combo.currentData() or "af_bella"
        VoiceFavoritesManager.get_instance().add_recent(voice_id)

        if voice_id.startswith("bf_") or voice_id.startswith("bm_"):
            lang_str = "Language: English (UK)"
        else:
            lang_str = "Language: English (US)"

        if voice_id.startswith("af_") or voice_id.startswith("bf_"):
            gender_str = "Female • Natural ★★★★★"
        else:
            gender_str = "Male • Natural ★★★★★"

        self.meta_lang_label.setText(f"{lang_str} • {gender_str}")

        is_fav = VoiceFavoritesManager.get_instance().is_favorite(voice_id)
        self.fav_btn.setText("⭐" if is_fav else "☆")

    def _toggle_favorite(self) -> None:
        voice_id = self.get_voice()
        is_fav = VoiceFavoritesManager.get_instance().toggle_favorite(voice_id)
        self.fav_btn.setText("⭐" if is_fav else "☆")

    def _on_narration_mode_changed(self) -> None:
        mode_val = self.narration_combo.currentData()
        try:
            mode = NarrationMode(mode_val)
            profile = NARRATION_MODE_PROFILES.get(mode, {})
            if "speed" in profile:
                spd_val = round(profile["speed"] * 10)
                self.speed_slider.setValue(spd_val)
            self.adv_panel.apply_profile_dict(profile)
        except ValueError:
            pass

    def _on_speed_changed(self, value: int) -> None:
        speed = value / 10.0
        self.speed_label.setText(f"{speed:.1f}×")
        self.speed_changed.emit(speed)

    def _on_generate_clicked(self) -> None:
        voice         = self.voice_combo.currentData()
        speed         = self.speed_slider.value() / 10.0
        whisper_model = self.model_combo.currentData()
        self.generate_requested.emit(voice, speed, whisper_model)

    def _open_voice_library(self) -> None:
        dlg = VoiceLibraryDialog(self)
        if dlg.exec():
            selected = dlg.selected_voice_id
            self.set_voice(selected)

    def _open_voice_cloning(self) -> None:
        dlg = VoiceCloningDialog(self)
        dlg.exec()

    def _open_dictionary_studio(self) -> None:
        from ui.dictionary_dialog import DictionaryDialog
        dlg = DictionaryDialog(self)
        dlg.exec()

    def _open_history_studio(self) -> None:
        dlg = HistoryDialog(self)
        dlg.exec()

    # ── Voice Preview Workflow ────────────────────────────────────────────────

    def _start_voice_preview(self) -> None:
        self._player.stop()
        voice = self.get_voice()
        speed = self.get_speed()

        self.preview_btn.setEnabled(False)
        self.preview_btn.setText("⏳  Generating Preview…")

        self._preview_worker = VoicePreviewWorker(voice, speed, self)
        self._preview_worker.finished.connect(self._on_preview_generated)
        self._preview_worker.start()

    def _on_preview_generated(self, success: bool, res_path_or_err: str) -> None:
        if success and os.path.exists(res_path_or_err):
            self._current_preview_wav = res_path_or_err
            self.preview_btn.setText("🔊  Playing…")
            self._player.setSource(QUrl.fromLocalFile(res_path_or_err))
            self._player.play()
        else:
            self.preview_btn.setText("❌  Preview Failed")
            QTimer.singleShot(2500, self._reset_preview_button)

    def _on_preview_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self._reset_preview_button()

    def _reset_preview_button(self) -> None:
        self.preview_btn.setEnabled(True)
        self.preview_btn.setText("▶  Preview Voice")

    # ── Elapsed Timer ─────────────────────────────────────────────────────────

    def _tick_elapsed(self) -> None:
        elapsed  = int(time.monotonic() - self._elapsed_start)
        m, s     = divmod(elapsed, 60)
        self.elapsed_label.setText(f"{m:02d}:{s:02d} elapsed")

    def _start_elapsed(self) -> None:
        self._elapsed_start = time.monotonic()
        self.elapsed_label.setText("00:00 elapsed")
        self._elapsed_timer.start()

    def _stop_elapsed(self) -> None:
        self._elapsed_timer.stop()
        self.elapsed_label.setText("")

    # ── State Management ─────────────────────────────────────────────────────

    def set_checking_dependencies(self) -> None:
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("▶  Checking Dependencies…")
        self.set_status("🟡  Checking dependencies…", "working")

    def set_dependency_missing(self, is_missing: bool) -> None:
        if is_missing:
            self.generate_btn.setEnabled(False)
            self.generate_btn.setText("▶  Generate (Dependency Missing)")
            self.set_status("🔴  Dependency Missing", "error")
        else:
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("▶  Generate")
            self.set_status("🟢  Ready", "ready")

    def set_working(self, status_text: str = "Generating…") -> None:
        self._stage_message = status_text
        self.generate_btn.hide()
        self.cancel_btn.show()
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.voice_combo.setEnabled(False)
        self.speed_slider.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.preview_btn.setEnabled(False)

        icon = "🟡"
        if "Aligning" in status_text:
            icon = "🟠"
        elif "Grouping" in status_text:
            icon = "🔵"

        self.set_status(f"{icon}  {status_text}", "working")
        self._start_elapsed()

    def set_ready(self, status_text: str = "Ready") -> None:
        self._stop_elapsed()
        self.cancel_btn.hide()
        self.generate_btn.show()
        self.generate_btn.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_bar.hide()
        self.voice_combo.setEnabled(True)
        self.speed_slider.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.set_status(f"🟢  {status_text}", "ready")

    def set_done(self) -> None:
        self._stop_elapsed()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.cancel_btn.hide()
        self.generate_btn.show()
        self.voice_combo.setEnabled(True)
        self.speed_slider.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.set_status("🟢  Finished ✓", "done")

    def set_status(self, formatted_text: str, state: str = "ready") -> None:
        colour_map = {
            "ready":   "#9E9E9E",
            "working": "#9EFF00",
            "done":    "#9EFF00",
            "error":   "#FF4D4D",
        }
        colour = colour_map.get(state, "#9E9E9E")
        self.status_label.setStyleSheet(f"color: {colour}; font-size: 9.5pt; font-weight: 700;")
        self.status_label.setText(formatted_text)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def get_voice(self) -> str:
        return self.voice_combo.currentData() or DEFAULT_VOICE

    def get_speed(self) -> float:
        return self.speed_slider.value() / 10.0

    def get_whisper_model(self) -> str:
        return self.model_combo.currentData() or DEFAULT_WHISPER_MODEL

    def set_voice(self, voice_id: str) -> None:
        self._set_combo_by_data(self.voice_combo, voice_id)
        self._update_voice_metadata()

    def set_speed(self, speed: float) -> None:
        self.speed_slider.setValue(round(speed * 10))

    def set_whisper_model(self, model_id: str) -> None:
        self._set_combo_by_data(self.model_combo, model_id)

    @staticmethod
    def _set_combo_by_data(combo: QComboBox, data_value: str) -> None:
        for i in range(combo.count()):
            if combo.itemData(i) == data_value:
                combo.setCurrentIndex(i)
                return

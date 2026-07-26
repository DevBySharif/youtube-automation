"""
controls_panel.py
Creator-First Voice Engine Controls Panel for YouTube Creators.
Design Highlights:
  • DOMINANT 60px Sticky Bottom Action Bar (Generate button fixed at bottom, never scrolls away!)
  • Merged 3-Card Layout (Voice Studio, Advanced Voice Settings, Subtitle Alignment)
  • Collapsible Advanced Voice Settings (Zero space when collapsed!)
  • Big Typography & Capability Badges (Offline • Neural • 24kHz)
"""

import os
import time
import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QSlider, QPushButton, QProgressBar, QSizePolicy, QFrame,
    QTabWidget, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from config import VOICES, WHISPER_MODELS, DEFAULT_VOICE, DEFAULT_SPEED, DEFAULT_WHISPER_MODEL, TEMP_DIR
from voice_engine.registry import VoiceProviderRegistry
from voice_engine.capabilities import QUALITY_PROFILES, QualityProfile
from voice_engine.narration_modes import (
    NarrationMode, NARRATION_MODE_LABELS, NARRATION_MODE_PROFILES,
    AdvancedVoiceSettings,
)
from voice_engine.dictionary import PronunciationDictionaryManager
from voice_engine.favorites import VoiceFavoritesManager
from ui.advanced_voice_panel import AdvancedVoicePanel
from ui.card_widget import CardWidget


class ControlsPanel(QWidget):
    """Right side panel containing Voice Studio, Advanced Settings, and Sticky Action Bar."""

    generation_requested = Signal()
    generate_requested   = Signal()
    cancel_requested     = Signal()
    speed_changed        = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._is_generating: bool = False
        self.fav_manager = VoiceFavoritesManager()

        # Preview Audio Player
        self._audio_output = QAudioOutput()
        self._media_player = QMediaPlayer()
        self._media_player.setAudioOutput(self._audio_output)
        self._preview_thread: Optional[QThread] = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ── MAIN SCROLL AREA FOR CARDS ────────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #161616;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #3E3E3E;
                border-radius: 3px;
            }
        """)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        c_layout = QVBoxLayout(self.scroll_content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(16)

        # ── CARD 1: VOICE STUDIO (Merged Workflow, Provider, Profile, Voice) ───
        voice_studio_card = CardWidget(title="VOICE STUDIO", icon="🎙")

        # Shortcuts row inside header
        if voice_studio_card.header_layout:
            self.fav_btn = QPushButton("⭐")
            self.fav_btn.setFixedWidth(28)
            self.fav_btn.setToolTip("Favorite Voice")
            self.fav_btn.clicked.connect(self._toggle_favorite)
            voice_studio_card.header_layout.addWidget(self.fav_btn)

            self.library_btn = QPushButton("📚 Library")
            self.library_btn.setStyleSheet("padding: 4px 8px; font-size: 8pt;")
            self.library_btn.clicked.connect(self._open_voice_library)
            voice_studio_card.header_layout.addWidget(self.library_btn)

            self.dict_btn = QPushButton("📖 Dict")
            self.dict_btn.setStyleSheet("padding: 4px 8px; font-size: 8pt;")
            self.dict_btn.setToolTip("Custom Pronunciation Dictionary Studio")
            self.dict_btn.clicked.connect(self._open_dictionary_studio)
            voice_studio_card.header_layout.addWidget(self.dict_btn)

            self.clone_btn = QPushButton("🎙 Clone")
            self.clone_btn.setStyleSheet("padding: 4px 8px; font-size: 8pt;")
            self.clone_btn.clicked.connect(self._open_voice_cloning)
            voice_studio_card.header_layout.addWidget(self.clone_btn)

        # Voice Selector
        self.voice_combo = QComboBox()
        self.voice_combo.setMinimumHeight(36)
        for voice_id, voice_label in VOICES:
            self.voice_combo.addItem(voice_label, userData=voice_id)
        voice_studio_card.content_layout.addWidget(self.voice_combo)

        # Metadata Row
        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        self.meta_lang_label = QLabel("Language: English (US)")
        self.meta_lang_label.setObjectName("subTextLabel")
        self.meta_lang_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        meta_row.addWidget(self.meta_lang_label)

        badge_lbl = QLabel("Offline • Neural • 24kHz")
        badge_lbl.setStyleSheet("background-color: #1E1E1E; color: #9EFF00; border: 1px solid #9EFF00; border-radius: 4px; padding: 2px 6px; font-size: 7.5pt; font-weight: 700;")
        meta_row.addWidget(badge_lbl)
        voice_studio_card.content_layout.addLayout(meta_row)

        # AI Narration Profile Selector
        n_row = QHBoxLayout()
        n_label = QLabel("STYLE PROFILE")
        n_label.setObjectName("sectionLabel")
        n_row.addWidget(n_label)

        self.narration_combo = QComboBox()
        self.narration_combo.setMinimumHeight(32)
        for mode in NarrationMode:
            label = NARRATION_MODE_LABELS[mode]
            self.narration_combo.addItem(label, userData=mode.value)
        n_row.addWidget(self.narration_combo, stretch=1)
        voice_studio_card.content_layout.addLayout(n_row)

        # Provider & Workflow Row
        p_row = QHBoxLayout()
        p_label = QLabel("PROVIDER")
        p_label.setObjectName("sectionLabel")
        p_row.addWidget(p_label)

        self.provider_combo = QComboBox()
        for prov in VoiceProviderRegistry.get_instance().list_providers():
            label = prov["name"] if prov["available"] else f"{prov['name']} (Plug-in)"
            self.provider_combo.addItem(label, userData=prov["id"])
        p_row.addWidget(self.provider_combo, stretch=1)
        voice_studio_card.content_layout.addLayout(p_row)

        wf_row = QHBoxLayout()
        wf_lbl = QLabel("WORKFLOW")
        wf_lbl.setObjectName("sectionLabel")
        wf_row.addWidget(wf_lbl)

        self.workflow_combo = QComboBox()
        self.workflow_combo.addItem("🎙  Voice Only", userData="voice_only")
        self.workflow_combo.addItem("📝  Voice + Timestamps", userData="voice_timestamps")
        self.workflow_combo.addItem("🎬  Full Video Automation", userData="full_automation")
        self.workflow_combo.setCurrentIndex(2)
        wf_row.addWidget(self.workflow_combo, stretch=1)
        voice_studio_card.content_layout.addLayout(wf_row)

        # Preview Button
        self.preview_btn = QPushButton("▶  Preview Voice")
        self.preview_btn.setObjectName("previewButton")
        self.preview_btn.setMinimumHeight(36)
        self.preview_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.preview_btn.clicked.connect(self._start_voice_preview)
        voice_studio_card.content_layout.addWidget(self.preview_btn)

        c_layout.addWidget(voice_studio_card)

        # ── CARD 2: ADVANCED VOICE SETTINGS CARD (Collapsible) ────────────────
        self.adv_panel = AdvancedVoicePanel()
        c_layout.addWidget(self.adv_panel)

        # ── CARD 3: SUBTITLE ALIGNMENT MODEL CARD ─────────────────────────────
        model_card = CardWidget(title="SUBTITLE ALIGNMENT MODEL", icon="⚡")
        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(32)
        for model_id, model_label in WHISPER_MODELS:
            self.model_combo.addItem(model_label, userData=model_id)
        self._set_combo_by_data(self.model_combo, DEFAULT_WHISPER_MODEL)
        model_card.content_layout.addWidget(self.model_combo)
        c_layout.addWidget(model_card)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # ── STICKY BOTTOM ACTION BAR (GENERATE BUTTON DOMINATES 60px TALL) ────
        action_bar = QFrame()
        action_bar.setStyleSheet("""
            QFrame {
                background-color: #161616;
                border: 1px solid #2A2A2A;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        act_layout = QVBoxLayout(action_bar)
        act_layout.setContentsMargins(8, 8, 8, 8)
        act_layout.setSpacing(6)

        self.generate_btn = QPushButton("▶   GENERATE NARRATION")
        self.generate_btn.setObjectName("generateButton")
        self.generate_btn.setMinimumHeight(60)  # Dominant 60px height
        self.generate_btn.setStyleSheet("""
            QPushButton#generateButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B8FF3B, stop:1 #9EFF00);
                border: 1px solid #9EFF00;
                color: #0D0D0D;
                font-size: 13pt;
                font-weight: 800;
                border-radius: 10px;
                letter-spacing: 0.8px;
            }
            QPushButton#generateButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #CEFF66, stop:1 #B8FF3B);
            }
            QPushButton#generateButton:pressed {
                background: #82D600;
            }
        """)
        self.generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        act_layout.addWidget(self.generate_btn)

        self.cancel_btn = QPushButton("✕  Cancel Generation")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setMinimumHeight(38)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.hide()
        act_layout.addWidget(self.cancel_btn)

        self.status_label = QLabel("🟢  Ready to Generate")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        act_layout.addWidget(self.status_label)

        self.elapsed_label = QLabel("")
        self.elapsed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.elapsed_label.setStyleSheet("color: #9E9E9E; font-size: 8.5pt; font-family: Consolas, monospace;")
        act_layout.addWidget(self.elapsed_label)

        main_layout.addWidget(action_bar)

    def _connect_signals(self) -> None:
        self.generate_btn.clicked.connect(self.generation_requested.emit)
        self.generate_btn.clicked.connect(self.generate_requested.emit)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        self.narration_combo.currentIndexChanged.connect(self._on_narration_profile_changed)

    def _on_provider_changed(self, idx: int) -> None:
        provider_id = self.provider_combo.itemData(idx)
        self.adv_panel.update_provider_capabilities(provider_id)

    def _on_narration_profile_changed(self, idx: int) -> None:
        mode_val = self.narration_combo.itemData(idx)
        prof = NARRATION_MODE_PROFILES.get(mode_val)
        if prof:
            self.adv_panel.apply_profile_dict(prof)

    def _toggle_favorite(self) -> None:
        voice_id = self.selected_voice_id
        if self.fav_manager.is_favorite(voice_id):
            self.fav_manager.remove_favorite(voice_id)
            self.fav_btn.setText("⭐")
        else:
            self.fav_manager.add_favorite(voice_id)
            self.fav_btn.setText("🌟")

    def _open_voice_library(self) -> None:
        from ui.voice_library_dialog import VoiceLibraryDialog
        dlg = VoiceLibraryDialog(self)
        if dlg.exec():
            selected = dlg.get_selected_voice_id()
            if selected:
                self._set_combo_by_data(self.voice_combo, selected)

    def _open_dictionary_studio(self) -> None:
        from ui.dictionary_dialog import DictionaryStudioDialog
        dlg = DictionaryStudioDialog(self)
        dlg.exec()

    def _open_voice_cloning(self) -> None:
        from ui.voice_cloning_dialog import VoiceCloningDialog
        dlg = VoiceCloningDialog(self)
        dlg.exec()

    def _open_history_studio(self) -> None:
        from ui.history_dialog import HistoryStudioDialog
        dlg = HistoryStudioDialog(self)
        dlg.exec()

    def _start_voice_preview(self) -> None:
        voice_id = self.selected_voice_id
        speed = self.selected_speed
        text = "The quick brown fox jumps over the lazy dog."

        self.preview_btn.setEnabled(False)
        self.preview_btn.setText("⏳ Synthesizing…")

        from voice_engine.preview_worker import VoicePreviewWorker
        self._preview_thread = QThread()
        self._preview_worker = VoicePreviewWorker(voice_id=voice_id, text=text, speed=speed)
        self._preview_worker.moveToThread(self._preview_thread)

        self._preview_thread.started.connect(self._preview_worker.run)
        self._preview_worker.finished.connect(self._on_preview_finished)
        self._preview_worker.error.connect(self._on_preview_error)

        self._preview_worker.finished.connect(self._preview_thread.quit)
        self._preview_worker.finished.connect(self._preview_worker.deleteLater)
        self._preview_thread.finished.connect(self._preview_thread.deleteLater)

        self._preview_thread.start()

    def _on_preview_finished(self, audio_path: str) -> None:
        self.preview_btn.setEnabled(True)
        self.preview_btn.setText("▶  Preview Voice")
        if os.path.isfile(audio_path):
            self._media_player.setSource(QUrl.fromLocalFile(audio_path))
            self._media_player.play()

    def _on_preview_error(self, err_msg: str) -> None:
        self.preview_btn.setEnabled(True)
        self.preview_btn.setText("▶  Preview Voice")

    @property
    def selected_voice_id(self) -> str:
        return self.voice_combo.currentData() or DEFAULT_VOICE

    @property
    def selected_whisper_model(self) -> str:
        return self.model_combo.currentData() or DEFAULT_WHISPER_MODEL

    @property
    def selected_provider_id(self) -> str:
        return self.provider_combo.currentData() or "kokoro"

    @property
    def selected_speed(self) -> float:
        return self.adv_panel.get_settings().speed

    def set_speed(self, speed: float) -> None:
        self.adv_panel.apply_profile_dict({"speed": speed})

    def get_advanced_settings(self) -> AdvancedVoiceSettings:
        return self.adv_panel.get_settings()

    def set_generating(self, is_generating: bool) -> None:
        self._is_generating = is_generating
        self.generate_btn.setEnabled(not is_generating)
        self.cancel_btn.setVisible(is_generating)
        self.voice_combo.setEnabled(not is_generating)
        self.model_combo.setEnabled(not is_generating)
        self.provider_combo.setEnabled(not is_generating)
        self.narration_combo.setEnabled(not is_generating)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def set_elapsed(self, seconds: float) -> None:
        self.elapsed_label.setText(f"Elapsed: {seconds:.1f}s")

    def set_voice(self, voice_id: str) -> None:
        self._set_combo_by_data(self.voice_combo, voice_id)

    def set_whisper_model(self, model_id: str) -> None:
        self._set_combo_by_data(self.model_combo, model_id)

    def set_checking_dependencies(self) -> None:
        self.status_label.setText("🔍 Checking Dependencies…")
        self.generate_btn.setEnabled(False)

    def set_ready(self) -> None:
        self.status_label.setText("🟢  Ready to Generate")
        self.generate_btn.setEnabled(True)

    def set_dependency_missing(self, missing: bool) -> None:
        if missing:
            self.status_label.setText("⚠️ Dependency Issue Detected")
            self.generate_btn.setEnabled(False)
        else:
            self.set_ready()

    def clear_elapsed(self) -> None:
        self.elapsed_label.setText("")

    def _set_combo_by_data(self, combo: QComboBox, target_data: Any) -> None:
        for idx in range(combo.count()):
            if combo.itemData(idx) == target_data:
                combo.setCurrentIndex(idx)
                return

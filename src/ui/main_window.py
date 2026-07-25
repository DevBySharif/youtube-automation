"""
main_window.py
QMainWindow — top-level window for Timestamp Script Analyzer.

Features:
  - Top notification banner for dependency warnings (Issue 15)
  - Disables Generate button when dependencies are missing (Issue 2)
  - Settings dialog (Issue 20)
  - Collapsible error dialogs with stack trace (Issue 5 & 18)
  - Open Log Folder menu action (Issue 17)
  - State machine (IDLE / GENERATING / CANCELLING)
"""

import os
import logging
from enum import Enum, auto

from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QMessageBox, QWidget, QVBoxLayout,
    QDialog, QVBoxLayout as QVL, QLabel, QDialogButtonBox,
)
from PySide6.QtCore import Qt, QThread, QSettings
from PySide6.QtGui  import QAction, QCloseEvent

from config import (
    APP_NAME, APP_VERSION, LOGS_DIR,
    DEFAULT_VOICE, DEFAULT_SPEED, DEFAULT_WHISPER_MODEL,
    make_run_dir,
)
from ui.script_panel        import ScriptPanel, LARGE_SCRIPT_WORD_THRESHOLD
from ui.controls_panel      import ControlsPanel
from ui.output_tabs         import OutputTabs
from ui.notification_banner import NotificationBanner
from ui.settings_dialog     import SettingsDialog
from ui.error_dialog        import show_error_dialog
from pipeline.worker        import PipelineWorker

log = logging.getLogger(__name__)

SETTINGS_VOICE  = "voice"
SETTINGS_SPEED  = "speed"
SETTINGS_MODEL  = "whisper_model"
SETTINGS_GEOM   = "window/geometry"
SETTINGS_SCRIPT = "lastScript"


class PipelineState(Enum):
    IDLE        = auto()
    GENERATING  = auto()
    CANCELLING  = auto()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._state:         PipelineState          = PipelineState.IDLE
        self._thread:        QThread | None         = None
        self._worker:        PipelineWorker | None  = None
        self._run_dir:       str                    = ""
        self._dep_worker:    Optional[Any]          = None
        self._settings = QSettings("TimestampAnalyzer", "App")

        self._setup_window()
        self._build_menu()
        self._build_layout()
        self._restore_settings()

        # Set checking status immediately
        self.controls_panel.set_checking_dependencies()

        log.info("%s %s started.", APP_NAME, APP_VERSION)

    def start_async_dependency_check(self) -> None:
        """Start background QThread for dependency scanning (Requirement 3)."""
        from dependency_check import AsyncDependencyWorker
        self._dep_worker = AsyncDependencyWorker(self)
        self._dep_worker.status_changed.connect(self._on_dep_status_changed)
        self._dep_worker.finished.connect(self._on_dep_check_finished)
        self._dep_worker.start()

    def _on_dep_status_changed(self, status_msg: str) -> None:
        self.statusBar().showMessage(status_msg)

    def _on_dep_check_finished(self, issues: list) -> None:
        self.show_dependency_warnings(issues)
        if not issues:
            self._has_dep_issue = False
            self.controls_panel.set_ready()
            log.info("[TIMELINE] Generate enabled")
            self.statusBar().showMessage("Ready", 3000)
        else:
            self._has_dep_issue = True
            self.controls_panel.set_dependency_missing(True)
            self.statusBar().showMessage("Dependency issue detected", 5000)

    def _setup_window(self) -> None:
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 850)
        self.setMinimumSize(1100, 700)

    # ── Menu Bar ──────────────────────────────────────────────────────────────

    def _build_menu(self) -> None:
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        save_script = QAction("Save Timestamp Script…", self)
        save_script.setShortcut("Ctrl+S")
        save_script.triggered.connect(lambda: self.output_tabs.timestamp_tab._save_to_file())
        file_menu.addAction(save_script)

        export_audio = QAction("Export Voiceover…", self)
        export_audio.triggered.connect(lambda: self.output_tabs.audio_tab._export_audio())
        file_menu.addAction(export_audio)

        open_folder = QAction("Open Output Folder", self)
        open_folder.triggered.connect(self._open_run_folder)
        file_menu.addAction(open_folder)

        file_menu.addSeparator()

        settings_action = QAction("Preferences & Settings…", self)  # Issue 20
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help Menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction(f"About {APP_NAME}", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        resource_action = QAction("Resource Manager…", self)  # Managed Resources
        resource_action.setShortcut("Ctrl+R")
        resource_action.triggered.connect(self._show_resource_manager)
        help_menu.addAction(resource_action)

        diag_action = QAction("System Diagnostics…", self)  # Requirement 7
        diag_action.setShortcut("Ctrl+Shift+D")
        diag_action.triggered.connect(self._show_diagnostics)
        help_menu.addAction(diag_action)

        copy_diag_action = QAction("Copy Diagnostic Report", self)
        copy_diag_action.triggered.connect(self._copy_diagnostic_report)
        help_menu.addAction(copy_diag_action)

        help_menu.addSeparator()

        open_logs_action = QAction("Open Log Folder", self)  # Issue 17
        open_logs_action.triggered.connect(self._open_log_folder)
        help_menu.addAction(open_logs_action)

        espeak_action = QAction("espeak-ng Install Guide", self)
        espeak_action.triggered.connect(self._show_espeak_guide)
        help_menu.addAction(espeak_action)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)

        # Top Notification Banner (Issue 15)
        self.banner = NotificationBanner()
        self.banner.recheck_requested.connect(self._recheck_dependencies)
        v_layout.addWidget(self.banner)

        # Main Splitters
        self.script_panel   = ScriptPanel()
        self.controls_panel = ControlsPanel()
        self.output_tabs    = OutputTabs()

        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.addWidget(self.script_panel)
        top_splitter.addWidget(self.controls_panel)
        top_splitter.setSizes([820, 340])
        top_splitter.setCollapsible(0, False)
        top_splitter.setCollapsible(1, False)

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self.output_tabs)
        main_splitter.setSizes([480, 280])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)

        v_layout.addWidget(main_splitter, stretch=1)
        self.setCentralWidget(container)

        # Signal connections
        self.controls_panel.generate_requested.connect(self._on_generate)
        self.controls_panel.cancel_requested.connect(self._on_cancel)
        self.controls_panel.speed_changed.connect(self.script_panel.set_speed_multiplier)
        self.script_panel.editor.textChanged.connect(self._save_last_script)

    # ── State Machine ─────────────────────────────────────────────────────────

    def _set_state(self, state: PipelineState) -> None:
        self._state = state
        log.debug("State -> %s", state.name)

        if state == PipelineState.IDLE:
            if self._has_dep_issue:
                self.controls_panel.set_dependency_missing(True)
            else:
                self.controls_panel.set_ready()

        elif state == PipelineState.GENERATING:
            self.controls_panel.set_working("Synthesizing Voice…")

        elif state == PipelineState.CANCELLING:
            self.controls_panel.cancel_btn.setEnabled(False)
            self.controls_panel.set_status("Cancelling…", "working")

    # ── Settings ──────────────────────────────────────────────────────────────

    def _restore_settings(self) -> None:
        voice  = self._settings.value(SETTINGS_VOICE,  DEFAULT_VOICE)
        speed  = float(self._settings.value(SETTINGS_SPEED, DEFAULT_SPEED))
        model  = self._settings.value(SETTINGS_MODEL,  DEFAULT_WHISPER_MODEL)
        geom   = self._settings.value(SETTINGS_GEOM,   None)
        script = self._settings.value(SETTINGS_SCRIPT, "")

        self.controls_panel.set_voice(voice)
        self.controls_panel.set_speed(speed)
        self.controls_panel.set_whisper_model(model)
        self.script_panel.set_speed_multiplier(speed)

        if geom:
            self.restoreGeometry(geom)
        if script:
            self.script_panel.set_script(script)

    def _save_settings(self) -> None:
        self._settings.setValue(SETTINGS_VOICE,  self.controls_panel.get_voice())
        self._settings.setValue(SETTINGS_SPEED,  self.controls_panel.get_speed())
        self._settings.setValue(SETTINGS_MODEL,  self.controls_panel.get_whisper_model())
        self._settings.setValue(SETTINGS_GEOM,   self.saveGeometry())

    def _save_last_script(self) -> None:
        self._settings.setValue(SETTINGS_SCRIPT, self.script_panel.get_script())

    def _show_settings(self) -> None:
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._restore_settings()

    # ── Pre-Generate Validation ───────────────────────────────────────────────

    def _validate_before_generate(self, script: str, voice: str, speed: float) -> bool:
        if not script:
            QMessageBox.warning(
                self, "Empty Script",
                "Please enter a voiceover script before generating.\n\n"
                "Tip: Paste your script or drag & drop a .txt file into the editor."
            )
            return False

        word_count = self.script_panel.word_count()
        if word_count > LARGE_SCRIPT_WORD_THRESHOLD:
            est_minutes = self.script_panel.estimated_minutes(speed)
            reply = QMessageBox.question(
                self, "Large Script",
                f"Your script contains <b>{word_count:,} words</b>.<br><br>"
                f"Estimated generation time: <b>~{est_minutes:.0f} minutes</b><br><br>"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False

        return True

    # ── Pipeline Execution ───────────────────────────────────────────────────

    def _on_generate(self, voice: str, speed: float, whisper_model: str) -> None:
        if self._state != PipelineState.IDLE or self._has_dep_issue:
            return

        script = self.script_panel.get_script()
        if not self._validate_before_generate(script, voice, speed):
            return

        self.output_tabs.audio_tab.stop_playback()
        self._save_settings()

        self._run_dir = make_run_dir()
        log.info("Generate — voice=%s speed=%.1f model=%s run_dir=%s", voice, speed, whisper_model, self._run_dir)

        self._set_state(PipelineState.GENERATING)

        self._worker = PipelineWorker(
            script             = script,
            voice              = voice,
            speed              = speed,
            output_dir         = self._run_dir,
            whisper_model_size = whisper_model,
        )
        self._thread = QThread(self)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.status_changed.connect(self._on_status_changed)
        self._worker.finished.connect(self._on_pipeline_finished)
        self._worker.partial_failure.connect(self._on_partial_failure)
        self._worker.error.connect(self._on_pipeline_error)
        self._worker.cancelled.connect(self._on_pipeline_cancelled)

        self._worker.finished.connect(self._thread.quit)
        self._worker.partial_failure.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._worker.cancelled.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_cancel(self) -> None:
        if self._state != PipelineState.GENERATING:
            return
        self._set_state(PipelineState.CANCELLING)
        if self._worker:
            self._worker.cancel()

    # ── Worker Callbacks ──────────────────────────────────────────────────────

    def _on_status_changed(self, message: str) -> None:
        self.controls_panel.set_working(message)
        self.statusBar().showMessage(message)

    def _on_pipeline_finished(self, timestamp_script: str, audio_path: str) -> None:
        log.info("Pipeline finished.")
        self._set_state(PipelineState.IDLE)
        self.controls_panel.set_done()

        auto_open = self._settings.value("auto_open_folder", "false") == "true"
        self.output_tabs.display_results(
            timestamp_script, audio_path, run_dir=self._run_dir, auto_open_folder=auto_open
        )
        self.statusBar().showMessage("Finished ✓", 5000)

    def _on_partial_failure(self, message: str, audio_path: str) -> None:
        log.warning("Partial failure — audio preserved at %s", audio_path)
        self._set_state(PipelineState.IDLE)
        self.controls_panel.set_status("🔴  Partial failure", "error")

        if audio_path and os.path.isfile(audio_path):
            self.output_tabs.display_partial(audio_path, run_dir=self._run_dir)

        show_error_dialog("Partial Failure", "Audio alignment or scene grouping failed, but your voiceover was preserved.", message, self)
        self.statusBar().showMessage("Partial failure — audio preserved", 6000)

    def _on_pipeline_error(self, message: str) -> None:
        log.error("Pipeline error: %s", message)
        self._set_state(PipelineState.IDLE)
        self.controls_panel.set_status("🔴  Error", "error")

        # Classify initialization failures by root cause (not converting every failure to espeak)
        msg_lower = message.lower()
        if "en_core_web_sm" in msg_lower or "spacy" in msg_lower or "e050" in msg_lower:
            dialog_title = "English NLP Model Missing (spaCy)"
            user_msg = (
                "The spaCy English NLP model <b>en_core_web_sm</b> is missing.<br><br>"
                "The application will attempt to download it automatically on the next run."
            )
        elif "espeak" in msg_lower or "phonemizer" in msg_lower:
            dialog_title = "eSpeak NG Engine Missing"
            user_msg = (
                "Voiceover generation failed due to missing <b>espeak-ng</b> engine.<br><br>"
                "Please ensure espeak-ng is installed on Windows."
            )
        elif "whisper" in msg_lower:
            dialog_title = "Whisper Alignment Error"
            user_msg = "Audio alignment failed while processing with Faster-Whisper."
        else:
            dialog_title = "Voiceover Generation Failed"
            user_msg = "Voiceover generation failed due to a runtime initialization error."

        show_error_dialog(dialog_title, user_msg, message, self)
        self.statusBar().showMessage("Error", 5000)

    def _on_pipeline_cancelled(self) -> None:
        log.info("Pipeline cancelled cleanly.")
        self._set_state(PipelineState.IDLE)
        self.controls_panel.set_status("🟢  Cancelled", "ready")
        self.statusBar().showMessage("Cancelled", 3000)

    # ── Dependency Banner & Check ─────────────────────────────────────────────

    def show_dependency_warnings(self, issues: list) -> None:
        """Sleek top banner for dependency issues (Requirements 2 & 3)."""
        if not issues:
            self._has_dep_issue = False
            self.banner.hide()
            self.controls_panel.set_dependency_missing(False)
            return

        self._has_dep_issue = True
        self.controls_panel.set_dependency_missing(True)

        issue_lines = "<br>".join(issues)
        msg_html = f"<b>Dependency Check Failed</b><br>{issue_lines}"
        self.banner.show_warning(msg_html, guide_callback=self._show_espeak_guide)

    def _recheck_dependencies(self) -> None:
        self.controls_panel.set_checking_dependencies()
        from dependency_check import DependencyManager
        DependencyManager.get_instance().get_espeak_result(force_rescan=True)
        self.start_async_dependency_check()

    # ── Actions ───────────────────────────────────────────────────────────────

    def _open_run_folder(self) -> None:
        from ui.output_tabs import _open_folder
        if self._run_dir and os.path.isdir(self._run_dir):
            _open_folder(self._run_dir)
        else:
            from config import TEMP_DIR
            _open_folder(TEMP_DIR)

    def _open_log_folder(self) -> None:
        import subprocess
        if os.path.exists(LOGS_DIR):
            subprocess.Popen(["explorer", os.path.normpath(LOGS_DIR)])

    def _show_resource_manager(self) -> None:
        from ui.resource_manager_dialog import ResourceManagerDialog
        dlg = ResourceManagerDialog(self)
        dlg.exec()

    def _show_diagnostics(self) -> None:
        from ui.diagnostics_dialog import DiagnosticsDialog
        dlg = DiagnosticsDialog(self)
        dlg.exec()

    def _copy_diagnostic_report(self) -> None:
        from ui.diagnostics_dialog import generate_diagnostic_report
        from PySide6.QtWidgets import QApplication, QMessageBox
        report = generate_diagnostic_report()
        QApplication.clipboard().setText(report)
        QMessageBox.information(self, "Report Copied", "System diagnostic report copied to clipboard!\n\nYou can paste it directly into support tickets or messages.")

    def _show_about(self) -> None:
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br><br>"
            "Converts voiceover scripts into synchronized timestamp scripts.<br><br>"
            "<b>Pipeline:</b><br>"
            "Voiceover Script → Kokoro TTS → Whisper Alignment → Scene Grouper → Timestamp Script<br><br>"
            "<b>Models Cache:</b><br>"
            "Saved permanently in %LOCALAPPDATA%\\Timestamp Script Analyzer\\models\\"
        )

    def _show_espeak_guide(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("espeak-ng Install Guide")
        dlg.setMinimumWidth(460)
        layout = QVL(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(QLabel("<b>espeak-ng is required for Kokoro TTS</b>"))
        layout.addWidget(QLabel(
            "1. Download the installer:<br>"
            "   <a href='https://github.com/espeak-ng/espeak-ng/releases'>https://github.com/espeak-ng/espeak-ng/releases</a><br><br>"
            "2. Run espeak-ng-X64.msi<br><br>"
            "3. Click Next → Install → Finish<br><br>"
            "4. Click <b>🔄 Re-check</b> on the top banner."
        ))
        for child in dlg.findChildren(QLabel):
            child.setOpenExternalLinks(True)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._state != PipelineState.IDLE:
            reply = QMessageBox.question(
                self, "Pipeline Running",
                "Generation is in progress.\n\nCancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            if self._worker:
                self._worker.cancel()
            if self._thread:
                self._thread.quit()
                self._thread.wait(3000)

        self._save_settings()
        self.output_tabs.audio_tab.stop_playback()
        event.accept()

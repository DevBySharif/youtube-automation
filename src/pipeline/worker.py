"""
worker.py
QObject-based pipeline worker — runs in a QThread.

Signals:
    status_changed(str)           — human-readable stage description
    finished(str, str)            — (timestamp_script, audio_path) — full success
    partial_failure(str, str)     — (error_message, audio_path) — TTS ok, later stage failed
    error(str)                    — fatal error (TTS failed, no audio)
    cancelled()                   — user cancelled cleanly

Recovery:
    If TTS succeeds but Whisper or grouping fails, partial_failure is emitted.
    The audio is preserved and surfaced to the user even on partial failure.
    Only if TTS itself fails is error() emitted (nothing to recover).
"""

import os
import time
import logging
import tempfile
import threading

from PySide6.QtCore import QObject, Signal, Slot

from pipeline.pipeline import Pipeline

log = logging.getLogger(__name__)


class PipelineWorker(QObject):
    status_changed  = Signal(str)
    finished        = Signal(str, str)   # (timestamp_script, audio_path)
    partial_failure = Signal(str, str)   # (error_message, audio_path) — audio preserved
    error           = Signal(str)        # fatal — no audio produced
    cancelled       = Signal()

    def __init__(
        self,
        script:             str,
        voice:              str,
        speed:              float,
        output_dir:         str,
        whisper_model_size: str = "base",
    ):
        super().__init__()
        self.script             = script
        self.voice              = voice
        self.speed              = speed
        self.output_dir         = output_dir
        self.whisper_model_size = whisper_model_size
        self._cancel_event      = threading.Event()

    def cancel(self) -> None:
        """Signal the worker to stop at the next checkpoint."""
        log.info("Cancellation requested.")
        self._cancel_event.set()

    def _is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    @Slot()
    def run(self) -> None:
        pipeline   = Pipeline(whisper_model_size=self.whisper_model_size)
        start_time = time.perf_counter()

        log.info(
            "Pipeline started — voice=%s  speed=%.1f  model=%s  dir=%s",
            self.voice, self.speed, self.whisper_model_size, self.output_dir,
        )

        # ── Stage 1: Kokoro TTS ────────────────────────────────────────────────
        # If TTS fails, there is nothing to recover — emit error() and exit.
        self.status_changed.emit("Generating audio…")
        t0 = time.perf_counter()
        audio_path: str = ""
        try:
            audio_path = pipeline.run_tts(
                self.script, self.voice, self.speed,
                self.output_dir, self._is_cancelled,
            )
        except Exception as exc:
            log.exception("TTS stage failed.")
            self.error.emit(f"Voice generation failed:\n\n{exc}")
            return

        if self._is_cancelled():
            log.info("Pipeline cancelled after TTS stage.")
            self.cancelled.emit()
            return

        log.info("TTS complete — %.2fs  path=%s", time.perf_counter() - t0, audio_path)

        # ── Stage 2: Faster-Whisper Alignment ─────────────────────────────────
        # If alignment fails, preserve audio and emit partial_failure().
        self.status_changed.emit("Aligning audio…")
        t0 = time.perf_counter()
        words = None
        try:
            words = pipeline.run_alignment(audio_path, self._is_cancelled)
        except Exception as exc:
            log.exception("Whisper alignment stage failed.")
            self.partial_failure.emit(
                f"Audio alignment failed:\n\n{exc}\n\n"
                "The generated audio is preserved and available in the Voiceover tab.",
                audio_path,
            )
            return

        if self._is_cancelled():
            log.info("Pipeline cancelled after alignment stage.")
            self.cancelled.emit()
            return

        log.info("Alignment complete — %.2fs  %d words", time.perf_counter() - t0, len(words))

        # ── Stage 3: Concept Grouper ───────────────────────────────────────────
        # If grouping fails, preserve audio and emit partial_failure().
        self.status_changed.emit("Grouping scenes…")
        t0 = time.perf_counter()
        timestamp_script: str = ""
        try:
            timestamp_script = pipeline.run_grouper(
                self.script, words, self._is_cancelled
            )
        except Exception as exc:
            log.exception("Scene grouping stage failed.")
            self.partial_failure.emit(
                f"Scene grouping failed:\n\n{exc}\n\n"
                "The generated audio is preserved and available in the Voiceover tab.",
                audio_path,
            )
            return

        if self._is_cancelled():
            log.info("Pipeline cancelled after grouping stage.")
            self.cancelled.emit()
            return

        log.info("Grouping complete — %.2fs", time.perf_counter() - t0)

        # ── Atomic auto-save of timestamp script ──────────────────────────────
        # Write to a .tmp file first, then rename — prevents a corrupt .txt
        # if the process is killed while writing.
        script_path = os.path.join(self.output_dir, "timestamp_script.txt")
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=self.output_dir, suffix=".txt.tmp", text=True
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
                fh.write(timestamp_script)
            os.replace(tmp_path, script_path)   # atomic on same volume
            log.info("Auto-saved timestamp script → %s", script_path)
        except OSError as exc:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            log.warning("Atomic auto-save failed: %s", exc)

        total = time.perf_counter() - start_time
        log.info("Pipeline complete — total=%.2fs", total)

        self.status_changed.emit("Finished ✓")
        self.finished.emit(timestamp_script, audio_path)

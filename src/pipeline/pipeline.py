"""
pipeline.py
Pipeline class — wraps the three processing stages.

The TTS stage uses the TTSEngine abstraction.
Swap the engine by passing a different implementation:

    Pipeline(tts_engine=PiperEngine())
    Pipeline(tts_engine=ElevenLabsEngine())

Only one file changes — this one (or not even this one, just the caller).

Alignment and grouping stages remain unchanged.
"""

import os
import logging
from typing import Callable, List, Dict, Optional

from tts_engines.base import TTSEngine

log = logging.getLogger(__name__)


class Pipeline:
    """
    Wraps TTS, Whisper alignment, and concept grouping.

    Args:
        whisper_model_size: 'tiny', 'base', or 'small'
        tts_engine:         Any TTSEngine implementation. Defaults to KokoroEngine.
    """

    def __init__(
        self,
        whisper_model_size: str             = "base",
        tts_engine:         TTSEngine | None = None,
    ):
        self.whisper_model_size = whisper_model_size

        if tts_engine is None:
            from tts_engines.kokoro_engine import KokoroEngine
            tts_engine = KokoroEngine()

        self.tts_engine: TTSEngine = tts_engine
        log.info("Pipeline ready — TTS=%s  Whisper=%s", tts_engine.name, whisper_model_size)

    def run_tts(
        self,
        script:       str,
        voice:        str,
        speed:        float,
        output_dir:   str,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> Optional[str]:
        """
        Stage 1 — Generate audio via the configured TTSEngine.
        Returns: path to voice.wav, or None if cancelled.
        """
        if cancel_check and cancel_check():
            return None

        output_path = os.path.join(output_dir, "voice.wav")
        return self.tts_engine.generate(
            text=script,
            output_path=output_path,
            voice=voice,
            speed=speed,
            cancel_check=cancel_check,   # chunk-level cancellation inside TTS
        )

    def run_alignment(
        self,
        audio_path:   str,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> Optional[List[Dict]]:
        """
        Stage 2 — Extract word-level timestamps with Faster-Whisper.
        Returns: list of { word, start, end }, or None if cancelled.
        """
        if cancel_check and cancel_check():
            return None
        from aligner import get_word_timestamps
        return get_word_timestamps(audio_path, model_size=self.whisper_model_size)

    def run_grouper(
        self,
        original_script: str,
        words:           List[Dict],
        cancel_check:     Optional[Callable[[], bool]] = None,
    ) -> Optional[str]:
        """
        Stage 3 — Group words into timestamped scenes.
        Returns: formatted timestamp script string, or None if cancelled.
        """
        if cancel_check and cancel_check():
            return None
        from concept_grouper import group_into_scenes
        return group_into_scenes(original_script, words)

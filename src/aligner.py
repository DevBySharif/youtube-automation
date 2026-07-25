"""
aligner.py
Faster-Whisper forced alignment module with timestamped runtime tracing.
"""

import logging
from datetime import datetime
from typing import List, Dict, Callable, Optional

log = logging.getLogger(__name__)

# Cache loaded Whisper model instances
_model_cache: dict = {}


def _get_whisper_model(model_size: str = "base"):
    if model_size not in _model_cache:
        # 1. Deterministic Stage 2 (Whisper Alignment) Resource Verification
        from resource_manager import ResourceManager
        mgr = ResourceManager.get_instance()
        mgr.verify_whisper_resource(model_size)

        try:
            from faster_whisper import WhisperModel
            _model_cache[model_size] = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8",
            )
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.info("[RUNTIME TRACE] %s WhisperModel loaded successfully (model_size=%s)", ts, model_size)
        except Exception as exc:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.error("[RUNTIME TRACE] %s First exception thrown in WhisperModel loading: %s", ts, exc)
            raise RuntimeError(f"Whisper Model Loading Error ({type(exc).__name__}): {exc}") from exc

    return _model_cache[model_size]


def get_word_timestamps(
    audio_path:   str,
    model_size:   str = "base",
    cancel_check: Optional[Callable[[], bool]] = None,
) -> List[Dict]:
    """
    Transcribe audio and extract word-level timestamps using Faster-Whisper.
    """
    model = _get_whisper_model(model_size)

    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log.info("[RUNTIME TRACE] %s Whisper transcription started — audio=%s", ts, audio_path)

    try:
        segments, _ = model.transcribe(
            audio_path,
            word_timestamps=True,
            language="en",
            beam_size=5,
        )
    except Exception as exc:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log.error("[RUNTIME TRACE] %s First exception thrown in Whisper transcription: %s", ts, exc)
        raise RuntimeError(f"Whisper Transcription Error ({type(exc).__name__}): {exc}") from exc

    words = []
    for segment in segments:
        if cancel_check and cancel_check():
            log.info("Whisper alignment cancelled during segment processing.")
            return []

        if segment.words:
            for w in segment.words:
                words.append({
                    "word":  w.word.strip(),
                    "start": round(w.start, 2),
                    "end":   round(w.end,   2),
                })

    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log.info("[RUNTIME TRACE] %s Whisper alignment completed — extracted %d words", ts, len(words))
    return words

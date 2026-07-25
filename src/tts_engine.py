"""
tts_engine.py  (src/)
Kokoro TTS wrapper — updated for desktop app paths.

Hidden preprocessing: strips [MM:SS] timestamps before synthesis.
The original timestamped script is never modified.
"""

import re
import os
import logging
import numpy as np
import soundfile as sf

from config import TEMP_DIR

log = logging.getLogger(__name__)

# Lazy-load the pipeline to avoid slow import at startup
_pipeline      = None
_pipeline_lang = None


def _get_pipeline(lang_code: str = "a"):
    """Return a cached KPipeline instance, reloading if language changes."""
    global _pipeline, _pipeline_lang
    if _pipeline is None or _pipeline_lang != lang_code:
        log.info("Loading Kokoro TTS pipeline (lang=%s)…", lang_code)
        from kokoro import KPipeline
        _pipeline      = KPipeline(lang_code=lang_code)
        _pipeline_lang = lang_code
        log.info("Kokoro TTS pipeline loaded.")
    return _pipeline


def _strip_timestamps(text: str) -> str:
    """
    Remove all [MM:SS] markers from text.
    Hidden preprocessing — timestamps never reach the TTS engine.
    """
    clean = re.sub(r'\[\d{2}:\d{2}\]', '', text)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    return clean.strip()


def generate_audio(
    script:     str,
    voice:      str  = "af_bella",
    speed:      float = 1.0,
    output_dir: str  = None,
) -> str:
    """
    Generate a WAV file from the given script using Kokoro TTS.

    Args:
        script:     Script text (may contain [MM:SS] — stripped internally).
        voice:      Kokoro voice name.
        speed:      Speaking speed multiplier (0.8–1.2).
        output_dir: Directory for the WAV. Defaults to TEMP_DIR.

    Returns:
        Absolute path to voiceover.wav.
    """
    clean_text = _strip_timestamps(script)
    if not clean_text:
        raise ValueError("Script is empty after timestamp removal.")

    # Detect language from voice prefix (b* = British, else American)
    lang_code = "b" if voice.startswith("b") else "a"
    pipeline  = _get_pipeline(lang_code)

    log.info("Generating audio — voice=%s speed=%.1f chars=%d", voice, speed, len(clean_text))

    audio_chunks = []
    try:
        for _, _, chunk in pipeline(clean_text, voice=voice, speed=speed):
            if chunk is not None and len(chunk) > 0:
                audio_chunks.append(chunk)
    except Exception as exc:
        raise RuntimeError(f"Kokoro TTS generation failed: {exc}") from exc

    if not audio_chunks:
        raise RuntimeError("Kokoro TTS produced no audio output.")

    audio = np.concatenate(audio_chunks, axis=0)

    out_dir = output_dir or TEMP_DIR
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "voiceover.wav")

    sf.write(output_path, audio, samplerate=24000)
    duration = len(audio) / 24000
    log.info("Audio saved — path=%s duration=%.2fs", output_path, duration)

    return output_path

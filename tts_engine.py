"""
tts_engine.py
Kokoro TTS wrapper for Timestamp Script Analyzer.

Responsibilities:
- Strip [MM:SS] timestamps from text before synthesis (hidden preprocessing)
- Generate WAV audio using Kokoro KPipeline
- Return path to the saved audio file

The original timestamped script is NEVER modified.
Only a clean copy is sent to the TTS engine.
"""

import re
import os
import tempfile
import numpy as np
import soundfile as sf

# Lazy-load the pipeline to avoid slow import at startup
_pipeline = None
_pipeline_lang = None


def _get_pipeline(lang_code: str = "a"):
    """Return a cached KPipeline instance, reloading if language changes."""
    global _pipeline, _pipeline_lang
    if _pipeline is None or _pipeline_lang != lang_code:
        from kokoro import KPipeline
        _pipeline = KPipeline(lang_code=lang_code)
        _pipeline_lang = lang_code
    return _pipeline


def _strip_timestamps(text: str) -> str:
    """
    Remove all [MM:SS] markers from text.
    This is the hidden preprocessing step — timestamps never reach the TTS engine.

    Example:
        "[00:00]\nThere is a stranger." -> "There is a stranger."
    """
    # Remove [MM:SS] patterns (e.g. [00:00], [01:24])
    clean = re.sub(r'\[\d{2}:\d{2}\]', '', text)
    # Collapse extra blank lines and strip leading/trailing whitespace
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    return clean.strip()


def generate_audio(
    script: str,
    voice: str = "af_bella",
    speed: float = 1.0,
    output_dir: str = None
) -> str:
    """
    Generate a WAV file from the given script using Kokoro TTS.

    Args:
        script:     The script text (may contain [MM:SS] timestamps — they will be stripped).
        voice:      Kokoro voice name (e.g. 'af_bella', 'am_adam').
        speed:      Speaking speed multiplier (0.8 – 1.2).
        output_dir: Directory to save the WAV file. Uses system temp if None.

    Returns:
        Absolute path to the generated voiceover.wav file.

    Raises:
        RuntimeError: If Kokoro fails to generate audio.
    """
    # Step 1: Strip timestamps — the TTS never sees [MM:SS]
    clean_text = _strip_timestamps(script)

    if not clean_text:
        raise ValueError("Script is empty after timestamp removal.")

    # Step 2: Determine language from voice prefix
    # af_ / am_ = American English ('a')
    # bf_ / bm_ = British English ('b')
    lang_code = "b" if voice.startswith("b") else "a"

    # Step 3: Load (or reuse) the pipeline
    pipeline = _get_pipeline(lang_code)

    # Step 4: Generate audio chunks
    audio_chunks = []
    try:
        for _, _, audio_chunk in pipeline(clean_text, voice=voice, speed=speed):
            if audio_chunk is not None and len(audio_chunk) > 0:
                audio_chunks.append(audio_chunk)
    except Exception as e:
        raise RuntimeError(f"Kokoro TTS generation failed: {e}") from e

    if not audio_chunks:
        raise RuntimeError("Kokoro TTS produced no audio output.")

    # Step 5: Concatenate all chunks into a single array
    audio = np.concatenate(audio_chunks, axis=0)

    # Step 6: Save to WAV
    if output_dir is None:
        output_dir = tempfile.gettempdir()

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "voiceover.wav")

    sf.write(output_path, audio, samplerate=24000)

    return output_path


# Available voices exposed to the frontend
AVAILABLE_VOICES = [
    {"id": "af_bella",   "label": "Bella — American Female (Warm)"},
    {"id": "af_sarah",   "label": "Sarah — American Female (Clear)"},
    {"id": "af_sky",     "label": "Sky — American Female (Bright)"},
    {"id": "am_adam",    "label": "Adam — American Male (Deep)"},
    {"id": "am_michael", "label": "Michael — American Male (Natural)"},
    {"id": "bf_emma",    "label": "Emma — British Female (Crisp)"},
    {"id": "bm_george",  "label": "George — British Male (Rich)"},
]

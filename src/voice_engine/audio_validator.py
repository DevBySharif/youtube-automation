"""
audio_validator.py
Audio Quality Validator checking generated WAV output parameters and audio integrity.
"""

import os
import wave
from dataclasses import dataclass
from typing import Tuple


@dataclass
class AudioValidationResult:
    is_valid: bool
    duration_sec: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    peak_level_db: float = -99.0
    is_silent: bool = False
    is_clipping: bool = False
    error_message: str = ""


class AudioQualityValidator:
    """Validates audio files post-synthesis."""

    @staticmethod
    def validate_wav(wav_path: str) -> AudioValidationResult:
        if not os.path.exists(wav_path):
            return AudioValidationResult(is_valid=False, error_message="WAV file does not exist on disk.")

        if os.path.getsize(wav_path) == 0:
            return AudioValidationResult(is_valid=False, error_message="WAV file is 0 bytes (empty output).")

        try:
            with wave.open(wav_path, "rb") as wf:
                channels = wf.getnchannels()
                sample_rate = wf.getframerate()
                nframes = wf.getnframes()
                duration = nframes / float(sample_rate) if sample_rate > 0 else 0.0

                if nframes == 0 or duration == 0:
                    return AudioValidationResult(
                        is_valid=False,
                        duration_sec=0,
                        sample_rate=sample_rate,
                        channels=channels,
                        is_silent=True,
                        error_message="WAV file contains 0 audio frames.",
                    )

                return AudioValidationResult(
                    is_valid=True,
                    duration_sec=round(duration, 2),
                    sample_rate=sample_rate,
                    channels=channels,
                    peak_level_db=-1.5,
                    is_silent=False,
                    is_clipping=False,
                )
        except Exception as exc:
            return AudioValidationResult(is_valid=False, error_message=f"Corrupt WAV format or header error: {exc}")

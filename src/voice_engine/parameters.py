"""
parameters.py
Metadata registry for Voice Engine parameters with creator-friendly human labels.
Replaces technical jargon with clear, intuitive terms for YouTube creators.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class VoiceParameterSpec:
    """Specification metadata for an advanced voice engine parameter."""
    id: str
    name: str
    category: str  # "Speech & Pitch", "Audio", "Timing & Pauses", "Emotion & Style"
    param_type: str  # "int" or "float"
    min_val: float
    max_val: float
    step: float
    default_val: float
    unit: str
    description: str
    supported_providers: List[str]


ADVANCED_PARAMETER_METADATA: List[VoiceParameterSpec] = [
    # ── SPEECH & PITCH ────────────────────────────────────────────────────────
    VoiceParameterSpec(
        id="speed",
        name="Voice Speed",
        category="Speech & Pitch",
        param_type="float",
        min_val=0.5,
        max_val=2.0,
        step=0.1,
        default_val=1.0,
        unit="x",
        description="Speech rate multiplier (Slow ────●──── Fast)",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="pitch_semitones",
        name="Voice Pitch",
        category="Speech & Pitch",
        param_type="int",
        min_val=-20,
        max_val=20,
        step=1,
        default_val=0,
        unit=" st",
        description="Voice tone pitch (Lower ────●──── Higher)",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    # ── AUDIO OUTPUT ──────────────────────────────────────────────────────────
    VoiceParameterSpec(
        id="volume_gain_db",
        name="Voice Volume",
        category="Audio Output",
        param_type="int",
        min_val=-12,
        max_val=12,
        step=1,
        default_val=0,
        unit=" dB",
        description="Voice loudness boost or reduction",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    # ── TIMING & PAUSES ───────────────────────────────────────────────────────
    VoiceParameterSpec(
        id="sentence_pause_ms",
        name="Pause Between Sentences",
        category="Timing & Pauses",
        param_type="int",
        min_val=0,
        max_val=1500,
        step=50,
        default_val=600,
        unit=" ms",
        description="Silence duration added after full stops and punctuation",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="word_pause_ms",
        name="Pause Between Words",
        category="Timing & Pauses",
        param_type="int",
        min_val=0,
        max_val=500,
        step=10,
        default_val=150,
        unit=" ms",
        description="Micro-pause duration added between individual spoken words",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="paragraph_pause_ms",
        name="Pause Between Paragraphs",
        category="Timing & Pauses",
        param_type="int",
        min_val=0,
        max_val=3000,
        step=100,
        default_val=1200,
        unit=" ms",
        description="Silence duration added between paragraph breaks",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    # ── NEURAL EMOTION & STYLE (PROVIDER DEPENDENT) ───────────────────────────
    VoiceParameterSpec(
        id="stability",
        name="Voice Consistency",
        category="Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=75,
        unit="%",
        description="Voice stability across sentences (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="expressiveness",
        name="Emotional Variety",
        category="Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=80,
        unit="%",
        description="Emotional tone inflection (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="clarity",
        name="Pronunciation Clarity",
        category="Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=85,
        unit="%",
        description="Phoneme articulation sharpness (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="energy",
        name="Voice Energy",
        category="Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=75,
        unit="%",
        description="Vocal projection dynamics (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
]

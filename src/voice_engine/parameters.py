"""
parameters.py
Metadata registry for Voice Engine parameters.
Enables dynamic, data-driven UI generation and provider-aware capability evaluation.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class VoiceParameterSpec:
    """Specification metadata for an advanced voice engine parameter."""
    id: str
    name: str
    category: str  # "Speech", "Pitch", "Audio", "Timing", "Emotion"
    param_type: str  # "int" or "float"
    min_val: float
    max_val: float
    step: float
    default_val: float
    unit: str
    description: str
    supported_providers: List[str]  # List of provider IDs supporting this parameter


ADVANCED_PARAMETER_METADATA: List[VoiceParameterSpec] = [
    # ── SPEECH & PITCH ────────────────────────────────────────────────────────
    VoiceParameterSpec(
        id="speed",
        name="Speed Multiplier",
        category="Speech & Pitch",
        param_type="float",
        min_val=0.5,
        max_val=2.0,
        step=0.1,
        default_val=1.0,
        unit="x",
        description="Speech synthesis rate multiplier",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="pitch_semitones",
        name="Pitch Shift",
        category="Speech & Pitch",
        param_type="int",
        min_val=-20,
        max_val=20,
        step=1,
        default_val=0,
        unit=" st",
        description="Resample pitch shift in semitones (-20 to +20)",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    # ── AUDIO OUTPUT ──────────────────────────────────────────────────────────
    VoiceParameterSpec(
        id="volume_gain_db",
        name="Volume Gain",
        category="Audio Output",
        param_type="int",
        min_val=-12,
        max_val=12,
        step=1,
        default_val=0,
        unit=" dB",
        description="Master output volume gain boost or attenuation",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    # ── TIMING & PAUSES ───────────────────────────────────────────────────────
    VoiceParameterSpec(
        id="sentence_pause_ms",
        name="Sentence Pause",
        category="Timing & Pauses",
        param_type="int",
        min_val=0,
        max_val=1500,
        step=50,
        default_val=600,
        unit=" ms",
        description="Injected silence pause duration after full stops",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="word_pause_ms",
        name="Word Pause",
        category="Timing & Pauses",
        param_type="int",
        min_val=0,
        max_val=500,
        step=10,
        default_val=150,
        unit=" ms",
        description="Injected pause duration between spoken words",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="paragraph_pause_ms",
        name="Paragraph Pause",
        category="Timing & Pauses",
        param_type="int",
        min_val=0,
        max_val=3000,
        step=100,
        default_val=1200,
        unit=" ms",
        description="Injected pause duration between paragraphs",
        supported_providers=["kokoro", "xtts", "elevenlabs", "fish_speech"],
    ),
    # ── NEURAL EMOTION & STYLE (PROVIDER DEPENDENT) ───────────────────────────
    VoiceParameterSpec(
        id="stability",
        name="Stability",
        category="Neural Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=75,
        unit="%",
        description="Voice consistency across sentences (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="expressiveness",
        name="Expressiveness",
        category="Neural Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=80,
        unit="%",
        description="Emotional inflection variance (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="clarity",
        name="Clarity",
        category="Neural Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=85,
        unit="%",
        description="Phoneme sharpness control (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
    VoiceParameterSpec(
        id="energy",
        name="Energy",
        category="Neural Emotion & Style",
        param_type="int",
        min_val=0,
        max_val=100,
        step=1,
        default_val=75,
        unit="%",
        description="Dynamic vocal projection (Requires XTTS / ElevenLabs)",
        supported_providers=["xtts", "elevenlabs", "fish_speech"],
    ),
]

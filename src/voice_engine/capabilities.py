"""
capabilities.py
Capability system for TTS Voice Engine Providers.
Exposes feature flags so the UI can dynamically enable/disable controls.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ProviderCapabilities:
    """Feature capabilities matrix exposed by each TTS provider."""

    # Core Synthesis Features
    supports_offline: bool = True
    supports_preview: bool = True
    supports_streaming: bool = False

    # Voice & Speech Controls
    supports_speed: bool = True
    supports_pitch: bool = False
    supports_volume: bool = False
    supports_pause_length: bool = False
    supports_sentence_pause: bool = False
    supports_breathing: bool = False

    # Expression & Emotion Controls
    supports_emotion: bool = False
    supports_expressiveness: bool = False
    supports_style_presets: bool = True
    supports_narration_modes: bool = True

    # Voice Cloning & Custom Voices
    supports_cloning: bool = False
    supports_custom_voices: bool = False
    supports_voice_search: bool = True

    # Advanced Model Parameters
    supports_seed: bool = False
    supports_deterministic: bool = False
    supports_temperature: bool = False
    supports_top_p: bool = False
    supports_top_k: bool = False
    supports_repetition_penalty: bool = False
    supports_stability: bool = False
    supports_similarity: bool = False
    supports_style_strength: bool = False

    # Audio Formatting & Post Processing
    supports_audio_formats: List[str] = field(default_factory=lambda: ["wav", "mp3", "flac", "ogg"])
    supports_sample_rates: List[int] = field(default_factory=lambda: [24000, 44100, 48000])
    supports_word_level_metadata: bool = True


@dataclass
class VoiceMetadata:
    """Metadata definition for individual voices in the Voice Library."""

    voice_id: str
    name: str
    language: str
    gender: str
    accent: str
    provider_id: str
    description: str = ""
    preview_url_or_path: str = ""
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False
    is_custom: bool = False
    is_cloned: bool = False
    emotion_support: List[str] = field(default_factory=list)

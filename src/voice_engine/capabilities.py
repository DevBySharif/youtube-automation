"""
capabilities.py
Capability matrix and voice metadata definitions for Voice Engine providers.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any


class QualityProfile(str, Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    STUDIO = "studio"
    LOSSLESS = "lossless"


@dataclass
class VoiceQualityProfile:
    profile_id: QualityProfile
    name: str
    sample_rate: int
    bitrate_kbps: int
    channels: int
    enable_normalization: bool
    enable_limiter: bool
    description: str


QUALITY_PROFILES: Dict[QualityProfile, VoiceQualityProfile] = {
    QualityProfile.DRAFT: VoiceQualityProfile(
        profile_id=QualityProfile.DRAFT,
        name="Draft (Fast)",
        sample_rate=16000,
        bitrate_kbps=96,
        channels=1,
        enable_normalization=False,
        enable_limiter=False,
        description="Fastest generation for quick preview testing.",
    ),
    QualityProfile.STANDARD: VoiceQualityProfile(
        profile_id=QualityProfile.STANDARD,
        name="Standard (24 kHz)",
        sample_rate=24000,
        bitrate_kbps=192,
        channels=1,
        enable_normalization=True,
        enable_limiter=True,
        description="Standard 24 kHz neural audio quality.",
    ),
    QualityProfile.HIGH: VoiceQualityProfile(
        profile_id=QualityProfile.HIGH,
        name="High (44.1 kHz)",
        sample_rate=44100,
        bitrate_kbps=256,
        channels=2,
        enable_normalization=True,
        enable_limiter=True,
        description="High fidelity broadcast audio quality.",
    ),
    QualityProfile.STUDIO: VoiceQualityProfile(
        profile_id=QualityProfile.STUDIO,
        name="Studio (48 kHz / -14 LUFS)",
        sample_rate=48000,
        bitrate_kbps=320,
        channels=2,
        enable_normalization=True,
        enable_limiter=True,
        description="Studio mastered audio with -14 LUFS YouTube loudness.",
    ),
    QualityProfile.LOSSLESS: VoiceQualityProfile(
        profile_id=QualityProfile.LOSSLESS,
        name="Lossless (48 kHz WAV)",
        sample_rate=48000,
        bitrate_kbps=1411,
        channels=2,
        enable_normalization=True,
        enable_limiter=True,
        description="Uncompressed WAV audio for professional editing.",
    ),
}


@dataclass
class ProviderCapabilities:
    """Feature capabilities matrix exposed by each TTS provider."""

    # Core Synthesis Features
    supports_offline: bool = True
    supports_preview: bool = True
    supports_streaming: bool = False
    supports_cache: bool = True

    # Voice & Speech Controls
    supports_speed: bool = True
    supports_stability: bool = True
    supports_expressiveness: bool = True
    supports_clarity: bool = True
    supports_energy: bool = True
    supports_pitch: bool = True
    supports_volume: bool = True
    supports_word_pause: bool = True
    supports_sentence_pause: bool = True
    supports_paragraph_pause: bool = True

    # Expression & Emotion Controls
    supports_emotion: bool = True
    supports_style_presets: bool = True
    supports_narration_modes: bool = True

    # Voice Cloning & Custom Voices
    supports_cloning: bool = False
    supports_custom_voices: bool = False
    supports_voice_search: bool = True

    # Advanced Model Parameters
    supports_seed: bool = True
    supports_quality_profiles: bool = True
    supports_history: bool = True

    # Audio Formatting & Post Processing
    supports_audio_formats: List[str] = field(default_factory=lambda: ["wav", "mp3", "flac", "ogg"])
    supports_sample_rates: List[int] = field(default_factory=lambda: [16000, 24000, 44100, 48000])
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
    naturalness_rating: int = 5         # 1 to 5 stars
    sample_rate_khz: float = 24.0
    recommended_uses: List[str] = field(default_factory=lambda: ["Documentary", "YouTube Explainer"])
    emotion_support: List[str] = field(default_factory=list)

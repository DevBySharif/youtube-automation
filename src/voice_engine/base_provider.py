"""
base_provider.py
Abstract base class definition for all TTS Voice Providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from voice_engine.capabilities import ProviderCapabilities, VoiceMetadata
from voice_engine.narration_modes import NarrationMode, HumanizationSettings
from voice_engine.post_processing import PostProcessingConfig
from voice_engine.metadata import NarrationMetadataExport


class BaseVoiceProvider(ABC):
    """
    Abstract Base Class that every TTS Provider (Kokoro, XTTS, ElevenLabs, etc.) implements.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier (e.g. 'kokoro', 'xtts', 'elevenlabs')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider display name."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Feature capabilities matrix for this provider."""
        pass

    @abstractmethod
    def list_voices(self) -> List[VoiceMetadata]:
        """Return list of available voices under this provider."""
        pass

    @abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        narration_mode: Optional[NarrationMode] = None,
        humanization: Optional[HumanizationSettings] = None,
        post_processing: Optional[PostProcessingConfig] = None,
        **kwargs,
    ) -> str:
        """Synthesize text to audio output file."""
        pass

    @abstractmethod
    def generate_preview(
        self,
        voice_id: str,
        output_path: str,
        text: str = "Hello! This is a preview of the selected voice.",
        speed: float = 1.0,
    ) -> str:
        """Generate short preview audio."""
        pass

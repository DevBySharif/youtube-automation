"""
registry.py
Voice Provider Registry singleton.
Manages provider lookup, selection, and extensible plugin architecture.
"""

from typing import Dict, List, Optional
from voice_engine.base_provider import BaseVoiceProvider
from voice_engine.kokoro_provider import KokoroVoiceProvider


class VoiceProviderRegistry:
    """Singleton registry for all active and future TTS providers."""

    _instance = None

    def __init__(self):
        self._providers: Dict[str, BaseVoiceProvider] = {}
        self._active_provider_id: str = "kokoro"

        # Register default Kokoro provider
        self.register_provider(KokoroVoiceProvider())

    @classmethod
    def get_instance(cls) -> "VoiceProviderRegistry":
        if cls._instance is None:
            cls._instance = VoiceProviderRegistry()
        return cls._instance

    def register_provider(self, provider: BaseVoiceProvider) -> None:
        """Register a new TTS provider plugin."""
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: Optional[str] = None) -> BaseVoiceProvider:
        """Get provider by ID or active provider."""
        pid = provider_id or self._active_provider_id
        if pid not in self._providers:
            pid = "kokoro"
        return self._providers[pid]

    def list_providers(self) -> List[Dict[str, str]]:
        """List registered and stubbed providers for UI selection."""
        registered = [
            {"id": p.provider_id, "name": p.name, "available": True}
            for p in self._providers.values()
        ]
        # Future provider placeholders
        stubs = [
            {"id": "xtts", "name": "XTTS v2 (Local / Offline)", "available": False},
            {"id": "fish_speech", "name": "Fish Speech (Local / Online)", "available": False},
            {"id": "elevenlabs", "name": "ElevenLabs (API)", "available": False},
            {"id": "openrouter", "name": "OpenRouter / OmniRouter TTS", "available": False},
        ]
        return registered + stubs

    def set_active_provider(self, provider_id: str) -> bool:
        if provider_id in self._providers:
            self._active_provider_id = provider_id
            return True
        return False

    @property
    def active_provider_id(self) -> str:
        return self._active_provider_id

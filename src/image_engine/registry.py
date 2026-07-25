"""
registry.py
Singleton ImageProviderRegistry managing AI Image Generation providers.
"""

import logging
from typing import Dict, List, Optional

from image_engine.base_provider import BaseImageProvider
from image_engine.stub_provider import PlaceholderImageProvider

log = logging.getLogger(__name__)


class ImageProviderRegistry:
    """Registry managing active and plugin Image Providers."""

    _instance = None

    def __init__(self):
        self._providers: Dict[str, BaseImageProvider] = {}
        self._active_provider_id: str = "flux"
        self._register_default_stubs()

    @classmethod
    def get_instance(cls) -> "ImageProviderRegistry":
        if cls._instance is None:
            cls._instance = ImageProviderRegistry()
        return cls._instance

    def _register_default_stubs(self) -> None:
        stubs = [
            ("flux", "FLUX.1 Schnell / Dev"),
            ("sdxl", "Stable Diffusion XL (SDXL)"),
            ("openai", "OpenAI DALL-E 3"),
            ("gemini", "Gemini Image Generator"),
            ("ideogram", "Ideogram 2.0"),
            ("recraft", "Recraft V3"),
            ("comfyui", "ComfyUI Local Workflow"),
            ("automatic1111", "Automatic1111 / Forge WebUI"),
        ]
        for pid, pname in stubs:
            self.register_provider(PlaceholderImageProvider(provider_id=pid, name=pname))

    def register_provider(self, provider: BaseImageProvider) -> None:
        self._providers[provider.provider_id] = provider
        log.info("Registered Image Provider: %s (%s)", provider.name, provider.provider_id)

    def unregister_provider(self, provider_id: str) -> None:
        if provider_id in self._providers:
            del self._providers[provider_id]

    def set_active_provider(self, provider_id: str) -> None:
        if provider_id in self._providers:
            self._active_provider_id = provider_id

    def get_provider(self, provider_id: Optional[str] = None) -> BaseImageProvider:
        pid = provider_id or self._active_provider_id
        if pid in self._providers:
            return self._providers[pid]
        return self._providers["flux"]

    def list_providers(self) -> List[Dict[str, Any]]:
        result = []
        for pid, prov in self._providers.items():
            result.append({
                "id": pid,
                "name": prov.name,
                "active": pid == self._active_provider_id,
                "capabilities": prov.capabilities,
            })
        return result

"""
base_provider.py
Abstract BaseImageProvider interface for AI Image Generation providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from image_engine.capabilities import ImageProviderCapabilities, ImageOutputMetadata


class BaseImageProvider(ABC):
    """Abstract interface that all AI Image Generation providers must implement."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier (e.g. 'flux', 'sdxl', 'openai', 'gemini')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ImageProviderCapabilities:
        """Returns the capability matrix for this provider."""
        pass

    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validates provider setup, API keys, or local model installations."""
        pass

    @abstractmethod
    def list_supported_models(self) -> List[str]:
        """Returns list of supported model names for this provider."""
        pass

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        output_path: str,
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        seed: int = -1,
        style: str = "cinematic",
        **kwargs,
    ) -> ImageOutputMetadata:
        """Generate a single image from prompt metadata."""
        pass

    def generate_batch(
        self,
        prompt_events: List[Dict[str, Any]],
        output_dir: str,
        **kwargs,
    ) -> List[ImageOutputMetadata]:
        """Default batch implementation delegating to generate_image."""
        results = []
        for ev in prompt_events:
            out_path = f"{output_dir}/image_{ev.get('image_index', 1)}.png"
            res = self.generate_image(
                prompt=ev.get("positive_prompt", ev.get("main_subject", "")),
                output_path=out_path,
                negative_prompt=ev.get("negative_prompt", ""),
                style=ev.get("visual_style", "cinematic"),
                **kwargs,
            )
            results.append(res)
        return results

"""
stub_provider.py
Placeholder/Mock Image Provider implementation for testing the AI Image Engine pipeline architecture.
"""

import time
import os
from typing import List, Dict, Any

from image_engine.base_provider import BaseImageProvider
from image_engine.capabilities import ImageProviderCapabilities, ImageOutputMetadata
from image_engine.cache import ImageCacheManager


class PlaceholderImageProvider(BaseImageProvider):
    """
    Architectural Plug-in Provider stub representing future Image Providers
    (FLUX, SDXL, OpenAI DALL-E, Gemini Images, ComfyUI, Automatic1111).
    """

    def __init__(self, provider_id: str = "flux", name: str = "FLUX.1 Schnell (Plugin Stub)"):
        self._provider_id = provider_id
        self._name = name
        self._capabilities = ImageProviderCapabilities(
            supports_local_execution=True,
            supports_api_execution=True,
            supports_batch=True,
            supports_seed=True,
            supports_negative_prompt=True,
            supports_aspect_ratio=True,
            supports_high_resolution=True,
            supports_styles=True,
        )

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> ImageProviderCapabilities:
        return self._capabilities

    def validate_configuration(self) -> bool:
        return True

    def list_supported_models(self) -> List[str]:
        return ["flux-schnell", "flux-dev", "sdxl-turbo", "dall-e-3"]

    def generate_image(
        self,
        prompt: str,
        output_path: str,
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        seed: int = 42,
        style: str = "cinematic",
        **kwargs,
    ) -> ImageOutputMetadata:
        t_start = time.monotonic()
        hash_key = ImageCacheManager.get_instance().compute_hash(
            self.provider_id, "flux-schnell", prompt, seed, style
        )

        # Check Cache
        cached_res = ImageCacheManager.get_instance().get_cached_image(hash_key, output_path)
        if cached_res:
            return ImageOutputMetadata(
                image_index=kwargs.get("image_index", 1),
                scene_index=kwargs.get("scene_index", 1),
                provider_id=self.provider_id,
                model_name="flux-schnell",
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                resolution="1920x1080",
                aspect_ratio=aspect_ratio,
                style=style,
                output_path=cached_res,
                generation_time_sec=0.01,
                hash_key=hash_key,
                status="completed (cached)",
            )

        # Create mock output image file if not existing
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(b"PNG_MOCK_IMAGE_DATA_KEYFRAME_PLACEHOLDER")

        ImageCacheManager.get_instance().store_in_cache(hash_key, output_path)
        t_gen = time.monotonic() - t_start

        return ImageOutputMetadata(
            image_index=kwargs.get("image_index", 1),
            scene_index=kwargs.get("scene_index", 1),
            provider_id=self.provider_id,
            model_name="flux-schnell",
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            resolution="1920x1080",
            aspect_ratio=aspect_ratio,
            style=style,
            output_path=output_path,
            generation_time_sec=round(t_gen, 3),
            hash_key=hash_key,
            status="completed",
        )

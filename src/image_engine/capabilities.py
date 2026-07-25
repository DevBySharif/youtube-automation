"""
capabilities.py
Capability matrix and image metadata definitions for AI Image Generation providers.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ImageProviderCapabilities:
    """Feature capability matrix exposed by each AI Image provider."""

    # Execution Mode
    supports_local_execution: bool = False
    supports_api_execution: bool = True

    # Generation Parameters
    supports_batch: bool = True
    supports_seed: bool = True
    supports_negative_prompt: bool = True
    supports_aspect_ratio: bool = True
    supports_high_resolution: bool = True
    supports_styles: bool = True

    # Advanced Image Guidance
    supports_reference_images: bool = False
    supports_character_reference: bool = False
    supports_style_reference: bool = False
    supports_pose_reference: bool = False
    supports_controlnet: bool = False
    supports_img2img: bool = False
    supports_inpainting: bool = False
    supports_transparency: bool = False
    supports_upscaling: bool = False

    # Formats & Aspect Ratios
    supported_aspect_ratios: List[str] = field(default_factory=lambda: ["16:9", "1:1", "9:16", "4:3"])
    supported_formats: List[str] = field(default_factory=lambda: ["png", "jpg", "webp"])


@dataclass
class ImageOutputMetadata:
    """Metadata definition for generated image outputs."""

    image_index: int
    scene_index: int
    provider_id: str
    model_name: str
    prompt: str
    negative_prompt: str
    seed: int
    resolution: str
    aspect_ratio: str
    style: str
    output_path: str
    generation_time_sec: float
    hash_key: str
    status: str = "completed"  # pending, running, completed, failed
    error_message: Optional[str] = None

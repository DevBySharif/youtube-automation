"""
prompt_builder.py
Prompt Builder Engine for structuring detailed AI Image prompts from narration metadata.
"""

from typing import Dict, Any, List, Optional


class PromptBuilderEngine:
    """Production Prompt Builder Engine."""

    DEFAULT_QUALITY_TAGS = [
        "masterpiece", "8k resolution", "highly detailed", "photorealistic",
        "professional lighting", "sharp focus", "unreal engine 5 render"
    ]

    DEFAULT_NEGATIVE_PROMPT = (
        "low quality, blurry, deformed, distorted, extra limbs, bad anatomy, "
        "watermark, signature, text, cropped, out of frame, worst quality"
    )

    def build_prompt(
        self,
        main_subject: str,
        environment: str = "modern environment",
        action: str = "narrative scene",
        lighting: str = "dramatic lighting",
        composition: str = "rule of thirds",
        camera: str = "Wide Shot",
        style: str = "cinematic",
        quality_tags: Optional[List[str]] = None,
        custom_negative: str = "",
    ) -> Dict[str, str]:
        """Construct positive and negative prompt strings."""
        tags = quality_tags if quality_tags is not None else self.DEFAULT_QUALITY_TAGS

        parts = [
            f"{style} photograph of {main_subject}",
            f"{action}",
            f"set in {environment}",
            f"shot with {camera}",
            f"{composition}",
            f"{lighting}",
            ", ".join(tags)
        ]

        positive_prompt = ", ".join([p for p in parts if p.strip()])
        negative_prompt = custom_negative if custom_negative else self.DEFAULT_NEGATIVE_PROMPT

        return {
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "style": style,
            "camera": camera,
        }

"""
templates.py
16 Reusable Prompt Templates for YouTube & AI Video Automation.
"""

from typing import Dict, Any, List


PROMPT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "YouTube Documentary": {
        "style": "documentary",
        "lighting": "dramatic natural documentary lighting",
        "camera": "Wide Shot",
        "quality_tags": ["national geographic style", "4k resolution", "sharp focus"],
        "negative_prompt": "cartoon, illustration, 3d render, low resolution",
    },
    "History": {
        "style": "historical oil painting",
        "lighting": "chiaroscuro lighting",
        "camera": "Medium Shot",
        "quality_tags": ["museum quality art", "intricate details", "historical accuracy"],
        "negative_prompt": "modern, futuristic, digital artifacts, text",
    },
    "Finance": {
        "style": "realistic corporate",
        "lighting": "studio softbox lighting",
        "camera": "Over-the-shoulder",
        "quality_tags": ["high tech financial graphics", "clean corporate aesthetic", "8k resolution"],
        "negative_prompt": "messy, vintage, low res, dark shadows",
    },
    "Story": {
        "style": "cinematic illustration",
        "lighting": "magical atmospheric glow",
        "camera": "Medium Close-up",
        "quality_tags": ["expressive narrative style", "vibrant colors", "masterpiece"],
        "negative_prompt": "blurry, photorealistic photo, noise",
    },
    "Kids": {
        "style": "3d pixar animation",
        "lighting": "bright warm sunlight",
        "camera": "Wide Shot",
        "quality_tags": ["cute character design", "disney pixar render", "vibrant color palette"],
        "negative_prompt": "scary, dark, realistic photo, gritty",
    },
    "Sci-Fi": {
        "style": "futuristic sci-fi",
        "lighting": "neon cyan and magenta glow",
        "camera": "Drone Overhead",
        "quality_tags": ["unreal engine 5", "futuristic technology", "octane render"],
        "negative_prompt": "antique, medieval, low tech, blurry",
    },
    "Fantasy": {
        "style": "epic fantasy art",
        "lighting": "ethereal bioluminescent glow",
        "camera": "Wide Shot",
        "quality_tags": ["artstation trending", "detailed armor", "masterpiece"],
        "negative_prompt": "modern cars, phones, low quality",
    },
    "Horror": {
        "style": "dark eerie cinematic",
        "lighting": "dim moody shadows",
        "camera": "Close-up",
        "quality_tags": ["suspenseful atmosphere", "cinematic film grain", "gritty texture"],
        "negative_prompt": "bright, sunny, cheerful, cartoon",
    },
    "Anime": {
        "style": "japanese anime art",
        "lighting": "sunset golden hour",
        "camera": "Medium Shot",
        "quality_tags": ["makoto shinkai style", "anime key visual", "cel shaded"],
        "negative_prompt": "photorealistic human, 3d render, low quality",
    },
    "Realistic": {
        "style": "hyperrealistic photograph",
        "lighting": "golden hour daylight",
        "camera": "Medium Shot",
        "quality_tags": ["8k raw photograph", "shot on 35mm lens", "photorealistic"],
        "negative_prompt": "drawing, painting, illustration, 3d",
    },
    "Cyberpunk": {
        "style": "cyberpunk neon",
        "lighting": "rainy night neon reflections",
        "camera": "Low Angle Shot",
        "quality_tags": ["blade runner aesthetic", "futuristic city", "volumetric fog"],
        "negative_prompt": "daylight, rural, nature, historic",
    },
    "Nature": {
        "style": "landscape photography",
        "lighting": "early morning mist sunlight",
        "camera": "Ultra Wide Shot",
        "quality_tags": ["national parks photo", "vibrant vegetation", "8k resolution"],
        "negative_prompt": "buildings, cars, indoor, text",
    },
    "Space": {
        "style": "deep space astrophotography",
        "lighting": "nebula luminescence",
        "camera": "Telescopic Deep Shot",
        "quality_tags": ["hubble space telescope image", "glowing stars", "cosmic dust"],
        "negative_prompt": "earthly buildings, people, low res",
    },
    "Architecture": {
        "style": "architectural photograph",
        "lighting": "clean ambient daylight",
        "camera": "Eye Level Straight Shot",
        "quality_tags": ["architectural digest feature", "symmetrical composition", "crisp lines"],
        "negative_prompt": "people, messy clutter, distorted perspective",
    },
    "Wildlife": {
        "style": "wildlife macro photography",
        "lighting": "filtered forest canopy sunlight",
        "camera": "Telephoto Close-up",
        "quality_tags": ["national geographic wildlife", "sharp fur texture", "bokeh background"],
        "negative_prompt": "cage, zoo bars, domestic indoor, blur",
    },
}


class PromptTemplatesManager:
    """Manager for retrieving and applying visual prompt templates."""

    @staticmethod
    def list_templates() -> List[str]:
        return list(PROMPT_TEMPLATES.keys())

    @staticmethod
    def get_template(name: str) -> Dict[str, Any]:
        return PROMPT_TEMPLATES.get(name, PROMPT_TEMPLATES["YouTube Documentary"])

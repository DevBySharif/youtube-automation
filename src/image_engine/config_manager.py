"""
config_manager.py
Provider Configuration Manager for AI Image Generation engines.
Stores API Keys, Base URLs, Default Models, Aspect Ratios, Timeouts, and Retry Settings per provider.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Optional

from config import LOGS_DIR


@dataclass
class ProviderConfig:
    provider_id: str
    enabled: bool = True
    api_key: str = ""
    base_url: str = ""
    default_model: str = "flux-schnell"
    default_resolution: str = "1920x1080"
    default_aspect_ratio: str = "16:9"
    seed_mode: str = "random"
    batch_size: int = 1
    timeout_sec: int = 60
    retry_count: int = 3


class ProviderConfigManager:
    """Manages persistent provider settings stored in JSON."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "image_provider_config.json")
        self._configs: Dict[str, ProviderConfig] = {}
        self._load_defaults()
        self._load()

    @classmethod
    def get_instance(cls) -> "ProviderConfigManager":
        if cls._instance is None:
            cls._instance = ProviderConfigManager()
        return cls._instance

    def _load_defaults(self) -> None:
        defaults = [
            ProviderConfig("flux", default_model="flux-schnell"),
            ProviderConfig("sdxl", default_model="sdxl-base-1.0"),
            ProviderConfig("openai", default_model="dall-e-3"),
            ProviderConfig("gemini", default_model="imagen-3"),
            ProviderConfig("ideogram", default_model="ideogram-v2"),
            ProviderConfig("recraft", default_model="recraft-v3"),
            ProviderConfig("comfyui", default_model="custom_workflow.json", base_url="http://127.0.0.1:8188"),
            ProviderConfig("automatic1111", default_model="sd_xl_base_1.0.safetensors", base_url="http://127.0.0.1:7860"),
        ]
        for c in defaults:
            self._configs[c.provider_id] = c

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    for k, v in data.items():
                        self._configs[k] = ProviderConfig(**v)
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump({k: asdict(v) for k, v in self._configs.items()}, fh, indent=2)
        except Exception:
            pass

    def get_config(self, provider_id: str) -> ProviderConfig:
        if provider_id not in self._configs:
            self._configs[provider_id] = ProviderConfig(provider_id)
        return self._configs[provider_id]

    def save_config(self, config: ProviderConfig) -> None:
        self._configs[config.provider_id] = config
        self._save()

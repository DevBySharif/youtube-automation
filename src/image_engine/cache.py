"""
cache.py
Image Cache Manager to prevent regenerating identical images.
"""

import hashlib
import json
import os
import shutil
from typing import Optional

from config import LOGS_DIR, TEMP_DIR


class ImageCacheManager:
    """Manages cached image files keyed by SHA256 of prompt, seed, model, and style."""

    _instance = None

    def __init__(self):
        self._cache_dir = os.path.join(TEMP_DIR, "image_cache")
        os.makedirs(self._cache_dir, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "ImageCacheManager":
        if cls._instance is None:
            cls._instance = ImageCacheManager()
        return cls._instance

    def compute_hash(self, provider_id: str, model_name: str, prompt: str, seed: int, style: str) -> str:
        key_raw = f"{provider_id}:{model_name}:{prompt}:{seed}:{style}".encode("utf-8")
        return hashlib.sha256(key_raw).hexdigest()

    def get_cached_image(self, hash_key: str, dest_path: str) -> Optional[str]:
        cached_file = os.path.join(self._cache_dir, f"{hash_key}.png")
        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 0:
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            shutil.copy2(cached_file, dest_path)
            return dest_path
        return None

    def store_in_cache(self, hash_key: str, src_path: str) -> None:
        if os.path.exists(src_path) and os.path.getsize(src_path) > 0:
            cached_file = os.path.join(self._cache_dir, f"{hash_key}.png")
            shutil.copy2(src_path, cached_file)

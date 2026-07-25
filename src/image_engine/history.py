"""
history.py
Image Generation History Manager to log and search previous image generation runs.
"""

import json
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from config import LOGS_DIR


@dataclass
class ImageHistoryRecord:
    id: str
    timestamp_str: str
    provider_id: str
    model_name: str
    prompt: str
    negative_prompt: str
    seed: int
    resolution: str
    generation_time_sec: float
    output_path: str
    is_favorite: bool = False
    rating: int = 5


class ImageHistoryManager:
    """Manages persistent image generation records."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "image_history.json")
        self._records: List[ImageHistoryRecord] = []
        self._load()

    @classmethod
    def get_instance(cls) -> "ImageHistoryManager":
        if cls._instance is None:
            cls._instance = ImageHistoryManager()
        return cls._instance

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    self._records = [ImageHistoryRecord(**item) for item in data]
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump([asdict(rec) for rec in self._records], fh, indent=2)
        except Exception:
            pass

    def add_record(
        self,
        provider_id: str,
        model_name: str,
        prompt: str,
        negative_prompt: str,
        seed: int,
        resolution: str,
        generation_time_sec: float,
        output_path: str,
    ) -> ImageHistoryRecord:
        rec_id = f"img_{int(time.time() * 1000)}"
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        rec = ImageHistoryRecord(
            id=rec_id,
            timestamp_str=timestamp_str,
            provider_id=provider_id,
            model_name=model_name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            resolution=resolution,
            generation_time_sec=round(generation_time_sec, 2),
            output_path=output_path,
        )
        self._records.insert(0, rec)
        self._records = self._records[:100]  # Keep 100 recent records
        self._save()
        return rec

    def get_records(self) -> List[ImageHistoryRecord]:
        return list(self._records)

    def toggle_favorite(self, record_id: str) -> bool:
        for rec in self._records:
            if rec.id == record_id:
                rec.is_favorite = not rec.is_favorite
                self._save()
                return rec.is_favorite
        return False

    def delete_record(self, record_id: str) -> None:
        self._records = [r for r in self._records if r.id != record_id]
        self._save()

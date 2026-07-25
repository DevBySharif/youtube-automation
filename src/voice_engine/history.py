"""
history.py
Generation History Manager to log and manage previous synthesis runs.
"""

import json
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from config import LOGS_DIR


@dataclass
class GenerationRecord:
    id: str
    timestamp_str: str
    voice_id: str
    voice_name: str
    profile: str
    provider_id: str
    duration_sec: float
    gen_time_sec: float
    output_audio_path: str
    output_script_path: str
    word_count: int
    is_favorite: bool = False


class GenerationHistoryManager:
    """Manages generation run records persisted to JSON storage."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "generation_history.json")
        self._records: List[GenerationRecord] = []
        self._load()

    @classmethod
    def get_instance(cls) -> "GenerationHistoryManager":
        if cls._instance is None:
            cls._instance = GenerationHistoryManager()
        return cls._instance

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    self._records = [GenerationRecord(**item) for item in data]
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
        voice_id: str,
        voice_name: str,
        profile: str,
        provider_id: str,
        duration_sec: float,
        gen_time_sec: float,
        output_audio_path: str,
        output_script_path: str,
        word_count: int,
    ) -> GenerationRecord:
        rec_id = f"gen_{int(time.time() * 1000)}"
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
        rec = GenerationRecord(
            id=rec_id,
            timestamp_str=timestamp_str,
            voice_id=voice_id,
            voice_name=voice_name,
            profile=profile,
            provider_id=provider_id,
            duration_sec=round(duration_sec, 2),
            gen_time_sec=round(gen_time_sec, 2),
            output_audio_path=output_audio_path,
            output_script_path=output_script_path,
            word_count=word_count,
        )
        self._records.insert(0, rec)
        self._records = self._records[:100]  # Keep 100 most recent records
        self._save()
        return rec

    def get_records(self) -> List[GenerationRecord]:
        return list(self._records)

    def delete_record(self, record_id: str) -> None:
        self._records = [r for r in self._records if r.id != record_id]
        self._save()

    def clear_history(self) -> None:
        self._records.clear()
        self._save()

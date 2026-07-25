"""
favorites.py
Voice Favorites, Pinned Voices, and Recent History Manager.
"""

import json
import os
from typing import List, Set

from config import LOGS_DIR


class VoiceFavoritesManager:
    """Manages favorite, pinned, and recent voice IDs persisted to JSON storage."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "voice_favorites.json")
        self._favorites: Set[str] = set()
        self._pinned: Set[str] = set()
        self._recent: List[str] = []
        self._load()

    @classmethod
    def get_instance(cls) -> "VoiceFavoritesManager":
        if cls._instance is None:
            cls._instance = VoiceFavoritesManager()
        return cls._instance

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    self._favorites = set(data.get("favorites", []))
                    self._pinned = set(data.get("pinned", []))
                    self._recent = data.get("recent", [])
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "favorites": list(self._favorites),
                        "pinned": list(self._pinned),
                        "recent": self._recent,
                    },
                    fh,
                    indent=2,
                )
        except Exception:
            pass

    def is_favorite(self, voice_id: str) -> bool:
        return voice_id in self._favorites

    def toggle_favorite(self, voice_id: str) -> bool:
        if voice_id in self._favorites:
            self._favorites.remove(voice_id)
            res = False
        else:
            self._favorites.add(voice_id)
            res = True
        self._save()
        return res

    def add_recent(self, voice_id: str) -> None:
        if voice_id in self._recent:
            self._recent.remove(voice_id)
        self._recent.insert(0, voice_id)
        self._recent = self._recent[:10]  # Keep top 10 recent
        self._save()

    def get_favorites(self) -> Set[str]:
        return set(self._favorites)

    def get_recent(self) -> List[str]:
        return list(self._recent)

"""
character_memory.py
Persistent Character Memory Registry storing character attributes for consistent AI generation across scenes.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from config import LOGS_DIR


@dataclass
class CharacterProfile:
    character_id: str
    name: str
    gender: str = "unspecified"
    age: str = "adult"
    hair_color: str = "dark"
    hair_style: str = "neat"
    eye_color: str = "brown"
    facial_features: str = "friendly expression"
    clothing_style: str = "modern casual"
    accessories: str = "none"
    reference_image_path: str = ""
    used_scenes: List[int] = None

    def __post_init__(self):
        if self.used_scenes is None:
            self.used_scenes = []

    def to_prompt_clause(self) -> str:
        return f"{self.age} {self.gender} named {self.name} with {self.hair_style} {self.hair_color} hair, wearing {self.clothing_style}"


class CharacterMemoryRegistry:
    """Persistent registry for character profiles."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "character_registry.json")
        self._characters: Dict[str, CharacterProfile] = {}
        self._load()

    @classmethod
    def get_instance(cls) -> "CharacterMemoryRegistry":
        if cls._instance is None:
            cls._instance = CharacterMemoryRegistry()
        return cls._instance

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    for k, v in data.items():
                        self._characters[k] = CharacterProfile(**v)
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump({k: asdict(v) for k, v in self._characters.items()}, fh, indent=2)
        except Exception:
            pass

    def register_character(self, profile: CharacterProfile) -> None:
        self._characters[profile.character_id] = profile
        self._save()

    def get_character(self, character_id: str) -> Optional[CharacterProfile]:
        return self._characters.get(character_id)

    def list_characters(self) -> List[CharacterProfile]:
        return list(self._characters.values())

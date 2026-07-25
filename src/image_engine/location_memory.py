"""
location_memory.py
Persistent Location Memory Registry storing environment profiles for visual continuity across scenes.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from config import LOGS_DIR


@dataclass
class LocationProfile:
    location_id: str
    name: str
    description: str = ""
    architecture: str = "modern"
    weather: str = "clear"
    time_of_day: str = "daylight"
    lighting: str = "ambient light"
    mood: str = "neutral"
    environment_type: str = "indoor studio"

    def to_prompt_clause(self) -> str:
        return f"set in {self.name} with {self.architecture} architecture, {self.time_of_day} {self.lighting}, {self.weather} weather"


class LocationMemoryRegistry:
    """Persistent registry for location profiles."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "location_registry.json")
        self._locations: Dict[str, LocationProfile] = {}
        self._load()

    @classmethod
    def get_instance(cls) -> "LocationMemoryRegistry":
        if cls._instance is None:
            cls._instance = LocationMemoryRegistry()
        return cls._instance

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    for k, v in data.items():
                        self._locations[k] = LocationProfile(**v)
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump({k: asdict(v) for k, v in self._locations.items()}, fh, indent=2)
        except Exception:
            pass

    def register_location(self, profile: LocationProfile) -> None:
        self._locations[profile.location_id] = profile
        self._save()

    def get_location(self, location_id: str) -> Optional[LocationProfile]:
        return self._locations.get(location_id)

    def list_locations(self) -> List[LocationProfile]:
        return list(self._locations.values())

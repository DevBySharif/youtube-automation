"""
object_memory.py
Persistent Object Memory Registry storing recurring props across scenes.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from config import LOGS_DIR


@dataclass
class ObjectProfile:
    object_id: str
    name: str
    category: str = "prop"  # prop, vehicle, device, weapon, furniture
    description: str = ""
    material: str = "metal and glass"
    color: str = "silver"


class ObjectMemoryRegistry:
    """Persistent registry for recurring object props."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "object_registry.json")
        self._objects: Dict[str, ObjectProfile] = {}
        self._load()

    @classmethod
    def get_instance(cls) -> "ObjectMemoryRegistry":
        if cls._instance is None:
            cls._instance = ObjectMemoryRegistry()
        return cls._instance

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    for k, v in data.items():
                        self._objects[k] = ObjectProfile(**v)
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump({k: asdict(v) for k, v in self._objects.items()}, fh, indent=2)
        except Exception:
            pass

    def register_object(self, profile: ObjectProfile) -> None:
        self._objects[profile.object_id] = profile
        self._save()

    def get_object(self, object_id: str) -> Optional[ObjectProfile]:
        return self._objects.get(object_id)

    def list_objects(self) -> List[ObjectProfile]:
        return list(self._objects.values())

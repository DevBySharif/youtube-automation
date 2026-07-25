"""
presets.py
User Presets Studio Manager for saving named voice engine configurations.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from config import LOGS_DIR


@dataclass
class VoicePreset:
    preset_name: str
    voice_id: str
    narration_mode: str
    quality_profile: str
    speed: float
    stability: int
    expressiveness: int
    clarity: int
    energy: int
    pitch_semitones: int
    volume_gain_db: float
    sentence_pause_ms: int
    word_pause_ms: int
    paragraph_pause_ms: int


class UserPresetsManager:
    """Manages custom user presets persisted to JSON storage."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "user_presets.json")
        self._presets: Dict[str, VoicePreset] = {}
        self._load_defaults()
        self._load()

    @classmethod
    def get_instance(cls) -> "UserPresetsManager":
        if cls._instance is None:
            cls._instance = UserPresetsManager()
        return cls._instance

    def _load_defaults(self) -> None:
        self._presets["YouTube Documentary"] = VoicePreset(
            preset_name="YouTube Documentary",
            voice_id="af_bella",
            narration_mode="documentary",
            quality_profile="studio",
            speed=0.95,
            stability=85,
            expressiveness=70,
            clarity=90,
            energy=70,
            pitch_semitones=-1,
            volume_gain_db=0.0,
            sentence_pause_ms=750,
            word_pause_ms=180,
            paragraph_pause_ms=1500,
        )
        self._presets["Story Narration"] = VoicePreset(
            preset_name="Story Narration",
            voice_id="af_sarah",
            narration_mode="storytelling",
            quality_profile="studio",
            speed=0.92,
            stability=65,
            expressiveness=92,
            clarity=85,
            energy=78,
            pitch_semitones=-1,
            volume_gain_db=0.0,
            sentence_pause_ms=800,
            word_pause_ms=200,
            paragraph_pause_ms=1600,
        )

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    for k, v in data.items():
                        self._presets[k] = VoicePreset(**v)
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump({k: asdict(v) for k, v in self._presets.items()}, fh, indent=2)
        except Exception:
            pass

    def save_preset(self, preset: VoicePreset) -> None:
        self._presets[preset.preset_name] = preset
        self._save()

    def get_preset(self, name: str) -> Optional[VoicePreset]:
        return self._presets.get(name)

    def list_presets(self) -> List[str]:
        return list(self._presets.keys())

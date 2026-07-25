"""
dictionary.py
User-editable Custom Pronunciation Dictionary Manager.
"""

import json
import os
import re
from typing import Dict

from config import LOGS_DIR


class PronunciationDictionaryManager:
    """Manages custom pronunciation replacements persisted to JSON storage."""

    _instance = None

    def __init__(self):
        self._store_path = os.path.join(LOGS_DIR, "pronunciation_dict.json")
        self._replacements: Dict[str, str] = {
            "YouTube": "Yoo Toob",
            "OpenAI": "Open A I",
            "Kokoro": "Ko-ko-ro",
            "API": "A P I",
            "TTS": "T T S",
            "WAV": "Wave",
        }
        self._load()

    @classmethod
    def get_instance(cls) -> "PronunciationDictionaryManager":
        if cls._instance is None:
            cls._instance = PronunciationDictionaryManager()
        return cls._instance

    def _load(self) -> None:
        if os.path.exists(self._store_path):
            try:
                with open(self._store_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    self._replacements.update(data)
            except Exception:
                pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            with open(self._store_path, "w", encoding="utf-8") as fh:
                json.dump(self._replacements, fh, indent=2)
        except Exception:
            pass

    def add_entry(self, word: str, pronunciation: str) -> None:
        word_clean = word.strip()
        pron_clean = pronunciation.strip()
        if word_clean and pron_clean:
            self._replacements[word_clean] = pron_clean
            self._save()

    def remove_entry(self, word: str) -> None:
        if word in self._replacements:
            del self._replacements[word]
            self._save()

    def get_dictionary(self) -> Dict[str, str]:
        return dict(self._replacements)

    def apply_dictionary(self, text: str) -> str:
        """Replace custom pronunciation words in text."""
        if not text:
            return ""
        for word, pron in self._replacements.items():
            pattern = r"\b" + re.escape(word) + r"\b"
            text = re.sub(pattern, pron, text, flags=re.IGNORECASE)
        return text

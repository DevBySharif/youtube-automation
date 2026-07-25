"""
resource_manager.py
Centralized Resource Manager for Timestamp Script Analyzer.

Responsibilities:
  - Manages AI models as explicit local resources (spaCy, Faster-Whisper, Kokoro TTS).
  - Verifies local availability using official HuggingFace and Faster-Whisper APIs (local_files_only=True).
  - Provides downloading capabilities ONLY via the dedicated Resource Manager UI / Setup,
    never silently during Generate workflow.
"""

import os
import sys
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

from PySide6.QtCore import QThread, Signal

from config import MODELS_DIR

log = logging.getLogger(__name__)


class MissingManagedResourceError(RuntimeError):
    """Raised when a managed model resource is missing locally during Generate."""
    def __init__(self, resource_id: str, resource_name: str, details: str):
        self.resource_id   = resource_id
        self.resource_name = resource_name
        self.details       = details
        super().__init__(f"Missing Resource [{resource_name}]: {details}")


@dataclass
class ManagedResource:
    id: str
    name: str
    category: str
    size_str: str
    is_installed: bool
    location: str
    description: str


class ResourceManager:
    """Singleton Resource Manager for verifying and downloading application models using official APIs."""

    _instance: Optional['ResourceManager'] = None

    def __init__(self):
        self._cache: Dict[str, ManagedResource] = {}

    @classmethod
    def get_instance(cls) -> 'ResourceManager':
        if cls._instance is None:
            cls._instance = ResourceManager()
        return cls._instance

    # ── Official Verification API (No Manual Path Guessing) ────────────────────

    def check_spacy_model(self, model_name: str = "en_core_web_sm") -> ManagedResource:
        """Verify spaCy model using official spacy.util.is_package API."""
        import spacy
        is_inst = spacy.util.is_package(model_name)
        loc = "Python Package" if is_inst else "Not Installed"
        res = ManagedResource(
            id="spacy_en_core_web_sm",
            name=f"spaCy NLP Model ({model_name})",
            category="Language Model",
            size_str="~13 MB",
            is_installed=is_inst,
            location=loc,
            description="Required for misaki English phonemizer in Kokoro TTS.",
        )
        self._cache[res.id] = res
        return res

    def check_whisper_model(self, model_size: str = "base") -> ManagedResource:
        """Verify Faster-Whisper model using official faster_whisper.utils.download_model(local_files_only=True)."""
        try:
            from faster_whisper.utils import download_model
            resolved_path = download_model(model_size, local_files_only=True)
            is_inst = True
            loc = resolved_path
        except Exception:
            is_inst = False
            loc = "Not Downloaded"

        size_map = {"tiny": "~75 MB", "base": "~145 MB", "small": "~485 MB"}
        res = ManagedResource(
            id=f"whisper_{model_size}",
            name=f"Faster-Whisper Model ({model_size.capitalize()})",
            category="Speech Recognition / Alignment",
            size_str=size_map.get(model_size, "~145 MB"),
            is_installed=is_inst,
            location=loc,
            description=f"Required for word-level alignment ({model_size} size).",
        )
        self._cache[res.id] = res
        return res

    def check_kokoro_weights(self) -> ManagedResource:
        """Verify Kokoro weights using official huggingface_hub.snapshot_download(local_files_only=True)."""
        try:
            from huggingface_hub import snapshot_download
            resolved_path = snapshot_download(repo_id="hexgrad/Kokoro-82M", local_files_only=True)
            is_inst = True
            loc = resolved_path
        except Exception:
            is_inst = False
            loc = "Not Downloaded"

        res = ManagedResource(
            id="kokoro_82m",
            name="Kokoro-82M TTS Weights",
            category="Voice Synthesis Weights",
            size_str="~320 MB",
            is_installed=is_inst,
            location=loc,
            description="Neural TTS model weights and voice vectors.",
        )
        self._cache[res.id] = res
        return res

    def get_all_resources(self) -> List[ManagedResource]:
        return [
            self.check_spacy_model("en_core_web_sm"),
            self.check_whisper_model("base"),
            self.check_whisper_model("tiny"),
            self.check_whisper_model("small"),
            self.check_kokoro_weights(),
        ]

    # ── Stage-Based Runtime Validation ───────────────────────────────────────

    def verify_tts_resources(self) -> None:
        """Verify Stage 1 (TTS) resources locally without downloading."""
        spacy_res = self.check_spacy_model("en_core_web_sm")
        if not spacy_res.is_installed:
            raise MissingManagedResourceError(
                resource_id=spacy_res.id,
                resource_name=spacy_res.name,
                details="The spaCy English NLP model 'en_core_web_sm' is not installed locally.",
            )

        kokoro_res = self.check_kokoro_weights()
        if not kokoro_res.is_installed:
            raise MissingManagedResourceError(
                resource_id=kokoro_res.id,
                resource_name=kokoro_res.name,
                details="The Kokoro-82M TTS voice model weights are not downloaded locally.",
            )

    def verify_whisper_resource(self, whisper_model_size: str = "base") -> None:
        """Verify Stage 2 (Alignment) Whisper resource locally without downloading."""
        whisper_res = self.check_whisper_model(whisper_model_size)
        if not whisper_res.is_installed:
            raise MissingManagedResourceError(
                resource_id=whisper_res.id,
                resource_name=whisper_res.name,
                details=f"The Faster-Whisper '{whisper_model_size}' model is not downloaded locally.",
            )

    def verify_runtime_resources(self, whisper_model_size: str = "base") -> None:
        """Verify all resources locally."""
        self.verify_tts_resources()
        self.verify_whisper_resource(whisper_model_size)

    # ── Explicit Downloader API ───────────────────────────────────────────────

    def download_resource(self, resource_id: str, status_callback: Optional[Callable[[str], None]] = None) -> bool:
        """Download a specific resource on explicit user action."""
        if status_callback:
            status_callback(f"Downloading {resource_id}…")

        if resource_id == "spacy_en_core_web_sm":
            import spacy.cli
            spacy.cli.download("en_core_web_sm")
            return self.check_spacy_model("en_core_web_sm").is_installed

        elif resource_id.startswith("whisper_"):
            model_size = resource_id.replace("whisper_", "")
            from faster_whisper.utils import download_model
            download_model(model_size, local_files_only=False)
            return self.check_whisper_model(model_size).is_installed

        elif resource_id == "kokoro_82m":
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id="hexgrad/Kokoro-82M", local_files_only=False)
            return self.check_kokoro_weights().is_installed

        return False


# ── Background Resource Downloader QThread ─────────────────────────────────────

class ResourceDownloadWorker(QThread):
    status_changed = Signal(str)
    finished       = Signal(bool, str)

    def __init__(self, resource_ids: List[str], parent=None):
        super().__init__(parent)
        self.resource_ids = resource_ids

    def run(self) -> None:
        mgr = ResourceManager.get_instance()
        for r_id in self.resource_ids:
            self.status_changed.emit(f"Downloading {r_id}…")
            try:
                ok = mgr.download_resource(r_id, status_callback=self.status_changed.emit)
                if not ok:
                    self.finished.emit(False, f"Failed to download resource: {r_id}")
                    return
            except Exception as exc:
                self.finished.emit(False, str(exc))
                return

        self.finished.emit(True, "All resources downloaded successfully!")

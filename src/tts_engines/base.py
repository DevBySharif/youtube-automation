"""
base.py
Abstract TTSEngine interface.

All TTS engines must implement this contract.
Swap engines by passing a different implementation to Pipeline().

Current implementations:
  - KokoroEngine  (local, default)

Future implementations (add without touching Pipeline or UI):
  - PiperEngine
  - ElevenLabsEngine
  - CoquiEngine
"""

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Tuple


class TTSEngine(ABC):
    """
    Abstract base class for all TTS engines.

    The Pipeline calls generate() with clean text (no [MM:SS] timestamps).
    Each engine is responsible for:
      - Accepting a plain text string
      - Writing audio to output_path
      - Returning the output_path on success
    """

    @abstractmethod
    def generate(
        self,
        text:         str,
        output_path:  str,
        voice:        str                            = "",
        speed:        float                          = 1.0,
        cancel_check: Optional[Callable[[], bool]]  = None,
    ) -> Optional[str]:
        """
        Synthesise speech from text and save to output_path.

        Args:
            text:         Clean plain text — no timestamps, no markup.
            output_path:  Absolute path where the WAV file should be saved.
            voice:        Engine-specific voice identifier.
            speed:        Speaking speed multiplier (0.5–2.0).
            cancel_check: Optional callable that returns True when the user
                          has requested cancellation. Engines should call this
                          between generation chunks and return None if True.

        Returns:
            Absolute path to the generated audio file, or None if cancelled.

        Raises:
            ValueError:   If text is empty or voice is invalid.
            RuntimeError: If audio generation fails.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable engine name (e.g. 'Kokoro TTS')."""
        ...

    @property
    @abstractmethod
    def available_voices(self) -> List[Tuple[str, str]]:
        """
        List of voices supported by this engine.
        Each item is a (voice_id, display_label) tuple.
        """
        ...

    def __repr__(self) -> str:
        return f"<TTSEngine: {self.name}>"

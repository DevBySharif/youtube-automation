"""
metadata.py
Rich Word-Level Metadata export structures for YouTube Video Automation pipelines
(Image Prompt Generator, Scene Detector, Subtitles, Camera Motion & Zoom Effects).
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class WordMetadata:
    """Rich word-level timestamp, emotion, emphasis, and pause metadata."""

    word: str
    start: float
    end: float
    emotion: str = "neutral"
    emphasis: float = 0.5           # 0.0 to 1.0
    pause_after: float = 0.0        # Seconds of pause following word
    pitch_hz: Optional[float] = None
    volume_db: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "emotion": self.emotion,
            "emphasis": round(self.emphasis, 2),
            "pause_after": round(self.pause_after, 3),
        }


@dataclass
class NarrationMetadataExport:
    """Complete metadata bundle exported for downstream video rendering tools."""

    script_title: str
    total_duration_sec: float
    narration_mode: str
    voice_id: str
    provider_id: str
    words: List[WordMetadata] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "script_title": self.script_title,
            "total_duration_sec": round(self.total_duration_sec, 2),
            "narration_mode": self.narration_mode,
            "voice_id": self.voice_id,
            "provider_id": self.provider_id,
            "word_count": len(self.words),
            "words": [w.to_dict() for w in self.words],
        }

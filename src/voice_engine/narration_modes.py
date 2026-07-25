"""
narration_modes.py
15 AI Narration Profiles and Humanization Engine for Professional YouTube & Content Automation.

Supported Profiles:
  1. 📖 Documentary
  2. 🎙 YouTube Explainer
  3. 📚 Storytelling
  4. 🚀 Motivation
  5. 💰 Finance
  6. 🏛 History
  7. 🎓 Educational
  8. 🎧 Podcast
  9. 📖 Audiobook
 10. 📰 News
 11. 🧘 Meditation
 12. 😱 Horror
 13. 🎈 Kids
 14. 😂 Comedy
 15. 🎬 Cinematic Trailer
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any


class NarrationMode(str, Enum):
    DOCUMENTARY = "documentary"
    YOUTUBE_EXPLAINER = "youtube_explainer"
    STORYTELLING = "storytelling"
    MOTIVATION = "motivation"
    FINANCE = "finance"
    HISTORY = "history"
    EDUCATIONAL = "educational"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    NEWS = "news"
    MEDITATION = "meditation"
    HORROR = "horror"
    KIDS = "kids"
    COMEDY = "comedy"
    CINEMATIC_TRAILER = "cinematic_trailer"


NARRATION_MODE_LABELS: Dict[NarrationMode, str] = {
    NarrationMode.DOCUMENTARY: "📖 Documentary",
    NarrationMode.YOUTUBE_EXPLAINER: "🎙 YouTube Explainer",
    NarrationMode.STORYTELLING: "📚 Storytelling",
    NarrationMode.MOTIVATION: "🚀 Motivation",
    NarrationMode.FINANCE: "💰 Finance",
    NarrationMode.HISTORY: "🏛 History",
    NarrationMode.EDUCATIONAL: "🎓 Educational",
    NarrationMode.PODCAST: "🎧 Podcast",
    NarrationMode.AUDIOBOOK: "📖 Audiobook",
    NarrationMode.NEWS: "📰 News",
    NarrationMode.MEDITATION: "🧘 Meditation",
    NarrationMode.HORROR: "😱 Horror",
    NarrationMode.KIDS: "🎈 Kids",
    NarrationMode.COMEDY: "😂 Comedy",
    NarrationMode.CINEMATIC_TRAILER: "🎬 Cinematic Trailer",
}


@dataclass
class AdvancedVoiceSettings:
    """Advanced Voice Controls parameters."""

    speed: float = 1.00                # 0.50x to 2.00x
    stability: int = 75                 # 0 to 100
    expressiveness: int = 80            # 0 to 100
    clarity: int = 85                  # 0 to 100
    energy: int = 75                   # 0 to 100
    pitch_semitones: int = 0           # -20 to +20 semitones
    volume_gain_db: float = 0.0        # -12.0 dB to +12.0 dB
    sentence_pause_ms: int = 600       # 0 to 1500 ms
    word_pause_ms: int = 150           # 0 to 500 ms
    paragraph_pause_ms: int = 1200     # 0 to 3000 ms


@dataclass
class HumanizationSettings:
    """Humanization parameter controls."""

    natural_pauses: bool = True
    micro_pauses: bool = True
    sentence_breathing: bool = True
    comma_pauses: bool = True
    paragraph_pauses: bool = True
    emphasis_injection: bool = True
    natural_pacing: bool = True
    question_intonation: bool = True
    exclamation_emphasis: bool = True
    ellipsis_pause: bool = True
    quote_handling: bool = True
    conversation_rhythm: bool = True


# 15 Complete Narration Mode Parameter Profiles
NARRATION_MODE_PROFILES: Dict[NarrationMode, Dict[str, Any]] = {
    NarrationMode.DOCUMENTARY: {
        "speed": 0.95,
        "stability": 85,
        "expressiveness": 70,
        "clarity": 90,
        "energy": 70,
        "pitch_semitones": -1,
        "sentence_pause_ms": 750,
        "word_pause_ms": 180,
        "paragraph_pause_ms": 1500,
    },
    NarrationMode.YOUTUBE_EXPLAINER: {
        "speed": 1.05,
        "stability": 70,
        "expressiveness": 85,
        "clarity": 88,
        "energy": 85,
        "pitch_semitones": 0,
        "sentence_pause_ms": 500,
        "word_pause_ms": 120,
        "paragraph_pause_ms": 1000,
    },
    NarrationMode.STORYTELLING: {
        "speed": 0.92,
        "stability": 65,
        "expressiveness": 92,
        "clarity": 85,
        "energy": 78,
        "pitch_semitones": -1,
        "sentence_pause_ms": 800,
        "word_pause_ms": 200,
        "paragraph_pause_ms": 1600,
    },
    NarrationMode.MOTIVATION: {
        "speed": 1.08,
        "stability": 60,
        "expressiveness": 95,
        "clarity": 90,
        "energy": 98,
        "pitch_semitones": 1,
        "sentence_pause_ms": 650,
        "word_pause_ms": 140,
        "paragraph_pause_ms": 1200,
    },
    NarrationMode.FINANCE: {
        "speed": 1.00,
        "stability": 90,
        "expressiveness": 65,
        "clarity": 95,
        "energy": 75,
        "pitch_semitones": 0,
        "sentence_pause_ms": 550,
        "word_pause_ms": 130,
        "paragraph_pause_ms": 1100,
    },
    NarrationMode.HISTORY: {
        "speed": 0.94,
        "stability": 88,
        "expressiveness": 75,
        "clarity": 92,
        "energy": 72,
        "pitch_semitones": -2,
        "sentence_pause_ms": 780,
        "word_pause_ms": 170,
        "paragraph_pause_ms": 1500,
    },
    NarrationMode.EDUCATIONAL: {
        "speed": 0.98,
        "stability": 85,
        "expressiveness": 75,
        "clarity": 95,
        "energy": 75,
        "pitch_semitones": 0,
        "sentence_pause_ms": 650,
        "word_pause_ms": 150,
        "paragraph_pause_ms": 1300,
    },
    NarrationMode.PODCAST: {
        "speed": 1.02,
        "stability": 75,
        "expressiveness": 88,
        "clarity": 85,
        "energy": 80,
        "pitch_semitones": 0,
        "sentence_pause_ms": 580,
        "word_pause_ms": 130,
        "paragraph_pause_ms": 1150,
    },
    NarrationMode.AUDIOBOOK: {
        "speed": 0.90,
        "stability": 80,
        "expressiveness": 90,
        "clarity": 92,
        "energy": 70,
        "pitch_semitones": -1,
        "sentence_pause_ms": 850,
        "word_pause_ms": 200,
        "paragraph_pause_ms": 1800,
    },
    NarrationMode.NEWS: {
        "speed": 1.10,
        "stability": 95,
        "expressiveness": 60,
        "clarity": 98,
        "energy": 82,
        "pitch_semitones": 0,
        "sentence_pause_ms": 450,
        "word_pause_ms": 100,
        "paragraph_pause_ms": 900,
    },
    NarrationMode.MEDITATION: {
        "speed": 0.75,
        "stability": 95,
        "expressiveness": 70,
        "clarity": 88,
        "energy": 40,
        "pitch_semitones": -3,
        "sentence_pause_ms": 1200,
        "word_pause_ms": 300,
        "paragraph_pause_ms": 2500,
    },
    NarrationMode.HORROR: {
        "speed": 0.85,
        "stability": 55,
        "expressiveness": 95,
        "clarity": 80,
        "energy": 65,
        "pitch_semitones": -4,
        "sentence_pause_ms": 1000,
        "word_pause_ms": 250,
        "paragraph_pause_ms": 2000,
    },
    NarrationMode.KIDS: {
        "speed": 0.95,
        "stability": 60,
        "expressiveness": 98,
        "clarity": 90,
        "energy": 90,
        "pitch_semitones": 3,
        "sentence_pause_ms": 700,
        "word_pause_ms": 180,
        "paragraph_pause_ms": 1400,
    },
    NarrationMode.COMEDY: {
        "speed": 1.10,
        "stability": 50,
        "expressiveness": 98,
        "clarity": 85,
        "energy": 92,
        "pitch_semitones": 2,
        "sentence_pause_ms": 500,
        "word_pause_ms": 120,
        "paragraph_pause_ms": 1000,
    },
    NarrationMode.CINEMATIC_TRAILER: {
        "speed": 0.88,
        "stability": 80,
        "expressiveness": 95,
        "clarity": 92,
        "energy": 95,
        "pitch_semitones": -5,
        "sentence_pause_ms": 1100,
        "word_pause_ms": 280,
        "paragraph_pause_ms": 2200,
    },
}

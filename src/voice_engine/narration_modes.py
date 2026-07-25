"""
narration_modes.py
AI Narration Modes and Humanization Settings Engine for YouTube Automation.

Supported Modes:
  • 📖 Documentary
  • 🎙 YouTube Explainer
  • 💰 Finance
  • 🧠 Psychology
  • 😱 Horror
  • ❤️ Emotional Story
  • 🚀 Motivation
  • 📰 News
  • 🎮 Gaming
  • 📚 Educational
  • 🎬 Cinematic
  • 😂 Funny
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any


class NarrationMode(str, Enum):
    DOCUMENTARY = "documentary"
    YOUTUBE_EXPLAINER = "youtube_explainer"
    FINANCE = "finance"
    PSYCHOLOGY = "psychology"
    HORROR = "horror"
    EMOTIONAL_STORY = "emotional_story"
    MOTIVATION = "motivation"
    NEWS = "news"
    GAMING = "gaming"
    EDUCATIONAL = "educational"
    CINEMATIC = "cinematic"
    FUNNY = "funny"


NARRATION_MODE_LABELS: Dict[NarrationMode, str] = {
    NarrationMode.DOCUMENTARY: "📖 Documentary",
    NarrationMode.YOUTUBE_EXPLAINER: "🎙 YouTube Explainer",
    NarrationMode.FINANCE: "💰 Finance",
    NarrationMode.PSYCHOLOGY: "🧠 Psychology",
    NarrationMode.HORROR: "😱 Horror",
    NarrationMode.EMOTIONAL_STORY: "❤️ Emotional Story",
    NarrationMode.MOTIVATION: "🚀 Motivation",
    NarrationMode.NEWS: "📰 News",
    NarrationMode.GAMING: "🎮 Gaming",
    NarrationMode.EDUCATIONAL: "📚 Educational",
    NarrationMode.CINEMATIC: "🎬 Cinematic",
    NarrationMode.FUNNY: "😂 Funny",
}


@dataclass
class HumanizationSettings:
    """Humanization parameter controls."""

    natural_pauses: bool = True
    micro_pauses: bool = True
    sentence_breathing: bool = True
    emphasis_weight: float = 1.0        # 0.5x to 2.0x
    pitch_variation: float = 1.0        # 0.5x to 1.5x
    dynamic_energy: float = 1.0         # 0.5x to 1.5x
    pause_length_sec: float = 0.35      # 0.1s to 1.0s
    sentence_pause_sec: float = 0.65    # 0.2s to 2.0s
    ending_softness: float = 0.8        # 0.0 to 1.0


# Default Humanization Profiles per AI Narration Mode
NARRATION_MODE_PROFILES: Dict[NarrationMode, Dict[str, Any]] = {
    NarrationMode.DOCUMENTARY: {
        "speed": 0.95,
        "pause_length_sec": 0.45,
        "sentence_pause_sec": 0.80,
        "pitch_variation": 0.85,
        "dynamic_energy": 0.90,
        "ending_softness": 0.90,
    },
    NarrationMode.YOUTUBE_EXPLAINER: {
        "speed": 1.05,
        "pause_length_sec": 0.30,
        "sentence_pause_sec": 0.55,
        "pitch_variation": 1.15,
        "dynamic_energy": 1.10,
        "ending_softness": 0.70,
    },
    NarrationMode.FINANCE: {
        "speed": 1.00,
        "pause_length_sec": 0.35,
        "sentence_pause_sec": 0.60,
        "pitch_variation": 0.90,
        "dynamic_energy": 1.00,
        "ending_softness": 0.80,
    },
    NarrationMode.PSYCHOLOGY: {
        "speed": 0.90,
        "pause_length_sec": 0.50,
        "sentence_pause_sec": 0.90,
        "pitch_variation": 0.80,
        "dynamic_energy": 0.85,
        "ending_softness": 0.95,
    },
    NarrationMode.HORROR: {
        "speed": 0.85,
        "pause_length_sec": 0.65,
        "sentence_pause_sec": 1.10,
        "pitch_variation": 0.70,
        "dynamic_energy": 0.75,
        "ending_softness": 1.00,
    },
    NarrationMode.EMOTIONAL_STORY: {
        "speed": 0.92,
        "pause_length_sec": 0.45,
        "sentence_pause_sec": 0.85,
        "pitch_variation": 1.10,
        "dynamic_energy": 0.95,
        "ending_softness": 0.90,
    },
    NarrationMode.MOTIVATION: {
        "speed": 1.08,
        "pause_length_sec": 0.40,
        "sentence_pause_sec": 0.70,
        "pitch_variation": 1.25,
        "dynamic_energy": 1.30,
        "ending_softness": 0.60,
    },
    NarrationMode.NEWS: {
        "speed": 1.10,
        "pause_length_sec": 0.25,
        "sentence_pause_sec": 0.45,
        "pitch_variation": 0.85,
        "dynamic_energy": 1.05,
        "ending_softness": 0.50,
    },
    NarrationMode.GAMING: {
        "speed": 1.12,
        "pause_length_sec": 0.20,
        "sentence_pause_sec": 0.40,
        "pitch_variation": 1.30,
        "dynamic_energy": 1.35,
        "ending_softness": 0.50,
    },
    NarrationMode.EDUCATIONAL: {
        "speed": 0.98,
        "pause_length_sec": 0.40,
        "sentence_pause_sec": 0.70,
        "pitch_variation": 1.00,
        "dynamic_energy": 1.00,
        "ending_softness": 0.85,
    },
    NarrationMode.CINEMATIC: {
        "speed": 0.88,
        "pause_length_sec": 0.55,
        "sentence_pause_sec": 1.00,
        "pitch_variation": 0.80,
        "dynamic_energy": 0.90,
        "ending_softness": 0.95,
    },
    NarrationMode.FUNNY: {
        "speed": 1.10,
        "pause_length_sec": 0.28,
        "sentence_pause_sec": 0.50,
        "pitch_variation": 1.40,
        "dynamic_energy": 1.25,
        "ending_softness": 0.65,
    },
}

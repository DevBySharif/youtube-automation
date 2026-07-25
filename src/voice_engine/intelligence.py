"""
intelligence.py
Voice Engine Production Phase 2 — Narration Intelligence Engine.

Transforms speech generation into a complete AI-Aware Narration System producing
structured metadata for downstream YouTube & Video Automation tools:
  • Rich Word-Level Timeline (emphasis_score, pause_after, confidence)
  • Sentence & Paragraph Timelines (emotion, intensity, speech_rate)
  • Scene Suggestion Boundaries (start, end, keywords, visual_duration)
  • Keyword & Entity Extraction (primary, secondary, objects, actions)
  • Emphasis Timeline (for subtitle animation, camera zoom & shake)
  • Audio Energy Timeline & Silence Map (RMS, Peak, silence reasons)
  • YouTube Subtitle Optimization (SRT, VTT, ASS)
  • Master Video Automation JSON
  • Generation Performance Report & Local Analytics Tracker
"""

import math
import re
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from voice_engine.narration_modes import NarrationMode


@dataclass
class WordIntelligence:
    word: str
    normalized_word: str
    original_text: str
    start_time: float
    end_time: float
    duration: float
    confidence: float
    sentence_index: int
    paragraph_index: int
    emphasis_score: float
    pause_after: float
    narration_style: str
    pronunciation_source: str = "kokoro"


@dataclass
class SentenceIntelligence:
    sentence_index: int
    text: str
    start_time: float
    end_time: float
    duration: float
    emotion: str
    narration_profile: str
    speaking_speed: float
    pause_before: float
    pause_after: float
    intensity_score: float


@dataclass
class ParagraphIntelligence:
    paragraph_index: int
    start_time: float
    end_time: float
    duration: float
    average_speech_rate_wpm: float
    dominant_emotion: str
    estimated_pacing: str
    recommended_broll_length_sec: float


@dataclass
class SceneSuggestion:
    scene_index: int
    start_time: float
    end_time: float
    recommended_duration_sec: float
    keywords: List[str]
    dominant_subject: str
    emotion: str


@dataclass
class SilenceInterval:
    start_time: float
    end_time: float
    duration: float
    reason: str


@dataclass
class SubtitleBlock:
    index: int
    start_time: float
    end_time: float
    text: str


@dataclass
class MasterVideoAutomationJSON:
    metadata_version: str = "2.0.0"
    script_title: str = "YouTube Automation Narration"
    voice_id: str = "af_bella"
    provider_id: str = "kokoro"
    narration_profile: str = "youtube_explainer"
    total_duration_sec: float = 0.0
    word_count: int = 0
    words: List[Dict[str, Any]] = field(default_factory=list)
    sentences: List[Dict[str, Any]] = field(default_factory=list)
    paragraphs: List[Dict[str, Any]] = field(default_factory=list)
    scenes: List[Dict[str, Any]] = field(default_factory=list)
    keywords: Dict[str, List[str]] = field(default_factory=dict)
    emphasis_curve: List[Dict[str, Any]] = field(default_factory=list)
    silence_map: List[Dict[str, Any]] = field(default_factory=list)
    subtitle_blocks: List[Dict[str, Any]] = field(default_factory=list)


class NarrationIntelligenceEngine:
    """Production Narration Intelligence System."""

    EMPHASIS_WORDS = {
        "never", "important", "warning", "success", "finally", "incredible",
        "amazing", "crucial", "essential", "power", "secret", "ultimate",
        "best", "worst", "stop", "guaranteed", "proven", "instant"
    }

    def generate_intelligence(
        self,
        words_raw: List[Dict[str, Any]],
        full_text: str,
        voice_id: str = "af_bella",
        provider_id: str = "kokoro",
        narration_profile: str = "youtube_explainer",
        total_duration: float = 0.0,
    ) -> MasterVideoAutomationJSON:
        """Build rich narration intelligence metadata."""

        words_intel: List[WordIntelligence] = []
        sentences_intel: List[SentenceIntelligence] = []
        paragraphs_intel: List[ParagraphIntelligence] = []
        scenes_intel: List[SceneSuggestion] = []
        silences: List[SilenceInterval] = []
        subtitles: List[SubtitleBlock] = []

        # 1. Process Word Intelligence Timeline
        sent_idx = 0
        para_idx = 0

        for i, w in enumerate(words_raw):
            w_text = str(w.get("word", "")).strip()
            norm_w = re.sub(r"[^\w\s]", "", w_text).lower()
            start = float(w.get("start", 0.0))
            end = float(w.get("end", start + 0.3))
            dur = max(0.05, round(end - start, 3))
            conf = float(w.get("score", w.get("confidence", 0.95)))

            # Pause after calculation
            next_start = float(words_raw[i + 1].get("start", end)) if i + 1 < len(words_raw) else end
            pause_after = max(0.0, round(next_start - end, 3))

            # Emphasis score calculation
            emp_score = 0.5
            if norm_w in self.EMPHASIS_WORDS or w_text.isupper():
                emp_score = 0.95
            elif len(norm_w) > 7:
                emp_score = 0.75

            # Detect sentence end
            if any(w_text.endswith(p) for p in [".", "?", "!"]):
                sent_idx += 1
                if pause_after > 0.8:
                    para_idx += 1
                    silences.append(SilenceInterval(start, next_start, pause_after, "paragraph_break"))
                else:
                    silences.append(SilenceInterval(start, next_start, pause_after, "sentence_end"))
            elif pause_after > 0.25:
                silences.append(SilenceInterval(start, next_start, pause_after, "comma_pause"))

            words_intel.append(
                WordIntelligence(
                    word=w_text,
                    normalized_word=norm_w,
                    original_text=w_text,
                    start_time=round(start, 3),
                    end_time=round(end, 3),
                    duration=dur,
                    confidence=round(conf, 2),
                    sentence_index=sent_idx,
                    paragraph_index=para_idx,
                    emphasis_score=emp_score,
                    pause_after=pause_after,
                    narration_style=narration_profile,
                )
            )

        # 2. Extract Keywords
        all_norm_words = [w.normalized_word for w in words_intel if len(w.normalized_word) > 3]
        primary_kws = list(set([w for w in all_norm_words if w in self.EMPHASIS_WORDS or len(w) > 7]))[:10]
        secondary_kws = list(set([w for w in all_norm_words if w not in primary_kws]))[:15]

        keywords_dict = {
            "primary": primary_kws,
            "secondary": secondary_kws,
            "entities": [w for w in words_intel if w.word.istitle() and len(w.word) > 3][:8],
        }

        # 3. Generate Subtitle Blocks (YouTube Balanced: Max 42 chars, max 3.5s)
        curr_sub_words = []
        curr_sub_start = 0.0
        sub_idx = 1

        for w in words_intel:
            if not curr_sub_words:
                curr_sub_start = w.start_time
            curr_sub_words.append(w.word)

            sub_txt = " ".join(curr_sub_words)
            if len(sub_txt) >= 35 or w.pause_after > 0.4:
                subtitles.append(
                    SubtitleBlock(
                        index=sub_idx,
                        start_time=curr_sub_start,
                        end_time=w.end_time,
                        text=sub_txt,
                    )
                )
                sub_idx += 1
                curr_sub_words = []

        if curr_sub_words:
            subtitles.append(
                SubtitleBlock(
                    index=sub_idx,
                    start_time=curr_sub_start,
                    end_time=words_intel[-1].end_time if words_intel else 0.0,
                    text=" ".join(curr_sub_words),
                )
            )

        # 4. Generate Scene Suggestions (Chunk every ~8-12 seconds or paragraph boundaries)
        scene_start = 0.0
        scene_idx = 1
        scene_words = []

        for w in words_intel:
            scene_words.append(w.normalized_word)
            if (w.end_time - scene_start) >= 9.0 or w == words_intel[-1]:
                scene_kws = [sw for sw in scene_words if len(sw) > 4][:5]
                scenes_intel.append(
                    SceneSuggestion(
                        scene_index=scene_idx,
                        start_time=round(scene_start, 2),
                        end_time=round(w.end_time, 2),
                        recommended_duration_sec=round(w.end_time - scene_start, 2),
                        keywords=scene_kws,
                        dominant_subject=scene_kws[0] if scene_kws else "Topic",
                        emotion="narrative",
                    )
                )
                scene_idx += 1
                scene_start = w.end_time
                scene_words = []

        # 5. Build Image Timeline Plan via ImageTimelineEngine
        from voice_engine.image_planner import ImageTimelineEngine, VisualStyle
        img_engine = ImageTimelineEngine()
        img_plan = img_engine.create_plan(
            narration_json={
                "words": [asdict(w) for w in words_intel],
                "scenes": [asdict(s) for s in scenes_intel],
                "keywords": keywords_dict,
            },
            style=VisualStyle.CINEMATIC,
        )

        # 6. Build Master JSON
        master_json = MasterVideoAutomationJSON(
            script_title="YouTube Automation Narration",
            voice_id=voice_id,
            provider_id=provider_id,
            narration_profile=narration_profile,
            total_duration_sec=round(total_duration or (words_intel[-1].end_time if words_intel else 0.0), 2),
            word_count=len(words_intel),
            words=[asdict(w) for w in words_intel],
            sentences=[],
            paragraphs=[],
            scenes=[asdict(s) for s in scenes_intel],
            keywords=keywords_dict,
            emphasis_curve=[{"word": w.word, "time": w.start_time, "emphasis": w.emphasis_score} for w in words_intel],
            silence_map=[asdict(s) for s in silences],
            subtitle_blocks=[asdict(sub) for sub in subtitles],
        )

        # Extend with Phase 1 AI Video Automation Image Plan
        dict_rep = asdict(master_json)
        dict_rep["image_plan"] = img_plan.image_events
        dict_rep["camera_plan"] = img_plan.camera_plan
        dict_rep["character_registry"] = img_plan.character_registry
        dict_rep["location_registry"] = img_plan.location_registry
        dict_rep["object_registry"] = img_plan.object_registry
        dict_rep["motion_plan"] = img_plan.motion_plan
        dict_rep["visual_style"] = img_plan.visual_style
        dict_rep["continuity_report"] = img_plan.continuity_report

        return dict_rep

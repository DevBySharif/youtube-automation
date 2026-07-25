"""
concept_grouper.py  (src/)
Scene grouper — unchanged from approved version.

Uses the original script as the source of truth for sentence boundaries.
Whisper word timestamps provide real audio timing only.

Rules (exactly as approved):
    1. New sentence   — candidate split point
    2. Concept shift  — strong scene-shift word at sentence start
    3. Duration ≥ 4s  — current segment has been running ≥ 4 seconds

NO pause detection.
"""

import re
from typing import List, Dict, Tuple

SCENE_SHIFT_WORDS = {
    "then", "suddenly", "now", "but", "yet", "later", "meanwhile", "elsewhere",
    "however", "though", "although", "still", "instead", "after", "before",
    "soon", "finally", "eventually", "once", "perhaps", "maybe",
    "somewhere", "nowhere", "always", "never", "often", "sometimes",
    "outside", "inside", "above", "below", "behind", "ahead", "away",
    "across", "through", "beyond", "among", "between", "here", "there",
}

MAX_SEGMENT_DURATION = 4.0  # seconds


def _split_sentences(text: str) -> List[str]:
    lines = [line.strip() for line in text.splitlines()]
    sentences = []
    for line in lines:
        if not line:
            continue
        parts = re.split(r'(?<=[.?!…])\s+', line)
        for part in parts:
            part = part.strip()
            if part:
                sentences.append(part)
    return sentences


def _normalize_word(word: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\']', '', word).lower()


def _find_sentence_start_time(
    sentence: str,
    words: List[Dict],
    search_from_index: int = 0,
) -> Tuple[float, int]:
    sentence_words = sentence.split()
    if not sentence_words:
        fallback = words[search_from_index]["start"] if search_from_index < len(words) else 0.0
        return fallback, search_from_index

    first_word = _normalize_word(sentence_words[0])

    for i in range(search_from_index, len(words)):
        if _normalize_word(words[i]["word"]) == first_word:
            return words[i]["start"], i + 1

    if search_from_index < len(words):
        return words[search_from_index]["start"], search_from_index + 1

    return 0.0, search_from_index


def _to_mmss(seconds: float) -> str:
    total = int(seconds)
    return f"[{total // 60:02d}:{total % 60:02d}]"


def _is_concept_shift(sentence: str) -> bool:
    words = sentence.split()
    if not words:
        return False
    return _normalize_word(words[0]) in SCENE_SHIFT_WORDS


def group_into_scenes(original_script: str, words: List[Dict]) -> str:
    """
    Map original sentences to real Whisper timings, then group into scenes.

    Args:
        original_script: Plain text as entered by the user (source of truth).
        words:           Word-level timestamps from Whisper aligner.

    Returns:
        Formatted timestamp script string.
    """
    if not words:
        return "[00:00]\n" + original_script.strip()

    sentences = _split_sentences(original_script)
    if not sentences:
        return "[00:00]\n" + original_script.strip()

    # Map each sentence to its real start_time
    sentence_timings: List[Tuple[str, float]] = []
    search_index = 0
    for sentence in sentences:
        start_time, search_index = _find_sentence_start_time(
            sentence, words, search_from_index=search_index
        )
        sentence_timings.append((sentence, start_time))

    # Group into concept segments
    segments = []
    current_lines: List[str] = []
    current_start: float = sentence_timings[0][1]

    for sentence, start_time in sentence_timings:
        if not current_lines:
            current_lines.append(sentence)
            current_start = start_time
            continue

        segment_duration = start_time - current_start
        should_split = (
            _is_concept_shift(sentence)
            or segment_duration >= MAX_SEGMENT_DURATION
        )

        if should_split:
            segments.append({"timestamp": current_start, "lines": current_lines})
            current_lines = [sentence]
            current_start = start_time
        else:
            current_lines.append(sentence)

    if current_lines:
        segments.append({"timestamp": current_start, "lines": current_lines})

    output_parts = []
    for seg in segments:
        ts   = _to_mmss(seg["timestamp"])
        text = "\n".join(seg["lines"])
        output_parts.append(f"{ts}\n{text}")

    return "\n\n".join(output_parts)

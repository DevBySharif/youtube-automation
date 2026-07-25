"""
concept_grouper.py
Scene grouper for Timestamp Script Analyzer.

Pipeline position:
    original_script + words[] (from Whisper)
            ↓
    Sentence Split (using original script — source of truth)
            ↓
    Map each sentence to its first Whisper word → get real start_time
            ↓
    Apply concept boundary rules
            ↓
    Timestamp Script

Rules for concept boundaries (exactly as approved):
    1. New sentence         — always a candidate split point
    2. Concept changed      — strong scene-shift word at sentence start
    3. Segment duration ≥ 4s — current group has been accumulating for ≥ 4 seconds

NO pause detection. Kokoro natural pauses within sentences must NEVER trigger a new segment.
"""

import re
from typing import List, Dict, Tuple


# Words that signal a new visual scene or concept shift
SCENE_SHIFT_WORDS = {
    "then", "suddenly", "now", "but", "yet", "later", "meanwhile", "elsewhere",
    "however", "though", "although", "still", "instead", "after", "before",
    "soon", "finally", "eventually", "suddenly", "once", "perhaps", "maybe",
    "somewhere", "nowhere", "always", "never", "often", "sometimes",
    "outside", "inside", "above", "below", "behind", "ahead", "away",
    "across", "through", "beyond", "among", "between", "here", "there",
}

MAX_SEGMENT_DURATION = 4.0  # seconds — maximum concept group length


def _split_sentences(text: str) -> List[str]:
    """
    Split original script into sentences.
    Uses the original script as source of truth — not Whisper output.

    Splits on:
        - Sentence-ending punctuation: . ? ! …
        - Explicit line breaks (the author's own formatting)

    Preserves the author's intent for sentence grouping.
    """
    # First split on line breaks (the author's own grouping)
    lines = [line.strip() for line in text.splitlines()]

    sentences = []
    for line in lines:
        if not line:
            continue
        # Further split long lines on sentence-ending punctuation
        # Keeps the punctuation attached to the sentence
        parts = re.split(r'(?<=[.?!…])\s+', line)
        for part in parts:
            part = part.strip()
            if part:
                sentences.append(part)

    return sentences


def _normalize_word(word: str) -> str:
    """Strip punctuation for word matching."""
    return re.sub(r'[^a-zA-Z0-9\']', '', word).lower()


def _find_sentence_start_time(
    sentence: str,
    words: List[Dict],
    search_from_index: int = 0
) -> Tuple[float, int]:
    """
    Find the real start_time of a sentence by matching its first word
    against the Whisper word list.

    Args:
        sentence:          The original sentence text.
        words:             Full list of Whisper word dicts.
        search_from_index: Start searching from this index (avoids re-matching earlier words).

    Returns:
        Tuple of (start_time_seconds, next_search_index).
        Returns (words[search_from_index].start, search_from_index + 1) if no match found.
    """
    # Extract first meaningful word from the sentence
    sentence_words = sentence.split()
    if not sentence_words:
        fallback_time = words[search_from_index]["start"] if search_from_index < len(words) else 0.0
        return fallback_time, search_from_index

    first_word_normalized = _normalize_word(sentence_words[0])

    # Search forward in the word list for a match
    for i in range(search_from_index, len(words)):
        whisper_word_normalized = _normalize_word(words[i]["word"])
        if whisper_word_normalized == first_word_normalized:
            return words[i]["start"], i + 1

    # Fallback: use the time of the next available word
    if search_from_index < len(words):
        return words[search_from_index]["start"], search_from_index + 1

    return 0.0, search_from_index


def _to_mmss(seconds: float) -> str:
    """
    Format seconds as [MM:SS].

    Example:
        4.7 -> "[00:04]"
        74.2 -> "[01:14]"
    """
    total = int(seconds)  # floor
    m = total // 60
    s = total % 60
    return f"[{m:02d}:{s:02d}]"


def _is_concept_shift(sentence: str) -> bool:
    """
    Return True if the sentence begins with a strong scene-shift word.
    Only checks the first word of the sentence.
    """
    words = sentence.split()
    if not words:
        return False
    first = _normalize_word(words[0])
    return first in SCENE_SHIFT_WORDS


def group_into_scenes(
    original_script: str,
    words: List[Dict]
) -> str:
    """
    Main entry point for the concept grouper.

    Args:
        original_script: The plain text script as typed by the user.
        words:           Word-level timestamps from Whisper aligner.
                         Each item: { "word": str, "start": float, "end": float }

    Returns:
        Formatted timestamp script string, e.g.:

            [00:00]
            There is a stranger you have never forgotten.

            [00:04]
            Someone you saw once.

            [00:08]
            Maybe on a train.
    """
    if not words:
        return "[00:00]\n" + original_script.strip()

    # Step 1: Split original script into sentences (source of truth)
    sentences = _split_sentences(original_script)

    if not sentences:
        return "[00:00]\n" + original_script.strip()

    # Step 2: Map each sentence to its real start_time from Whisper
    sentence_timings = []  # [(sentence_text, start_time_seconds), ...]
    search_index = 0

    for sentence in sentences:
        start_time, search_index = _find_sentence_start_time(
            sentence, words, search_from_index=search_index
        )
        sentence_timings.append((sentence, start_time))

    # Step 3: Group sentences into concept segments
    # Each segment is a list of sentences that share one [MM:SS] timestamp
    segments = []           # [{ "timestamp": float, "lines": [str, ...] }, ...]
    current_lines = []
    current_start = sentence_timings[0][1]

    for sentence, start_time in sentence_timings:
        if not current_lines:
            # First sentence — start a new segment
            current_lines.append(sentence)
            current_start = start_time
            continue

        # Calculate how long the current segment has been running
        segment_duration = start_time - current_start

        # Apply the three concept boundary rules:
        should_split = (
            _is_concept_shift(sentence)          # Rule 2: concept-shift word
            or segment_duration >= MAX_SEGMENT_DURATION  # Rule 3: ≥ 4 seconds
        )
        # Rule 1 (new sentence) is the base — always a candidate.
        # We only actually split when rule 2 or 3 fires, OR when
        # we're at the natural end of the previous sentence
        # and the next sentence starts a fresh concept.
        # For simple scripts where no rule fires, sentences are grouped together.

        if should_split:
            # Emit the current segment
            segments.append({
                "timestamp": current_start,
                "lines": current_lines,
            })
            # Start a new segment
            current_lines = [sentence]
            current_start = start_time
        else:
            # Continue accumulating into the current segment
            current_lines.append(sentence)

    # Don't forget the last open segment
    if current_lines:
        segments.append({
            "timestamp": current_start,
            "lines": current_lines,
        })

    # Step 4: Format the output
    output_parts = []
    for segment in segments:
        ts = _to_mmss(segment["timestamp"])
        text = "\n".join(segment["lines"])
        output_parts.append(f"{ts}\n{text}")

    return "\n\n".join(output_parts)

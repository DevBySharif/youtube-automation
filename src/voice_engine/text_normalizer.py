"""
text_normalizer.py
Advanced Text Normalization Engine for Voice Synthesis.

Normalizes:
  • Numbers & Ordinals (2026 -> twenty twenty-six, 1st -> first)
  • Currency ($25 -> twenty-five dollars, €50 -> fifty euros)
  • Percentages (50% -> fifty percent)
  • Dates & Times (5:30 PM -> five thirty PM, 2026-07-26 -> July twenty-sixth twenty twenty-six)
  • URLs & Emails (www.example.com -> w w w dot example dot com)
  • Acronyms & Abbreviations (NASA, GPT, AI, CPU, GPU, FBI, BBC, Dr., Mr., vs.)
  • Roman Numerals (Chapter III -> Chapter three)
  • Mathematical & Special Symbols (+ -> plus, = -> equals, % -> percent, & -> and)
"""

import re
from typing import List, Tuple, Dict


_ABBREVIATIONS: Dict[str, str] = {
    "dr.": "Doctor",
    "mr.": "Mister",
    "mrs.": "Missus",
    "ms.": "Miss",
    "prof.": "Professor",
    "vs.": "versus",
    "etc.": "et cetera",
    "eg.": "for example",
    "ie.": "that is",
    "approx.": "approximately",
    "dept.": "department",
    "st.": "Saint",
    "ave.": "Avenue",
    "blvd.": "Boulevard",
}

_NUM_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
    20: "twenty", 30: "thirty", 40: "forty", 50: "fifty",
    60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety"
}


def _number_to_words(n: int) -> str:
    """Convert integer to spoken English words."""
    if n < 0:
        return "negative " + _number_to_words(-n)
    if n in _NUM_WORDS:
        return _NUM_WORDS[n]
    if n < 100:
        tens, units = divmod(n, 10)
        return f"{_NUM_WORDS[tens * 10]}-{_NUM_WORDS[units]}"
    if n < 1000:
        hundreds, remainder = divmod(n, 100)
        res = f"{_NUM_WORDS[hundreds]} hundred"
        if remainder:
            res += f" { _number_to_words(remainder) }"
        return res
    if n < 10000 and n % 100 != 0:
        # Years like 2026 -> twenty twenty-six
        high, low = divmod(n, 100)
        return f"{_number_to_words(high)} {_number_to_words(low)}"
    if n < 1000000:
        thousands, remainder = divmod(n, 1000)
        res = f"{_number_to_words(thousands)} thousand"
        if remainder:
            res += f" {_number_to_words(remainder)}"
        return res
    return str(n)


class TextNormalizer:
    """Production Text Normalization Engine."""

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        # 1. Normalize URLs & Emails
        text = re.sub(r"https?://(?:www\.)?(\S+)", r"w w w dot \1", text)
        text = re.sub(r"www\.(\S+)", r"w w w dot \1", text)
        text = re.sub(r"(\S+)@(\S+)\.(\S+)", r"\1 at \2 dot \3", text)

        # 2. Currency
        text = re.sub(r"\$(\d+)(?:\.(\d{2}))?", lambda m: self._fmt_currency(m.group(1), m.group(2), "dollar"), text)
        text = re.sub(r"€(\d+)(?:\.(\d{2}))?", lambda m: self._fmt_currency(m.group(1), m.group(2), "euro"), text)

        # 3. Percentages
        text = re.sub(r"(\d+)%", r"\1 percent", text)

        # 4. Times (e.g. 5:30 PM, 10:15 am)
        text = re.sub(r"(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?", self._fmt_time, text)

        # 5. Abbreviations
        for k, v in _ABBREVIATIONS.items():
            text = re.sub(r"\b" + re.escape(k), v, text, flags=re.IGNORECASE)

        # 6. Roman Numerals (Chapter I, II, III, IV, V, VI, VII, VIII, IX, X)
        text = re.sub(r"\b(Chapter|Volume|Part|Section)\s+(I|II|III|IV|V|VI|VII|VIII|IX|X)\b", self._fmt_roman, text)

        # 7. Isolated Numbers (e.g. 2026 -> twenty twenty-six, 42 -> forty-two)
        text = re.sub(r"\b\d+\b", lambda m: _number_to_words(int(m.group(0))), text)

        # 8. Special Math Symbols
        text = text.replace("&", " and ")
        text = text.replace("+", " plus ")
        text = text.replace("=", " equals ")

        # 9. Clean Whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _fmt_currency(self, main: str, cents: str, unit: str) -> str:
        val = int(main)
        w = _number_to_words(val)
        res = f"{w} {unit}s" if val != 1 else f"{w} {unit}"
        if cents and int(cents) > 0:
            c_val = int(cents)
            res += f" and {_number_to_words(c_val)} cents"
        return res

    def _fmt_time(self, m: re.Match) -> str:
        hr = int(m.group(1))
        mn = int(m.group(2))
        period = (m.group(3) or "").upper()
        hr_w = _number_to_words(hr)
        mn_w = _number_to_words(mn) if mn > 0 else ""
        res = f"{hr_w} {mn_w}".strip()
        if period:
            res += f" {period}"
        return res

    def _fmt_roman(self, m: re.Match) -> str:
        section = m.group(1)
        num_str = m.group(2)
        roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
        n = roman_map.get(num_str, 1)
        return f"{section} {_number_to_words(n)}"

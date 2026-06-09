"""Automated classifier for ranking Tanglish naturalness (chosen vs rejected)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

# Tamil Unicode block
TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")
# Common Tanglish English filler words
TANGLISH_MARKERS = {
    "da", "di", "machan", "bro", "seri", "illa", "enna", "epdi", "na", "nee",
    "ok", "super", "scene", "matter", "plan", "chill", "cool", "actually",
    "basically", "literally", "only", "just", "like", "kinda", "sorta",
}
# Robotic / overly formal patterns
ROBOTIC_PATTERNS = [
    re.compile(r"\b(therefore|hence|furthermore|moreover|nevertheless)\b", re.I),
    re.compile(r"\b(I am|you are|he is|she is|it is|we are|they are)\b"),
    re.compile(r"\b(shall|ought|wherein|whereby)\b", re.I),
    re.compile(r"[\u0B80-\u0BFF]{30,}"),  # long uninterrupted Tamil blocks
]


@dataclass
class NaturalnessScore:
    tanglish: str
    score: float
    breakdown: dict


def score_tanglish(text: str) -> NaturalnessScore:
    """
    Heuristic naturalness scorer for Tamil+English colloquial text.

    Higher score = more natural Tanglish. Factors:
    - Tamil script presence (required for code-mixing)
    - English word mixing (Tanglish markers)
    - Penalties for robotic/formal patterns
    - Length appropriateness
    """
    text_lower = text.lower().strip()
    breakdown = {}

    # Tamil script presence
    tamil_chars = len(TAMIL_RE.findall(text))
    breakdown["tamil_chars"] = tamil_chars
    tamil_score = min(tamil_chars / 10, 1.0) if tamil_chars > 0 else 0.0

    # English mixing
    words = set(re.findall(r"[a-zA-Z]+", text_lower))
    marker_hits = len(words & TANGLISH_MARKERS)
    breakdown["marker_hits"] = marker_hits
    mix_score = min(marker_hits / 3, 1.0)

    # Robotic penalty
    robotic_hits = sum(1 for p in ROBOTIC_PATTERNS if p.search(text))
    breakdown["robotic_hits"] = robotic_hits
    robotic_penalty = robotic_hits * 0.25

    # Length: prefer concise colloquial (10-80 chars)
    length = len(text)
    breakdown["length"] = length
    if 10 <= length <= 80:
        length_score = 1.0
    elif length < 10:
        length_score = length / 10
    else:
        length_score = max(0.0, 1.0 - (length - 80) / 100)

    # Punctuation naturalness (casual)
    exclaim = text.count("!") + text.count("?")
    breakdown["punctuation"] = exclaim
    punct_score = min(exclaim / 2, 0.5)

    total = (
        tamil_score * 0.35
        + mix_score * 0.30
        + length_score * 0.20
        + punct_score * 0.15
        - robotic_penalty
    )
    total = max(0.0, min(1.0, total))

    return NaturalnessScore(tanglish=text, score=total, breakdown=breakdown)


class NaturalnessClassifier:
    """Pick chosen (most natural) and rejected (most robotic) from candidates."""

    def rank(self, candidates: List[str]) -> List[Tuple[str, float]]:
        scored = [(c, score_tanglish(c).score) for c in candidates]
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def pick_pair(self, candidates: List[str]) -> Tuple[str, str] | None:
        """Return (chosen, rejected) or None if fewer than 2 candidates."""
        if len(candidates) < 2:
            return None
        ranked = self.rank(candidates)
        chosen = ranked[0][0]
        rejected = ranked[-1][0]
        if chosen == rejected:
            return None
        return chosen, rejected

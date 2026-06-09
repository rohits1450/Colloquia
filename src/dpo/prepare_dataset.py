"""Format DPO preference pairs from multi-candidate generations."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from src.dpo.classifier import NaturalnessClassifier


def load_candidates(path: str | Path) -> List[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_dpo_pairs(
    candidates_path: str | Path,
    output_path: str | Path,
    min_score_gap: float = 0.05,
) -> int:
    """
    Group candidates by English input, classify, and write DPO pairs.

    Output format (JSONL):
      {"prompt": ..., "chosen": ..., "rejected": ...}
    """
    records = load_candidates(candidates_path)
    grouped: Dict[str, List[str]] = defaultdict(list)
    prompts: Dict[str, str] = {}

    for rec in records:
        eng = rec["english"]
        grouped[eng].append(rec["tanglish"])
        if eng not in prompts:
            prompts[eng] = (
                f"Translate to natural spoken Tanglish (Tamil+English mix):\n{eng}"
            )

    classifier = NaturalnessClassifier()
    pairs_written = 0
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for eng, tanglish_list in grouped.items():
            unique = list(dict.fromkeys(tanglish_list))
            if len(unique) < 2:
                continue

            ranked = classifier.rank(unique)
            chosen, chosen_score = ranked[0]
            rejected, rejected_score = ranked[-1]

            if chosen_score - rejected_score < min_score_gap:
                continue

            pair = {
                "prompt": prompts[eng],
                "chosen": chosen,
                "rejected": rejected,
                "chosen_score": round(chosen_score, 4),
                "rejected_score": round(rejected_score, 4),
                "english": eng,
            }
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
            pairs_written += 1

    print(f"Wrote {pairs_written} DPO pairs to {output_path}")
    return pairs_written

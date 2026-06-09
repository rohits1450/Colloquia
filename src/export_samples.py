"""Export DailyDialog inputs with Tanglish outputs to a text file."""

from __future__ import annotations

import argparse
from itertools import islice
from pathlib import Path

from src.config import load_config
from src.data.load_dailydialog import extract_utterances
from src.dpo.classifier import NaturalnessClassifier
from src.generation.multi_candidate import MultiCandidateGenerator
from src.rag.retriever import SlangRetriever


def export_sample_io(
    output_path: str | Path,
    limit: int = 25,
    config: dict | None = None,
) -> int:
    cfg = config or load_config()
    ds_cfg = cfg["dataset"]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    utterances = list(
        islice(
            extract_utterances(
                dataset_name=ds_cfg["name"],
                config=ds_cfg["config"],
                split=ds_cfg["split"],
            ),
            limit,
        )
    )

    retriever = SlangRetriever(cfg)
    generator = MultiCandidateGenerator(config=cfg, retriever=retriever)
    classifier = NaturalnessClassifier()

    lines = [
        "Tanglish RAG Translation Samples",
        f"Dataset: {ds_cfg['name']} ({ds_cfg['split']} split)",
        f"Model: {cfg['generation']['model']}",
        "=" * 72,
        "",
    ]

    for i, utt in enumerate(utterances, 1):
        candidates = generator.generate(utt.text)
        ranked = classifier.rank([c.tanglish for c in candidates])
        best_tanglish = ranked[0][0]
        best_score = ranked[0][1]

        lines.extend(
            [
                f"Sample {i}",
                f"Dialogue ID : {utt.dialogue_id}",
                f"Emotion     : {utt.emotion}",
                f"Act         : {utt.act}",
                f"Input (EN)  : {utt.text}",
                f"Output (Tanglish): {best_tanglish}",
                f"Naturalness score: {best_score:.3f}",
                "-" * 72,
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(utterances)} samples to {output_path}")
    return len(utterances)


def main():
    parser = argparse.ArgumentParser(description="Export sample input/output text file")
    parser.add_argument(
        "--output",
        default="./outputs/sample_input_output.txt",
        help="Output text file path",
    )
    parser.add_argument("--limit", type=int, default=25, help="Number of DailyDialog samples")
    args = parser.parse_args()
    export_sample_io(args.output, limit=args.limit)


if __name__ == "__main__":
    main()

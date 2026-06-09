"""End-to-end RAG + DPO pipeline orchestration."""

from __future__ import annotations

import argparse
from itertools import islice

from src.config import load_config
from src.data.load_dailydialog import extract_utterances
from src.rag.build_kb import build_knowledge_base


def cmd_build_kb(args):
    cfg = load_config()
    build_knowledge_base(config=cfg, limit=args.limit)


def cmd_generate(args):
    from src.generation.multi_candidate import MultiCandidateGenerator

    cfg = load_config()
    utterances = extract_utterances(
        dataset_name=cfg["dataset"]["name"],
        config=cfg["dataset"]["config"],
        split=cfg["dataset"]["split"],
    )
    english_inputs = [u.text for u in islice(utterances, args.limit)]
    generator = MultiCandidateGenerator(config=cfg)
    count = generator.generate_batch_to_file(english_inputs, cfg["paths"]["candidates"])
    print(f"Generated {count} translation candidates")


def cmd_prepare_dpo(args):
    from src.dpo.prepare_dataset import build_dpo_pairs

    cfg = load_config()
    build_dpo_pairs(cfg["paths"]["candidates"], cfg["paths"]["dpo_dataset"])


def cmd_train(args):
    from src.dpo.train import train_dpo

    cfg = load_config()
    train_dpo(config=cfg)


def cmd_translate(args):
    from src.rag.retriever import SlangRetriever
    from src.generation.multi_candidate import MultiCandidateGenerator

    cfg = load_config()
    retriever = SlangRetriever(cfg)
    context = retriever.format_context(args.text)
    print(context)
    print("---")
    generator = MultiCandidateGenerator(config=cfg, retriever=retriever)
    for i, cand in enumerate(generator.generate(args.text), 1):
        print(f"[{i}] (temp={cand.temperature}) {cand.tanglish}")


def main():
    parser = argparse.ArgumentParser(
        description="Tanglish RAG + DPO translation pipeline"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_kb = sub.add_parser("build-kb", help="Build Qdrant slang knowledge base")
    p_kb.add_argument("--limit", type=int, default=None, help="Max utterances to index")
    p_kb.set_defaults(func=cmd_build_kb)

    p_gen = sub.add_parser("generate", help="Generate multi-candidate translations")
    p_gen.add_argument("--limit", type=int, default=50, help="Number of English inputs")
    p_gen.set_defaults(func=cmd_generate)

    p_dpo = sub.add_parser("prepare-dpo", help="Build DPO preference pairs")
    p_dpo.set_defaults(func=cmd_prepare_dpo)

    p_train = sub.add_parser("train", help="Run DPO + LoRA fine-tuning")
    p_train.set_defaults(func=cmd_train)

    p_tr = sub.add_parser("translate", help="Translate a single sentence")
    p_tr.add_argument("text", type=str, help="English input")
    p_tr.set_defaults(func=cmd_translate)

    p_export = sub.add_parser(
        "export-samples",
        help="Write DailyDialog inputs + Tanglish outputs to a text file",
    )
    p_export.add_argument("--limit", type=int, default=25)
    p_export.add_argument(
        "--output", default="./outputs/sample_input_output.txt"
    )
    p_export.set_defaults(
        func=lambda args: __import__(
            "src.export_samples", fromlist=["export_sample_io"]
        ).export_sample_io(args.output, limit=args.limit)
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

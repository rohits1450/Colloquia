#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Starting Qdrant"
docker compose up -d qdrant
sleep 3

echo "==> Step 1: Build RAG slang knowledge base (BGE-M3 -> Qdrant)"
python -m src.pipeline build-kb

echo "==> Step 2: Multi-candidate generation (RAG + Gemma-2)"
python -m src.pipeline generate --limit 100

echo "==> Step 3: Prepare DPO preference pairs"
python -m src.pipeline prepare-dpo

echo "==> Step 4: DPO + LoRA fine-tuning"
python -m src.pipeline train

echo "==> Pipeline complete. Adapter saved to outputs/dpo-lora/"

# Tanglish RAG + DPO Translation System

English-to-Tanglish (Tamil+English colloquial) translation pipeline using **RAG** for conversational context retrieval and **DPO + LoRA** for preference-aligned fine-tuning.

## Architecture

```
DailyDialog (HF) ──► BGE-M3 embeddings ──► Qdrant (offline KB)
                                                    │
English input ──► LangChain similarity search ◄─────┘
                         │
                         ▼
              Prompt + retrieved slang context
                         │
                         ▼
              Gemma-2 (multi-temp candidates)
                         │
                         ▼
         Naturalness classifier (chosen vs rejected)
                         │
                         ▼
              DPOTrainer + LoRA fine-tune
```

## Prerequisites

- Python 3.10+
- Docker (for Qdrant)
- NVIDIA GPU with 4GB+ VRAM (Gemma-2-2B in 4-bit)
- HuggingFace account (accept Gemma-2 license)

```bash
huggingface-cli login
```

## Setup

```bash
cd ~/Projects/tanglish-rag-dpo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
```

## Pipeline Steps

### 1. Build RAG Slang Knowledge Base

Indexes DailyDialog utterances with BGE-M3 vectors into Qdrant:

```bash
python -m src.pipeline build-kb
# optional: limit for quick test
python -m src.pipeline build-kb --limit 500
```

### 2. Multi-Candidate Generation

Retrieves similar conversational patterns, prompts Gemma-2 with varying temperature:

```bash
python -m src.pipeline generate --limit 100
```

### 3. Prepare DPO Dataset

Automated classifier ranks candidates; best = `chosen`, most robotic = `rejected`:

```bash
python -m src.pipeline prepare-dpo
```

### 4. DPO + LoRA Training

Fine-tunes Gemma-2 with preference pairs:

```bash
python -m src.pipeline train
```

### Run Full Pipeline

```bash
bash scripts/run_pipeline.sh
```

### Single Sentence Translation

```bash
python -m src.pipeline translate "How are you doing today?"
```

## Configuration

Edit `config/settings.yaml` to change models, Qdrant settings, LoRA hyperparameters, etc.

| Setting | Default | Notes |
|---------|---------|-------|
| Embedding model | `BAAI/bge-m3` | 1024-dim dense vectors |
| Generator | `google/gemma-2-2b-it` | 4-bit quantized for 4GB GPU |
| Qdrant collection | `dailydialog_slang_kb` | Local, offline-capable |
| LoRA rank | 16 | Target: q/k/v/o projections |

## Project Structure

```
tanglish-rag-dpo/
├── config/settings.yaml
├── docker-compose.yml          # Qdrant
├── src/
│   ├── data/load_dailydialog.py
│   ├── rag/
│   │   ├── build_kb.py         # BGE-M3 → Qdrant
│   │   ├── retriever.py        # LangChain similarity search
│   │   └── embeddings.py
│   ├── generation/
│   │   └── multi_candidate.py  # Gemma-2 multi-temp generation
│   ├── dpo/
│   │   ├── classifier.py       # Naturalness scoring
│   │   ├── prepare_dataset.py  # chosen/rejected pairs
│   │   └── train.py            # DPOTrainer + LoRA
│   └── pipeline.py             # CLI entry point
└── scripts/run_pipeline.sh
```

## License Note

DailyDialog is CC BY-NC-SA 4.0 (non-commercial). Gemma-2 has its own license terms on HuggingFace.

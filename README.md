# Colloquial Conversion System

An advanced, production-scale English-to-Tanglish (Tamil+English colloquial) translation pipeline. The system utilizes **Retrieval-Augmented Generation (RAG)** to dynamically inject localized South Indian slang rules and colloquial phrasing templates into a massive, cloud-hosted **Llama-3.3-70B** model, followed by a local **DPO + LoRA** preference-alignment loop.

## Architecture

```
Local Slang Dictionary ──► BGE-M3 embeddings ──► Qdrant Vector Store (Offline KB)
                                                        │
English input ──► LangChain similarity search ◄─────────┘
                         │
                         ▼
             Prompt + retrieved slang mappings
                         │
                         ▼
        Groq API: Llama-3.3-70B (Async Multi-Candidate)
                         │
                         ▼
         Naturalness classifier (chosen vs rejected)
                         │
                         ▼
        Local DPOTrainer + LoRA fine-tune (Gemma-2)

```

## Enhancements & Modernizations

* **High-Fidelity Code-Switching:** Replaced weak, lower-parameter local models with **Llama-3.3-70B-Versatile** via Groq API, eliminating translation hallucinations, non-Tamil language bleeding, and raw metadata leakage.
* **True Slang Mapping Base:** Upgraded the RAG index layer from plain English context match loops to a dedicated semantic lookup engine pointing to curated Tamil colloquial idioms and text slang phrases.
* **Asynchronous Multi-Threading:** Generation pipeline leverages a thread-pool executor to process bulk translation candidates in parallel, scaling system capabilities to whole multi-turn datasets.
* **Rate-Limit Guarding:** Integrated exponential backoff wrappers to handle API transaction rates smoothly without losing data state or breaking runtime tasks.

## Prerequisites

* Python 3.10+
* Docker (for Qdrant Vector DB)
* NVIDIA GPU with 4GB+ VRAM (for running local DPO training loops)
* HuggingFace account (for storing the target fine-tuned adapter)
* Groq Cloud Developer API Key

```bash
huggingface-cli login

```

## Setup

1. **Clone and Navigate:**
```bash
git clone https://github.com/rohits1450/ColloquialConversionRAG
cd ColloquialConversionRAG

```



```

2. **Initialize Environment & Dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install groq tenacity

```

3. **Configure Environment Variables:**
Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your_actual_api_key_here

```



```

4. **Boot Infrastructure:**
   ```bash
docker compose up -d

```

## Pipeline Steps

### 1. Seed & Build Slang Knowledge Base

Converts the structured local dictionary mapping (`data/tamil_slang_dict.json`) into 1024-dimensional dense vectors using BGE-M3 and upserts them into Qdrant:

```bash
python -m src.pipeline build-kb

```

### 2. Scalable Asynchronous Generation

Processes English text sources in parallel, retrieving matching lexical metadata structures and calling remote endpoints concurrently to produce multi-temperature variants:

```bash
python -m src.pipeline generate --limit 100

```

### 3. Build DPO Preference Pairs

Ranks translation candidate outputs automatically using a naturalness classifier, separating clean structural vernacular translations into `chosen` segments and robotic strings into `rejected` segments:

```bash
python -m src.pipeline prepare-dpo

```

### 4. DPO + LoRA Training

Fine-tunes the base open-weights model locally using the generated preference files to anchor high-tier colloquial reasoning natively on-device:

```bash
python -m src.pipeline train

```

### Single Sentence Inference Mode

Test individual phrases interactively via the terminal:

```bash
python -m src.pipeline translate "Say, Jim, how about going for a few beers after dinner?"

```

## Configuration

Modify system hyperparameters and target endpoints inside `config/settings.yaml`:

| Section | Setting | Value / Target | Notes |
| --- | --- | --- | --- |
| **embeddings** | `model` | `BAAI/bge-m3` | 1024-dim dense cross-lingual representations |
| **qdrant** | `collection` | `dailydialog_slang_kb` | Local isolated vector instance |
| **generation** | `model` | `llama-3.3-70b-versatile` | Routed via Groq API cloud engine |
| **generation** | `max_new_tokens` | `256` | Extended limit to prevent clipping errors |
| **dpo** | `lora_r` | `16` | Rank target for local fine-tuning steps |

## Project Structure

```
ColloquialConversionRAG/
├── config/settings.yaml        # Complete pipeline parameters
├── docker-compose.yml          # Qdrant engine environment configuration
├── data/
│   └── tamil_slang_dict.json   # Curated English-to-Slang text dictionary source
├── src/
│   ├── data/load_dailydialog.py
│   ├── rag/
│   │   ├── build_kb.py         # Dictionary mapping embedding & vector streaming
│   │   ├── retriever.py        # LangChain similarity match query logic
│   │   └── embeddings.py
│   ├── generation/
│   │   └── multi_candidate.py  # Parallelized multi-temp generation with retry logic
│   ├── dpo/
│   │   ├── classifier.py       # Metrics scoring backend
│   │   ├── prepare_dataset.py  # Pair alignment generation mapping
│   │   └── train.py            # Local DPOTrainer orchestration
│   └── pipeline.py             # CLI application entry terminal
└── scripts/run_pipeline.sh

```
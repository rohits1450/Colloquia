"""Build offline-searchable slang knowledge base in Qdrant using BGE-M3."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Iterable

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm

from src.config import load_config
from src.data.load_dailydialog import DialogueUtterance, extract_utterances
from src.rag.embeddings import BGEM3Embeddings


def _utterance_to_payload(utt: DialogueUtterance) -> dict:
    return {
        "text": utt.text,
        "emotion": utt.emotion,
        "act": utt.act,
        "dialogue_id": utt.dialogue_id,
        "turn_index": utt.turn_index,
        "source_id": utt.id,
    }


def _batched(items: Iterable, batch_size: int):
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def build_knowledge_base(
    config: dict | None = None,
    limit: int | None = None,
) -> int:
    """Embed DailyDialog utterances and upsert into Qdrant."""
    cfg = config or load_config()
    emb_cfg = cfg["embeddings"]
    qdrant_cfg = cfg["qdrant"]
    ds_cfg = cfg["dataset"]
    paths = cfg["paths"]

    Path(paths["data_dir"]).mkdir(parents=True, exist_ok=True)
    metadata_path = Path(paths["kb_metadata"])

    embeddings = BGEM3Embeddings(
        model_name=emb_cfg["model"],
        device=emb_cfg["device"],
    )

    client = QdrantClient(host=qdrant_cfg["host"], port=qdrant_cfg["port"])
    collection = qdrant_cfg["collection"]
    vector_size = qdrant_cfg["vector_size"]

    if client.collection_exists(collection):
        client.delete_collection(collection)

    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    utterances = extract_utterances(
        dataset_name=ds_cfg["name"],
        config=ds_cfg["config"],
        split=ds_cfg["split"],
    )
    if limit:
        from itertools import islice

        utterances = islice(utterances, limit)

    total = 0
    batch_size = emb_cfg["batch_size"]

    with metadata_path.open("w", encoding="utf-8") as meta_f:
        for batch in tqdm(
            _batched(utterances, batch_size),
            desc="Embedding & indexing",
        ):
            texts = [u.text for u in batch]
            vectors = embeddings.embed_documents(texts)
            points = []

            for utt, vector in zip(batch, vectors):
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, utt.id))
                payload = _utterance_to_payload(utt)
                points.append(PointStruct(id=point_id, vector=vector, payload=payload))
                meta_f.write(json.dumps(payload, ensure_ascii=False) + "\n")

            client.upsert(collection_name=collection, points=points)
            total += len(batch)

    print(f"Indexed {total} utterances into Qdrant collection '{collection}'")
    return total


if __name__ == "__main__":
    build_knowledge_base()

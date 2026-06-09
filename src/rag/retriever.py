"""LangChain-based similarity search over the Qdrant slang knowledge base."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.config import load_config
from src.rag.embeddings import BGEM3Embeddings


@dataclass
class RetrievedSlang:
    text: str
    emotion: str
    act: str
    score: float


class SlangRetriever:
    """Retrieve top contextual slang phrases via similarity search."""

    def __init__(self, config: dict | None = None):
        cfg = config or load_config()
        self.cfg = cfg
        qdrant_cfg = cfg["qdrant"]
        emb_cfg = cfg["embeddings"]
        ret_cfg = cfg["retrieval"]

        self.top_k = ret_cfg["top_k"]
        self.score_threshold = ret_cfg.get("score_threshold", 0.0)

        self.embeddings = BGEM3Embeddings(
            model_name=emb_cfg["model"],
            device=emb_cfg["device"],
        )

        client = QdrantClient(host=qdrant_cfg["host"], port=qdrant_cfg["port"])
        self.store = QdrantVectorStore(
            client=client,
            collection_name=qdrant_cfg["collection"],
            embedding=self.embeddings,
            content_payload_key="text",
            validate_collection_config=False,
        )

    def retrieve(self, english_input: str, top_k: int | None = None) -> List[RetrievedSlang]:
        k = top_k or self.top_k
        docs = self.store.similarity_search_with_score(english_input, k=k)

        results = []
        for doc, score in docs:
            # Qdrant cosine distance: lower is more similar; convert to similarity
            similarity = 1.0 - score
            if similarity < self.score_threshold:
                continue
            meta = doc.metadata or {}
            results.append(
                RetrievedSlang(
                    text=doc.page_content,
                    emotion=meta.get("emotion", ""),
                    act=meta.get("act", ""),
                    score=similarity,
                )
            )
        return results

    def format_context(self, english_input: str, top_k: int | None = None) -> str:
        """Format retrieved slang into a prompt context block."""
        hits = self.retrieve(english_input, top_k=top_k)
        if not hits:
            return "No similar conversational patterns found."

        lines = ["Similar conversational patterns from the slang knowledge base:"]
        for i, hit in enumerate(hits, 1):
            lines.append(
                f"{i}. \"{hit.text}\" (emotion={hit.emotion}, act={hit.act}, "
                f"similarity={hit.score:.2f})"
            )
        return "\n".join(lines)

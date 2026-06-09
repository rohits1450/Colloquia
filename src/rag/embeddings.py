"""Embedding wrapper compatible with LangChain (BGE-M3 via sentence-transformers)."""

from __future__ import annotations

from typing import List

import torch
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


class BGEM3Embeddings(Embeddings):
    """LangChain-compatible wrapper around BAAI/bge-m3."""

    def __init__(self, model_name: str = "BAAI/bge-m3", device: str = "cuda"):
        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"
        self.model = SentenceTransformer(model_name, device=device)
        self.device = device
        dim_fn = getattr(self.model, "get_embedding_dimension", None) or self.model.get_sentence_embedding_dimension
        self.vector_size = dim_fn()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors = self.model.encode(texts, batch_size=32, show_progress_bar=False)
        return vectors.tolist()

    def embed_query(self, text: str) -> List[float]:
        vector = self.model.encode([text], show_progress_bar=False)
        return vector[0].tolist()

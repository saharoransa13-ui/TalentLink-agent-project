
import math
import os
from functools import lru_cache
from typing import Sequence

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=2)
def _load_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


class SentenceTransformerEmbedder:
    """Generate normalized embeddings with a consistent interface."""

    def __init__(self, model_name: str | None = None, model=None):
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL", DEFAULT_MODEL
        )
        self._model = model

    @property
    def model(self):
        if self._model is None:
            self._model = _load_model(self.model_name)
        return self._model

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        # Normalize here rather than relying on a model-specific argument.
        vectors = self.model.encode(list(texts))
        if hasattr(vectors, "tolist"):
            vectors = vectors.tolist()

        normalized = []
        for vector in vectors:
            values = [float(value) for value in vector]
            norm = math.sqrt(sum(value * value for value in values))
            if norm > 0:
                values = [value / norm for value in values]
            normalized.append(values)

        return normalized

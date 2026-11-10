from dataclasses import dataclass

from .vector_store import RAGVectorStore


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source: str
    file_type: str
    chunk_index: int
    similarity: float


class RAGRetriever:
    def __init__(self, store: RAGVectorStore):
        self.store = store

    def retrieve(self, question: str, top_k: int = 4) -> list[RetrievedChunk]:
        results = self.store.query(question, top_k=top_k)
        return [
            RetrievedChunk(
                text=item["text"],
                source=item["source"],
                file_type=item["file_type"],
                chunk_index=item["chunk_index"],
                similarity=item["similarity"],
            )
            for item in results
        ]

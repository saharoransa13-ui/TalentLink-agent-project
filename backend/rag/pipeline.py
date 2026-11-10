from pathlib import Path

from .chunker import chunk_text
from .document_loader import discover_documents, load_document
from .embeddings import SentenceTransformerEmbedder
from .retriever import RAGRetriever, RetrievedChunk
from .vector_store import RAGVectorStore


class RAGPipeline:
    """Document ingestion and semantic retrieval. No LLM answer generation yet."""

    def __init__(
        self,
        persist_directory: str | Path | None = None,
        collection_name: str = "cv_knowledge",
        embedder: SentenceTransformerEmbedder | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.store = RAGVectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedder=self.embedder,
        )
        self.retriever = RAGRetriever(self.store)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def ingest_file(self, path: str | Path) -> dict:
        document = load_document(path)
        chunks = chunk_text(
            document.text,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
        )
        count = self.store.upsert_chunks(document.source, document.file_type, chunks)
        return {"source": document.source, "chunks_added_or_updated": count}

    def ingest_directory(self, directory: str | Path) -> dict:
        results = []
        errors = []
        for path in discover_documents(directory):
            try:
                results.append(self.ingest_file(path))
            except Exception as exc:
                errors.append({"source": path.name, "error": f"{type(exc).__name__}: {exc}"})
        return {
            "documents_processed": len(results),
            "chunks_added_or_updated": sum(item["chunks_added_or_updated"] for item in results),
            "results": results,
            "errors": errors,
        }

    def retrieve(self, question: str, top_k: int = 4) -> list[RetrievedChunk]:
        return self.retriever.retrieve(question, top_k=top_k)

    def stats(self) -> dict:
        return {
            "collection": self.store.collection.name,
            "chunks_indexed": self.store.count(),
            "persist_directory": str(self.store.persist_directory),
        }

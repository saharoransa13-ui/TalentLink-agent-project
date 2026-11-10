from pathlib import Path
import re

import pytest

from backend.rag.chunker import chunk_text
from backend.rag.document_loader import load_document
from backend.rag.embeddings import SentenceTransformerEmbedder
from backend.rag.pipeline import RAGPipeline


class TinyTestEmbedder:
    """Tiny deterministic vectorizer so tests never download a model."""
    def encode(self, texts):
        vocabulary = ["python", "network", "backup", "storage", "database", "security"]
        vectors = []
        for text in texts:
            words = set(re.findall(r"[a-z]+", text.lower()))
            vector = [float(word in words) for word in vocabulary]
            if not any(vector):
                vector[0] = 0.01
            norm = sum(value * value for value in vector) ** 0.5
            vectors.append([value / norm for value in vector])
        return vectors


def test_chunk_text_returns_chunks_with_overlap():
    text = " ".join(f"word{i}" for i in range(100))
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert set(chunks[0].text.split()) & set(chunks[1].text.split())


def test_chunk_text_validates_settings():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=10, overlap=10)


def test_load_txt_document(tmp_path):
    path = tmp_path / "guide.txt"
    path.write_text("Python networking and security guide.", encoding="utf-8")
    document = load_document(path)
    assert document.source == "guide.txt"
    assert document.file_type == "txt"
    assert "networking" in document.text


def test_rag_ingest_retrieve_and_persist(tmp_path):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "backup.txt").write_text(
        "Backup systems protect data and support recovery after outages.",
        encoding="utf-8",
    )
    (knowledge / "network.txt").write_text(
        "Network security uses segmentation, firewalls, and access controls.",
        encoding="utf-8",
    )

    db_path = tmp_path / "chroma"
    pipeline = RAGPipeline(
        persist_directory=db_path,
        collection_name="test_knowledge",
        embedder=SentenceTransformerEmbedder(model=TinyTestEmbedder()),
        chunk_size=200,
        chunk_overlap=20,
    )
    result = pipeline.ingest_directory(knowledge)
    assert result["documents_processed"] == 2
    assert result["chunks_added_or_updated"] == 2
    assert result["errors"] == []

    matches = pipeline.retrieve("backup recovery", top_k=1)
    assert matches
    assert matches[0].source == "backup.txt"
    assert "recovery" in matches[0].text.lower()

    # A new pipeline instance reads the same persistent collection.
    reopened = RAGPipeline(
        persist_directory=db_path,
        collection_name="test_knowledge",
        embedder=SentenceTransformerEmbedder(model=TinyTestEmbedder()),
    )
    assert reopened.stats()["chunks_indexed"] == 2
    assert reopened.retrieve("network security", top_k=1)[0].source == "network.txt"


def test_retrieve_rejects_empty_question(tmp_path):
    pipeline = RAGPipeline(
        persist_directory=tmp_path / "empty",
        collection_name="empty_test",
        embedder=SentenceTransformerEmbedder(model=TinyTestEmbedder()),
    )
    with pytest.raises(ValueError):
        pipeline.retrieve("   ")

from pathlib import Path
from typing import Any
import hashlib
import os
import re

import chromadb

from .embeddings import SentenceTransformerEmbedder


def _stable_id(source: str, chunk_index: int, text: str) -> str:
    raw = f"{source}\0{chunk_index}\0{text}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class RAGVectorStore:
    """Persistent ChromaDB collection with filename-aware and semantic retrieval."""

    def __init__(
        self,
        persist_directory: str | Path | None = None,
        collection_name: str = "cv_knowledge",
        embedder: SentenceTransformerEmbedder | None = None,
    ):
        default_path = Path(__file__).resolve().parents[2] / "data" / "chroma_db"
        self.persist_directory = Path(
            persist_directory or os.getenv("RAG_CHROMA_PATH", str(default_path))
        )
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder or SentenceTransformerEmbedder()
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, source: str, file_type: str, chunks: list[Any]) -> int:
        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]
        vectors = self.embedder.encode(texts)
        ids = [_stable_id(source, chunk.chunk_index, chunk.text) for chunk in chunks]
        metadatas = [
            {
                "source": source,
                "file_type": file_type,
                "chunk_index": int(chunk.chunk_index),
            }
            for chunk in chunks
        ]
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas,
        )
        return len(chunks)

    def _find_named_source(self, question: str) -> str | None:
        """Return an indexed filename explicitly mentioned in the question."""
        result = self.collection.get(include=["metadatas"])
        sources = {
            metadata.get("source", "")
            for metadata in (result.get("metadatas") or [])
            if metadata and metadata.get("source")
        }

        question_lower = question.casefold()

        # Prefer the longest match so that similarly named files are not confused.
        for source in sorted(sources, key=len, reverse=True):
            if source.casefold() in question_lower:
                return source

        # Also recognize a filename when the user omits its extension.
        for source in sorted(sources, key=len, reverse=True):
            stem = Path(source).stem
            if len(stem) >= 8 and stem.casefold() in question_lower:
                return source

        return None

    def query(self, question: str, top_k: int = 4) -> list[dict]:
        if not question or not question.strip():
            raise ValueError("question must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if self.collection.count() == 0:
            return []

        # Exact source filtering is used only when a filename is named.
        named_source = self._find_named_source(question)
        if named_source:
            result = self.collection.get(
                where={"source": named_source},
                include=["documents", "metadatas"],
            )
            documents = result.get("documents") or []
            metadatas = result.get("metadatas") or []

            output = []
            for document, metadata in zip(documents, metadatas):
                output.append(
                    {
                        "text": document,
                        "source": metadata.get("source", "unknown"),
                        "file_type": metadata.get("file_type", "unknown"),
                        "chunk_index": metadata.get("chunk_index", -1),
                        "distance": 0.0,
                        "similarity": 1.0,
                    }
                )

            output.sort(key=lambda item: item["chunk_index"])
            return output[:top_k]

        # Retrieve a wider semantic candidate set so exact course matches
        # can be prioritized without losing general semantic relevance.
        candidate_count = min(max(top_k * 5, 20), self.collection.count())
        result = self.collection.query(
            query_embeddings=self.embedder.encode([question]),
            n_results=candidate_count,
            include=["documents", "metadatas", "distances"],
        )
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        output = []
        for document, metadata, distance in zip(docs, metas, distances):
            output.append(
                {
                    "text": document,
                    "source": metadata.get("source", "unknown"),
                    "file_type": metadata.get("file_type", "unknown"),
                    "chunk_index": metadata.get("chunk_index", -1),
                    "distance": float(distance),
                    "similarity": 1.0 - float(distance),
                }
            )

        # When a question names a specific course, prefer chunks from course
        # pages whose title or filename matches that course. Keep semantic
        # results as fallbacks, and preserve source/chunk identity.
        q = question.casefold()
        course_terms = {
            term for term in re.findall(r"[a-z0-9]+", q)
            if len(term) >= 3
        }
        specific_course = any(
            marker in q for marker in (
                "course", "training", "foundation", "certification",
                "exam", "duration", "prerequisite",
            )
        )

        if specific_course and course_terms:
            def normalize(value):
                return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))

            # Extract a likely requested course title from phrases such as
            # "course for ITIL (Version 5) Foundation?".
            title_phrase = ""
            match = re.search(
                r"\bfor\s+(.+?)(?:\?|\.|;|\bdistinguish\b|\binclude\b)",
                question,
                flags=re.IGNORECASE,
            )
            if match:
                candidate = match.group(1).strip()
                if len(candidate.split()) <= 10:
                    title_phrase = normalize(candidate)

            def course_match(item):
                source = Path(item["source"]).stem.casefold()
                text = item["text"].casefold()
                title_area = normalize(text[:1800])
                exact_title = bool(
                    title_phrase and title_phrase in title_area
                )
                title_terms = set(re.findall(r"[a-z0-9]+", source))
                title_overlap = len(course_terms & title_terms)
                text_overlap = sum(1 for term in course_terms if term in text)
                return (
                    exact_title,
                    title_overlap > 0,
                    title_overlap,
                    text_overlap,
                    item["similarity"],
                )

            output.sort(key=course_match, reverse=True)

            # If the requested title is present in retrieved course pages,
            # return only chunks from those matching pages. This prevents
            # related courses from supplying unsupported course details.
            if title_phrase:
                matching_sources = {
                    item["source"]
                    for item in output
                    if title_phrase in normalize(item["text"][:1800])
                }
                if matching_sources:
                    output = [
                        item for item in output
                        if item["source"] in matching_sources
                    ]

        unique = []
        seen = set()
        for item in output:
            key = (item["source"], item["chunk_index"])
            if key not in seen:
                seen.add(key)
                unique.append(item)
            if len(unique) >= top_k:
                break
        return unique

    def count(self) -> int:
        return self.collection.count()

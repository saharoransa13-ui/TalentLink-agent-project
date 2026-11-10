"""Local retrieval-augmented generation foundation for the CV Gap project."""
from .pipeline import RAGPipeline
from .retriever import RetrievedChunk

__all__ = ["RAGPipeline", "RetrievedChunk"]

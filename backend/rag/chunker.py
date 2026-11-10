from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[TextChunk]:
    """Split text into overlapping chunks, preferring nearby paragraph/sentence boundaries."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if not normalized:
        return []

    chunks: list[TextChunk] = []
    start = 0
    length = len(normalized)

    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            # Prefer a readable boundary in the latter half of the candidate chunk.
            lower_bound = start + int(chunk_size * 0.60)
            candidates = [
                normalized.rfind("\n", lower_bound, end),
                normalized.rfind(". ", lower_bound, end),
                normalized.rfind("? ", lower_bound, end),
                normalized.rfind("! ", lower_bound, end),
                normalized.rfind("; ", lower_bound, end),
            ]
            boundary = max(candidates)
            if boundary > start:
                end = boundary + (1 if normalized[boundary] == "\n" else 2)

        piece = normalized[start:end].strip()
        if piece:
            chunks.append(TextChunk(text=piece, chunk_index=len(chunks)))

        if end >= length:
            break
        start = max(end - overlap, start + 1)

    return chunks

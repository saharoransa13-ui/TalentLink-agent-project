"""Optional local semantic matching. Install the 'semantic' extra to enable it."""
import os
import re
from functools import lru_cache
from typing import Dict, List, Tuple


def _sentences(text: str) -> List[str]:
    chunks = [re.sub(r"\s+", " ", x).strip(" -•\t") for x in re.split(r"[\n.!?;|]+", text) if x.strip()]
    return [x[:500] for x in chunks if len(x) >= 12][:300]


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))


def semantic_skill_evidence(cv_text: str, role) -> Tuple[Dict[str, Tuple[float, str]], str | None]:
    """Return best sentence per skill when similarity passes threshold; never upgrades to full match."""
    if os.getenv("ENABLE_EMBEDDING_MATCHING", "false").lower() not in {"1", "true", "yes"}:
        return {}, None
    try:
        chunks = _sentences(cv_text)
        if not chunks:
            return {}, None
        model = _model()
        chunk_vectors = model.encode(chunks, normalize_embeddings=True)
        threshold = float(os.getenv("EMBEDDING_PARTIAL_THRESHOLD", "0.58"))
        matches = {}
        for skill in role.skills:
            query = f"Professional experience and demonstrated skills in {skill.name}. Related terms: {', '.join(skill.aliases)}."
            vector = model.encode([query], normalize_embeddings=True)[0]
            scores = chunk_vectors @ vector
            best_index = int(scores.argmax())
            score = float(scores[best_index])
            if score >= threshold:
                matches[skill.skill_id] = (score, chunks[best_index])
        return matches, None
    except ImportError:
        return {}, "Embedding matching is enabled but sentence-transformers is not installed. Install requirements-semantic.txt."
    except Exception as exc:
        return {}, f"Embedding matching could not run ({type(exc).__name__}); keyword matching was used."

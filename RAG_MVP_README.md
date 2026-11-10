# RAG MVP — CV Gap Recommendation System

> **Historical note:** this file describes the first RAG milestone. The project has since added LLM answers, the `/rag/*` API endpoints, the website assistant and a multilingual embedding model. See `README.md` for the current setup.

This milestone adds local document ingestion and semantic retrieval. It does **not** yet generate natural-language answers with the LLM or expose RAG through FastAPI/UI.

## Included
- PDF, DOCX, TXT, and Markdown text extraction
- Overlapping text chunks
- Sentence-transformer embeddings using `EMBEDDING_MODEL` (defaults to `sentence-transformers/all-MiniLM-L6-v2`)
- Persistent ChromaDB storage
- Semantic retrieval with source, file type, chunk index, and similarity metadata
- Unit tests that use a tiny test embedder and do not download a model

## Install
From the project root, in Windows CMD:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements-rag.txt
```

## Add knowledge documents
Create `data\knowledge_base` and place supported documents inside it. This folder is intended for source documents and is not automatically committed to Git unless you choose to change `.gitignore`.

## Quick smoke test
After copying `backend\rag` into your project, run:

```cmd
.venv\Scripts\python.exe -m pytest tests\test_rag.py -q
```

## Example usage
Run this from the project root after adding files to `data\knowledge_base`:

```python
from backend.rag import RAGPipeline

rag = RAGPipeline()
print(rag.ingest_directory("data/knowledge_base"))
print(rag.retrieve("What does the policy say about backup and recovery?", top_k=4))
print(rag.stats())
```

The default persistent database directory is `data/chroma_db`. It is local generated data and should not be committed.

## Notes
- RAG retrieval scores are similarity indicators, not calibrated probabilities.
- A PDF containing scanned images without a text layer may yield no extractable text; OCR is not included in this milestone.
- This version indexes the file name as the source label. If different subfolders contain identical file names, they can collide; the next iteration should preserve relative paths and support re-indexing/deletion policies.
- Ingestion catches per-document errors and reports them instead of aborting the entire folder run.

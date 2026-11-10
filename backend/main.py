from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

import json
import uuid
import os
import requests
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.cv_parser import CVUploadError, extract_text
from backend.llm_extractor import extract_candidate_profile_smart
from backend.embedding_matcher import semantic_skill_evidence
from backend.live_sources import search_jobs, search_courses
from backend.skill_engine import calculate_gaps
from backend.recommender import recommend
from backend.schemas import JobProfile, GapReport
from backend.storage import init_db, log_request
from pydantic import BaseModel, Field
from backend.rag.pipeline import RAGPipeline
from backend.rag.answerer import answer_question


ROOT = Path(__file__).resolve().parents[1]
ROLES_PATH = ROOT / "data" / "roles.json"

app = FastAPI(title="CV Gap Analysis & Recommendation API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"]
)

def load_roles():
    with ROLES_PATH.open("r", encoding="utf-8") as f:
        return {r["role_id"]: JobProfile.model_validate(r) for r in json.load(f)}

@app.on_event("startup")
def startup():
    init_db()
    # Load the embedding model now, so the first assistant question is fast.
    try:
        get_rag_pipeline().embedder.encode(["warm up"])
    except Exception as exc:
        print(f"RAG warm-up skipped: {type(exc).__name__}: {exc}")
@app.get("/health")
def health():
    return {"status": "ok", "service": "cv-gap-analysis"}

@app.get("/debug/roles")
def debug_roles():
    """Show configured role skills and their aliases for troubleshooting."""
    return [
        {
            "role_id": role.role_id,
            "title": role.title,
            "skills": [
                {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "aliases": skill.aliases,
                    "weight": skill.weight,
                }
                for skill in role.skills
            ],
        }
        for role in load_roles().values()
    ]


@app.get("/roles")
def roles():
    return [{"role_id": r.role_id, "title": r.title, "description": r.description} for r in load_roles().values()]

@app.get("/discover/jobs")
def discover_jobs(query: str, where: str = "Egypt", page: int = 1, limit: int = 10):
    try:
        return search_jobs(query=query, where=where, page=page, results_per_page=limit)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Job source request failed: {exc}")
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=502, detail=f"Invalid job source response: {exc}")


@app.get("/discover/courses")
def discover_courses(query: str, limit: int = 10):
    try:
        return search_courses(query=query, limit=limit)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Course source request failed: {exc}")
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=502, detail=f"Invalid course source response: {exc}")


@app.post("/analyze", response_model=GapReport)
async def analyze(file: UploadFile = File(...), role_id: str = Form(...)):
    all_roles = load_roles()
    role = all_roles.get(role_id)
    if not role:
        raise HTTPException(status_code=400, detail=f"Unknown role_id '{role_id}'. See GET /roles.")
    content = await file.read()
    try:
        text = extract_text(file.filename or "cv.txt", content)
    except CVUploadError as exc:
        raise HTTPException(status_code=400, detail={"code": exc.code, "message": str(exc)})
    profile, extraction_method, extraction_warning = extract_candidate_profile_smart(text, file.filename or "")
    semantic_matches, embedding_warning = semantic_skill_evidence(text, role)
    score, gaps = calculate_gaps(profile, role, semantic_matches=semantic_matches)
    recommendations, roadmap = recommend(gaps)
    request_id = str(uuid.uuid4())
    log_request(request_id, role_id, score)
    warnings: list[str] = []
    warning_codes: list[str] = []

    def add_warning(code: str, message: str) -> None:
        warnings.append(message)
        warning_codes.append(code)

    if extraction_warning:
        add_warning("llm_failed", extraction_warning)
    if embedding_warning:
        add_warning("semantic_unavailable", embedding_warning)
    warnings.append(f"Skill extraction method: {extraction_method}.")  # technical info, no code
    if extraction_method.startswith("llm"):
        add_warning("llm_privacy", "LLM extraction is enabled: CV text was sent to the configured external provider. Use only with candidate consent and an appropriate privacy notice.")
    if not profile.skills:
        add_warning("no_skills", "No known skills were detected. Try a text-based CV or extend the alias map.")
    if (file.filename or "").lower().endswith(".pdf") and len(text) < 100:
        add_warning("little_pdf_text", "Very little PDF text was extracted; this may be a scanned PDF.")
    return GapReport(
        request_id=request_id, role_id=role.role_id, role_title=role.title,
        match_score=score, candidate_profile=profile, gaps=gaps,
        recommendations=recommendations, roadmap=roadmap, warnings=warnings,
        warning_codes=warning_codes,
    )

# --- RAG API: document ingestion, grounded answers, and knowledge-base stats ---

RAG_DOCUMENTS_DIR = Path(
    os.getenv("RAG_DOCUMENTS_DIR", str(ROOT / "data" / "knowledge_base"))
)
if not RAG_DOCUMENTS_DIR.is_absolute():
    RAG_DOCUMENTS_DIR = ROOT / RAG_DOCUMENTS_DIR

RAG_STORE_DIR = ROOT / "data" / "chroma_db"
_rag_pipeline = None


class RAGQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    context: str = Field(default="", max_length=6000)   # جديد
    top_k: int = Field(default=4, ge=1, le=10)


def get_rag_pipeline():
    """Initialize the persistent RAG pipeline only when first needed."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(
            persist_directory=RAG_STORE_DIR,
            collection_name="cv_knowledge",
        )
    return _rag_pipeline


@app.post("/rag/ask")
def rag_ask(request: RAGQuestion):
    """Answer a question using retrieved documents and return source citations."""
    try:
        return answer_question(
            get_rag_pipeline(),
            request.question,
            top_k=request.top_k,
            context=request.context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG request failed: {type(exc).__name__}",
        )


@app.post("/rag/ingest")
def rag_ingest():
    """Index supported documents from the configured knowledge-base directory."""
    try:
        RAG_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        result = get_rag_pipeline().ingest_directory(RAG_DOCUMENTS_DIR)
        return {
            **result,
            "knowledge_base_directory": str(RAG_DOCUMENTS_DIR),
            "stats": get_rag_pipeline().stats(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {type(exc).__name__}",
        )


@app.get("/rag/stats")
def rag_stats():
    """Return persistent vector-store statistics."""
    try:
        return {
            **get_rag_pipeline().stats(),
            "knowledge_base_directory": str(RAG_DOCUMENTS_DIR),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read RAG stats: {type(exc).__name__}",
        )



# --- Web UI: serve the HTML/JS frontend from the same server ---

WEB_DIR = ROOT / "web"


@app.get("/", include_in_schema=False)
def home():
    """Serve the main web page."""
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

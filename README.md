# CV Gap Analysis & Recommendation System

An extensible MVP for analyzing CVs, identifying skill gaps, and recommending relevant training courses, certifications, and practical projects. The system combines deterministic skill scoring, optional LLM-powered extraction, local semantic matching, live job/course discovery, and a Retrieval-Augmented Generation (RAG) knowledge base.

The application includes a **FastAPI backend**, a bilingual **web interface** (Arabic by default, with English) served by the same backend, a persistent **ChromaDB vector database**, and a growing collection of technical learning resources, certifications and course catalogs. The older **Streamlit dashboard** is still included as an alternative interface.

## Key Features

- **Web interface:** Bilingual Arabic/English website (HTML + JavaScript) served at `http://127.0.0.1:8000/`.
- **CV parsing:** Extract text from PDF, DOCX, and TXT files (English CVs only, maximum 10 MB).
- **Candidate profiling:** Identify skills and normalize aliases against a known skill taxonomy.
- **Role matching:** Compare candidate skills against a selected IT role.
- **Deterministic gap scoring:** Calculate match scores, missing skills, partial matches, and priorities.
- **Course recommendations:** Recommend relevant courses, certifications, and hands-on projects.
- **Optional LLM extraction:** Use an OpenAI-compatible API for structured skill extraction.
- **Optional semantic matching:** Use local sentence-transformer embeddings to identify additional potential skill matches.
- **Live discovery:** Integrate supported job and course search providers.
- **RAG knowledge retrieval:** Search indexed technical documentation, training materials, and course descriptions.
- **Grounded answers:** Generate responses using retrieved passages and clickable source citations such as `[S1]`.
- **Arabic and English questions:** The RAG index uses a multilingual embedding model, so the assistant can answer questions written in Arabic or English.
- **Persistent knowledge index:** Store indexed content in ChromaDB for reuse across sessions.

## Requirements

- Python 3.12 (tested with 3.12.9). Python 3.11 should also work.
- Internet access for package installation, model downloads, and optional external APIs.
- An API key is optional for the core CV analysis functionality.
- An OpenAI-compatible LLM endpoint is required for LLM-based extraction and RAG answer generation.
- Optional dependencies are installed separately for semantic matching.

## Quick Start

### Windows PowerShell

From the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-semantic.txt
pip install -r requirements-rag.txt
Copy-Item .env.example .env
```

The semantic dependencies are optional. Install them only if you intend to use local embedding-based matching or the RAG functionality that depends on sentence-transformer embeddings.

Configure `.env` as needed, then start the backend:

```powershell
python -m uvicorn backend.main:app --reload
```

Then open the website at http://127.0.0.1:8000/ .

The first start can take a few minutes because the embedding model is downloaded. The server loads the model at startup so the first assistant question is fast.

The old Streamlit dashboard is optional. To use it, open a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run .\frontend\app.py
```

On Windows you can also use the helper scripts in the project root: `1_setup.bat`, `2_check_key.bat`, `3_run_backend.bat`, `4_run_frontend.bat` (Streamlit) and `5_run_tests.bat`.

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-semantic.txt
pip install -r requirements-rag.txt
cp .env.example .env
```

Start the backend:

```bash
python -m uvicorn backend.main:app --reload
```

Then open http://127.0.0.1:8000/ . The Streamlit dashboard is optional:

```bash
source .venv/bin/activate
python -m streamlit run frontend/app.py
```

### Application URLs

| Service | URL |
|---|---|
| Website (main interface) | http://127.0.0.1:8000/ |
| Streamlit dashboard (optional) | http://localhost:8501 |
| API documentation | http://127.0.0.1:8000/docs |
| Health check | http://127.0.0.1:8000/health |

## Using the Website

1. Open http://127.0.0.1:8000/ . Use the language button to switch between Arabic and English.
2. Upload a CV that follows the upload rules (below).
3. Select the target IT role.
4. Click **Analyze my CV**.
5. Review the match score, matched skills, partial matches, missing skills, the learning roadmap and recommendations.
6. Ask the **smart assistant** follow-up questions about courses and certifications. Your results are sent with the question as context. Click a citation such as `[S1]` to jump to its source.

### CV Upload Rules

| Rule | Limit |
|---|---|
| Language | English only |
| File types | PDF, DOCX, TXT |
| Maximum size | 10 MB |
| Content | Selectable text (scanned image-only PDFs are not supported) |

The website checks the file type and size before uploading. The server checks all rules again. A CV is rejected as non-English when more than 30% of its letters are Arabic, so an English CV that contains an Arabic name or address is still accepted.

Upload errors return HTTP 400 with a code so the website can show the message in the selected language:

```json
{"detail": {"code": "cv_not_english", "message": "The CV must be written in English. ..."}}
```

| Code | Meaning |
|---|---|
| `cv_not_english` | The CV is not written in English |
| `bad_file_type` | The file type is not PDF, DOCX or TXT |
| `file_too_large` | The file is larger than 10 MB |
| `pdf_unreadable` | The PDF is damaged or not a real PDF |
| `docx_unreadable` | The Word file is damaged or not a real .docx |
| `no_text` | No text could be extracted (for example a scanned PDF) |

The analysis report contains `warnings` (English text) and `warning_codes` (`llm_failed`, `semantic_unavailable`, `llm_privacy`, `no_skills`, `little_pdf_text`) that the website translates.

You can also submit a CV through the API:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@sample_cv.txt" \
  -F "role_id=network_engineer"
```

## Skill Scoring

For each skill required by a role, the engine assigns:

- `1.0` — Matched skill: a sentence shows a practical action with the skill (for example "Developed REST APIs with FastAPI").
- `0.5` — Partial skill match: the skill appears with context such as training, a project or a course, or a semantic match was found.
- `0.25` — Listed only: the skill is only listed (for example in a skills line or a table) with no example of use. The evidence starts with `Listed only (no example of use)`.
- `0.0` — Missing skill.

Broad self-assessments such as "proficient in Python" and future plans such as "want to learn Docker" do not earn credit.

The overall match score is calculated as:

`match_score = 100 × sum(weight × skill_score) / sum(weight)`

The priority of each skill gap is:

`priority = weight × (1 − skill_score)`

The score is deterministic and does not depend on an LLM generating the result. Role definitions, skill weights, and aliases influence the outcome and should be reviewed before production use.

## RAG Knowledge Base

The project includes a Retrieval-Augmented Generation pipeline for searching technical resources and training-course information.

### Architecture

1. **Document discovery and loading:** Read supported source files.
2. **Text chunking:** Split documents into overlapping chunks.
3. **Embedding generation:** Convert chunks and queries into vectors.
4. **Persistent indexing:** Store vectors and metadata in ChromaDB.
5. **Semantic retrieval:** Retrieve relevant passages for a question.
6. **Answer generation:** Send the question and retrieved evidence to the configured LLM.
7. **Source citations:** Return references to the retrieved documents.

### Supported Knowledge-Base Formats

The document loader supports:

- PDF
- DOCX
- TXT
- Markdown (`.md`)

Raw HTML pages are not directly indexed by the document loader. Web-scraping scripts convert selected web content into Markdown before ingestion.

### Current Knowledge Sources

The knowledge base includes:

- Original technical learning notes covering networking, network security, Linux, Windows Server, automation, virtualization, cloud networking, backup and recovery, monitoring, and troubleshooting.
- Cisco Networking Academy learning resources.
- Selected Microsoft Windows Server and PowerShell documentation.
- Ansible playbook and inventory guides.
- Fast Lane MENA training-course pages.
- Global Knowledge training-course pages.
- **Curated certifications and programmes** (`data/knowledge_base/curated/`):
  - `curated/global/` — international certifications and online programmes (Microsoft, AWS, Google, Cisco, CompTIA, Red Hat, Linux Foundation, Kaggle, freeCodeCamp and others), plus learning-resource files for the Data Analyst, Backend Developer, Database Administrator and Systems Administrator roles.
  - `curated/egypt/` — Egyptian programmes and scholarships (DEPI, NTI, ITI, Mahara-Tech and others), including who can join.

Each curated entry lists the type, provider, region, cost, level, what it covers, the skills it teaches and its official source page with the date it was checked.

The scraped course catalog contains individual Markdown course records, including available course codes, durations, descriptions, prerequisites, objectives, course content, and pricing information. Fields vary by source page.

Course schedules, prices, availability, and certification requirements may change. Verify them against the provider's current course page before making purchasing or certification decisions.

### RAG API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /rag/ask` | Retrieve supporting passages and generate a grounded answer |
| `GET /rag/stats` | Report the collection name, indexed chunk count, and persistence directory |
| `POST /rag/ingest` | Ingest the configured knowledge base (can take several minutes; the server is busy until it finishes) |

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/rag/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Recommend relevant networking and backup training courses.\",\"top_k\":6}"
```

The response includes the question, generated answer, citations, and LLM status.

**Important:** `/rag/ingest` processes the configured knowledge base. For incremental ingestion of a specific folder, use the pipeline's `ingest_directory()` method with that folder as the argument rather than invoking the full ingestion endpoint.

### Embedding Model

The RAG index uses the model set in `EMBEDDING_MODEL`. The recommended value is the multilingual model, which supports Arabic and English questions:

```dotenv
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

If `EMBEDDING_MODEL` is not set, the code falls back to the English-only `sentence-transformers/all-MiniLM-L6-v2`.

### Persistent Index and Safe Ingestion

The default ChromaDB directory is:

```text
data/chroma_db/
```

The collection name is:

```text
cv_knowledge
```

The vector store uses persistent storage and stable chunk identifiers. Re-ingesting documents can update existing records and add new records.

- Preserve `data/chroma_db/` when continuing development.
- Do not delete or recreate the collection merely to add new documents.
- **Rebuild the index from scratch** in two cases: when you change `EMBEDDING_MODEL` (vectors from different models cannot be mixed), and when you delete or rename source files (ingestion adds and updates records but does not remove chunks of deleted files). To rebuild: stop the server, rename or delete `data/chroma_db/`, start the server, then call `POST /rag/ingest`.
- Ingest only the intended folder when working with a new source.
- Back up the index before making destructive changes.
- Avoid duplicate or navigation-heavy pages that add little learning value.

### Current Retrieval Limitations

Semantic similarity does not guarantee that a retrieved passage belongs to the exact course being discussed. Related courses may mention one another in prerequisite sections.

The answer-generation prompt instructs the LLM to cite evidence and avoid unsupported claims, but prompt instructions alone cannot guarantee correct retrieval or citation quality. Validate course-specific answers against the cited source files, especially when comparing similarly named courses.

## Web Scraping and Course Catalog Collection

The project includes scripts for collecting selected training information from provider websites.

| Script | Purpose |
|---|---|
| `scrape_cisco_netacad.py` | Collect selected Cisco Networking Academy learning resources |
| `scrape_multi_source.py` | Collect selected Microsoft and Ansible resources |
| `scrape_fastlane.py` | Collect Fast Lane MENA landing-page and catalog information |
| `scrape_fastlane_courses.py` | Collect individual Fast Lane course pages |
| `scrape_globalknowledge_courses.py` | Discover and collect Global Knowledge course pages |

Scraped records are saved as Markdown under:

```text
data/knowledge_base/technical_resources/
```

Examples of source-specific folders include:

```text
data/knowledge_base/technical_resources/cisco_netacad/
data/knowledge_base/technical_resources/multi_source/
data/knowledge_base/technical_resources/fastlane/
data/knowledge_base/technical_resources/globalknowledge/
```

The scripts and folder names may evolve as new providers are added.

Before running a scraper at scale:

- Respect the provider's terms of service, robots rules, and applicable copyright requirements.
- Prefer official APIs or explicitly permitted content sources.
- Use reasonable request rates and handle failed pages.
- Store source URLs and retrieval timestamps where possible.
- Review scraped content before ingestion.
- Do not treat a successful scrape as proof that a course is currently available.

Scraped course information is a reference dataset, not a substitute for the provider's live catalog.

## Optional LLM Configuration

Copy `.env.example` to `.env` and configure the OpenAI-compatible endpoint:

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_chat_completions_base_url
OPENAI_MODEL=your_model_name
LLM_TIMEOUT_SECONDS=35
```

Use the exact base URL expected by your provider. The application sends requests to the chat-completions endpoint.

The project is tested with **Groq** (free tier):

```dotenv
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=openai/gpt-oss-120b
```

Run `2_check_key.bat` (or `python check_key.py`) to confirm the key and model work. Never share your API key or commit `.env`.

When the provider is busy (HTTP 429 or 5xx), the request is retried up to two times, waiting 2 then 4 seconds (or the provider's `Retry-After`, at most 10 seconds). Other errors are not retried.

When enabled, candidate CV text may be sent to the configured provider. Obtain informed candidate consent and update the privacy notice before enabling external processing.

LLM extraction is restricted to known skill IDs, and skills without supporting evidence in the CV are discarded.

## Optional Semantic Matching

Install the semantic dependencies:

```powershell
python -m pip install -r requirements-semantic.txt
```

Set the following options in `.env` as appropriate:

```dotenv
ENABLE_EMBEDDING_MATCHING=true
EMBEDDING_PARTIAL_THRESHOLD=0.58
```

The first run may download the configured sentence-transformer model. On Windows, if drive C: is short on space, set `HF_HOME` to a folder on another drive (for example `setx HF_HOME D:\hf_cache`) before the first run.

Semantic matching can add partial credit but cannot independently turn a semantic similarity into a full skill match. Supporting CV evidence should be displayed for semantic matches.

The RAG pipeline also uses the embedding model to retrieve knowledge-base passages. Model availability and the installed semantic dependencies are therefore relevant to RAG operation.

## Optional Live Job and Course Discovery

### Jobs

Configure either provider:

- **SerpAPI:** Set `SERPAPI_API_KEY` for supported Google Jobs searches.
- **Adzuna:** Set `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, and the appropriate `ADZUNA_COUNTRY`.

### Courses

Set `SERPAPI_API_KEY` to use Google Search results through SerpAPI where supported.

Live discovery is separate from the curated and scraped course knowledge base. Verify course information and availability before adding results to a production catalog.

The dashboard's **Live job and course discovery** section and the `/discover/jobs` and `/discover/courses` endpoints expose these integrations. Missing provider credentials should not prevent the core CV analysis workflow from operating.

## Project Structure

```text
backend/
  main.py                    FastAPI endpoints and the website (/ and /static)
  schemas.py                 Pydantic API contracts
  cv_parser.py               PDF/DOCX/TXT extraction and upload rules (English only, 10 MB)
  extractor.py               Deterministic fallback extraction
  llm_extractor.py           Optional structured LLM extraction
  llm_client.py              LLM requests with retry when the provider is busy
  embedding_matcher.py       Optional local semantic matching
  live_sources.py            Optional jobs/courses provider APIs
  skill_engine.py             Alias normalization and gap scoring
  recommender.py              Catalog-backed recommendations
  storage.py                  SQLite request metadata and catalog helpers
  rag/
    answerer.py               Grounded LLM answer generation
    retriever.py              Retrieved-chunk interface
    pipeline.py               Ingestion and retrieval pipeline
    vector_store.py            Persistent ChromaDB vector store
    document_loader.py         Supported document loading
    chunker.py                 Text chunking
    embeddings.py              Embedding model integration

web/
  index.html                  Website page
  style.css                   Website styles
  app.js                      Website logic and Arabic/English texts

frontend/
  app.py                      Streamlit dashboard (optional, older interface)
  translations.py             Streamlit Arabic/English texts

contracts/
  candidate_profile.json
  job_profile.json
  gap_report.json

data/
  roles.json                  Target-role definitions
  catalog.json                Curated starter catalog
  knowledge_base/
    technical_resources/      Technical notes and scraped resources
    curated/global/           International certifications and learning resources
    curated/egypt/            Egyptian programmes and scholarships
    Career_Resources/, Certifications/, Courses/  Additional source documents
  chroma_db/                  Persistent ChromaDB index

tests/
  test_engine.py              Extraction, scoring and recommendations
  test_listed_skills.py       Partial credit for listed-only skills
  test_cv_upload.py           Upload rules and error codes
  test_llm_client.py          Retry behaviour
  test_rag.py                 RAG pipeline
  test_rag_answerer.py        Grounded answers and citations

scrape_cisco_netacad.py
scrape_multi_source.py
scrape_fastlane.py
scrape_fastlane_courses.py
scrape_globalknowledge_courses.py

sample_cv.txt
requirements.txt
requirements-semantic.txt
requirements-rag.txt
.env.example
check_key.py                  Checks the LLM key and model
1_setup.bat ... 5_run_tests.bat  Windows helper scripts
```

Some paths and optional modules may vary by project version. Keep the structure section synchronized with the actual repository when adding or renaming files.

## Privacy and Limitations

- Uploaded CV text is processed in memory by the application and is not intentionally stored as CV content in the SQLite request-metadata database.
- SQLite stores request metadata such as request ID, role, score, and timestamp.
- External LLM providers may receive CV text when LLM extraction is enabled.
- The RAG index persists ingested document content and metadata in ChromaDB. Do not ingest confidential CVs or sensitive documents without an appropriate data-handling policy.
- The system is a demonstrator, not a hiring decision system.
- Match scores depend on role profiles, weights, aliases, and the quality of extracted CV text.
- Scanned or image-only PDFs require OCR, which is not included in this MVP.
- Only English CVs are analysed. Skill evidence is detected from English wording.
- Scraped information may be incomplete, stale, or affected by changes to source websites.
- Generated answers can contain errors. Validate important recommendations against their cited sources.

## Recent Project Improvements

- Added Windows Server and Backup & Recovery catalog entries to cover gaps identified in the Systems Administrator example.
- Added Windows Server lab and backup/restore project ideas.
- Added a regression test confirming that these gaps can generate relevant recommendations.
- Added technical knowledge notes and official learning-resource extracts.
- Added Cisco Networking Academy course resources.
- Collected and ingested individual Fast Lane MENA course pages.
- Collected and ingested Global Knowledge course pages.
- Added persistent ChromaDB-based RAG retrieval and source-cited answer generation.
- Improved answer-generation instructions to emphasize source grounding, requested fields, and clear formatting.
- Started refining course-specific retrieval to reduce confusion between related courses.
- Added a bilingual (Arabic/English) website served by FastAPI, replacing Streamlit as the main interface.
- Switched the LLM configuration to Groq (`openai/gpt-oss-120b`) and added automatic retries when the provider is busy.
- Switched RAG to a multilingual embedding model so Arabic questions retrieve relevant sources, and load the model at server start.
- Added curated international certifications and Egyptian programmes, plus learning resources for the Data Analyst, Backend Developer, Database Administrator and Systems Administrator roles.
- Removed duplicate scraped files from the knowledge base.
- Added CV upload rules (English only, PDF/DOCX/TXT, 10 MB) with error codes, and translated warnings with `warning_codes`.
- Added partial credit (0.25) for skills that are only listed in the CV.
- The assistant receives the analysis results as separate `context`, answers in Modern Standard Arabic when the site is in Arabic, and shows clickable citations grouped by source file.
- Damaged PDF or Word files now return a clear error instead of a server error.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

or run `5_run_tests.bat`. All tests run offline and do not call the LLM.

The knowledge base and RAG retrieval logic continue to evolve. Confirm the current code and test results before describing any experimental retrieval enhancement as production-ready.

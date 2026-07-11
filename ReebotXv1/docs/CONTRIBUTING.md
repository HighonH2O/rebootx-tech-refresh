# Contributing — RebootX

> Team workflow, responsibilities, Git conventions, and development guidelines.

---

## Team Structure

RebootX is built by a 4-person team. Each person owns a specific domain but all collaborate on integration and testing.

```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│  Person A   │  │  Person B   │  │  Person C   │  │  Person D   │
│  Data & RAG │  │ Backend &   │  │    LLM      │  │  Rules &    │
│             │  │    API      │  │  Reasoning  │  │   Domain    │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │                │                │                │
      ▼                ▼                ▼                ▼
┌──────────┐   ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Collect   │   │ FastAPI   │    │ Prompt    │    │ Risk      │
│ corpus    │   │ setup     │    │ design    │    │ taxonomy  │
│ (release  │   │ (input    │    │ (risk     │    │ (risk     │
│  notes)   │   │  schema)  │    │  template)│    │ categories│
└─────┬─────┘   └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
      │                │                │                │
      ▼                ▼                ▼                ▼
┌──────────┐   ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Chunk &   │   │ Streamlit │    │ Ollama    │    │ Rating   │
│ embed     │   │ UI        │    │ setup     │    │ rules    │
│ (nomic)   │   │ (form)    │    │ (local    │    │ (Low to  │
│           │   │           │    │  Llama 3) │    │ Critical)│
└─────┬─────┘   └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
      │                │                │                │
      ▼                ▼                ▼                ▼
┌──────────┐   ┌──────────┐    ┌──────────┐    ┌──────────┐
│ ChromaDB  │   │ Report    │    │ RAG-LLM   │    │ Check    │
│ index     │   │ builder   │    │ wiring    │    │ mapper   │
│ (store)   │   │(weasyprint│    │ (context  │    │ (risk →  │
│           │   │  / PDF)   │    │  inject)  │    │  check)  │
└───────────┘   └───────────┘    └───────────┘    └───────────┘
```

---

## Person Responsibilities

### Person A — Data and RAG

**Owns:** Knowledge corpus, embedding pipeline, ChromaDB index

| Task | Deliverable | Status |
|------|------------|--------|
| Collect release notes & changelogs for pilot technologies | `app/knowledge/corpus/` populated | ⬜ |
| Design chunking strategy (~500 tokens, section-aware splits) | `scripts/seed_corpus.py` | ⬜ |
| Set up `nomic-embed-text` embeddings via Ollama | `app/services/rag_service.py` | ⬜ |
| Build ChromaDB index with metadata filtering | ChromaDB persistent store | ⬜ |
| Implement retrieval function (top-K, score threshold) | `retrieve_context()` | ⬜ |
| Test retrieval quality against sample scenarios | Retrieval eval results | ⬜ |

---

### Person B — Backend and API

**Owns:** FastAPI app, Streamlit frontend, report generation

| Task | Deliverable | Status |
|------|------------|--------|
| Set up FastAPI project structure with Pydantic schemas | `app/main.py`, `app/models/` | ⬜ |
| Implement `POST /assess` and `GET /health` endpoints | `app/api/routes/` | ⬜ |
| Build Streamlit capture form (tech type, versions, deps) | `frontend/app.py` | ⬜ |
| Implement report generation (HTML + PDF via weasyprint) | `app/services/report_service.py` | ⬜ |
| Wire up all services into the assessment pipeline | End-to-end API flow | ⬜ |
| Set up error handling and validation | FastAPI exception handlers | ⬜ |

---

### Person C — LLM Reasoning

**Owns:** Prompt engineering, Ollama setup, RAG-LLM integration

| Task | Deliverable | Status |
|------|------------|--------|
| Install and configure Ollama with Llama 3 | Working `ollama run llama3` | ⬜ |
| Design the risk analysis prompt template | `app/services/llm_service.py` | ⬜ |
| Implement structured JSON output parsing | Response parser + validation | ⬜ |
| Wire RAG context injection into LLM prompts | Context → Prompt pipeline | ⬜ |
| Tune temperature and prompt parameters | Consistent, deterministic output | ⬜ |
| Handle LLM failures and retries | Retry logic with fallback prompt | ⬜ |

---

### Person D — Rules and Domain

**Owns:** Risk taxonomy, rating rules, validation check mapping

| Task | Deliverable | Status |
|------|------------|--------|
| Define risk categories and severity heuristics | `docs/RISK_TAXONOMY.md` | ⬜ |
| Implement risk scoring algorithm | `app/services/risk_engine.py` | ⬜ |
| Build risk-to-check mapping table | Check mapper logic | ⬜ |
| Define validation check types and priority rules | Check assignment rules | ⬜ |
| Implement overall risk calculation (weighted scoring) | `calculate_overall_risk()` | ⬜ |
| Create verdict logic (Go / Caution / No-Go) | Verdict generator | ⬜ |

---

## Development Workflow

### Branch Strategy

```
main
 ├── dev                         ← integration branch
 │    ├── feature/rag-pipeline   ← Person A
 │    ├── feature/fastapi-setup  ← Person B
 │    ├── feature/llm-prompts    ← Person C
 │    └── feature/risk-rules     ← Person D
 │
 └── release/v0.1                ← demo-ready milestone
```

### Branch Naming Convention

```
feature/<short-description>    — new feature work
fix/<short-description>        — bug fixes
docs/<short-description>       — documentation updates
refactor/<short-description>   — code cleanup
```

### Commit Message Format

```
<type>(<scope>): <description>

Examples:
feat(rag): implement ChromaDB indexing with metadata filtering
feat(api): add POST /assess endpoint with Pydantic validation
fix(llm): handle JSON parse errors in Llama 3 response
docs(risk): add severity heuristics for deprecated API category
refactor(report): extract PDF styling into template file
```

---

## Integration Points

Teams need to coordinate at these integration boundaries:

| From → To | Interface | Contract |
|-----------|-----------|----------|
| Person A → Person C | `retrieve_context()` returns `list[dict]` | Each dict has `text`, `source`, `section`, `relevance_score` |
| Person C → Person D | LLM returns structured JSON | JSON matches `Risk` and `ValidationCheck` Pydantic schemas |
| Person D → Person B | Risk engine returns `AssessmentResponse` | Fully populated response object |
| Person B → Person A | Seed script callable from API | `seed_corpus.py` can be run independently |

### Integration Schedule

| Milestone | When | What |
|-----------|------|------|
| Interface agreement | End of Week 1 | All teams agree on data contracts (Pydantic schemas) |
| Vertical slice | Mid Week 2 | One scenario works end-to-end (even with stubs) |
| Full integration | End of Week 2 | All modules connected and tested |
| Demo ready | Week 3 | 2+ scenarios working, report generation, UI polished |

---

## Code of Conduct

- Maintain ethical behaviour and inclusive communication
- Respect others' ideas, time, and effort
- Avoid the use of proprietary data or unauthorised tools
- Adhere to the Tata code of conduct in its entirety

---

## Development Guidelines

### Code Quality

- Use Python type hints throughout
- Write docstrings for all public functions
- Run `ruff` or `flake8` for linting
- Format code with `black`
- Keep functions under 50 lines where possible

### Testing

- Write unit tests for risk engine and check mapper logic
- Write integration tests for the assessment pipeline
- Use the sample scenarios as test fixtures
- Aim for > 70% test coverage on core services

### Documentation

- Keep docs up to date as code changes
- Add inline comments for non-obvious logic
- Update `RISK_TAXONOMY.md` when adding new risk categories
- Update `API_SPEC.md` when changing endpoints

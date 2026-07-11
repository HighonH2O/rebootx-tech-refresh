# Project Plan — RebootX

> Timeline, milestones, task breakdown, and delivery schedule for the 2–4 week prototype.

---

## Timeline Overview

```
Week 1                    Week 2                    Week 3                    Week 4
├─────────────────────────┼─────────────────────────┼─────────────────────────┼──────────────┤
│  Foundation & Setup     │  Core Implementation    │  Integration & Testing  │  Demo & Docs │
│                         │                         │                         │              │
│  • Project scaffold     │  • RAG pipeline         │  • End-to-end wiring    │  • Polish UI │
│  • Ollama + models      │  • LLM prompts          │  • 2+ scenarios tested  │  • README    │
│  • Corpus collection    │  • Risk engine          │  • Report generation    │  • Demo prep │
│  • Schema design        │  • FastAPI endpoints    │  • Bug fixes            │  • Present   │
└─────────────────────────┴─────────────────────────┴─────────────────────────┴──────────────┘
```

---

## Phase 1: Foundation & Setup (Week 1)

### Goals
- Project structure in place
- Dev environment working for all team members
- Core data contracts (schemas) agreed upon
- Initial corpus collected

### Tasks

| # | Task | Owner | Priority | Est. Hours | Status |
|---|------|-------|----------|-----------|--------|
| 1.1 | Set up Git repo and project structure | Person B | P0 | 2h | ⬜ |
| 1.2 | Create documentation (.md files) | All | P0 | 4h | 🔲 |
| 1.3 | Install & verify Ollama + Llama 3 + nomic-embed-text | Person C | P0 | 2h | ⬜ |
| 1.4 | Define Pydantic schemas (request/response) | Person B | P0 | 3h | ⬜ |
| 1.5 | Define risk taxonomy and severity rules | Person D | P0 | 4h | ⬜ |
| 1.6 | Collect release notes for PostgreSQL 12→16 | Person A | P0 | 4h | ⬜ |
| 1.7 | Collect release notes for Python 3.8→3.12 | Person A | P0 | 4h | ⬜ |
| 1.8 | Design chunking strategy and test | Person A | P1 | 3h | ⬜ |
| 1.9 | Set up FastAPI skeleton with health endpoint | Person B | P1 | 2h | ⬜ |
| 1.10 | Draft initial prompt template | Person C | P1 | 3h | ⬜ |

### Milestone: ✅ **Foundation Complete**
- All team members can run the project locally
- Schemas are agreed upon and documented
- Ollama responds to API calls
- Initial corpus files exist in `app/knowledge/corpus/`

---

## Phase 2: Core Implementation (Week 2)

### Goals
- Each team member's core module is functional independently
- Modules can be tested in isolation with mock data

### Tasks

| # | Task | Owner | Priority | Est. Hours | Status |
|---|------|-------|----------|-----------|--------|
| 2.1 | Implement `seed_corpus.py` (chunk + embed + store) | Person A | P0 | 6h | ⬜ |
| 2.2 | Implement `retrieve_context()` with ChromaDB | Person A | P0 | 4h | ⬜ |
| 2.3 | Implement `POST /assess` endpoint | Person B | P0 | 4h | ⬜ |
| 2.4 | Build Streamlit input form | Person B | P0 | 4h | ⬜ |
| 2.5 | Implement LLM service with Ollama client | Person C | P0 | 6h | ⬜ |
| 2.6 | Design & iterate on risk analysis prompt | Person C | P0 | 6h | ⬜ |
| 2.7 | Implement JSON response parser + validation | Person C | P0 | 3h | ⬜ |
| 2.8 | Implement risk scoring algorithm | Person D | P0 | 4h | ⬜ |
| 2.9 | Implement check mapper (risk → validation checks) | Person D | P0 | 4h | ⬜ |
| 2.10 | Implement overall risk calculator + verdict | Person D | P0 | 3h | ⬜ |
| 2.11 | Collect MWAA / EMR corpus documents | Person A | P1 | 4h | ⬜ |
| 2.12 | Start report template (HTML) | Person B | P1 | 3h | ⬜ |

### Milestone: ✅ **Modules Functional**
- RAG retrieves relevant documents for test queries
- LLM produces structured risk JSON from a hardcoded prompt
- Risk engine scores and classifies sample risk data
- API accepts requests and returns stub responses

---

## Phase 3: Integration & Testing (Week 3)

### Goals
- All modules wired together into end-to-end pipeline
- Minimum 2 sample scenarios pass end-to-end
- Report generation works (PDF + HTML)

### Tasks

| # | Task | Owner | Priority | Est. Hours | Status |
|---|------|-------|----------|-----------|--------|
| 3.1 | Wire RAG → LLM → Risk Engine → Report | All | P0 | 8h | ⬜ |
| 3.2 | Test Scenario 1: PostgreSQL 12.4 → 16.2 | All | P0 | 4h | ⬜ |
| 3.3 | Test Scenario 2: Python 3.8 → 3.12 | All | P0 | 4h | ⬜ |
| 3.4 | Implement PDF report generation (weasyprint) | Person B | P0 | 4h | ⬜ |
| 3.5 | Build Streamlit results display | Person B | P0 | 3h | ⬜ |
| 3.6 | Fix integration bugs | All | P0 | 6h | ⬜ |
| 3.7 | Add error handling and edge cases | Person B | P1 | 3h | ⬜ |
| 3.8 | Tune retrieval parameters (top-K, threshold) | Person A | P1 | 3h | ⬜ |
| 3.9 | Tune prompt for consistent JSON output | Person C | P1 | 3h | ⬜ |
| 3.10 | Write unit tests for risk engine | Person D | P1 | 3h | ⬜ |
| 3.11 | (Optional) Test Scenario 3: MWAA 2.4 → 2.8 | All | P2 | 3h | ⬜ |

### Milestone: ✅ **End-to-End Working**
- 2 scenarios produce correct readiness reports
- API returns structured JSON with all fields populated
- Reports can be downloaded as PDF
- No critical bugs in the pipeline

---

## Phase 4: Demo Prep & Documentation (Week 4)

### Goals
- Polished UI for demonstration
- Complete documentation
- Demo script prepared and rehearsed

### Tasks

| # | Task | Owner | Priority | Est. Hours | Status |
|---|------|-------|----------|-----------|--------|
| 4.1 | Polish Streamlit UI (styling, loading states) | Person B | P0 | 4h | ⬜ |
| 4.2 | Complete README with setup instructions | All | P0 | 2h | ⬜ |
| 4.3 | Prepare demo script (walkthrough) | All | P0 | 3h | ⬜ |
| 4.4 | Record demo video (backup) | Person B | P1 | 2h | ⬜ |
| 4.5 | Final testing with fresh setup | All | P0 | 2h | ⬜ |
| 4.6 | Code cleanup and comments | All | P1 | 3h | ⬜ |
| 4.7 | Prepare presentation slides | All | P1 | 4h | ⬜ |

### Milestone: ✅ **Demo Ready**
- Live demo works end-to-end without errors
- Documentation is complete and accurate
- Presentation slides cover architecture, approach, and results

---

## Risk Register (Project Risks)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Ollama/Llama 3 too slow on team machines | Medium | High | Use smaller model (Llama 3 8B), reduce context window |
| LLM produces inconsistent JSON | High | Medium | Strict prompt template, JSON parser with retry logic |
| Insufficient corpus for accurate retrieval | Medium | High | Prioritise PostgreSQL + Python scenarios; quality over quantity |
| ChromaDB performance with large corpus | Low | Medium | Keep corpus focused on pilot technologies |
| Team coordination / merge conflicts | Medium | Medium | Clear module boundaries, daily standups, early integration |
| Weasyprint installation issues on Windows | Medium | Low | Fallback to HTML-only reports; use reportlab as alternative |

---

## Definition of Done

A task is considered **done** when:

1. ✅ Code is written, tested, and committed
2. ✅ Code passes linting (ruff/flake8) and formatting (black)
3. ✅ Relevant documentation is updated
4. ✅ At least one team member has reviewed the changes
5. ✅ Feature works end-to-end with the sample scenarios

---

## Key Dates

| Date | Milestone |
|------|-----------|
| End of Week 1 | Foundation complete, schemas agreed |
| Mid Week 2 | First vertical slice (one scenario, even with stubs) |
| End of Week 2 | All core modules functional in isolation |
| End of Week 3 | 2+ scenarios working end-to-end |
| End of Week 4 | Demo ready, documentation complete |

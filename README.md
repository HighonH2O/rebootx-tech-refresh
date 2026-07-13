# RebootX – AI Driven Tech Refresh Engine

**Pilot Prototype | Preliminary Presentation Document**

---

## Executive Summary

**RebootX** is an automated compatibility validation framework designed to proactively verify interoperability for any technical upgrade or refresh. The goal is to reduce manual testing effort, shorten the time required to identify integration risks, and eventually reduce reliance on Subject Matter Experts (SMEs).

This repository contains the **2–4 week pilot prototype** scoped to four upgrade domains:

- Database upgrades
- EMR (Elastic MapReduce) upgrades
- Python runtime upgrades
- MWAA (Managed Workflows for Apache Airflow) upgrades

The prototype demonstrates automated compatibility assessment, integration risk identification, and AI-generated impact reports to support enterprise technology refresh decisions.

---

## The Problem We Are Solving

### Current State (Before RebootX)

| Challenge | Impact |
|---|---|
| Manual compatibility review | Days to weeks per upgrade assessment |
| Tribal knowledge / SME dependency | Bottleneck on a few senior experts |
| Late discovery of integration risks | Failed upgrades, rollbacks, production incidents |
| Inconsistent assessment quality | Outcome depends on who was asked |
| Fragmented documentation | Release notes, runbooks, and configs scattered across systems |

### Desired Future State (After RebootX)

| Outcome | Benefit |
|---|---|
| Automated risk assessment in minutes | Faster change approval cycles |
| Evidence-backed risk ratings | Consistent, repeatable decisions |
| AI-generated explanations | SME knowledge captured and scaled |
| Proactive integration risk detection | Issues found before production |
| Structured impact reports | Ready for CAB / change governance |

### One-Line Vision

> **A proposed technical upgrade is assessed in minutes — with evidence — showing whether it is safe, what may break, and what to do about it, without requiring an expert for every review.**

---

## Pilot Scope

### In Scope (This Prototype)

| Domain | Example Upgrade |
|---|---|
| **Database** | PostgreSQL 13 → 15 |
| **EMR** | Amazon EMR 6.10 → 7.0 |
| **Python** | Python 3.9 → 3.12 |
| **MWAA** | Amazon MWAA 2.x → 3.x |

### Out of Scope (Future Phases)

- Full CMDB / enterprise inventory integration
- Automated CI/CD pipeline gates
- Hardware refresh validation
- Production deployment automation
- Multi-tenant enterprise SSO

---

## Expected Outcomes (Pilot Deliverables)

The prototype must deliver four core capabilities:

| # | Capability | Expected Output |
|---|---|---|
| 1 | **Capture upgrade input** | Accept current version, target version, technology type, dependencies, and integrations |
| 2 | **Analyse compatibility** | Identify risks across dependencies, versions, configurations, and integrations |
| 3 | **Generate risk rating** | Assign **Low / Medium / High / Critical** overall risk |
| 4 | **Explain risks** | Provide clear, AI-generated reasoning for each identified risk |

### Sample Output Structure

```json
{
  "technology_type": "python",
  "current_version": "Python 3.9",
  "target_version": "Python 3.12",
  "overall_risk": "High",
  "summary": "Major Python runtime upgrade with dependency and integration impact.",
  "risks": [
    {
      "category": "dependency",
      "risk_level": "High",
      "title": "Dependency compatibility review required",
      "explanation": "Legacy packages may not support Python 3.12.",
      "recommendation": "Regenerate lock files and validate each dependency."
    }
  ],
  "recommended_actions": [
    "Validate upgrade path in staging",
    "Run full regression suite",
    "Prepare rollback plan"
  ],
  "confidence": "Medium",
  "analysis_mode": "ai"
}
```

---

## Solution Architecture

### High-Level Flow

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   User /    │     │   FastAPI        │     │  ChromaDB       │     │  Ollama          │
│   API Call  │────▶│   /assess-upgrade│────▶│  (RAG Retrieval)│────▶│  Llama 3         │
└─────────────┘     └──────────────────┘     └─────────────────┘     └──────────────────┘
                            │                         │                        │
                            │                         ▼                        ▼
                            │                  Release notes,           Risk rating +
                            │                  runbooks, CVEs,            explanations +
                            ▼                  compatibility docs         impact report
                     Structured JSON Response
                     (Low/Medium/High/Critical)
```

### Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend API** | Python + FastAPI | REST API, input validation, orchestration |
| **Vector Store** | ChromaDB | Store and retrieve compatibility knowledge (RAG) |
| **Local LLM** | Ollama + Llama 3 | AI reasoning, risk explanation (data stays on-prem) |
| **Development** | VS Code + GitHub Copilot | Accelerated development for pilot team |

### Why Local LLM (Ollama)?

- **Security**: Sensitive infrastructure data never leaves the machine
- **Compliance**: Suitable for enterprise / air-gapped environments
- **Cost**: No per-token API charges during development
- **Fallback**: Rules-based assessment runs even when Ollama is unavailable

---

## Project Structure

```
rebootx/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Environment configuration
│   ├── models/
│   │   └── schemas.py          # Request/response data models
│   ├── services/
│   │   ├── assessment_service.py   # Core assessment orchestration
│   │   ├── knowledge_service.py    # ChromaDB RAG retrieval
│   │   └── ollama_service.py       # Local LLM integration
│   └── data/
│       └── knowledge_loader.py     # Seed compatibility knowledge
├── data/
│   └── chroma/                 # ChromaDB persistence (auto-created)
├── samples/
│   └── example_requests.json   # Demo payloads for the meeting
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+ (tested on 3.12)
- pip
- *(Optional but recommended)* [Ollama](https://ollama.com/) with Llama 3 model

### 1. Clone / Open Project

```bash
cd "C:\Coding Practice\rebootx"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

```bash
copy .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3` | Model name |
| `USE_OLLAMA` | `true` | Enable AI analysis (falls back to rules if unavailable) |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | Vector store location |

### 5. Install Ollama + Llama 3 (Optional)

```bash
# Install Ollama from https://ollama.com/download
ollama pull llama3
ollama serve
```

> **Note:** The app works without Ollama using a rules-based fallback. AI mode activates automatically when Ollama is detected.

### 6. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Open API Documentation

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

---

## Demo Guide (For Today's Meeting)

### Step 1: Verify System Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "app_name": "RebootX",
  "version": "0.1.0",
  "ollama_available": true,
  "knowledge_documents": 8
}
```

### Step 2: Assess a Python Upgrade

```bash
curl -X POST http://localhost:8000/api/v1/assess-upgrade ^
  -H "Content-Type: application/json" ^
  -d "{\"technology_type\":\"python\",\"current_version\":\"Python 3.9\",\"target_version\":\"Python 3.12\",\"dependencies\":[\"numpy==1.21\",\"pandas==1.3\"],\"integrations\":[\"Airflow DAGs\",\"EMR Spark jobs\"],\"environment\":\"production\"}"
```

### Step 3: Assess an EMR Upgrade

```bash
curl -X POST http://localhost:8000/api/v1/assess-upgrade ^
  -H "Content-Type: application/json" ^
  -d "{\"technology_type\":\"emr\",\"current_version\":\"EMR 6.10\",\"target_version\":\"EMR 7.0\",\"dependencies\":[\"spark-submit scripts\"],\"integrations\":[\"MWAA\",\"S3 data lake\"],\"environment\":\"staging\"}"
```

### Step 4: Walk Through the Response

Highlight these fields during the demo:

1. **`overall_risk`** — Go / Caution / No-Go signal
2. **`risks[]`** — Individual issues with category, level, and explanation
3. **`recommended_actions`** — What the team should do next
4. **`analysis_mode`** — `ai` (Ollama) vs `rules_fallback`
5. **`confidence`** — How much knowledge supported the assessment

---

## API Reference

### `POST /api/v1/assess-upgrade`

Assess compatibility and integration risk for a proposed upgrade.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `technology_type` | enum | Yes | `database`, `emr`, `python`, `mwaa` |
| `current_version` | string | Yes | Current version identifier |
| `target_version` | string | Yes | Target version identifier |
| `dependencies` | string[] | No | Libraries, packages, or components |
| `integrations` | string[] | No | Connected systems or pipelines |
| `environment` | string | No | e.g. `production`, `staging` |
| `notes` | string | No | Additional context |

**Response:** `UpgradeAssessment` with risk rating, explanations, and recommendations.

### `GET /health`

Returns application status, Ollama availability, and knowledge base document count.

### `POST /api/v1/reload-knowledge`

Reloads seed compatibility documents into ChromaDB.

---

## How Assessment Works

### AI Mode (Ollama Available)

1. User submits upgrade request via API
2. System builds a semantic query from the request
3. ChromaDB retrieves relevant compatibility documents (RAG)
4. Llama 3 analyzes the request + retrieved context
5. Structured JSON response with risk rating and explanations

### Rules Fallback Mode (Ollama Unavailable)

1. Same input capture and knowledge retrieval
2. Deterministic rules evaluate version jumps, dependencies, integrations, environment
3. Knowledge base snippets enrich the assessment
4. Structured response with `analysis_mode: "rules_fallback"`

---

## Success Metrics (Pilot → Production)

| Metric | Baseline (Manual) | Pilot Target | Production Target |
|---|---|---|---|
| Time to assess an upgrade | 2–5 days | < 30 minutes | < 5 minutes |
| Manual testing effort | 100% | 60% reduction | 70%+ reduction |
| SME escalations per assessment | ~80% | ~40% | < 20% |
| Integration risks caught pre-deploy | Unknown | Demonstrate capability | 80%+ detection |
| Failed / rolled-back upgrades | Baseline TBD | Track during pilot | Measurable reduction |

---

## 2–4 Week Delivery Plan

| Week | Focus | Deliverables |
|---|---|---|
| **Week 1** | Foundation | FastAPI scaffold, input schema, ChromaDB seed data, Ollama setup |
| **Week 2** | Intelligence | RAG pipeline, prompt engineering, risk rating + explanations |
| **Week 3** | Validation | Test all 4 upgrade types, refine reports, edge case handling |
| **Week 4** | Demo & polish | API docs, demo scripts, stakeholder presentation, feedback loop |

### Current Status

| Item | Status |
|---|---|
| Project scaffold | Done |
| FastAPI API + Swagger docs | Done |
| Input capture (4 technology types) | Done |
| ChromaDB knowledge base (8 seed documents) | Done |
| Ollama / Llama 3 integration | Done |
| Rules-based fallback | Done |
| Risk rating (Low/Medium/High/Critical) | Done |
| AI-generated risk explanations | Done (when Ollama available) |
| Demo-ready README | Done |

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| No historical upgrade outcome data | Start with rules + RAG; collect outcomes during pilot |
| Teams may not trust AI over SMEs | Explainability built into every risk; run in shadow mode first |
| Incomplete / stale inventory data | Accept manual input for pilot; plan CMDB integration later |
| Ollama not installed on demo machine | Rules fallback ensures demo always works |
| Scope creep across all upgrade types | Pilot limited to DB, EMR, Python, MWAA only |

---

## Roadmap Beyond the Pilot

```
Phase 1 (Now)          Phase 2                 Phase 3                  Phase 4
─────────────          ───────                 ───────                  ───────
Working prototype  →   ML risk scoring     →   CI/CD pipeline gate  →   Self-improving
RAG + rules            Historical learning     CMDB integration         enterprise platform
4 upgrade types        NL Q&A interface        Multi-domain expansion   Reduced SME dependency
```

---

## Key Talking Points for Today's Meeting

1. **RebootX addresses a real enterprise pain point** — slow, manual, expert-dependent upgrade assessments.
2. **The pilot is intentionally scoped** — 4 upgrade types, 2–4 weeks, working prototype.
3. **Security-first design** — local LLM (Ollama) keeps sensitive data on-premises.
4. **Four capabilities delivered** — input capture, compatibility analysis, risk rating, risk explanation.
5. **Demo-ready today** — API is functional with seeded knowledge and fallback mode.
6. **Clear path to production** — pilot proves concept; subsequent phases add ML, integrations, and automation.

---

## Team and Tools

| Role | Tool |
|---|---|
| Backend development | Python, FastAPI |
| AI / LLM | Ollama, Llama 3 |
| Knowledge retrieval | ChromaDB (RAG) |
| IDE / AI assistant | VS Code, GitHub Copilot |
| API testing | Swagger UI (`/docs`) |

---

## License

Internal pilot prototype — not for external distribution.

---

## Contact / Next Steps

**Recommended next steps after today's meeting:**

1. Validate pilot scope and success criteria with stakeholders
2. Identify 2–3 real upgrade scenarios for Week 2 testing
3. Confirm Ollama deployment approach for team environments
4. Define baseline metrics for current manual assessment process
5. Assign intern team and begin Week 1 execution

---

*RebootX Pilot Prototype v0.1.0 — Generated for preliminary stakeholder presentation.*

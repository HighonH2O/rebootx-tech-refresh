# RebootX — AI-Driven Tech Refresh Engine

> An AI-assisted compatibility validation framework that accepts technical upgrade details, analyses dependency and integration risks, recommends focused validation checks, and generates a **Tech Refresh Readiness Report**.

---

## 🎯 Overview

Insurance organisations operate complex technology ecosystems. Technology upgrades require manual compatibility validation across applications, middleware, databases and integrations. This process relies heavily on SMEs, architecture documents and spreadsheets.

**RebootX** automates this assessment by combining:

- **RAG (Retrieval-Augmented Generation)** — semantic search over release notes, changelogs and CVE docs
- **Local LLM reasoning** — Ollama + Llama 3 for compatibility and risk analysis
- **Rule-based risk taxonomy** — structured risk categories with Low → Critical severity bands
- **Structured reporting** — JSON API responses + PDF/HTML readiness reports

---

## 🏗️ Architecture (4-Stage Pipeline)

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐    ┌────────────────────────┐
│  STAGE 1         │    │  STAGE 2              │    │  STAGE 3             │    │  STAGE 4                │
│  INPUT LAYER     │───▶│  KNOWLEDGE RETRIEVAL  │───▶│  LLM ANALYSIS        │───▶│  IMPACT REPORT          │
│                  │    │  (RAG)                │    │  ENGINE              │    │  LAYER                  │
├─────────────────┤    ├──────────────────────┤    ├─────────────────────┤    ├────────────────────────┤
│ • Current ver    │    │ • Semantic query      │    │ • Ollama + Llama 3   │    │ • Overall risk rating   │
│ • Target ver     │    │ • ChromaDB search     │    │ • Compatibility      │    │ • Per-risk explanations  │
│ • Tech type      │    │ • Release notes &     │    │   analysis           │    │ • Recommendations       │
│ • Dependencies   │    │   changelogs          │    │ • Dependency risk    │    │ • Structured JSON + API │
│ • Integrations   │    │ • Match runbooks      │    │   detection          │    │ • Swagger UI delivery   │
│ • Environment    │    │   & CVE docs          │    │ • Integration impact │    │                        │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘    └────────────────────────┘
```

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full technical deep-dive.

---

## 🛠️ Tech Stack

| Layer               | Tool                             | Why                                                                 |
|----------------------|----------------------------------|---------------------------------------------------------------------|
| **Backend API**      | FastAPI + Python                 | Async support; handles slow LLM calls well                          |
| **LLM**             | Ollama running Llama 3           | Fully local — no external API calls, satisfies data privacy reqs    |
| **Vector Store**     | ChromaDB                         | Lightweight, embeds well with local models                          |
| **Embeddings**       | `nomic-embed-text` (via Ollama)  | Keeps everything in one local stack                                 |
| **Frontend**         | Streamlit (or plain HTML/JS)     | Speed of development over polish; served by FastAPI                 |
| **Report Output**    | `weasyprint` or `reportlab`      | Turns structured JSON into PDF assessment reports                   |
| **Storage**          | SQLite or JSON files             | Prototype — no need for a full production DB                        |
| **Dev Environment**  | VS Code + AI coding assistant    | Accelerates boilerplate (schemas, routes, tests)                    |

---

## 📂 Project Structure

```
ReebotX1/
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_SPEC.md
│   ├── RISK_TAXONOMY.md
│   ├── RAG_PIPELINE.md
│   ├── CONTRIBUTING.md
│   └── PROJECT_PLAN.md
├── references/                    # Reference materials
│   ├── problem_statement.md
│   └── sample_scenarios.md
├── app/                           # FastAPI application
│   ├── main.py                    # App entry point
│   ├── api/
│   │   └── routes/
│   │       ├── assessment.py      # POST /assess endpoint
│   │       └── health.py          # GET /health
│   ├── core/
│   │   ├── config.py              # Settings & env vars
│   │   └── logging.py
│   ├── models/
│   │   ├── schemas.py             # Pydantic request/response models
│   │   └── enums.py               # TechnologyType, RiskLevel enums
│   ├── services/
│   │   ├── rag_service.py         # ChromaDB retrieval logic
│   │   ├── llm_service.py         # Ollama/Llama 3 integration
│   │   ├── risk_engine.py         # Risk scoring & classification
│   │   └── report_service.py      # PDF/HTML report generation
│   └── knowledge/
│       ├── corpus/                # Release notes, changelogs, CVE docs
│       └── embeddings/            # ChromaDB persistent storage
├── frontend/                      # Streamlit UI
│   └── app.py
├── tests/
│   ├── test_assessment.py
│   └── test_risk_engine.py
├── scripts/
│   ├── seed_corpus.py             # Seed ChromaDB with reference docs
│   └── run_scenarios.py           # Run sample upgrade scenarios
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running
- Llama 3 model pulled: `ollama pull llama3`
- Embedding model pulled: `ollama pull nomic-embed-text`

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd ReebotX1

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment config
cp .env.example .env

# 5. Seed the knowledge corpus
python scripts/seed_corpus.py

# 6. Start the API server
uvicorn app.main:app --reload --port 8000

# 7. (Optional) Start the Streamlit frontend
streamlit run frontend/app.py
```

### API Usage

```bash
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "technology_type": "Database",
    "current_version": "PostgreSQL 12.4",
    "target_version": "PostgreSQL 16.2",
    "dependencies": ["psycopg2", "pgbouncer", "SQLAlchemy"],
    "integrations": ["ETL pipeline", "reporting service", "API gateway"],
    "environment": "Production"
  }'
```

---

## 📊 Output: Tech Refresh Readiness Report

The system produces a structured report containing:

- **Overall Risk Rating** — Low / Medium / High / Critical
- **Risks Found** — count of identified issues
- **Checks Recommended** — suggested validation actions
- **Per-Risk Breakdown** — category, severity, explanation, recommendation

### Risk Levels

| Level      | Colour  | Meaning                                                   |
|------------|---------|-----------------------------------------------------------|
| 🟢 Low     | Green   | Minor or no compatibility issues expected                 |
| 🟡 Medium  | Yellow  | Some changes required; manageable with standard processes |
| 🟠 High    | Orange  | Significant risks; thorough testing and planning needed   |
| 🔴 Critical| Red     | Breaking changes; upgrade may require major rework        |

---

## 👥 Team Responsibilities

| Person     | Focus Area          | Key Tasks                                              |
|------------|---------------------|--------------------------------------------------------|
| **Person A** | Data and RAG        | Collect corpus, chunk & embed, ChromaDB index          |
| **Person B** | Backend and API     | FastAPI setup, Streamlit UI, report builder             |
| **Person C** | LLM Reasoning       | Prompt design, Ollama setup, RAG-LLM wiring            |
| **Person D** | Rules and Domain    | Risk taxonomy, rating rules, check mapper              |

See [`CONTRIBUTING.md`](./docs/CONTRIBUTING.md) for detailed team workflow.

---

## 📄 License

This project is developed as a prototype for internal assessment purposes.

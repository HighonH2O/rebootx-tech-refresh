# Architecture — RebootX

> Detailed system architecture for the AI-Driven Tech Refresh Engine.

---

## High-Level Architecture

RebootX follows a **4-stage pipeline** architecture. Each stage is a decoupled module that can be developed, tested, and replaced independently.

```
┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────────┐
│  STAGE 1 │────▶│    STAGE 2    │────▶│   STAGE 3    │────▶│    STAGE 4     │
│  Input   │     │  Knowledge    │     │  LLM Analysis│     │  Impact Report │
│  Layer   │     │  Retrieval    │     │  Engine      │     │  Layer         │
│          │     │  (RAG)        │     │              │     │                │
└──────────┘     └───────────────┘     └──────────────┘     └────────────────┘
```

---

## Stage 1: Input Layer

**Purpose:** Capture structured upgrade request details from the user.

### Input Schema

```python
class UpgradeRequest(BaseModel):
    technology_type: TechnologyType       # Database | Runtime | MWAA | EMR
    current_version: str                  # e.g., "PostgreSQL 12.4"
    target_version: str                   # e.g., "PostgreSQL 16.2"
    dependencies: list[str]              # e.g., ["psycopg2", "pgbouncer"]
    integrations: list[str]              # e.g., ["ETL pipeline", "API gateway"]
    environment: Environment              # Production | Staging
```

### Entry Points

| Entry Point | Description |
|------------|-------------|
| `POST /assess` | REST API endpoint (FastAPI) |
| Streamlit Form | Web form with dropdowns and text inputs |

### Enumerations

```python
class TechnologyType(str, Enum):
    DATABASE = "Database"
    RUNTIME = "Runtime"
    MWAA = "MWAA"
    EMR = "EMR"

class Environment(str, Enum):
    PRODUCTION = "Production"
    STAGING = "Staging"
```

---

## Stage 2: Knowledge Retrieval Layer (RAG)

**Purpose:** Build a semantic query from the upgrade request and retrieve relevant context from the knowledge corpus.

### Components

```
Upgrade Request
      │
      ▼
┌─────────────────┐
│  Query Builder   │  Construct semantic search query from
│                  │  tech type + versions + dependencies
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ChromaDB        │  Vector similarity search
│  Vector Store    │  over embedded corpus documents
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Context         │  Rank, deduplicate, and format
│  Assembler       │  retrieved chunks for LLM prompt
└─────────────────┘
```

### Knowledge Corpus Sources

| Source Type | Examples | Purpose |
|-----------|----------|---------|
| Release Notes | PostgreSQL 16 release notes, Python 3.12 changelog | Version-specific breaking changes |
| Migration Guides | Official upgrade guides, community migration runbooks | Step-by-step upgrade procedures |
| CVE Databases | NVD entries for specific versions | Security vulnerabilities in current version |
| Compatibility Matrices | Library/driver compatibility tables | Dependency version support |
| Deprecation Notices | Removed features, deprecated APIs | Breaking change identification |

### Embedding Pipeline

1. **Collect** — Gather release notes, changelogs, and CVE docs as raw text/HTML
2. **Chunk** — Split documents into ~500-token chunks with overlap using `langchain` text splitters
3. **Embed** — Generate embeddings via `nomic-embed-text` model through Ollama
4. **Index** — Store in ChromaDB with metadata (source, version, tech type, date)
5. **Retrieve** — Top-K similarity search (k=5–10) filtered by technology type

See [`RAG_PIPELINE.md`](./RAG_PIPELINE.md) for implementation details.

---

## Stage 3: LLM Analysis Engine

**Purpose:** Use a local LLM (Ollama + Llama 3) to analyse the upgrade request with retrieved context and produce structured risk assessments.

### Flow

```
┌─────────────────────────────────────────────────┐
│                 PROMPT TEMPLATE                  │
│                                                  │
│  System: You are a tech upgrade risk analyst...  │
│                                                  │
│  Context: {retrieved_documents}                  │
│                                                  │
│  Request: {upgrade_request_json}                 │
│                                                  │
│  Instructions:                                   │
│  1. Identify compatibility risks                 │
│  2. Rate each risk (Low/Medium/High/Critical)    │
│  3. Explain reasoning                            │
│  4. Recommend validation checks                  │
│  5. Return structured JSON                       │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Ollama API     │
              │  (Llama 3)      │
              │  localhost:11434│
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Response Parser│
              │  JSON extraction│
              │  + validation   │
              └─────────────────┘
```

### Key Design Decisions

- **Fully local** — no external API calls, satisfies data privacy requirements
- **Structured output** — prompt instructs Llama 3 to return JSON; parser validates against Pydantic schema
- **Context injection** — only relevant retrieved documents are sent to the LLM (not the entire corpus)
- **Temperature** — set low (0.1–0.3) for consistent, deterministic assessments
- **Fallback** — if JSON parsing fails, retry with a stricter prompt template

---

## Stage 4: Impact Report Layer

**Purpose:** Transform the structured LLM output into a user-friendly Tech Refresh Readiness Report.

### Report Contents

```
┌────────────────────────────────────────────┐
│         TECH REFRESH READINESS REPORT       │
├────────────────────────────────────────────┤
│                                            │
│  Overall Risk:  🟠 High                    │
│  Risks Found:   6                          │
│  Checks Recommended: 9                     │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  RISK DETAILS                              │
│  ┌────────────────────────────────────┐    │
│  │ R-001: Deprecated API    [Critical]│    │
│  │ Description: ...                   │    │
│  │ Recommendation: ...                │    │
│  └────────────────────────────────────┘    │
│  ...                                       │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  RECOMMENDED VALIDATION CHECKS             │
│  □ Regression: Full test suite on PG 16    │
│  □ Build: Verify psycopg2 compiles...      │
│  □ Integration: Test ETL pipeline...       │
│  ...                                       │
│                                            │
└────────────────────────────────────────────┘
```

### Output Formats

| Format | Delivery | Use Case |
|--------|----------|----------|
| JSON | REST API response | Programmatic consumption |
| HTML | Rendered in Streamlit | Interactive browser viewing |
| PDF | Generated via `weasyprint` | Downloadable report deliverable |

---

## Data Flow (End-to-End)

```
User Input (Streamlit / API)
       │
       ▼
  UpgradeRequest (Pydantic model)
       │
       ▼
  RAG Query Builder
       │
       ▼
  ChromaDB Similarity Search ──── nomic-embed-text (Ollama)
       │
       ▼
  Retrieved Context (top-K chunks)
       │
       ▼
  Prompt Template + Context + Request
       │
       ▼
  Ollama Llama 3 (localhost:11434)
       │
       ▼
  Structured JSON Response
       │
       ▼
  Risk Engine (score + classify)
       │
       ▼
  Report Generator (JSON / HTML / PDF)
       │
       ▼
  Tech Refresh Readiness Report
```

---

## Technology Stack Summary

| Component | Technology | Port/Path |
|-----------|-----------|-----------|
| API Server | FastAPI + Uvicorn | `localhost:8000` |
| LLM Server | Ollama (Llama 3) | `localhost:11434` |
| Vector Store | ChromaDB | Embedded (in-process) or `localhost:8001` |
| Embedding Model | `nomic-embed-text` | Via Ollama API |
| Frontend | Streamlit | `localhost:8501` |
| Storage | SQLite / JSON | `./data/` directory |

---

## Deployment Architecture (Development)

```
┌─────────────────────────────────────────────┐
│              Developer Machine               │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Streamlit │  │ FastAPI  │  │  Ollama   │  │
│  │  :8501    │─▶│  :8000   │─▶│  :11434   │  │
│  └──────────┘  └────┬─────┘  └──────────┘  │
│                     │                        │
│                     ▼                        │
│               ┌──────────┐                   │
│               │ ChromaDB │                   │
│               │(embedded)│                   │
│               └──────────┘                   │
│                                              │
└─────────────────────────────────────────────┘
```

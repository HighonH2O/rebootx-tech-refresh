# RebootX Knowledge Base — Working Guide

> Aligned to the official problem statement: *"Build an AI-assisted compatibility validation engine ... generates a Tech Refresh Readiness Report ... convert manual SME-led compatibility assessment into a reusable, explainable, semi-automated framework."*

This guide is your day-to-day reference for building and refining the knowledge base (KB).

---

## Why the Knowledge Base Is the Core of This Project

The official spec asks us to **convert SME tribal knowledge into a reusable, explainable framework**. The knowledge base *is* that captured SME knowledge. RebootX does not guess — it retrieves relevant KB documents and reasons over them.

**The quality of the KB directly determines the quality of every assessment and every Tech Refresh Readiness Report.** This is the highest-leverage work in the pilot.

---

## How the KB Maps to the Official Capabilities

| Spec Capability | How the KB Supports It |
|---|---|
| Analyse compatibility | KB documents describe dependency / version / config / integration risks |
| Generate risk rating | `risk_hint` guides Low / Medium / High / Critical |
| Explain risks | Document `text` provides the grounded reasoning |
| **Recommend validation checks** | `validation_checks` tags map each risk to focused checks |
| Produce readiness report | Retrieved documents feed the structured report |
| Demonstrate with examples | KB must cover the 2+ sample upgrade scenarios end-to-end |

---

## Data & Sourcing Guidelines

Keep the knowledge base clean, legal, and reusable:

- Use only **public, official sources**: vendor release notes, official docs, public CVE feeds.
- Do **not** paste internal/client architecture documents, credentials, or private runbooks into KB files.
- Cite the public source in the `source` field for every document.
- Our stack (Python, FastAPI, ChromaDB, Ollama/Llama 3) is all open-source and local — no data leaves the machine.

---

## Current State

Run this any time to see where the KB stands:

```powershell
cd "C:\Coding Practice\rebootx"
venv\Scripts\python scripts\ingest_knowledge.py --stats
```

Starting point: **21 documents** across database (5), EMR (5), Python (6), MWAA (5).

---

## Folder Structure

```
rebootx/knowledge/
├── _template.json              ← Copy this when adding docs
├── database/postgresql.json    ← Reference example (fully tagged)
├── emr/emr-upgrades.json
├── python/python-upgrades.json
└── mwaa/mwaa-upgrades.json
```

---

## Document Format

```json
{
  "id": "db-postgres-13-to-15-breaking",
  "text": "3-8 sentences of specific compatibility knowledge with exact versions, breaking changes, and what to verify.",
  "metadata": {
    "technology_type": "database",
    "source": "PostgreSQL 15 Release Notes",
    "topic": "version",
    "version_from": "13",
    "version_to": "15",
    "risk_hint": "High",
    "validation_checks": ["regression", "integration", "rollback"],
    "domain": "insurance"
  }
}
```

### Required Fields

| Field | Allowed Values |
|---|---|
| `id` | Unique kebab-case string |
| `text` | Min 20 chars; aim for 3–8 specific sentences |
| `metadata.technology_type` | `database`, `emr`, `python`, `mwaa` |
| `metadata.source` | Public/official source name |
| `metadata.topic` | `version`, `dependency`, `config`, `integration` |

### Optional Fields (Strongly Recommended)

| Field | Allowed Values | Purpose |
|---|---|---|
| `version_from` / `version_to` | e.g. `"13"`, `"3.12"` | Helps retrieval match upgrade paths |
| `risk_hint` | `Low`, `Medium`, `High`, `Critical` | Guides the risk rating |
| `validation_checks` | `regression`, `build`, `integration`, `data`, `performance`, `rollback` | Drives the "Recommend validation checks" capability |
| `domain` | `insurance`, `general` | Business-context tagging (spec = insurance) |

---

## The Six Validation Check Types (from the Spec)

When tagging `validation_checks`, use these definitions:

| Check | When to tag it |
|---|---|
| `regression` | Existing functionality could break; behavior changes |
| `build` | Compilation, packaging, wheels, JARs, dependency builds |
| `integration` | Connected systems / APIs / pipelines could be affected |
| `data` | Data format, schema, migration, or integrity risk |
| `performance` | Query plans, throughput, latency, resource usage may shift |
| `rollback` | Change is risky enough to require a tested rollback path |

**Rule of thumb:** tag 2–4 checks per document — the ones a reviewer would actually run for that specific risk.

---

## Your KB Refinement Workflow

### Step 1 — Check current state and gaps
```powershell
venv\Scripts\python scripts\ingest_knowledge.py --stats
```
Look at the `[WARN]` list — documents missing `validation_checks` are your first fix targets.

### Step 2 — Pick a technology and research public sources

| Tech | Official Source |
|---|---|
| PostgreSQL | https://www.postgresql.org/docs/release/ |
| EMR | https://docs.aws.amazon.com/emr/latest/ReleaseGuide/ |
| Python | https://docs.python.org/3/whatsnew/ |
| MWAA | https://docs.aws.amazon.com/mwaa/latest/userguide/ |

### Step 3 — Write documents
- One risk per document (don't merge version + integration)
- Be specific: exact versions, function names, error messages
- Tag `topic`, `risk_hint`, and `validation_checks`
- Use `knowledge/database/postgresql.json` as the reference pattern

### Step 4 — Reload into ChromaDB
```powershell
venv\Scripts\python scripts\ingest_knowledge.py
```

### Step 5 — Verify with an assessment
```powershell
curl -X POST http://localhost:8000/api/v1/assess-upgrade `
  -H "Content-Type: application/json" `
  -d "{\"technology_type\":\"database\",\"current_version\":\"PostgreSQL 13.4\",\"target_version\":\"PostgreSQL 15.2\",\"dependencies\":[\"psycopg2-binary\",\"sqlalchemy==1.4\"],\"integrations\":[\"BI reporting layer\"],\"environment\":\"production\"}"
```
Confirm your new knowledge shows up in the risk explanations.

---

## Coverage Targets for the Pilot

| Technology | Now | Target | Must cover topics |
|---|---|---|---|
| Database | 5 | 10–15 | version, dependency, config, integration |
| EMR | 5 | 10–15 | Spark, Hive, bootstrap, integration |
| Python | 6 | 12–18 | version paths, libraries, build, config |
| MWAA | 5 | 10–15 | DAG migration, providers, integration |
| **Total** | **21** | **40–60** | + validation_checks on every doc |

**Definition of done for the KB:** every document has `validation_checks`, both sample scenarios retrieve strong matches, and each tech type covers all four topics.

---

## Quality Checklist Per Document

- [ ] Unique `id`
- [ ] `text` is specific (versions, names, errors) — not vague
- [ ] Correct `technology_type` and `topic`
- [ ] `source` cites a **public** document (compliance)
- [ ] `risk_hint` set
- [ ] `validation_checks` tagged (2–4 relevant checks)
- [ ] `domain` set (`insurance` where domain-relevant)
- [ ] Reloaded and tested with an assessment

---

## Common Mistakes to Avoid

1. **Vague text** — "may cause issues" helps no one; name the exact breaking change.
2. **No validation_checks** — the report can't recommend focused checks without them.
3. **Duplicate IDs** — silently skipped on load.
4. **Wrong topic** — `integration` = cross-system; `config` = settings.
5. **Proprietary content** — never paste internal or client-confidential docs; use public sources only.
6. **Forgetting to reload** — JSON edits don't apply until reload/restart.

---

## Useful Commands

| Command | Purpose |
|---|---|
| `venv\Scripts\python scripts\ingest_knowledge.py --stats` | Report + lint, no ingest |
| `venv\Scripts\python scripts\ingest_knowledge.py` | Report + ingest into ChromaDB |
| `venv\Scripts\python scripts\ingest_knowledge.py --reset` | Clear + re-ingest (server-safe, in-place) |
| `venv\Scripts\python scripts\test_retrieval.py python "numpy upgrade"` | Test which docs a query retrieves |
| `curl http://localhost:8000/api/v1/knowledge/stats` | Live stats from running server |
| `curl -X POST http://localhost:8000/api/v1/reload-knowledge` | Reload KB into a running server |

---

*Start with the `[WARN]` list, add `validation_checks` to untagged docs, then expand coverage one technology at a time.*

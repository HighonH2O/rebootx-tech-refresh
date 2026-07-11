# REBOOTX — AI-Driven Tech Refresh Engine

> TCS Confidential

---

## Business Context

Insurance organisations operate complex technology ecosystems. Technology upgrades require manual compatibility validation across applications, middleware, databases and integrations. This process relies heavily on SMEs, architecture documents and spreadsheets.

The lack of automation increases assessment effort, delays refresh programs and raises the risk of missed interoperability issues. An AI-assisted compatibility validation framework can improve consistency, reduce manual effort, accelerate planning and improve upgrade success rates.

---

## Problem Statement

Build an AI-assisted compatibility validation engine that accepts technical upgrade details, analyses dependency and integration risks, recommends focused validation checks, and generates a **Tech Refresh Readiness Report**.

The solution should demonstrate how manual SME-led compatibility assessment can be converted into a reusable, explainable, and semi-automated framework.

---

## Scope of Work

| In Scope | Out of Scope |
|----------|-------------|
| Capture technology upgrade or refresh requests | Automated production deployments |
| Analyse application and dependency information | Real-time infrastructure monitoring |
| Retrieve relevant documentation and compatibility references | Auto-remediation of identified issues |
| Identify potential interoperability risks | Enterprise-wide integration with production systems |
| Generate upgrade impact assessment summaries | |
| Provide compatibility recommendations and insights | |
| Produce a user-friendly assessment report | |
| Demonstrate end-to-end prototype workflow | |

---

## Recommended Pilot

- **Scope:** Database upgrades, EMR upgrades, Python Upgrades, MWAA Upgrades
- **Stack:** VS Code + GitHub Copilot Coding Agent + Python + FastAPI + ChromaDB + Ollama (Llama 3)
- **Duration:** 2–4 Weeks

---

## Expected Outcome

Working prototype demonstrating automated compatibility assessment, integration risk identification, and AI-generated impact reports for enterprise technology refresh decisions.

By the end of the assignment, the interns should demonstrate a working prototype that can:

| Capability | Expected Output |
|-----------|----------------|
| Capture upgrade input | Current version, target version, technology type, dependencies, integrations |
| Analyse compatibility | Identify dependency, version, configuration, and integration risks |
| Generate risk rating | Low / Medium / High / Critical |
| Explain risks | Provide clear reason for each risk |
| Recommend validation checks | Focused regression, build, integration, data, performance, and rollback checks |
| Produce readiness report | Structured Tech Refresh Readiness Report |
| Demonstrate with examples | Minimum 2 sample upgrade scenarios |

---

## Guidelines to Follow Always

### Code of Conduct

- Maintain ethical behaviour and inclusive communication
- Respect others' ideas, time, and effort
- Avoid the use of proprietary data or unauthorised tools
- Adhere to the Tata code of conduct in its entirety

---

## Key Technology Decisions

| Layer | Tool | Rationale |
|-------|------|-----------|
| Backend API | FastAPI + Python | Async support; handles slow LLM calls well |
| LLM | Ollama running Llama 3 | Fully local — satisfies "avoid unauthorised tools/proprietary data" cleanly |
| Vector Store | ChromaDB | Lightweight, embeds well with local models |
| Embeddings | `nomic-embed-text` (via Ollama) | Keeps everything in one local stack, no external API calls |
| Frontend | Plain HTML/JS served by FastAPI, or Streamlit | Speed matters more than polish for a 2–4 week prototype |
| Report Output | `weasyprint` or `reportlab` | Turns structured JSON into the "user-friendly assessment report" deliverable |
| Storage | SQLite or plain JSON files | Prototype — no need for a full DB |
| Dev Environment | VS Code + GitHub Copilot Coding Agent | Use Copilot for boilerplate (schema classes, FastAPI routes) so time goes into RAG/prompt design |

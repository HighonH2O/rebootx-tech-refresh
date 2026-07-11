# API Specification — RebootX

> FastAPI endpoint specifications, request/response schemas, and error handling.

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### `GET /health`

Health check endpoint to verify the API server, Ollama, and ChromaDB are running.

**Response** `200 OK`

```json
{
  "status": "healthy",
  "services": {
    "api": "up",
    "ollama": "up",
    "ollama_model": "llama3",
    "chromadb": "up",
    "chromadb_documents": 1247
  },
  "version": "0.1.0",
  "timestamp": "2026-07-10T18:00:00Z"
}
```

**Response** `503 Service Unavailable`

```json
{
  "status": "degraded",
  "services": {
    "api": "up",
    "ollama": "down",
    "chromadb": "up"
  },
  "error": "Ollama service not reachable at localhost:11434"
}
```

---

### `POST /assess`

Submit a technology upgrade request for risk assessment. This is the primary endpoint.

**Request Body**

```json
{
  "technology_type": "Database",
  "current_version": "PostgreSQL 12.4",
  "target_version": "PostgreSQL 16.2",
  "dependencies": [
    "psycopg2 2.9.3",
    "pgbouncer 1.17",
    "SQLAlchemy 1.4.39"
  ],
  "integrations": [
    "ETL pipeline (Apache Airflow 2.5)",
    "Reporting service (Metabase 0.44)",
    "API gateway (Kong 3.1)"
  ],
  "environment": "Production"
}
```

**Request Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `technology_type` | `enum` | ✅ | One of: `Database`, `Runtime`, `MWAA`, `EMR` |
| `current_version` | `string` | ✅ | Current version string (e.g., `"PostgreSQL 12.4"`) |
| `target_version` | `string` | ✅ | Target version string (e.g., `"PostgreSQL 16.2"`) |
| `dependencies` | `list[string]` | ✅ | List of dependent libraries/tools with optional versions |
| `integrations` | `list[string]` | ✅ | List of integrated systems/services |
| `environment` | `enum` | ❌ | `Production` (default) or `Staging` |

**Response** `200 OK`

```json
{
  "assessment_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-07-10T18:00:00Z",
  "request_summary": {
    "technology_type": "Database",
    "current_version": "PostgreSQL 12.4",
    "target_version": "PostgreSQL 16.2",
    "environment": "Production"
  },
  "overall_risk": {
    "level": "High",
    "score": 7.2,
    "verdict": "Proceed with caution — thorough testing and dependency updates required"
  },
  "summary": {
    "risks_found": 6,
    "checks_recommended": 9,
    "critical_count": 1,
    "high_count": 1,
    "medium_count": 3,
    "low_count": 1
  },
  "risks": [
    {
      "risk_id": "R-001",
      "category": "Deprecated API",
      "severity": "Critical",
      "title": "Deprecated connection pooling API in v16",
      "description": "psycopg2 connection handling patterns may break due to removed connection pooling API in PostgreSQL 16.",
      "affected_components": ["psycopg2", "pgbouncer"],
      "recommendation": "Migrate to psycopg3 or verify psycopg2 2.9.3+ compatibility with PG 16. Test connection pooling under load.",
      "references": [
        "PostgreSQL 16 Release Notes — Deprecated Features",
        "psycopg2 compatibility matrix"
      ]
    }
  ],
  "validation_checks": [
    {
      "check_id": "C-001",
      "type": "Regression",
      "description": "Run full test suite against PG 16 staging instance",
      "priority": "P0",
      "related_risks": ["R-001", "R-004"]
    }
  ],
  "rag_context": {
    "documents_retrieved": 8,
    "top_sources": [
      "postgresql-16-release-notes.md",
      "psycopg2-pg16-compatibility.md"
    ]
  }
}
```

**Response** `422 Validation Error`

```json
{
  "detail": [
    {
      "loc": ["body", "technology_type"],
      "msg": "value is not a valid enumeration member; permitted: 'Database', 'Runtime', 'MWAA', 'EMR'",
      "type": "type_error.enum"
    }
  ]
}
```

**Response** `503 Service Unavailable`

```json
{
  "detail": "LLM service (Ollama) is not available. Ensure Ollama is running on localhost:11434 with llama3 model loaded."
}
```

---

### `GET /assess/{assessment_id}`

Retrieve a previously generated assessment by ID.

**Response** `200 OK`

Returns the same schema as `POST /assess` response.

**Response** `404 Not Found`

```json
{
  "detail": "Assessment a1b2c3d4-... not found"
}
```

---

### `GET /assess/{assessment_id}/report`

Download the assessment as a PDF report.

**Query Parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | `enum` | `pdf` | `pdf` or `html` |

**Response** `200 OK`

Returns the report file with appropriate `Content-Type` header (`application/pdf` or `text/html`).

---

### `GET /scenarios`

List available pre-loaded sample scenarios for demo purposes.

**Response** `200 OK`

```json
{
  "scenarios": [
    {
      "id": "postgresql-12-to-16",
      "name": "PostgreSQL 12.4 → 16.2",
      "technology_type": "Database",
      "description": "Database upgrade with psycopg2, pgbouncer, and ETL pipeline dependencies"
    },
    {
      "id": "python-38-to-312",
      "name": "Python 3.8 → 3.12",
      "technology_type": "Runtime",
      "description": "Runtime upgrade with Django, numpy, and AWS Lambda integration"
    }
  ]
}
```

---

### `POST /scenarios/{scenario_id}/run`

Execute a pre-loaded sample scenario through the assessment pipeline.

**Response** `200 OK`

Returns the same schema as `POST /assess` response.

---

## Pydantic Schemas (Python)

```python
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from uuid import UUID


class TechnologyType(str, Enum):
    DATABASE = "Database"
    RUNTIME = "Runtime"
    MWAA = "MWAA"
    EMR = "EMR"


class Environment(str, Enum):
    PRODUCTION = "Production"
    STAGING = "Staging"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class CheckPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


# --- Request ---

class UpgradeRequest(BaseModel):
    technology_type: TechnologyType
    current_version: str = Field(..., example="PostgreSQL 12.4")
    target_version: str = Field(..., example="PostgreSQL 16.2")
    dependencies: list[str] = Field(..., example=["psycopg2", "pgbouncer"])
    integrations: list[str] = Field(..., example=["ETL pipeline", "API gateway"])
    environment: Environment = Environment.PRODUCTION


# --- Response Components ---

class Risk(BaseModel):
    risk_id: str
    category: str
    severity: RiskLevel
    title: str
    description: str
    affected_components: list[str]
    recommendation: str
    references: list[str] = []


class ValidationCheck(BaseModel):
    check_id: str
    type: str  # Regression | Build | Integration | Data | Performance | Rollback
    description: str
    priority: CheckPriority
    related_risks: list[str] = []


class OverallRisk(BaseModel):
    level: RiskLevel
    score: float = Field(..., ge=0.0, le=10.0)
    verdict: str


class AssessmentSummary(BaseModel):
    risks_found: int
    checks_recommended: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class RAGContext(BaseModel):
    documents_retrieved: int
    top_sources: list[str]


# --- Full Response ---

class AssessmentResponse(BaseModel):
    assessment_id: UUID
    timestamp: datetime
    request_summary: UpgradeRequest
    overall_risk: OverallRisk
    summary: AssessmentSummary
    risks: list[Risk]
    validation_checks: list[ValidationCheck]
    rag_context: RAGContext
```

---

## Error Handling

| Status Code | Meaning | When |
|-------------|---------|------|
| `200` | Success | Assessment completed successfully |
| `400` | Bad Request | Malformed JSON body |
| `422` | Validation Error | Schema validation failure (Pydantic) |
| `404` | Not Found | Assessment ID doesn't exist |
| `503` | Service Unavailable | Ollama or ChromaDB is down |
| `500` | Internal Server Error | Unexpected failure in pipeline |

---

## Interactive Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

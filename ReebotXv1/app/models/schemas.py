"""Pydantic schemas for the RebootX API.

These define the data contracts for all API endpoints.
They are intentionally compatible with the rebootx-tech-refresh
knowledge retrieval system so both repos can exchange data.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TechnologyType(str, Enum):
    """Supported technology domains for upgrade assessment."""
    DATABASE = "database"
    EMR = "emr"
    PYTHON = "python"
    MWAA = "mwaa"


class RiskLevel(str, Enum):
    """Risk severity bands — matches the risk taxonomy."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class UpgradeRequest(BaseModel):
    """Input for a compatibility assessment.

    Can be constructed manually or auto-populated by the bridge service
    from a repository scan result.
    """
    technology_type: TechnologyType = Field(
        ...,
        description="Type of technology being upgraded",
    )
    current_version: str = Field(
        ...,
        examples=["PostgreSQL 13.4", "Python 3.9", "EMR 6.10"],
    )
    target_version: str = Field(
        ...,
        examples=["PostgreSQL 15.2", "Python 3.12", "EMR 7.0"],
    )
    dependencies: list[str] = Field(
        default_factory=list,
        examples=[["sqlalchemy==1.4", "psycopg2-binary"]],
    )
    integrations: list[str] = Field(
        default_factory=list,
        examples=[["Airflow DAGs", "Spark jobs", "BI reporting layer"]],
    )
    environment: Optional[str] = Field(
        default="production",
        examples=["production", "staging"],
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional context (e.g., scanner risk flags, graph summary)",
    )


class ScanAndAssessRequest(BaseModel):
    """Bridge endpoint: scan a repo then run an assessment in one call."""
    repo_path: str = Field(
        ...,
        description="Path to the repository to scan",
        examples=["./", "/path/to/my-project"],
    )
    target_version: str = Field(
        ...,
        description="Target version for the upgrade",
        examples=["PostgreSQL 16", "Python 3.12"],
    )
    current_version: Optional[str] = Field(
        default=None,
        description="Current version (auto-detected if omitted)",
    )
    environment: Optional[str] = Field(
        default="production",
    )


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class IdentifiedRisk(BaseModel):
    """A single risk identified during the assessment."""
    category: str = Field(
        ...,
        description="Risk category: dependency, version, config, integration",
    )
    risk_level: RiskLevel
    title: str
    explanation: str
    recommendation: str


class UpgradeAssessment(BaseModel):
    """Complete assessment output — the Tech Refresh Readiness Report data."""
    technology_type: str
    current_version: str
    target_version: str
    overall_risk: RiskLevel
    summary: str
    risks: list[IdentifiedRisk] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    confidence: str = "Medium"
    analysis_mode: str = Field(
        default="rules",
        description="'ai' if Ollama was used, 'rules' for deterministic fallback",
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str
    ollama_available: bool
    knowledge_documents: int


class KnowledgeStatsResponse(BaseModel):
    """Knowledge base statistics."""
    total_documents: int
    by_technology: dict[str, int] = Field(default_factory=dict)

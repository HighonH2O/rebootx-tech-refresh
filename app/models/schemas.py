"""Pydantic schemas for RebootX API."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TechnologyType(str, Enum):
    DATABASE = "database"
    EMR = "emr"
    PYTHON = "python"
    MWAA = "mwaa"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class UpgradeRequest(BaseModel):
    technology_type: TechnologyType = Field(..., description="Type of technology being upgraded")
    current_version: str = Field(..., examples=["PostgreSQL 13.4", "Python 3.9", "EMR 6.10"])
    target_version: str = Field(..., examples=["PostgreSQL 15.2", "Python 3.12", "EMR 7.0"])
    dependencies: list[str] = Field(default_factory=list, examples=[["sqlalchemy==1.4", "psycopg2-binary"]])
    integrations: list[str] = Field(
        default_factory=list,
        examples=[["Airflow DAGs", "Spark jobs", "BI reporting layer"]],
    )
    environment: Optional[str] = Field(default="production", examples=["production", "staging"])
    notes: Optional[str] = Field(default=None, description="Additional context about the upgrade")


class IdentifiedRisk(BaseModel):
    category: str = Field(..., description="Risk category: dependency, version, config, integration")
    risk_level: RiskLevel
    title: str
    explanation: str
    recommendation: str


class UpgradeAssessment(BaseModel):
    technology_type: TechnologyType
    current_version: str
    target_version: str
    overall_risk: RiskLevel
    summary: str
    risks: list[IdentifiedRisk]
    recommended_actions: list[str]
    confidence: str = Field(..., description="Assessment confidence based on available knowledge")
    analysis_mode: str = Field(..., description="ai or rules_fallback")


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    ollama_available: bool
    knowledge_documents: int


class SourceType(str, Enum):
    LOCAL = "local"
    GITHUB = "github"


class CaptureRequest(BaseModel):
    source_type: SourceType = Field(..., description="Where to capture upgrade input from")
    location: str = Field(
        ...,
        description="Local folder path or public GitHub repo URL",
        examples=["C:/Coding Practice/rebootx", "https://github.com/apache/airflow"],
    )
    target_version: Optional[str] = Field(
        default=None,
        description="Desired upgrade target; if omitted it is left unspecified",
        examples=["Python 3.12", "PostgreSQL 15.2"],
    )
    technology_type: Optional[TechnologyType] = Field(
        default=None,
        description="Override the auto-detected technology type",
    )
    environment: Optional[str] = Field(default="production", examples=["production", "staging"])


class CapturedInput(BaseModel):
    technology_type: TechnologyType
    current_version: str
    target_version: str
    dependencies: list[str]
    integrations: list[str]
    environment: Optional[str] = "production"
    detected_from: list[str] = Field(default_factory=list, description="Manifest files that were read")
    warnings: list[str] = Field(default_factory=list, description="Anything the user should confirm manually")
    source_type: SourceType
    location: str


class KnowledgeDocumentInput(BaseModel):
    id: str = Field(..., description="Unique document ID, e.g. python-39-to-312-breaking")
    text: str = Field(..., min_length=20, description="Compatibility knowledge content (3-8 sentences)")
    technology_type: TechnologyType
    source: str = Field(..., examples=["PostgreSQL 15 Release Notes"])
    topic: str = Field(..., examples=["version", "dependency", "config", "integration"])
    version_from: Optional[str] = None
    version_to: Optional[str] = None
    risk_hint: Optional[str] = Field(default=None, examples=["Low", "Medium", "High", "Critical"])


class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    chroma_documents: int
    source_files: int
    by_technology_type: dict[str, int]
    by_topic: dict[str, int]
    knowledge_dir: str

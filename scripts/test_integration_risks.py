"""Quick check: multi-language DB upgrade should surface non-trivial integration risks.

Runs the rules-based path directly (no server / no Ollama needed) so the
deterministic integration analyzer output is easy to inspect.
"""

import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.schemas import IntegrationDetail, TechnologyType, UpgradeRequest
from app.services.assessment_service import AssessmentService
from app.services.knowledge_service import KnowledgeService
from app.services.ollama_service import OllamaService


async def main() -> None:
    request = UpgradeRequest(
        technology_type=TechnologyType.DATABASE,
        current_version="PostgreSQL 13",
        target_version="PostgreSQL 15",
        dependencies=["sqlalchemy==1.4"],
        integration_details=[
            IntegrationDetail(name="Claims processing service", consumer_technology="java", protocol="JDBC", owner_team="Claims"),
            IntegrationDetail(name="Analytics ETL", consumer_technology="python", protocol="psycopg2", owner_team="Data"),
            IntegrationDetail(name="Reporting dashboard", consumer_technology="dotnet", protocol="ODBC", owner_team="BI"),
            IntegrationDetail(name="Event stream", consumer_technology="scala", protocol="Kafka", owner_team="Platform"),
        ],
        environment="production",
    )

    knowledge = KnowledgeService()
    ollama = OllamaService()
    service = AssessmentService(knowledge, ollama)

    assessment = await service.assess(request)

    print(f"\nOverall risk: {assessment.overall_risk.value}  (mode: {assessment.analysis_mode})")
    print(f"Summary: {assessment.summary}\n")
    print(f"Risks ({len(assessment.risks)}):")
    for i, r in enumerate(assessment.risks, 1):
        print(f"\n[{i}] ({r.risk_level.value}) [{r.category}] {r.title}")
        print(f"    why: {r.explanation}")
        print(f"    fix: {r.recommendation}")


if __name__ == "__main__":
    asyncio.run(main())

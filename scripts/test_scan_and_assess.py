"""End-to-end check: scan a repo -> bridge -> assessment (with integration analyzer)."""

import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.assessment_service import AssessmentService
from app.services.bridge_service import BridgeService
from app.services.knowledge_service import KnowledgeService
from app.services.ollama_service import OllamaService


async def main() -> None:
    repo = str(Path(__file__).resolve().parents[1] / "repository_scanner" / "tests" / "fixtures" / "sample_repo")

    scan_dict, request = BridgeService.scan_and_build_request(
        repo_path=repo,
        target_version="PostgreSQL 16",
    )

    print(f"Detected technology : {request.technology_type.value}")
    print(f"Dependencies        : {request.dependencies}")
    print(f"Integration details :")
    for d in request.integration_details:
        print(f"   - {d.name} ({d.consumer_technology} / {d.protocol})")

    service = AssessmentService(KnowledgeService(), OllamaService())
    assessment = await service.assess(request)

    print(f"\nOverall risk: {assessment.overall_risk.value}  (mode: {assessment.analysis_mode})")
    print(f"Risks ({len(assessment.risks)}):")
    for i, r in enumerate(assessment.risks, 1):
        print(f"  [{i}] ({r.risk_level.value}) [{r.category}] {r.title}")


if __name__ == "__main__":
    asyncio.run(main())

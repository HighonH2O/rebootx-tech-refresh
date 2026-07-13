"""Upgrade assessment orchestration (AI + rules fallback)."""

import logging
from typing import Iterable

from app.models.schemas import (
    IdentifiedRisk,
    RiskLevel,
    TechnologyType,
    UpgradeAssessment,
    UpgradeRequest,
)
from app.services.knowledge_service import KnowledgeService
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

RISK_ORDER = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

SYSTEM_PROMPT = """You are RebootX, an enterprise technology refresh compatibility analyst.
Analyze upgrade requests using ONLY the provided knowledge context.
Return valid JSON with this exact shape:
{
  "overall_risk": "Low|Medium|High|Critical",
  "summary": "2-3 sentence executive summary",
  "risks": [
    {
      "category": "dependency|version|config|integration",
      "risk_level": "Low|Medium|High|Critical",
      "title": "short title",
      "explanation": "clear reason grounded in context",
      "recommendation": "specific mitigation step"
    }
  ],
  "recommended_actions": ["action 1", "action 2"],
  "confidence": "High|Medium|Low"
}
Identify at least 2 risks when possible. Be conservative for production environments."""


class AssessmentService:
    def __init__(self, knowledge: KnowledgeService, ollama: OllamaService) -> None:
        self.knowledge = knowledge
        self.ollama = ollama

    async def assess(self, request: UpgradeRequest) -> UpgradeAssessment:
        query = self._build_query(request)
        context_docs = self.knowledge.retrieve(
            query=query,
            technology_type=request.technology_type.value,
            n_results=5,
        )
        context_block = self._format_context(context_docs)

        if await self.ollama.is_available():
            ai_result = await self._assess_with_ai(request, context_block)
            if ai_result:
                return ai_result

        return self._assess_with_rules(request, context_docs)

    def _build_query(self, request: UpgradeRequest) -> str:
        deps = ", ".join(request.dependencies) if request.dependencies else "none"
        integrations = ", ".join(request.integrations) if request.integrations else "none"
        return (
            f"{request.technology_type.value} upgrade from {request.current_version} "
            f"to {request.target_version}. Dependencies: {deps}. Integrations: {integrations}."
        )

    @staticmethod
    def _format_context(docs: list[dict]) -> str:
        if not docs:
            return "No specific knowledge documents retrieved."
        lines = []
        for idx, doc in enumerate(docs, start=1):
            source = doc.get("metadata", {}).get("source", "Unknown")
            lines.append(f"[{idx}] Source: {source}\n{doc['text']}")
        return "\n\n".join(lines)

    async def _assess_with_ai(self, request: UpgradeRequest, context: str) -> UpgradeAssessment | None:
        prompt = f"""Upgrade Request:
- Technology: {request.technology_type.value}
- Current Version: {request.current_version}
- Target Version: {request.target_version}
- Dependencies: {', '.join(request.dependencies) or 'none'}
- Integrations: {', '.join(request.integrations) or 'none'}
- Environment: {request.environment}
- Notes: {request.notes or 'none'}

Retrieved Knowledge:
{context}

Produce the JSON assessment."""

        raw = await self.ollama.generate(prompt=prompt, system=SYSTEM_PROMPT)
        parsed = self.ollama.extract_json(raw or "")
        if not parsed:
            logger.warning("Failed to parse Ollama JSON response")
            return None

        try:
            risks = [
                IdentifiedRisk(
                    category=item["category"],
                    risk_level=RiskLevel(item["risk_level"]),
                    title=item["title"],
                    explanation=item["explanation"],
                    recommendation=item["recommendation"],
                )
                for item in parsed.get("risks", [])
            ]
            return UpgradeAssessment(
                technology_type=request.technology_type,
                current_version=request.current_version,
                target_version=request.target_version,
                overall_risk=RiskLevel(parsed["overall_risk"]),
                summary=parsed["summary"],
                risks=risks,
                recommended_actions=parsed.get("recommended_actions", []),
                confidence=parsed.get("confidence", "Medium"),
                analysis_mode="ai",
            )
        except (KeyError, ValueError) as exc:
            logger.warning("Invalid AI assessment payload: %s", exc)
            return None

    def _assess_with_rules(self, request: UpgradeRequest, context_docs: list[dict]) -> UpgradeAssessment:
        risks: list[IdentifiedRisk] = []

        major_jump = self._is_major_version_jump(request.current_version, request.target_version)
        if major_jump:
            risks.append(
                IdentifiedRisk(
                    category="version",
                    risk_level=RiskLevel.HIGH,
                    title="Major version jump detected",
                    explanation=(
                        f"Upgrade from {request.current_version} to {request.target_version} "
                        "crosses a major release boundary and commonly introduces breaking changes."
                    ),
                    recommendation="Run full regression and integration test suites in staging before production.",
                )
            )

        if request.dependencies:
            risks.append(
                IdentifiedRisk(
                    category="dependency",
                    risk_level=RiskLevel.MEDIUM,
                    title="Dependency compatibility review required",
                    explanation=(
                        f"The upgrade affects {len(request.dependencies)} declared dependencies "
                        "that may not support the target runtime or platform version."
                    ),
                    recommendation="Regenerate lock files and validate each dependency against the target version.",
                )
            )

        if request.integrations:
            risks.append(
                IdentifiedRisk(
                    category="integration",
                    risk_level=RiskLevel.MEDIUM,
                    title="Downstream integration impact",
                    explanation=(
                        f"{len(request.integrations)} integrations may be affected by API, "
                        "configuration, or runtime behavior changes."
                    ),
                    recommendation="Notify integration owners and execute end-to-end validation for each connected system.",
                )
            )

        if request.environment and request.environment.lower() == "production":
            risks.append(
                IdentifiedRisk(
                    category="config",
                    risk_level=RiskLevel.HIGH,
                    title="Production environment upgrade",
                    explanation="Production upgrades require stricter change controls and rollback planning.",
                    recommendation="Require CAB approval, backup verification, and a documented rollback plan.",
                )
            )

        for doc in context_docs[:2]:
            topic = doc.get("metadata", {}).get("topic", "compatibility")
            risks.append(
                IdentifiedRisk(
                    category=topic if topic in {"dependency", "version", "config", "integration"} else "version",
                    risk_level=RiskLevel.MEDIUM,
                    title=f"Known compatibility concern ({doc.get('metadata', {}).get('source', 'Knowledge Base')})",
                    explanation=doc["text"][:280] + ("..." if len(doc["text"]) > 280 else ""),
                    recommendation="Review referenced release notes and apply documented migration steps.",
                )
            )

        if not risks:
            risks.append(
                IdentifiedRisk(
                    category="version",
                    risk_level=RiskLevel.LOW,
                    title="Limited knowledge available",
                    explanation="No specific compatibility issues were found in the knowledge base for this upgrade path.",
                    recommendation="Proceed with standard pre-upgrade checks and monitor closely after deployment.",
                )
            )

        overall = self._aggregate_risk(r.risk_level for r in risks)
        summary = (
            f"Rules-based assessment for {request.technology_type.value} upgrade "
            f"({request.current_version} → {request.target_version}) indicates {overall.value} overall risk."
        )

        return UpgradeAssessment(
            technology_type=request.technology_type,
            current_version=request.current_version,
            target_version=request.target_version,
            overall_risk=overall,
            summary=summary,
            risks=risks,
            recommended_actions=[
                "Validate upgrade path in a non-production environment",
                "Review dependency and integration test results",
                "Prepare rollback and communication plan",
            ],
            confidence="Medium" if context_docs else "Low",
            analysis_mode="rules_fallback",
        )

    @staticmethod
    def _is_major_version_jump(current: str, target: str) -> bool:
        current_parts = [int(p) for p in __import__("re").findall(r"\d+", current)[:2]]
        target_parts = [int(p) for p in __import__("re").findall(r"\d+", target)[:2]]
        if not current_parts or not target_parts:
            return current.strip().lower() != target.strip().lower()
        return target_parts[0] > current_parts[0] or (
            len(current_parts) > 1 and len(target_parts) > 1 and target_parts[0] == current_parts[0] and target_parts[1] > current_parts[1] + 1
        )

    @staticmethod
    def _aggregate_risk(levels: Iterable[RiskLevel]) -> RiskLevel:
        max_idx = max(RISK_ORDER.index(level) for level in levels)
        return RISK_ORDER[max_idx]

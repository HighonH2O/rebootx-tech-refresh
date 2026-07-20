"""Upgrade assessment orchestration — AI mode + rules-based fallback.

This is the CORE BRAIN of RebootX. It orchestrates the full assessment:
1. Build a semantic query from the UpgradeRequest
2. Retrieve relevant knowledge docs from ChromaDB
3. If Ollama is available → AI assessment via Llama 3
4. If Ollama is down → deterministic rules-based fallback
5. Return a structured UpgradeAssessment
"""

import json
import logging

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
Identify at least 2 risks when possible. Be conservative for production environments.
Return ONLY the JSON object, no other text."""


class AssessmentService:
    """Orchestrates RAG-powered upgrade compatibility assessment."""

    def __init__(self, knowledge: KnowledgeService, ollama: OllamaService) -> None:
        self.knowledge = knowledge
        self.ollama = ollama

    async def assess(self, request: UpgradeRequest) -> UpgradeAssessment:
        """Run the full assessment pipeline.

        Tries AI mode first, falls back to rules if Ollama is unavailable
        or the LLM response cannot be parsed.
        """
        # Step 1: Build semantic query
        query = self._build_query(request)

        # Step 2: Retrieve relevant knowledge
        context_docs = self.knowledge.retrieve(
            query=query,
            technology_type=request.technology_type.value,
            n_results=5,
        )
        context_block = self._format_context(context_docs)

        # Step 3: Try AI assessment
        if await self.ollama.is_available():
            ai_result = await self._assess_with_ai(request, context_block)
            if ai_result:
                return ai_result
            logger.warning("AI assessment failed, falling back to rules")

        # Step 4: Rules-based fallback
        return self._assess_with_rules(request, context_docs)

    # ------------------------------------------------------------------
    # Query Building
    # ------------------------------------------------------------------

    def _build_query(self, request: UpgradeRequest) -> str:
        """Construct a semantic search query from the upgrade request."""
        deps = ", ".join(request.dependencies[:5]) if request.dependencies else "none"
        integrations = ", ".join(request.integrations[:3]) if request.integrations else "none"
        return (
            f"{request.technology_type.value} upgrade from {request.current_version} "
            f"to {request.target_version}. "
            f"Dependencies: {deps}. Integrations: {integrations}. "
            f"Breaking changes and compatibility issues."
        )

    # ------------------------------------------------------------------
    # Context Formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _format_context(docs: list[dict]) -> str:
        """Format retrieved knowledge documents for the LLM prompt."""
        if not docs:
            return "No specific knowledge documents retrieved."
        lines = []
        for idx, doc in enumerate(docs, start=1):
            source = doc.get("metadata", {}).get("source", "Unknown")
            topic = doc.get("metadata", {}).get("topic", "")
            lines.append(f"[{idx}] Source: {source} (topic: {topic})\n{doc['text']}")
        return "\n\n".join(lines)

    # ------------------------------------------------------------------
    # AI Assessment (Ollama / Llama 3)
    # ------------------------------------------------------------------

    async def _assess_with_ai(
        self, request: UpgradeRequest, context: str,
    ) -> UpgradeAssessment | None:
        """Generate assessment using the local LLM."""
        prompt = f"""Upgrade Request:
- Technology: {request.technology_type.value}
- Current Version: {request.current_version}
- Target Version: {request.target_version}
- Dependencies: {', '.join(request.dependencies) if request.dependencies else 'None specified'}
- Integrations: {', '.join(request.integrations) if request.integrations else 'None specified'}
- Environment: {request.environment or 'production'}
{f'- Additional Notes: {request.notes}' if request.notes else ''}

Knowledge Context:
{context}

Analyze this upgrade and return a JSON risk assessment."""

        raw = await self.ollama.generate(prompt=prompt, system=SYSTEM_PROMPT)
        if not raw:
            return None

        parsed = OllamaService.extract_json(raw)
        if not parsed:
            return None

        try:
            return self._parse_ai_response(parsed, request)
        except Exception as exc:
            logger.error("Failed to parse AI response: %s", exc)
            return None

    def _parse_ai_response(
        self, data: dict, request: UpgradeRequest,
    ) -> UpgradeAssessment:
        """Convert raw LLM JSON output into a validated UpgradeAssessment."""
        risks = []
        for r in data.get("risks", []):
            try:
                risks.append(IdentifiedRisk(
                    category=r.get("category", "version"),
                    risk_level=RiskLevel(r.get("risk_level", "Medium")),
                    title=r.get("title", "Unnamed risk"),
                    explanation=r.get("explanation", ""),
                    recommendation=r.get("recommendation", ""),
                ))
            except (ValueError, KeyError):
                continue

        overall = RiskLevel.MEDIUM
        try:
            overall = RiskLevel(data.get("overall_risk", "Medium"))
        except ValueError:
            if risks:
                overall = max(
                    (r.risk_level for r in risks),
                    key=lambda x: RISK_ORDER.index(x),
                )

        return UpgradeAssessment(
            technology_type=request.technology_type.value,
            current_version=request.current_version,
            target_version=request.target_version,
            overall_risk=overall,
            summary=data.get("summary", "AI-generated assessment"),
            risks=risks,
            recommended_actions=data.get("recommended_actions", []),
            confidence=data.get("confidence", "Medium"),
            analysis_mode="ai",
        )

    # ------------------------------------------------------------------
    # Rules-Based Fallback
    # ------------------------------------------------------------------

    def _assess_with_rules(
        self, request: UpgradeRequest, context_docs: list[dict],
    ) -> UpgradeAssessment:
        """Generate assessment using deterministic rules when LLM is unavailable.

        Uses risk_hint metadata from knowledge documents and dependency
        matching to produce a structured assessment.
        """
        risks: list[IdentifiedRisk] = []

        # Generate risks from retrieved knowledge documents
        for doc in context_docs:
            meta = doc.get("metadata", {})
            topic = meta.get("topic", "version")
            risk_hint = meta.get("risk_hint", "Medium")
            source = meta.get("source", "Knowledge Base")

            try:
                level = RiskLevel(risk_hint)
            except ValueError:
                level = RiskLevel.MEDIUM

            # Extract first sentence as title
            text = doc.get("text", "")
            title = text.split(". ")[0][:80] if text else "Compatibility concern"

            # Build recommendation from validation_checks
            checks_str = meta.get("validation_checks", "")
            checks = [c.strip() for c in checks_str.split(",") if c.strip()]
            if checks:
                rec = f"Run {', '.join(checks)} testing before production deployment."
            else:
                rec = "Validate in staging environment before production deployment."

            risks.append(IdentifiedRisk(
                category=topic,
                risk_level=level,
                title=title,
                explanation=text[:300] + ("..." if len(text) > 300 else ""),
                recommendation=rec,
            ))

        # Add dependency-based risks
        dep_lower = {d.lower() for d in request.dependencies}
        if "psycopg2" in dep_lower or "psycopg2-binary" in dep_lower:
            risks.append(IdentifiedRisk(
                category="dependency",
                risk_level=RiskLevel.HIGH,
                title="psycopg2 version compatibility",
                explanation=(
                    "psycopg2 older than 2.9 may not support SCRAM-SHA-256 "
                    "authentication defaults in newer PostgreSQL versions."
                ),
                recommendation="Upgrade psycopg2 to >= 2.9.3 or migrate to psycopg3.",
            ))

        # Calculate overall risk
        if risks:
            overall = max(
                (r.risk_level for r in risks),
                key=lambda x: RISK_ORDER.index(x),
            )
        else:
            overall = RiskLevel.LOW

        # Build recommended actions
        actions = [
            f"Validate upgrade path in staging ({request.current_version} → {request.target_version})",
            "Run full regression test suite",
            "Prepare rollback plan",
        ]
        if request.environment == "production":
            actions.append("Schedule maintenance window for production cutover")

        # Build summary
        risk_count = len(risks)
        summary = (
            f"Rules-based assessment for {request.technology_type.value} upgrade "
            f"from {request.current_version} to {request.target_version}. "
            f"Found {risk_count} potential risk{'s' if risk_count != 1 else ''} "
            f"based on knowledge base analysis."
        )

        return UpgradeAssessment(
            technology_type=request.technology_type.value,
            current_version=request.current_version,
            target_version=request.target_version,
            overall_risk=overall,
            summary=summary,
            risks=risks,
            recommended_actions=actions,
            confidence="Medium" if context_docs else "Low",
            analysis_mode="rules",
        )

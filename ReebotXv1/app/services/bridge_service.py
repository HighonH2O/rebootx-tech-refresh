"""Bridge Service — connects the Repository Scanner to the Assessment Engine.

This is the KEY INTEGRATION PIECE. It takes the output of the existing
repository_scanner module and converts it into an UpgradeRequest that the
assessment service can process.

Flow:
    repo_path + target_version
        → repository_scanner.scan()
        → ScanResult
        → BridgeService.scan_result_to_request()
        → UpgradeRequest
        → AssessmentService.assess()
        → UpgradeAssessment
"""

import logging

from app.models.schemas import TechnologyType, UpgradeRequest
from repository_scanner.services.scan_service import scan

logger = logging.getLogger(__name__)

# Map detected database names to TechnologyType
DATABASE_TECH_MAP = {
    "postgresql": TechnologyType.DATABASE,
    "mysql": TechnologyType.DATABASE,
    "oracle": TechnologyType.DATABASE,
}

# Map detected languages to TechnologyType
LANGUAGE_TECH_MAP = {
    "python": TechnologyType.PYTHON,
}


class BridgeService:
    """Adapter that converts ScanResult → UpgradeRequest."""

    @staticmethod
    def scan_repository(repo_path: str) -> dict:
        """Run the repository scanner and return the result as a dict.

        Args:
            repo_path: Path to the repository to scan.

        Returns:
            ScanResult.to_dict() — the full scan output.
        """
        result = scan(repo_path)
        return result.to_dict()

    @staticmethod
    def detect_technology_type(scan_dict: dict) -> TechnologyType:
        """Auto-detect the technology type from scan results.

        Priority:
        1. Database detection (if scanner found PostgreSQL, etc.)
        2. Language detection (if Python is the dominant language)
        3. Default to PYTHON
        """
        # Check database
        database = scan_dict.get("database", "").lower()
        if database and database in DATABASE_TECH_MAP:
            return DATABASE_TECH_MAP[database]

        # Check dominant language
        languages = scan_dict.get("languages", {})
        if languages:
            dominant = max(languages, key=languages.get)
            if dominant.lower() in LANGUAGE_TECH_MAP:
                return LANGUAGE_TECH_MAP[dominant.lower()]

        return TechnologyType.PYTHON

    @staticmethod
    def build_dependency_list(scan_dict: dict) -> list[str]:
        """Convert scanner dependencies to string list for UpgradeRequest.

        Format: "package_name==version" if version known, else "package_name"
        """
        deps = scan_dict.get("dependencies", [])
        result = []
        for dep in deps:
            name = dep.get("name", "")
            version = dep.get("version")
            if name:
                if version:
                    result.append(f"{name}=={version}")
                else:
                    result.append(name)
        return result

    @staticmethod
    def build_integration_list(scan_dict: dict) -> list[str]:
        """Infer integration points from the dependency graph.

        Looks at database connections, external service clients,
        and framework usage to identify integration surfaces.
        """
        integrations = []
        deps = {d.get("name", "").lower() for d in scan_dict.get("dependencies", [])}

        # Database integrations
        database = scan_dict.get("database", "")
        if database:
            integrations.append(f"{database} database connections")

        # Framework integrations
        if "fastapi" in deps or "flask" in deps or "django" in deps:
            integrations.append("Web API layer")
        if "celery" in deps:
            integrations.append("Celery task queue")
        if "airflow" in deps or "apache-airflow" in deps:
            integrations.append("Airflow DAGs")
        if "boto3" in deps or "botocore" in deps:
            integrations.append("AWS service integrations")
        if "pyspark" in deps:
            integrations.append("Spark jobs")
        if "redis" in deps:
            integrations.append("Redis cache/messaging")
        if "kafka" in deps or "confluent-kafka" in deps:
            integrations.append("Kafka streaming")
        if "requests" in deps or "httpx" in deps:
            integrations.append("External HTTP API clients")

        return integrations

    @staticmethod
    def build_notes(scan_dict: dict) -> str:
        """Build enriched notes from scanner risk flags and graph stats.

        This gives the LLM additional context about what the scanner
        already detected deterministically.
        """
        parts = []

        # Include scanner risk flags
        risk_flags = scan_dict.get("risk_flags", [])
        if risk_flags:
            parts.append("Scanner risk flags:")
            for flag in risk_flags:
                parts.append(f"  - [{flag['component']}] {flag['reason']}")

        # Include graph stats
        graph = scan_dict.get("dependency_graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        if nodes:
            source_count = sum(1 for n in nodes if n.get("type") == "source")
            pkg_count = sum(1 for n in nodes if n.get("type") == "package")
            parts.append(
                f"Dependency graph: {source_count} source files, "
                f"{pkg_count} packages, {len(edges)} edges."
            )

        # Include language breakdown
        languages = scan_dict.get("languages", {})
        if languages:
            lang_str = ", ".join(f"{k}: {v}" for k, v in languages.items())
            parts.append(f"Languages: {lang_str}")

        return "\n".join(parts) if parts else ""

    @classmethod
    def scan_result_to_request(
        cls,
        scan_dict: dict,
        target_version: str,
        current_version: str | None = None,
        environment: str = "production",
    ) -> UpgradeRequest:
        """Convert a ScanResult dict into an UpgradeRequest.

        This is the main adapter method — the bridge between the two systems.

        Args:
            scan_dict: Output of ScanResult.to_dict()
            target_version: e.g., "PostgreSQL 16" or "Python 3.12"
            current_version: Explicit current version, or auto-detected
            environment: "production" or "staging"
        """
        tech_type = cls.detect_technology_type(scan_dict)

        # Auto-detect current version from scan context if not provided
        if not current_version:
            database = scan_dict.get("database", "")
            if database and tech_type == TechnologyType.DATABASE:
                current_version = f"{database} (version detected by scanner)"
            else:
                current_version = f"{tech_type.value} (current)"

        return UpgradeRequest(
            technology_type=tech_type,
            current_version=current_version,
            target_version=target_version,
            dependencies=cls.build_dependency_list(scan_dict),
            integrations=cls.build_integration_list(scan_dict),
            environment=environment,
            notes=cls.build_notes(scan_dict),
        )

    @classmethod
    def scan_and_build_request(
        cls,
        repo_path: str,
        target_version: str,
        current_version: str | None = None,
        environment: str = "production",
    ) -> tuple[dict, UpgradeRequest]:
        """One-shot: scan a repo and produce an UpgradeRequest.

        Returns:
            Tuple of (scan_result_dict, upgrade_request)
        """
        scan_dict = cls.scan_repository(repo_path)
        request = cls.scan_result_to_request(
            scan_dict=scan_dict,
            target_version=target_version,
            current_version=current_version,
            environment=environment,
        )
        return scan_dict, request

"""Load and validate knowledge documents from JSON files.

On application startup, all JSON files under the knowledge/ directory are
read, validated, and returned as a flat list ready for ChromaDB ingestion.
"""

import json
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

# Required metadata fields for every knowledge document
REQUIRED_METADATA_FIELDS = {"technology_type", "source", "topic"}

VALID_TECH_TYPES = {"database", "emr", "python", "mwaa"}
VALID_TOPICS = {"version", "dependency", "config", "integration"}
VALID_VALIDATION_CHECKS = {
    "regression", "build", "integration", "data", "performance", "rollback",
}
VALID_RISK_HINTS = {"Low", "Medium", "High", "Critical"}


def _knowledge_root() -> Path:
    """Return the absolute path to the knowledge directory."""
    return Path(settings.knowledge_dir)


def _validate_document(doc: dict, source_file: str) -> dict | None:
    """Validate a single knowledge document. Returns cleaned doc or None."""
    doc_id = doc.get("id")
    text = doc.get("text", "").strip()
    metadata = dict(doc.get("metadata", {}))

    if not doc_id:
        logger.warning("Skipping document in %s: missing 'id'", source_file)
        return None
    if not text or len(text) < 20:
        logger.warning("Skipping document %s in %s: text too short", doc_id, source_file)
        return None
    if not REQUIRED_METADATA_FIELDS.issubset(metadata.keys()):
        missing = REQUIRED_METADATA_FIELDS - set(metadata.keys())
        logger.warning(
            "Skipping document %s in %s: missing metadata fields %s",
            doc_id, source_file, missing,
        )
        return None
    if metadata["technology_type"] not in VALID_TECH_TYPES:
        logger.warning(
            "Skipping document %s: invalid technology_type '%s'",
            doc_id, metadata["technology_type"],
        )
        return None
    if metadata["topic"] not in VALID_TOPICS:
        logger.warning(
            "Skipping document %s: invalid topic '%s'",
            doc_id, metadata["topic"],
        )
        return None

    # Validate optional risk_hint
    risk_hint = metadata.get("risk_hint")
    if risk_hint and risk_hint not in VALID_RISK_HINTS:
        logger.warning(
            "Document %s: invalid risk_hint '%s', removing it",
            doc_id, risk_hint,
        )
        metadata.pop("risk_hint", None)

    # Validate optional validation_checks — serialize list to CSV for ChromaDB
    raw_checks = metadata.get("validation_checks")
    if raw_checks:
        if isinstance(raw_checks, list):
            valid = [c for c in raw_checks if c in VALID_VALIDATION_CHECKS]
            metadata["validation_checks"] = ",".join(valid) if valid else ""
        else:
            metadata["validation_checks"] = str(raw_checks)

    return {"id": doc_id, "text": text, "metadata": metadata}


def load_from_directory() -> list[dict]:
    """Load all valid knowledge documents from the knowledge/ directory.

    Reads every .json file, validates each document, and returns a flat
    list of {id, text, metadata} dicts ready for ingestion.
    """
    root = _knowledge_root()
    if not root.is_dir():
        logger.warning("Knowledge directory not found: %s", root)
        return []

    all_docs: list[dict] = []
    json_files = sorted(root.rglob("*.json"))

    for json_path in json_files:
        # Skip template files
        if json_path.name.startswith("_"):
            continue

        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read %s: %s", json_path, exc)
            continue

        documents = raw.get("documents", [])
        if not isinstance(documents, list):
            logger.warning("File %s: 'documents' is not a list, skipping", json_path)
            continue

        for doc in documents:
            validated = _validate_document(doc, str(json_path.name))
            if validated:
                all_docs.append(validated)

    logger.info(
        "Loaded %d knowledge documents from %d files",
        len(all_docs), len(json_files),
    )
    return all_docs


def get_knowledge_stats() -> dict[str, int]:
    """Return document counts grouped by technology_type."""
    docs = load_from_directory()
    stats: dict[str, int] = {}
    for doc in docs:
        tech = doc["metadata"].get("technology_type", "unknown")
        stats[tech] = stats.get(tech, 0) + 1
    return stats

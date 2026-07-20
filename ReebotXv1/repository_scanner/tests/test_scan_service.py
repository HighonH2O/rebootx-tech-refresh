"""End-to-end tests for the Scan Service orchestrator."""

import os
import json

from repository_scanner.services.scan_service import scan

FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), "fixtures", "sample_repo"
)


def test_full_scan_returns_result():
    """Full scan should return a ScanResult with all fields populated."""
    result = scan(FIXTURES_DIR)

    assert result.repository == "sample_repo"
    assert len(result.languages) > 0, "Should detect at least one language"
    assert len(result.dependencies) > 0, "Should find dependencies"


def test_detects_python():
    """Should detect Python as a language."""
    result = scan(FIXTURES_DIR)
    assert "Python" in result.languages, "Should detect Python files"
    assert result.languages["Python"] >= 3, "Should find at least 3 Python files"


def test_detects_sql():
    """Should detect SQL as a language."""
    result = scan(FIXTURES_DIR)
    assert "SQL" in result.languages, "Should detect SQL files"


def test_detects_postgresql():
    """Should detect PostgreSQL from psycopg2 dependency."""
    result = scan(FIXTURES_DIR)
    assert result.database == "PostgreSQL", "Should detect PostgreSQL"


def test_finds_risk_flags():
    """Should raise risk flags for known issues."""
    result = scan(FIXTURES_DIR)
    assert len(result.risk_flags) > 0, "Should find at least one risk"

    # psycopg2 should be flagged
    flagged_components = [r.component for r in result.risk_flags]
    assert "psycopg2" in flagged_components, "Should flag psycopg2"


def test_sqlalchemy_v1_flagged():
    """Should flag SQLAlchemy 1.x as a risk."""
    result = scan(FIXTURES_DIR)
    flagged_components = [r.component for r in result.risk_flags]
    assert any("SQLAlchemy" in c for c in flagged_components), \
        "Should flag SQLAlchemy 1.x"


def test_dependency_graph_has_nodes():
    """Graph should have source, package, and database nodes."""
    result = scan(FIXTURES_DIR)

    assert len(result.graph_nodes) > 0, "Graph should have nodes"
    assert len(result.graph_edges) > 0, "Graph should have edges"

    node_types = {n.type for n in result.graph_nodes}
    assert "source" in node_types, "Should have source file nodes"
    assert "package" in node_types, "Should have package nodes"
    assert "database" in node_types, "Should have database node"


def test_graph_connects_driver_to_database():
    """psycopg2 should connect to PostgreSQL in the graph."""
    result = scan(FIXTURES_DIR)

    pg_edge = next(
        (e for e in result.graph_edges
         if e.source == "psycopg2" and e.target == "PostgreSQL"),
        None,
    )
    assert pg_edge is not None, "psycopg2 → PostgreSQL edge should exist"


def test_graph_connects_source_to_package():
    """Source files should connect to the packages they import."""
    result = scan(FIXTURES_DIR)

    # db.py should connect to psycopg2
    db_to_psycopg = next(
        (e for e in result.graph_edges
         if "db.py" in e.source and e.target == "psycopg2"),
        None,
    )
    assert db_to_psycopg is not None, "db.py → psycopg2 edge should exist"


def test_to_dict_produces_valid_json():
    """ScanResult.to_dict() should produce valid, serializable JSON."""
    result = scan(FIXTURES_DIR)
    output = result.to_dict()

    # Should not raise
    json_str = json.dumps(output, indent=2)
    assert len(json_str) > 0

    # Verify structure
    parsed = json.loads(json_str)
    assert "repository" in parsed
    assert "languages" in parsed
    assert "dependencies" in parsed
    assert "database" in parsed
    assert "risk_flags" in parsed
    assert "dependency_graph" in parsed
    assert "nodes" in parsed["dependency_graph"]
    assert "edges" in parsed["dependency_graph"]


def test_scan_empty_repo(tmp_path):
    """Scanning an empty directory should not crash."""
    result = scan(str(tmp_path))
    assert result.repository == tmp_path.name
    assert len(result.languages) == 0
    assert len(result.dependencies) == 0
    assert result.database == ""

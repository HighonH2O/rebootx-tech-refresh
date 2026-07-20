"""Tests for the Dependency Extractor (extractor.py)."""

import os
from pathlib import Path

from repository_scanner.scanner.traversal import discover_files
from repository_scanner.scanner.classifier import classify
from repository_scanner.scanner.extractor import extract_all

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "sample_repo")


def test_extracts_requirements_txt_deps():
    """Should extract dependencies with versions from requirements.txt."""
    files = discover_files(FIXTURES_DIR)
    files = classify(files)
    deps = extract_all(files)

    dep_names = {d.name.lower() for d in deps}

    assert "psycopg2" in dep_names, "Should find psycopg2"
    assert "sqlalchemy" in dep_names, "Should find SQLAlchemy"
    assert "pandas" in dep_names, "Should find pandas"
    assert "fastapi" in dep_names, "Should find fastapi"


def test_extracts_versions():
    """Dependencies from requirements.txt should have versions."""
    files = discover_files(FIXTURES_DIR)
    files = classify(files)
    deps = extract_all(files)

    psycopg2_dep = next((d for d in deps if d.name.lower() == "psycopg2"), None)
    assert psycopg2_dep is not None
    assert psycopg2_dep.version == "2.9.3"

    sqlalchemy_dep = next((d for d in deps if d.name.lower() == "sqlalchemy"), None)
    assert sqlalchemy_dep is not None
    assert sqlalchemy_dep.version == "1.4.39"


def test_extracts_ast_imports():
    """Should extract imports from Python source files via AST."""
    files = discover_files(FIXTURES_DIR)
    files = classify(files)
    _ = extract_all(files)  # this populates file.imports

    # Find db.py and check its imports
    db_file = next((f for f in files if f.path.name == "db.py"), None)
    assert db_file is not None
    assert "psycopg2" in db_file.imports, "db.py should import psycopg2"
    assert "sqlalchemy" in db_file.imports, "db.py should import sqlalchemy"

    # Find etl.py and check its imports
    etl_file = next((f for f in files if f.path.name == "etl.py"), None)
    assert etl_file is not None
    assert "pandas" in etl_file.imports or "pd" in etl_file.imports, \
        "etl.py should import pandas"


def test_merge_deduplicates():
    """Should not have duplicate entries for the same package."""
    files = discover_files(FIXTURES_DIR)
    files = classify(files)
    deps = extract_all(files)

    # psycopg2 appears in both requirements.txt AND db.py imports
    # but should only appear once in the final list
    psycopg2_count = sum(1 for d in deps if d.name.lower() == "psycopg2")
    assert psycopg2_count == 1, f"psycopg2 should appear once, found {psycopg2_count}"


def test_requirements_txt_parsing_edge_cases(tmp_path):
    """Should handle comments, blank lines, and flags in requirements.txt."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text(
        "# This is a comment\n"
        "\n"
        "requests==2.31.0\n"
        "  # Another comment\n"
        "-e ./local-package\n"
        "numpy>=1.24\n"
    )
    (tmp_path / "app.py").write_text("import requests\n")

    files = discover_files(str(tmp_path))
    files = classify(files)
    deps = extract_all(files)

    dep_names = {d.name.lower() for d in deps}
    assert "requests" in dep_names
    assert "numpy" in dep_names

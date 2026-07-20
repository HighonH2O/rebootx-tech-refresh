"""Tests for the File Discovery component (traversal.py)."""

import os
from pathlib import Path

from repository_scanner.scanner.traversal import discover_files

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "sample_repo")


def test_discovers_all_files():
    """Should discover all files in the sample repo."""
    files = discover_files(FIXTURES_DIR)
    assert len(files) > 0, "Should discover at least one file"

    # Check that we got the expected files
    relative_paths = [f.relative_path for f in files]
    assert any("main.py" in p for p in relative_paths), "Should find main.py"
    assert any("db.py" in p for p in relative_paths), "Should find db.py"
    assert any("etl.py" in p for p in relative_paths), "Should find etl.py"
    assert any("requirements.txt" in p for p in relative_paths), "Should find requirements.txt"
    assert any(".sql" in p for p in relative_paths), "Should find SQL files"


def test_ignores_git_directory(tmp_path):
    """Should skip .git directories."""
    # Create a temp repo with a .git folder
    (tmp_path / ".git" / "objects").mkdir(parents=True)
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")
    (tmp_path / "real_file.py").write_text("print('hello')")

    files = discover_files(str(tmp_path))
    relative_paths = [f.relative_path for f in files]

    assert "real_file.py" in relative_paths, "Should find real files"
    assert not any(".git" in p for p in relative_paths), "Should ignore .git"


def test_ignores_venv(tmp_path):
    """Should skip venv directories."""
    (tmp_path / "venv" / "lib").mkdir(parents=True)
    (tmp_path / "venv" / "lib" / "site.py").write_text("# venv file")
    (tmp_path / "app.py").write_text("print('app')")

    files = discover_files(str(tmp_path))
    relative_paths = [f.relative_path for f in files]

    assert "app.py" in relative_paths
    assert not any("venv" in p for p in relative_paths)


def test_ignores_pycache(tmp_path):
    """Should skip __pycache__ directories."""
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "module.cpython-312.pyc").write_bytes(b"")
    (tmp_path / "module.py").write_text("x = 1")

    files = discover_files(str(tmp_path))
    relative_paths = [f.relative_path for f in files]

    assert "module.py" in relative_paths
    assert not any("__pycache__" in p for p in relative_paths)


def test_file_extensions():
    """Each discovered file should have its extension populated."""
    files = discover_files(FIXTURES_DIR)
    for f in files:
        if f.path.suffix:
            assert f.extension == f.path.suffix.lower()


def test_raises_on_invalid_path():
    """Should raise ValueError for a nonexistent path."""
    try:
        discover_files("/nonexistent/path/that/does/not/exist")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

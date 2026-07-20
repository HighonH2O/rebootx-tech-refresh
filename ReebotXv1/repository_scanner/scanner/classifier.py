"""Component 2: Language Detector — Tag each file with its detected language.

Input:  list[FileInfo] (from traversal.py)
Output: Same list, but each FileInfo.language is now filled in.

V1 focuses on: Python, SQL, and config files.
"""

from repository_scanner.models.file_info import FileInfo

# Extension → language mapping
EXTENSION_MAP = {
    ".py": "Python",
    ".sql": "SQL",
    ".txt": "Config",
    ".toml": "Config",
    ".yaml": "Config",
    ".yml": "Config",
    ".cfg": "Config",
    ".ini": "Config",
    ".json": "Config",
    ".md": "Documentation",
    ".rst": "Documentation",
}

# Specific filenames → language mapping (takes priority over extension)
FILENAME_MAP = {
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "requirements.txt": "Python (deps)",
    "pyproject.toml": "Python (config)",
    "setup.py": "Python (config)",
    "setup.cfg": "Python (config)",
    "Pipfile": "Python (deps)",
    "Makefile": "Make",
    ".gitignore": "Git",
    ".dockerignore": "Docker",
}


def classify(files: list[FileInfo]) -> list[FileInfo]:
    """Classify each file by language based on its filename and extension.

    Args:
        files: List of FileInfo objects from traversal.py.

    Returns:
        Same list with each FileInfo.language populated.
    """
    for f in files:
        # Priority 1: Check exact filename
        if f.path.name in FILENAME_MAP:
            f.language = FILENAME_MAP[f.path.name]
        # Priority 2: Check file extension
        elif f.extension in EXTENSION_MAP:
            f.language = EXTENSION_MAP[f.extension]
        # Fallback
        else:
            f.language = "Other"

    return files

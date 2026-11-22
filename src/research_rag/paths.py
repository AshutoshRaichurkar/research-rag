"""Absolute paths to project folders, so code works from any working directory.

Notebooks live a few folders deep (notebooks/week-1/day-02-.../), so relative
paths like "data/papers" would break there. Import these instead:

    from research_rag.paths import PAPERS_DIR
"""

from pathlib import Path

# This file is src/research_rag/paths.py, so the project root is two folders up from its folder.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


DATA_DIR = PROJECT_ROOT / "data"
PAPERS_DIR = DATA_DIR / "papers"
EVALS_DIR = PROJECT_ROOT / "evals"
ENV_FILE = PROJECT_ROOT / ".env"

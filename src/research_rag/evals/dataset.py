"""The golden dataset: hand-checked questions with known answers and chunks."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ValidationError

from research_rag.paths import EVALS_DIR

GOLDEN_FILE = EVALS_DIR / "golden.jsonl"

QuestionType = Literal[
    "factual", "conceptual", "multi_chunk", "exact_term", "unanswerable", "adversarial"
]


class GoldenItem(BaseModel):
    id: str
    question: str
    expected_answer: str
    relevant_chunk_ids: list[str]
    type: QuestionType


class GoldenFileError(ValueError):
    """A line in the golden file is broken."""


def load_golden(path: Path = GOLDEN_FILE) -> list[GoldenItem]:
    """Read every line. Fail loudly with the line number if one is broken."""
    items = []
    lines = path.read_text().splitlines()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = GoldenItem.model_validate_json(line)
        except ValidationError as error:
            raise GoldenFileError(f"{path.name} line {line_number}: {error}") from error
        items.append(item)
    return items

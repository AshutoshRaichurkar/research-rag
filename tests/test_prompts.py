from research_rag.generation.prompts import NO_ANSWER, build_prompt
from research_rag.retrieval.search import RetrievedChunk


def make_chunk(number: int) -> RetrievedChunk:
    return RetrievedChunk(
        id=f"paper.pdf::{number:04d}",
        source="paper.pdf",
        page_number=number,
        text=f"text of chunk {number}",
        similarity=0.5,
    )


def test_prompt_numbers_chunks_with_source_and_page():
    prompt = build_prompt("What is X?", [make_chunk(4), make_chunk(7)])
    assert "[1] (paper.pdf, page 4)" in prompt
    assert "[2] (paper.pdf, page 7)" in prompt


def test_prompt_contains_question_and_no_answer_rule():
    prompt = build_prompt("What is X?", [make_chunk(1)])
    assert "Question: What is X?" in prompt
    assert NO_ANSWER in prompt

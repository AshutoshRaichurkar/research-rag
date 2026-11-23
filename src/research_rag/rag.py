"""Answer a question from the papers: search → prompt → LLM → citations."""

import argparse
import time

from pydantic import BaseModel

from research_rag.generation.citations import Citation, extract_citations
from research_rag.generation.llm import generate
from research_rag.generation.prompts import NO_ANSWER, PROMPT_VERSION, build_prompt
from research_rag.retrieval.search import RetrievedChunk, search


class Answer(BaseModel):
    """Everything about one answered question, so it can be shown, logged or evaluated."""

    question: str
    text: str
    citations: list[Citation]
    chunks: list[RetrievedChunk]
    answered: bool  # False when the model said it doesn't know
    prompt_version: str
    latency_ms: int


def answer(question: str, k: int = 5) -> Answer:
    """Run the full RAG pipeline for one question."""
    start = time.perf_counter()

    chunks = search(question, k=k)
    prompt = build_prompt(question, chunks)
    text = generate(prompt)
    citations = extract_citations(text, chunks)
    answered = NO_ANSWER.lower() not in text.lower()

    latency_ms = int((time.perf_counter() - start) * 1000)
    return Answer(
        question=question,
        text=text,
        citations=citations,
        chunks=chunks,
        answered=answered,
        prompt_version=PROMPT_VERSION,
        latency_ms=latency_ms,
    )


def main() -> None:
    """Command line: python -m research_rag.rag "your question" """
    parser = argparse.ArgumentParser(description="Ask the papers a question.")
    parser.add_argument("question", help="the question to answer")
    parser.add_argument("-k", type=int, default=5, help="how many chunks to retrieve")
    args = parser.parse_args()

    result = answer(args.question, k=args.k)

    print(result.text)
    print()
    if result.citations:
        print("Sources:")
        for citation in result.citations:
            print(f"  [{citation.number}] {citation.source}, page {citation.page_number}")
    print(f"\n({result.latency_ms} ms · prompt {result.prompt_version})")


if __name__ == "__main__":
    main()

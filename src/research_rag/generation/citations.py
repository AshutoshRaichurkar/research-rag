"""Turn [n] markers in an answer into paper + page citations."""

import re

from pydantic import BaseModel

from research_rag.retrieval.search import RetrievedChunk

CITATION_MARKER = re.compile(r"\[(\d+)\]")  # [1], [23], ... with the number captured


class Citation(BaseModel):
    """A source the answer points to."""

    number: int  # the [n] used in the answer
    chunk_id: str
    source: str
    page_number: int


def extract_citations(answer: str, chunks: list[RetrievedChunk]) -> list[Citation]:
    """Find every [n] in the answer and map it to the chunk it refers to."""
    citations = []
    seen = set()

    for match in CITATION_MARKER.finditer(answer):
        number = int(match.group(1))
        if number in seen:
            continue  # already listed
        if number < 1 or number > len(chunks):
            continue  # the model cited a chunk it was never given: drop it
        seen.add(number)

        chunk = chunks[number - 1]  # [1] is the first chunk, at position 0
        citation = Citation(
            number=number,
            chunk_id=chunk.id,
            source=chunk.source,
            page_number=chunk.page_number,
        )
        citations.append(citation)

    return citations

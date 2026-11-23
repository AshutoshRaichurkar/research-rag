from research_rag.generation.citations import extract_citations
from research_rag.retrieval.search import RetrievedChunk


def make_chunks(count: int) -> list[RetrievedChunk]:
    chunks = []
    for number in range(1, count + 1):
        chunk = RetrievedChunk(
            id=f"paper.pdf::{number:04d}",
            source="paper.pdf",
            page_number=number * 10,
            text="...",
            similarity=0.5,
        )
        chunks.append(chunk)
    return chunks


def test_citation_maps_number_to_page():
    citations = extract_citations("A fact [2].", make_chunks(3))
    assert len(citations) == 1
    assert citations[0].page_number == 20


def test_repeats_listed_once_and_unknown_numbers_dropped():
    citations = extract_citations("One [2]. Two [2][3]. Made up [9].", make_chunks(5))
    numbers = []
    for citation in citations:
        numbers.append(citation.number)
    assert numbers == [2, 3]


def test_no_citations_gives_empty_list():
    assert extract_citations("No sources here.", make_chunks(3)) == []

import pytest

from research_rag.ingestion.chunker import ENCODING, chunk_pages, split_into_windows
from research_rag.ingestion.models import Page


def test_split_into_windows_overlaps():
    windows = split_into_windows(list(range(10)), size=4, overlap=1)
    assert windows == [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9]]


def test_split_into_windows_last_window_can_be_shorter():
    windows = split_into_windows(list(range(10)), size=4, overlap=0)
    assert windows[-1] == [8, 9]


def test_split_into_windows_rejects_overlap_as_big_as_size():
    with pytest.raises(ValueError):
        split_into_windows(list(range(10)), size=4, overlap=4)


def test_chunk_pages_with_no_pages_returns_empty_list():
    assert chunk_pages([], size=200, overlap=40) == []


def make_pages() -> list[Page]:
    """Two fake pages of numbered words, so every part of the text is unique."""
    first_words = []
    for number in range(0, 300):
        first_words.append(f"word{number}")

    second_words = []
    for number in range(300, 600):
        second_words.append(f"word{number}")

    page_one = Page(source="test.pdf", page_number=1, text=" ".join(first_words))
    page_two = Page(source="test.pdf", page_number=2, text=" ".join(second_words))
    return [page_one, page_two]

def test_chunk_pages_respects_size_and_builds_ids():
    chunks = chunk_pages(make_pages(), size=200, overlap=40)
    assert len(chunks) > 1
    assert chunks[0].id == "test.pdf::0000"
    for chunk in chunks:
        assert chunk.token_count <= 200


def test_chunk_pages_tracks_the_starting_page():
    chunks = chunk_pages(make_pages(), size=200, overlap=40)
    assert chunks[0].page_number == 1
    assert chunks[-1].page_number == 2


def test_consecutive_chunks_share_the_overlap():
    chunks = chunk_pages(make_pages(), size=200, overlap=40)
    start_of_second = chunks[1].text[:50]        # the first 50 characters of chunk 1
    assert start_of_second in chunks[0].text      # ...must also appear in chunk 0
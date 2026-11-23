import psycopg
import pytest

from research_rag.retrieval.search import RetrievedChunk, search


def test_search_returns_k_results_best_first():
    try:
        results = search("Does LoRA add inference latency?", k=3)
    except psycopg.OperationalError:
        pytest.skip("Postgres is not running (run: make up)")

    assert len(results) == 3
    assert isinstance(results[0], RetrievedChunk)
    assert results[0].similarity >= results[1].similarity >= results[2].similarity

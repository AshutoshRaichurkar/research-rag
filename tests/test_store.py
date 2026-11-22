"""Tests for the vector store. They run in a throwaway database, never the real one."""

import numpy as np
import psycopg
import pytest

from research_rag.config import get_settings
from research_rag.embeddings.store import (
    connect,
    count_chunks,
    delete_stale_chunks,
    upsert_chunks,
)
from research_rag.ingestion.models import Chunk
from research_rag.paths import PROJECT_ROOT

TEST_DB = "research_rag_test"


@pytest.fixture
def test_database(monkeypatch):
    """Create a fresh test database with our table, point the code at it, then drop it."""
    main_url = get_settings().database_url
    try:
        admin = psycopg.connect(main_url, autocommit=True)
    except psycopg.OperationalError:
        pytest.skip("Postgres is not running (run: make up)")

    admin.execute(f"DROP DATABASE IF EXISTS {TEST_DB}")
    admin.execute(f"CREATE DATABASE {TEST_DB}")

    test_url = main_url.rsplit("/", 1)[0] + "/" + TEST_DB  # same server, different database
    with psycopg.connect(test_url, autocommit=True) as conn:
        conn.execute((PROJECT_ROOT / "db" / "init.sql").read_text())

    monkeypatch.setenv("DATABASE_URL", test_url)  # connect() now uses the test DB
    get_settings.cache_clear()

    yield  # the test runs here

    get_settings.cache_clear()
    admin.execute(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)")
    admin.close()


def make_chunks(count: int) -> list[Chunk]:
    """Fake chunks: test.pdf::0000, test.pdf::0001, ..."""
    chunks = []
    for index in range(count):
        chunk = Chunk(
            id=f"test.pdf::{index:04d}",
            source="test.pdf",
            page_number=1,
            chunk_index=index,
            text=f"chunk number {index}",
            token_count=3,
        )
        chunks.append(chunk)
    return chunks


def fake_embeddings(count: int) -> np.ndarray:
    """Random length-1 vectors, so the tests don't need the embedding model."""
    vectors = np.random.default_rng(0).normal(size=(count, 384))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def test_upsert_twice_does_not_duplicate(test_database):
    chunks = make_chunks(3)
    with connect() as conn:
        upsert_chunks(conn, chunks, fake_embeddings(3))
        upsert_chunks(conn, chunks, fake_embeddings(3))
        assert count_chunks(conn) == 3


def test_upsert_updates_changed_text(test_database):
    chunks = make_chunks(1)
    with connect() as conn:
        upsert_chunks(conn, chunks, fake_embeddings(1))
        chunks[0].text = "new text"
        upsert_chunks(conn, chunks, fake_embeddings(1))
        stored = conn.execute("SELECT text FROM document_chunks").fetchone()[0]
        assert stored == "new text"


def test_delete_stale_chunks_removes_only_missing_ids(test_database):
    chunks = make_chunks(5)
    with connect() as conn:
        upsert_chunks(conn, chunks, fake_embeddings(5))
        keep_ids = [chunks[0].id, chunks[1].id, chunks[2].id]
        deleted = delete_stale_chunks(conn, keep_ids)
        assert deleted == 2
        assert count_chunks(conn) == 3

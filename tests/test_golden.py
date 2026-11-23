from collections import Counter

import psycopg
import pytest

from research_rag.embeddings.store import connect
from research_rag.evals.dataset import load_golden

ALL_TYPES = {"factual", "conceptual", "multi_chunk", "exact_term", "unanswerable", "adversarial"}
NO_CHUNK_TYPES = {"unanswerable", "adversarial"}


def test_every_line_parses():
    assert len(load_golden()) >= 15


def test_ids_are_unique():
    counts = Counter()
    for item in load_golden():
        counts[item.id] += 1
    duplicates = []
    for item_id, count in counts.items():
        if count > 1:
            duplicates.append(item_id)
    assert duplicates == []


def test_every_type_is_covered():
    types = set()
    for item in load_golden():
        types.add(item.type)
    assert types == ALL_TYPES


def test_chunk_labels_match_type():
    for item in load_golden():
        if item.type in NO_CHUNK_TYPES:
            assert item.relevant_chunk_ids == [], item.id
        else:
            assert item.relevant_chunk_ids, f"{item.id} has no relevant chunks"


def test_every_chunk_id_exists_in_database():
    try:
        conn = connect()
    except psycopg.OperationalError:
        pytest.skip("database not running")
    with conn:
        rows = conn.execute("SELECT id FROM document_chunks").fetchall()
    known_ids = set()
    for row in rows:
        known_ids.add(row[0])
    for item in load_golden():
        for chunk_id in item.relevant_chunk_ids:
            assert chunk_id in known_ids, f"{item.id}: unknown chunk {chunk_id}"

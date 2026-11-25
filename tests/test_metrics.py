import pytest

from research_rag.evals.metrics import recall_at_k, reciprocal_rank

# (retrieved chunk IDs, relevant chunk IDs). Relevant is at position 1, 3, not found, 2.
EXAMPLE = [
    (["a", "x", "x", "x", "x"], ["a"]),
    (["x", "x", "b", "x", "x"], ["b"]),
    (["x", "x", "x", "x", "x"], ["c"]),
    (["x", "d", "x", "x", "x"], ["d"]),
]


def test_recall_at_5_matches_worked_example():
    scores = []
    for retrieved, relevant in EXAMPLE:
        scores.append(recall_at_k(retrieved, relevant, k=5))
    assert sum(scores) / len(scores) == 0.75


def test_mrr_matches_worked_example():
    scores = []
    for retrieved, relevant in EXAMPLE:
        scores.append(reciprocal_rank(retrieved, relevant))
    assert sum(scores) / len(scores) == pytest.approx(0.458, abs=0.001)


def test_recall_depends_on_k():
    retrieved = ["x", "x", "b"]
    assert recall_at_k(retrieved, ["b"], k=2) == 0.0
    assert recall_at_k(retrieved, ["b"], k=3) == 1.0


def test_any_relevant_chunk_counts():
    assert reciprocal_rank(["x", "q2", "q1"], ["q1", "q2"]) == 0.5

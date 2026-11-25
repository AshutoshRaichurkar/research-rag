"""Retrieval metrics. Each function scores one question."""


def recall_at_k(retrieved: list[str], relevant: list[str], k: int) -> float:
    """1.0 if any relevant chunk is in the top k results, else 0.0."""
    top_k = retrieved[:k]
    for chunk_id in top_k:
        if chunk_id in relevant:
            return 1.0
    return 0.0


def reciprocal_rank(retrieved: list[str], relevant: list[str]) -> float:
    """1 / position of the first relevant chunk (1-based). 0.0 if none is found."""
    for position, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant:
            return 1 / position
    return 0.0

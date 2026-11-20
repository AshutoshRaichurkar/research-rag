"""Turn text into embeddings (lists of 384 numbers) with a sentence-transformers model."""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from research_rag.config import get_settings


@lru_cache
def get_model() -> SentenceTransformer:
    """Load the embedding model the first time it's needed, then reuse it."""
    return SentenceTransformer(get_settings().embedding_model)


def embed_texts(texts: list[str], batch_size: int = 64) -> np.ndarray:
    """Embed many texts at once. Returns one row of 384 numbers per text, each of length 1."""
    model = get_model()
    return model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,  # length 1, so cosine is all that matters
        show_progress_bar=len(texts) > batch_size,
    )

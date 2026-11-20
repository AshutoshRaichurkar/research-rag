"""Write chunks and their embeddings to Postgres (pgvector)."""

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from research_rag.config import get_settings
from research_rag.ingestion.models import Chunk

UPSERT_SQL = """
INSERT INTO document_chunks (id, source, page_number, chunk_index, text, token_count, embedding)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
    source      = EXCLUDED.source,
    page_number = EXCLUDED.page_number,
    chunk_index = EXCLUDED.chunk_index,
    text        = EXCLUDED.text,
    token_count = EXCLUDED.token_count,
    embedding   = EXCLUDED.embedding
"""


def connect() -> psycopg.Connection:
    """Open a database connection that understands the vector type."""
    conn = psycopg.connect(get_settings().database_url)
    register_vector(conn)  # lets psycopg send NumPy arrays as pgvector vectors
    return conn


def upsert_chunks(conn: psycopg.Connection, chunks: list[Chunk], embeddings: np.ndarray) -> None:
    """Insert new chunks, or update the ones that already exist (matched on id)."""
    rows = []
    for chunk, embedding in zip(chunks, embeddings, strict=True):
        row = (
            chunk.id,
            chunk.source,
            chunk.page_number,
            chunk.chunk_index,
            chunk.text,
            chunk.token_count,
            embedding,
        )
        rows.append(row)

    with conn.cursor() as cursor:
        cursor.executemany(UPSERT_SQL, rows)
    conn.commit()


def count_chunks(conn: psycopg.Connection) -> int:
    """How many chunks are in the table."""
    return conn.execute("SELECT count(*) FROM document_chunks").fetchone()[0]


def delete_stale_chunks(conn: psycopg.Connection, keep_ids: list[str]) -> int:
    """Delete rows whose id is not in keep_ids (chunks that no longer exist). Returns how many."""
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM document_chunks WHERE NOT (id = ANY(%s))", (keep_ids,))
        deleted = cursor.rowcount
    conn.commit()
    return deleted

-- Runs once, the first time the database volume is created.
-- To re-run it: docker compose down -v && docker compose up -d

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    id           TEXT PRIMARY KEY,
    source       TEXT NOT NULL,
    page_number  INT  NOT NULL,
    chunk_index  INT  NOT NULL,
    text         TEXT NOT NULL,
    token_count  INT  NOT NULL,
    embedding    vector(384) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- HNSW index: makes "find the nearest vectors" fast (built for cosine distance)
CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw
    ON document_chunks USING hnsw (embedding vector_cosine_ops);

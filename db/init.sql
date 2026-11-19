-- Runs once, the first time the database volume is created.
-- To re-run it: docker compose down -v && docker compose up -d

CREATE EXTENSION IF NOT EXISTS vector;

-- Day 3: the document_chunks table and its HNSW index go here.

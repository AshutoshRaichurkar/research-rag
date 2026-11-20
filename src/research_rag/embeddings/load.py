"""Embed every chunk from chunks.jsonl and store it in Postgres."""

import time
from pathlib import Path

from research_rag.embeddings.embedder import embed_texts
from research_rag.embeddings.store import connect, count_chunks, delete_stale_chunks, upsert_chunks
from research_rag.ingestion.models import Chunk
from research_rag.ingestion.run import CHUNKS_FILE

BATCH_SIZE = 256


def read_chunks(path: Path = CHUNKS_FILE) -> list[Chunk]:
    """Read chunks.jsonl back into validated Chunk objects."""
    chunks = []
    with open(path) as file:
        for line in file:
            chunks.append(Chunk.model_validate_json(line))
    return chunks


def load_all() -> None:
    """Embed and store every chunk, one batch at a time."""
    chunks = read_chunks()
    print(f"Read {len(chunks)} chunks from {CHUNKS_FILE.name}")
    start = time.perf_counter()

    with connect() as conn:
        for begin in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[begin : begin + BATCH_SIZE]

            texts = []
            for chunk in batch:
                texts.append(chunk.text)

            embeddings = embed_texts(texts)
            upsert_chunks(conn, batch, embeddings)
            print(f"  stored {begin + len(batch):>5} / {len(chunks)}")

        keep_ids = []
        for chunk in chunks:
            keep_ids.append(chunk.id)
        deleted = delete_stale_chunks(conn, keep_ids)
        print(f"  removed {deleted} stale chunks")

        total = count_chunks(conn)

    seconds = time.perf_counter() - start
    print(f"Done: {total} chunks in the database ({seconds:.1f} s)")


if __name__ == "__main__":
    load_all()

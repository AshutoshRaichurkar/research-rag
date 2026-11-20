"""Run ingestion for every PDF: load → clean → chunk, then save the chunks to a JSONL file."""

from pathlib import Path

from research_rag.config import get_settings
from research_rag.ingestion.chunker import chunk_pages
from research_rag.ingestion.loader import load_pdf
from research_rag.ingestion.models import Chunk
from research_rag.paths import DATA_DIR

CHUNKS_FILE = DATA_DIR / "processed" / "chunks.jsonl"


def ingest_all() -> list[Chunk]:
    """Load, clean and chunk every PDF in the papers folder."""
    settings = get_settings()
    pdf_paths = sorted(settings.papers_dir.glob("*.pdf"))
    all_chunks = []

    for pdf_path in pdf_paths:
        pages = load_pdf(pdf_path)
        chunks = chunk_pages(pages, size=settings.chunk_size, overlap=settings.chunk_overlap)
        print(f"{pdf_path.name}: {len(pages):>3} pages -> {len(chunks):>4} chunks")
        all_chunks.extend(chunks)

    print(f"Total: {len(pdf_paths)} papers -> {len(all_chunks)} chunks")
    return all_chunks


def save_chunks(chunks: list[Chunk], path: Path = CHUNKS_FILE) -> None:
    """Write one chunk per line as JSON (the JSON Lines format)."""
    path.parent.mkdir(parents=True, exist_ok=True)     # create data/processed/ if needed
    with open(path, "w") as file:
        for chunk in chunks:
            file.write(chunk.model_dump_json() + "\n")
    print(f"Saved to {path}")


if __name__ == "__main__":
    save_chunks(ingest_all())
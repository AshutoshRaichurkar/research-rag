"""Find chunks by exact text, for labelling the golden dataset."""

from research_rag.embeddings.store import connect

FIND_SQL = """
SELECT id, page_number, text
FROM document_chunks
WHERE text ILIKE %(pattern)s
  AND (%(source)s::text IS NULL OR source = %(source)s)
ORDER BY id
"""


def find_chunks(phrase: str, source: str | None = None, preview: int = 150) -> None:
    """Print every chunk whose text contains the phrase (case-insensitive)."""
    params = {"pattern": f"%{phrase}%", "source": source}
    with connect() as conn:
        rows = conn.execute(FIND_SQL, params).fetchall()
    print(f"{len(rows)} chunk(s) contain {phrase!r}")
    for chunk_id, page_number, text in rows:
        start = text.lower().find(phrase.lower())
        snippet = text[max(start, 0) : start + preview].replace("\n", " ")
        print(f"  {chunk_id}  p.{page_number}  …{snippet}…")

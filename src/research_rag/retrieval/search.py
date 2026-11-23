"""Find the chunks whose meaning is closest to a question."""

from pydantic import BaseModel

from research_rag.embeddings.embedder import embed_texts
from research_rag.embeddings.store import connect


class RetrievedChunk(BaseModel):
    """One search result: a chunk plus how similar it is to the question."""

    id: str
    source: str
    page_number: int
    text: str
    similarity: float  # 1 = same meaning, 0 = unrelated


SEARCH_SQL = """
SELECT id, source, page_number, text,
       1 - (embedding <=> %(question)s) AS similarity
FROM document_chunks
ORDER BY embedding <=> %(question)s
LIMIT %(k)s
"""


def search(question: str, k: int = 5) -> list[RetrievedChunk]:
    """Embed the question and return the k chunks closest in meaning, best first."""
    question_vector = embed_texts([question])[0]

    with connect() as conn:
        rows = conn.execute(SEARCH_SQL, {"question": question_vector, "k": k}).fetchall()

    results = []
    for chunk_id, source, page_number, text, similarity in rows:
        result = RetrievedChunk(
            id=chunk_id,
            source=source,
            page_number=page_number,
            text=text,
            similarity=float(similarity),
        )
        results.append(result)
    return results

"""Prompt templates for answering questions from retrieved chunks."""

from research_rag.retrieval.search import RetrievedChunk

PROMPT_VERSION = "v1"  # change this whenever you edit the prompt, so results can be compared
NO_ANSWER = "I don't know based on the provided papers."

RAG_PROMPT = """You are a careful research assistant.
Answer the question using ONLY the numbered context below.

Rules:
- Cite every fact with the number of the context it came from, like [1] or [2][3].
- If the context does not contain the answer, reply exactly: "{no_answer}"
- Do not use outside knowledge. Keep the answer short.

Context:
{context}

Question: {question}
Answer:"""


def format_context(chunks: list[RetrievedChunk]) -> str:
    """Number each chunk and label it with its paper and page."""
    blocks = []
    for number, chunk in enumerate(chunks, start=1):
        block = f"[{number}] ({chunk.source}, page {chunk.page_number})\n{chunk.text}"
        blocks.append(block)
    return "\n\n".join(blocks)


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Fill the template with the rules, the numbered chunks and the question."""
    return RAG_PROMPT.format(
        no_answer=NO_ANSWER,
        context=format_context(chunks),
        question=question,
    )

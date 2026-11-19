"""Split clean text into overlapping, token-sized chunks."""

import tiktoken
from research_rag.ingestion.cleaner import clean_text
from research_rag.ingestion.models import Chunk, Page

# Same tokenizer as the Day 1 notebook (gpt-4o's). Counts are close estimates for any model.
ENCODING = tiktoken.get_encoding("o200k_base")


def split_into_windows(token_ids: list[int], size: int, overlap: int) -> list[list[int]]:
    """Cut a list of tokens into windows of `size`, each overlapping the previous by `overlap`."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    step = size - overlap
    windows = []

    for start in range(0, len(token_ids), step):
        window = token_ids[start : start + size]
        windows.append(window)
        if start + size >= len(token_ids):   # this window reached the end: stop
            break

    return windows

def chunk_pages(pages: list[Page], size: int, overlap: int) -> list[Chunk]:
    """Clean every page, join them into one token stream, and cut it into overlapping chunks."""
    all_tokens = []
    token_pages = []        # the page number of each token, same length as all_tokens

    for page in pages:
        cleaned = clean_text(page.text)
        if not cleaned:     # skip empty pages
            continue
        page_tokens = ENCODING.encode(cleaned + " ")   # the space keeps pages from gluing together
        all_tokens.extend(page_tokens)
        token_pages.extend([page.page_number] * len(page_tokens))

    token_windows = split_into_windows(all_tokens, size, overlap)
    page_windows = split_into_windows(token_pages, size, overlap)   # lines up with token_windows

    chunks = []
    for index in range(len(token_windows)):
        window = token_windows[index]
        source = pages[0].source
        chunk = Chunk(
            id=f"{source}::{index:04d}",          # e.g. "2106.09685.pdf::0003"
            source=source,
            page_number=page_windows[index][0],   # page of the chunk's first token
            chunk_index=index,
            text=ENCODING.decode(window).strip(),
            token_count=len(window),
        )
        chunks.append(chunk)

    return chunks
"""Data models for the ingestion pipeline: what a page and a chunk look like."""

from pydantic import BaseModel


class Page(BaseModel):
    """The text of one PDF page."""

    source: str          # file name, e.g. "2106.09685.pdf"
    page_number: int     # starts at 1, like humans count pages
    text: str


class Chunk(BaseModel):
    """A small piece of text, ready to embed and search."""

    id: str              # unique and stable (see the question below)
    source: str
    page_number: int     # the page where this chunk starts
    chunk_index: int    # position in the paper: 0, 1, 2, ...
    text: str
    token_count: int
"""Load PDFs into Page objects."""

from pathlib import Path

import pymupdf

from research_rag.ingestion.models import Page


def load_pdf(path: Path) -> list[Page]:
    """Read a PDF and return one Page per page, numbered from 1."""
    pages = []

    with pymupdf.open(path) as document:             # 'with' closes the file automatically
        for index, pdf_page in enumerate(document):  # index: 0, 1, 2 ...
            page = Page(
                source=path.name,                    # just the file name, not the full path
                page_number=index + 1,               # humans count from 1
                text=pdf_page.get_text(),            # the page's raw text
            )
            pages.append(page)

    return pages
"""Clean raw PDF text before chunking."""

import re
import unicodedata

ARXIV_WATERMARK = re.compile(r"^arXiv:\d{4}\.\d{4,5}v\d+.*$", re.MULTILINE)


def fix_ligatures(text: str) -> str:
    """Replace combined characters like 'ﬁ' with normal letters ('fi')."""
    return unicodedata.normalize("NFKC", text)


def join_hyphenated_words(text: str) -> str:
    """Rejoin words split across lines with a hyphen: 'indepen-\\ndent' -> 'independent'."""
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def remove_page_number(text: str) -> str:
    """Delete a page number if it's the first or last non-empty line of the page."""
    lines = text.strip().split("\n")

    if lines and lines[-1].strip().isdigit():  # last line is only a number
        lines = lines[:-1]
    if lines and lines[0].strip().isdigit():  # first line is only a number
        lines = lines[1:]

    return "\n".join(lines)


def remove_noise_lines(text: str) -> str:
    """Delete the arXiv watermark line and the page number."""
    text = ARXIV_WATERMARK.sub("", text)
    text = remove_page_number(text)
    return text


def collapse_whitespace(text: str) -> str:
    """Turn every run of spaces, tabs and line breaks into a single space."""
    return re.sub(r"\s+", " ", text).strip()


def remove_control_characters(text: str) -> str:
    """Drop invisible control characters (like NUL) that PDFs leave inside equations.

    Keeps line breaks and tabs, because later cleaning steps still need the line breaks.
    """
    kept = []
    for character in text:
        if character in "\n\t" or unicodedata.category(character) != "Cc":
            kept.append(character)
    return "".join(kept)


def clean_text(text: str) -> str:
    """Run every cleaning step, in order. Line-based steps must run before collapse_whitespace."""
    text = fix_ligatures(text)
    text = remove_control_characters(text)
    text = remove_noise_lines(text)
    text = join_hyphenated_words(text)
    text = collapse_whitespace(text)
    return text

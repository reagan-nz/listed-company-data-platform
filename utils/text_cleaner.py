"""Text normalization helpers.

These helpers exist to keep extracted *metadata* tidy. They are deliberately
conservative: this framework stores short snippets / titles only, never full
article or report bodies.
"""

import re

_WHITESPACE_RE = re.compile(r"\s+")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(text: str | None) -> str:
    """Collapse whitespace and strip control characters."""
    if not text:
        return ""
    text = _CONTROL_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def truncate(text: str | None, limit: int = 200) -> str:
    """Return a short, single-line snippet suitable for CSV cells.

    Used for titles / sample results / evidence sentences. Keeping this short
    enforces the "metadata only, no full text" policy at the storage boundary.
    """
    cleaned = clean_text(text)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "\u2026"


def first_sentence(text: str | None, limit: int = 200) -> str:
    """Return the first sentence of `text` (for evidence extraction fallback)."""
    cleaned = clean_text(text)
    if not cleaned:
        return ""
    # Split on common Chinese/English sentence terminators.
    parts = re.split(r"(?<=[。！？.!?])\s*", cleaned, maxsplit=1)
    return truncate(parts[0] if parts else cleaned, limit)

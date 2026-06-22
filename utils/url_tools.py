"""URL building and query helpers."""

from urllib.parse import quote, urlparse


def is_valid_url(url: str | None) -> bool:
    """True if `url` has a scheme and network location."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


def domain_of(url: str | None) -> str:
    """Return the host portion of a URL, or "" if unparseable."""
    if not url:
        return ""
    try:
        return urlparse(url).netloc
    except ValueError:
        return ""


def build_query(company: dict) -> str:
    """Derive the default search query for a company.

    Preference order: short_name -> company_name -> first keyword.
    Company-specific values come only from config, never from code.
    """
    for key in ("short_name", "company_name"):
        value = (company.get(key) or "").strip()
        if value:
            return value
    keywords = company.get("keywords") or []
    if keywords:
        return str(keywords[0]).strip()
    return (company.get("stock_code") or "").strip()


def apply_query_template(template: str | None, query: str) -> str:
    """Substitute `{query}` (URL-encoded) into a search template."""
    if not template:
        return ""
    return template.replace("{query}", quote(query))

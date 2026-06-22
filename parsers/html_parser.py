"""HTML parsing helpers built on BeautifulSoup.

Only extracts lightweight metadata: page title, candidate article/list links,
and short snippets. Never returns or stores full article bodies.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from utils.text_cleaner import clean_text, truncate


def _soup(html: str) -> BeautifulSoup:
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def page_title(html: str) -> str:
    if not html:
        return ""
    soup = _soup(html)
    if soup.title and soup.title.string:
        return truncate(soup.title.string, 200)
    h1 = soup.find("h1")
    if h1:
        return truncate(h1.get_text(" "), 200)
    return ""


def meta_description(html: str) -> str:
    if not html:
        return ""
    soup = _soup(html)
    for attrs in ({"name": "description"}, {"property": "og:description"}):
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return truncate(tag["content"], 200)
    return ""


def extract_links(html: str, keyword: str | None = None, limit: int = 20) -> list[dict]:
    """Return a list of {text, href} dicts, optionally filtered by keyword."""
    if not html:
        return []
    soup = _soup(html)
    out: list[dict] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        text = clean_text(a.get_text(" "))
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript"):
            continue
        if keyword and keyword not in text and keyword not in href:
            continue
        key = (text, href)
        if key in seen:
            continue
        seen.add(href)
        out.append({"text": truncate(text, 120), "href": href})
        if len(out) >= limit:
            break
    return out


def find_section_links(html: str, section_keywords: dict[str, list[str]]) -> dict[str, str]:
    """Map a section name -> first matching link href.

    `section_keywords` example:
        {"news": ["新闻", "资讯", "news"], "ir": ["投资者", "investor"]}
    """
    found: dict[str, str] = {}
    if not html:
        return found
    soup = _soup(html)
    anchors = soup.find_all("a", href=True)
    for section, keywords in section_keywords.items():
        for a in anchors:
            text = a.get_text(" ")
            href = a["href"]
            blob = f"{text} {href}".lower()
            if any(kw.lower() in blob for kw in keywords):
                found[section] = href.strip()
                break
    return found

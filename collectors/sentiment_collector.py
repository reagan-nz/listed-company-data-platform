"""Sentiment / social platform collector (HIGH RISK, metadata only).

Sources: 雪球, 股吧, 微博. Only validates existence and possible value. Does NOT
collect full text at scale. Output metadata only: platform, query, result_count
(if available), sample_title or sample_link, risk_note.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import extract_links, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class SentimentCollector(BaseCollector):
    category = "sentiment"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        sample_link = ""
        result_count = None
        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            links = extract_links(result.text, keyword=row.query_used, limit=5)
            if links:
                sample_link = links[0].get("href", "")
                result_count = len(links)
        row.set_extracted(
            {
                "platform": source.get("name", ""),
                "query": row.query_used,
                "result_count": result_count,
                "sample_link": sample_link,
                "risk_note": "high-risk UGC: copyright/privacy/anti-crawl; metadata only, no scale scraping",
            }
        )
        row.sample_result = sample_link or "existence validated; metadata only (no full text)"
        row.fetch_status = "partial" if result.ok else row.fetch_status
        row.recommended_next_step = (
            "Validate value via existence + counts only; do NOT collect full posts. Legal review required."
        )

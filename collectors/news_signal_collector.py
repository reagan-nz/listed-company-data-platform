"""News signal collector (metadata only).

Sources: 财联社, 证券时报, 上海证券报, 中国证券报, 第一财经, 21世纪经济报道,
经济观察报, 澎湃财经, 新浪财经, 东方财富资讯, 腾讯财经.

Collects ONLY: title, source, publish_time, url, short_summary (if accessible).
Never scrapes or stores full news text.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import extract_links, meta_description, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class NewsSignalCollector(BaseCollector):
    category = "news_signal"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        row.set_extracted(
            {
                "collect_fields": ["title", "source", "publish_time", "url", "short_summary"],
                "policy": "metadata only; never store full article text",
            }
        )
        if not result.ok or not result.text:
            row.recommended_next_step = (
                "Site may need JS; retry with --use-playwright, then collect headline metadata only."
            )
            return
        row.title = page_title(result.text) or row.title
        hits = extract_links(result.text, keyword=row.query_used, limit=10)
        row.sample_result = (
            f"{len(hits)} headline link(s) mention company name"
            if hits
            else "news site reachable; run keyword search for headlines"
        )
        # short_summary only, from meta description (never full body)
        row.evidence_sentence = self.llm.evidence_sentence(meta_description(result.text), row.query_used)
        row.fetch_status = "success" if hits else "partial"
        row.recommended_next_step = (
            "Collect headline title + url + publish_time via site search; store metadata only."
        )

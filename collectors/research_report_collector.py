"""Research reports / expert opinions collector (metadata only).

Sources: 东方财富研报, public broker report pages, public white papers/consulting
reports, public expert-interview metadata.

Never scrapes paid reports, login-required reports, or copyrighted full text.
Collects metadata only: title, institution, publish_date, source_url,
authorization_required.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import extract_links, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class ResearchReportCollector(BaseCollector):
    category = "research_report"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        row.authorization_required = True if source.get("authorization_required") else row.needs_legal_review
        row.set_extracted(
            {
                "collect_fields": ["title", "institution", "publish_date", "source_url"],
                "authorization_required": bool(source.get("authorization_required", False)),
                "policy": "metadata only; never store paid/login/copyrighted full text",
            }
        )
        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            hits = extract_links(result.text, keyword=row.query_used, limit=10)
            row.sample_result = (
                f"{len(hits)} report link(s) mention company"
                if hits
                else "research listing reachable; metadata search required"
            )
            row.fetch_status = "partial"
            row.recommended_next_step = (
                "Collect report title/institution/date/url only; do not store report bodies."
            )
        else:
            row.recommended_next_step = (
                "Listing may need JS/auth; retry with --use-playwright, collect metadata only."
            )

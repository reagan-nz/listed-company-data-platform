"""Standards and technical documents collector (P1).

Sources: 国家标准全文公开系统, industry standard announcement pages. Collect
metadata and links only unless terms clearly allow full-text use.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class StandardsCollector(BaseCollector):
    category = "standards"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        row.set_extracted(
            {
                "collect": ["standard_number", "title", "status", "publish_date", "link"],
                "full_text": "metadata + links only unless terms clearly allow",
            }
        )
        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            row.sample_result = "standards portal reachable; keyword search required"
            row.fetch_status = "partial"
            row.recommended_next_step = (
                "Search standards by industry keyword; store standard metadata + links."
            )
        else:
            row.recommended_next_step = (
                "Portal may need JS; retry with --use-playwright or configure an accessible standards source."
            )

"""Local government collector (P1).

Config-driven per company location: local DRC, local IIT department, local S&T
department, industrial park / development zone sites. Base URLs are intentionally
empty in sources.yaml and must be configured per region; otherwise the row is
recorded as skipped with a clear configuration next-step.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import extract_links, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class LocalGovernmentCollector(BaseCollector):
    category = "local_government"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        if not result.ok or not result.text:
            return
        row.title = page_title(result.text) or row.title
        links = extract_links(result.text, limit=10)
        row.set_extracted(
            {
                "doc_targets": ["industrial_plan", "industry_policy", "subsidy/support_notice"],
                "sample_link_count": len(links),
            }
        )
        row.sample_result = f"local government portal reachable; {len(links)} links discovered"
        row.fetch_status = "partial"
        row.recommended_next_step = (
            "Search the local portal with company/industry keywords for policy + plan documents."
        )

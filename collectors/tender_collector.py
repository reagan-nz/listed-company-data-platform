"""Tender / procurement collector (P1).

Sources: 中国政府采购网, 全国公共资源交易平台, regional trading centers.
Searches public bidding / winning-bid announcements by company name and records
metadata + links only.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import extract_links, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class TenderCollector(BaseCollector):
    category = "tender"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        if not result.ok or not result.text:
            return
        row.title = page_title(result.text) or row.title
        hits = extract_links(result.text, keyword=row.query_used, limit=10)
        row.set_extracted(
            {
                "announcement_types": [
                    "bidding_announcement",
                    "winning_bid_announcement",
                    "procurement_contract",
                    "project_announcement",
                ],
                "name_match_links": len(hits),
            }
        )
        row.sample_result = (
            f"{len(hits)} result link(s) matched company name on search page"
            if hits
            else "search page reachable; no direct name match parsed (may need JS/query tuning)"
        )
        row.fetch_status = "success" if hits else "partial"
        row.recommended_next_step = (
            "Parse search-result list for bid/winning announcements; store title + url + publish_date."
        )

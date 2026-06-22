"""Patent / trademark collector (P1).

Sources: CNIPA patent search, CNIPA trademark query. These portals typically
require JS rendering and apply captcha/anti-crawl. We validate reachability and
record that applicant-name search is the recommended (often Playwright-assisted)
method. We never bypass captcha.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class PatentTrademarkCollector(BaseCollector):
    category = "patent_trademark"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        kind = "patent" if "PATENT" in source.get("name", "").upper() else "trademark"
        row.set_extracted(
            {
                "search_type": f"{kind}_by_applicant_name",
                "applicant_query": row.query_used,
                "note": "captcha/anti-crawl likely; do not bypass protections",
            }
        )
        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            row.sample_result = f"{kind} search portal reachable; applicant-name query required"
            row.fetch_status = "partial"
            row.recommended_next_step = (
                f"Submit applicant-name {kind} search (Playwright if blocked); store record metadata + links."
            )
        else:
            row.recommended_next_step = (
                f"{kind} portal blocked/needs JS; retry with --use-playwright or use official open-data API."
            )

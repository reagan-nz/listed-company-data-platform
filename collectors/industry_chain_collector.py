"""Industry / supply chain collector (P1).

Config-driven only. No industry-specific logic is hard-coded. Sources are
public white papers, industry reports, government industry documents, and
upstream/downstream relationships derived from annual-report disclosures and
product pages. When a source is not accessible or its terms are unclear, record
failure_reason and needs_legal_review.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class IndustryChainCollector(BaseCollector):
    category = "industry_chain"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        # Terms for industry reports are frequently unclear -> always flag review.
        row.needs_legal_review = True
        row.set_extracted(
            {
                "config_driven": True,
                "derivation": "use annual-report customer/supplier disclosure + product pages",
                "terms_status": "unclear - legal review required before storing report content",
            }
        )
        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            row.sample_result = "configured industry source reachable; verify reuse terms"
            row.fetch_status = "partial"
            row.recommended_next_step = (
                "Confirm reuse rights; collect public white-paper/report metadata + links only."
            )
        else:
            row.recommended_next_step = (
                "Configure a concrete industry-source base_url in sources.yaml and verify its terms."
            )

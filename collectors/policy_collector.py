"""Policy sources collector (P0/P1).

Sources: CSRC, NDRC, MIIT, MOF, MOFCOM, NBS. Validates that the regulator /
ministry portal is reachable and records that policy-document search by the
company's industry keywords is the recommended collection method.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import extract_links, meta_description, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class PolicyCollector(BaseCollector):
    category = "policy"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        if not result.ok or not result.text:
            return
        row.title = page_title(result.text) or row.title
        links = extract_links(result.text, limit=10)
        row.set_extracted(
            {
                "portal_reachable": True,
                "sample_link_count": len(links),
                "note": "policy/document search by industry keywords recommended",
            }
        )
        row.sample_result = (
            f"{len(links)} navigation/document links discovered on portal landing page"
        )
        row.evidence_sentence = self.llm.evidence_sentence(meta_description(result.text), row.query_used)
        row.fetch_status = "partial"
        row.recommended_next_step = (
            "Search portal with company industry keywords to enumerate relevant policy documents."
        )

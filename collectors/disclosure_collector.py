"""Legal disclosure collector (P0).

Sources: CNINFO, SSE, SZSE, BSE. Validates that the statutory disclosure
portal is reachable and records what would be extracted from periodic reports
and announcements. Real collection would query announcement lists and download
official PDFs (which this framework is allowed to store).
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import meta_description, page_title
from parsers.pdf_parser import SECTION_ANCHORS, extract_text, find_sections
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult

# Announcement / document types we aim to monitor at disclosure portals.
DISCLOSURE_DOC_TYPES = [
    "annual_report",
    "semiannual_report",
    "quarterly_report",
    "temporary_announcement",
    "investor_relations_activity_record",
    "inquiry_letter",
    "regulatory_letter",
    "penalty_announcement",
    "disciplinary_action",
    "shareholding_change",
    "performance_forecast",
    "buyback_announcement",
]


class DisclosureCollector(BaseCollector):
    category = "legal_disclosure"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        # If we happened to fetch a PDF (e.g. a direct report URL), extract sections.
        if result.content and ("pdf" in (result.content_type or "").lower()):
            text = extract_text(result.content)
            sections = find_sections(text)
            row.set_extracted(
                {"report_sections_found": list(sections.keys()), **sections}
            )
            row.fetch_status = "success" if sections else "partial"
            row.sample_result = "; ".join(list(sections.keys())[:6]) or "PDF fetched, no anchors matched"
            if text:
                row.evidence_sentence = self.llm.evidence_sentence(text, row.query_used)
            return

        if not result.ok:
            return

        row.title = page_title(result.text) or row.title
        row.evidence_sentence = self.llm.evidence_sentence(meta_description(result.text), row.query_used)
        # Portal reachable: record monitoring targets. Actual list/PDF retrieval
        # needs the structured query described in recommended_method.
        row.set_extracted(
            {
                "monitor_doc_types": DISCLOSURE_DOC_TYPES,
                "target_report_sections": list(SECTION_ANCHORS.keys()),
                "note": "portal reachable; announcement-list query + PDF download required for content",
            }
        )
        row.sample_result = (
            "Disclosure portal reachable; announcement-list query required to enumerate filings."
        )
        row.fetch_status = "partial"
        row.recommended_next_step = (
            "Run announcement-list query for the stock_code, then download official PDFs "
            "and extract periodic-report sections."
        )

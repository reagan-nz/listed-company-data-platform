"""Association + litigation/enforcement collector.

Sources:
  - 中国上市公司协会 and config-driven industry associations / alliances (P1).
  - 中国裁判文书网 / 中国执行信息公开网 as litigation/enforcement public info.

Litigation/enforcement are treated as P2 risk signals ONLY:
  - never first-stage core data,
  - never collect personal information beyond what is legally public and necessary,
  - always record legal risk notes.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import extract_links, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult

LITIGATION_SOURCES = {"中国裁判文书网", "中国执行信息公开网"}


class AssociationCollector(BaseCollector):
    category = "association"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        name = source.get("name", "")
        if name in LITIGATION_SOURCES:
            row.needs_legal_review = True
            row.set_extracted(
                {
                    "usage": "P2_risk_signal_only",
                    "first_stage_core": False,
                    "personal_data": "avoid; collect only legally public minimum",
                    "policy": "metadata only; strong anti-crawl; do not bypass",
                }
            )
            row.sample_result = "litigation/enforcement source: existence validated, P2 risk signal only"
            row.fetch_status = "partial" if result.ok else row.fetch_status
            row.recommended_next_step = (
                "Use only as secondary risk signal; legal review required; avoid personal data."
            )
            return

        # Association sources
        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            links = extract_links(result.text, limit=10)
            row.set_extracted(
                {
                    "doc_targets": ["public_notices", "industry_documents", "white_papers"],
                    "sample_link_count": len(links),
                }
            )
            row.sample_result = f"association portal reachable; {len(links)} links discovered"
            row.fetch_status = "partial"
            row.recommended_next_step = (
                "Collect public association notices/industry documents metadata + links."
            )
        else:
            row.recommended_next_step = (
                "Configure a concrete association base_url and verify reuse terms."
            )

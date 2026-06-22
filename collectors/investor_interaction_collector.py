"""Investor interaction collector (P1).

Sources: 互动易 (SZSE), 上证e互动 (SSE). Collects only question title/summary,
company answer summary, source_url, publish_time, and event tags. Q&A content
is explicitly NOT treated as confirmed investment advice.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import meta_description, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult


class InvestorInteractionCollector(BaseCollector):
    category = "investor_interaction"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        row.set_extracted(
            {
                "collect_fields": [
                    "question_title_or_summary",
                    "company_answer_summary",
                    "publish_time",
                    "event_tags",
                ],
                "advice_disclaimer": "Q&A is not confirmed investment advice",
            }
        )
        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            row.evidence_sentence = self.llm.evidence_sentence(meta_description(result.text), row.query_used)
            row.sample_result = "interaction platform reachable; per-company Q&A query required"
            row.fetch_status = "partial"
            row.recommended_next_step = (
                "Query platform by stock_code; store Q&A summaries + metadata only (no advice claims)."
            )
        else:
            row.recommended_next_step = (
                "Platform likely needs JS; retry with --use-playwright, then query by stock_code."
            )

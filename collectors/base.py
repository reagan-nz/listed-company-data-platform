"""BaseCollector: shared logic for every category collector.

The contract is simple and strict: `collect(company, source)` ALWAYS returns
exactly one `CoverageRow`, whether the attempt succeeds or fails. Subclasses
override `enrich()` to add category-specific metadata extraction; they never
need to worry about row creation, fetching, or failure recording.
"""

from __future__ import annotations

from utils.coverage import CoverageRow
from utils.fetcher import FetchResult, Fetcher
from utils.llm import LLMClient
from utils.url_tools import apply_query_template, build_query, is_valid_url


class BaseCollector:
    #: subclasses set this to the source category they handle (documentation only)
    category: str = ""

    def __init__(self, fetcher: Fetcher, llm: LLMClient | None = None) -> None:
        self.fetcher = fetcher
        self.llm = llm or LLMClient(enabled=False)

    # -- row scaffolding ----------------------------------------------------
    def new_row(self, company: dict, source: dict) -> CoverageRow:
        """Pre-fill a row from company + source config (no network yet)."""
        row = CoverageRow(
            company_name=company.get("company_name", ""),
            short_name=company.get("short_name", ""),
            stock_code=company.get("stock_code", ""),
            exchange=company.get("exchange", ""),
            data_category=source.get("category", ""),
            data_source=source.get("name", ""),
            query_used=build_query(company),
            recommended_method=source.get("recommended_method", ""),
            needs_playwright=bool(source.get("needs_playwright", False)),
            needs_llm=bool(source.get("needs_llm", False)),
            can_store_full_text=bool(source.get("can_store_full_text", False)),
            suggested_storage=source.get("suggested_storage", ""),
            legal_risk_note=source.get("legal_risk_note", ""),
            needs_legal_review=bool(source.get("needs_legal_review", False)),
        )
        return row

    def resolve_url(self, company: dict, source: dict, row: CoverageRow) -> str:
        """Decide which URL to hit. Subclasses may override.

        Default: use the search template (if any) with the company query,
        otherwise the configured base_url.
        """
        template = source.get("query_template", "")
        if template:
            return apply_query_template(template, row.query_used)
        return source.get("base_url", "")

    # -- orchestration ------------------------------------------------------
    def collect(self, company: dict, source: dict) -> CoverageRow:
        row = self.new_row(company, source)
        target_url = self.resolve_url(company, source, row)
        row.source_url = target_url

        if not is_valid_url(target_url):
            row.fetch_status = "skipped"
            row.failure_reason = "no_valid_base_url_configured"
            row.recommended_next_step = (
                "Configure base_url for this source in sources.yaml "
                "(region/industry-specific sources must be filled per company)."
            )
            return row

        mode = source.get("fetch_mode", "fetch")
        result = self.fetcher.fetch(
            target_url, mode=mode, needs_playwright=bool(source.get("needs_playwright", False))
        )
        self._apply_result(row, result)

        try:
            self.enrich(company, source, row, result)
        except Exception as exc:  # noqa: BLE001 - never lose a row over enrichment
            note = f"enrich_error: {type(exc).__name__}"
            row.failure_reason = (f"{row.failure_reason}; {note}".strip("; ")) if row.failure_reason else note
        return row

    def _apply_result(self, row: CoverageRow, result: FetchResult) -> None:
        row.status_code = str(result.status_code) if result.status_code is not None else ""
        row.content_type = result.content_type
        if result.used_playwright:
            row.needs_playwright = True
        if result.final_url:
            row.source_url = result.final_url or row.source_url

        if result.ok:
            row.fetch_status = "success"
        else:
            row.fetch_status = "failure"
            row.failure_reason = result.error or "fetch_failed"
            row.recommended_next_step = self._recommend_next_step(row, result)

    def _recommend_next_step(self, row: CoverageRow, result: FetchResult) -> str:
        err = (result.error or "").lower()
        if "403" in err or "401" in err:
            return "Access likely restricted (auth/anti-crawl). Use official API or request authorization; do not bypass."
        if "404" in err:
            return "Entry URL not found; update base_url/query_template in sources.yaml."
        if "timeout" in err:
            return "Retry later with a longer timeout; site may be slow or rate-limiting."
        if "ssl" in err:
            return "Verify TLS/cert; consider official endpoint or updated URL."
        if row.needs_playwright:
            return "Page likely requires JS rendering; retry with --use-playwright."
        return "Manually verify the URL and source availability; adjust sources.yaml."

    # -- subclass hook ------------------------------------------------------
    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        """Override to add category-specific metadata. Default: page title only."""
        if result.ok and result.text:
            from parsers.html_parser import page_title

            title = page_title(result.text)
            if title:
                row.title = title

"""Market / financial data collector (P1).

Sources: exchange public data, CNINFO financials, 东方财富/新浪/腾讯 quote pages,
and open-source libraries (Tushare/AkShare/BaoStock).

For open-source libraries: record license / usage uncertainty, do not assume
commercial permission, and do not redistribute raw data without confirmation.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult

LIBRARY_SOURCES = {"Tushare", "AkShare", "BaoStock"}


class MarketFinancialCollector(BaseCollector):
    category = "market_financial"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        name = source.get("name", "")
        if name in LIBRARY_SOURCES:
            row.set_extracted(
                {
                    "access": "python_library",
                    "license_status": "uncertain - verify before commercial use",
                    "redistribution": "not permitted without confirmation",
                }
            )
            row.sample_result = f"{name} project page reachable; usage/license must be confirmed"
            row.fetch_status = "success" if result.ok else row.fetch_status
            row.recommended_next_step = (
                f"Review {name} license + data-source terms; obtain token/permission before commercial use."
            )
            return

        if result.ok and result.text:
            row.title = page_title(result.text) or row.title
            row.set_extracted(
                {
                    "data_fields": ["quote", "valuation", "financial_summary"],
                    "redistribution": "may be restricted; verify",
                }
            )
            row.sample_result = "market data page reachable; redistribution terms must be verified"
            row.fetch_status = "partial"
            row.recommended_next_step = (
                "Pull quote/financial summary by stock_code; verify redistribution rights before storing."
            )

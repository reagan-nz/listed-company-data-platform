"""Enterprise relationship collector.

Sources: 国家企业信用信息公示系统 (official) + commercial platforms
企查查 / 天眼查 / 爱企查 / 启信宝.

For commercial platforms:
  - Do NOT scrape at scale.
  - Only check whether public pages exist.
  - Record that authorization/API may be required.
  - Do NOT bypass login or anti-crawling.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult

COMMERCIAL_PLATFORMS = {"企查查", "天眼查", "爱企查", "启信宝"}


class EnterpriseRelationCollector(BaseCollector):
    category = "enterprise_relation"

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        name = source.get("name", "")
        is_commercial = name in COMMERCIAL_PLATFORMS
        row.set_extracted(
            {
                "source_type": "commercial_platform" if is_commercial else "official_registry",
                "access": "existence_check_only",
                "authorization_required": bool(source.get("authorization_required", is_commercial)),
                "policy": "no scale scraping; do not bypass login/anti-crawl",
                "target_relations": ["shareholders", "subsidiaries", "investments", "key_personnel"],
            }
        )
        if result.ok:
            row.title = page_title(result.text) if result.text else row.title
            row.sample_result = (
                f"{name} public page exists; authorization/API likely required"
                if is_commercial
                else f"{name} reachable; official lookup needs structured query (anti-crawl heavy)"
            )
            row.fetch_status = "partial"
            row.recommended_next_step = (
                "Use official API / authorized access for relationship data; do not scrape at scale."
            )
        else:
            row.recommended_next_step = (
                "Page blocked/needs auth; record existence only and pursue official API/authorization."
            )

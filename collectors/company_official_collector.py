"""Company official sources collector (P0).

Sources: COMPANY_OFFICIAL_WEBSITE, COMPANY_INVESTOR_RELATIONS. The target URL
is taken from the company config (official_website / investor_relations_url),
never hard-coded. Discovers public sections: news, product/solution, ESG,
recruitment, contact, announcements.
"""

from __future__ import annotations

from collectors.base import BaseCollector
from parsers.html_parser import find_section_links, meta_description, page_title
from utils.coverage import CoverageRow
from utils.fetcher import FetchResult

SECTION_KEYWORDS = {
    "news_center": ["新闻", "资讯", "news", "media", "press"],
    "investor_relations": ["投资者", "investor", "ir"],
    "product_solution": ["产品", "解决方案", "product", "solution"],
    "esg_sustainability": ["esg", "可持续", "社会责任", "sustainab"],
    "recruitment": ["招聘", "人才", "career", "join", "recruit"],
    "contact": ["联系", "contact"],
    "announcement": ["公告", "announcement", "disclosure"],
}


class CompanyOfficialCollector(BaseCollector):
    category = "company_official"

    def resolve_url(self, company: dict, source: dict, row: CoverageRow) -> str:
        name = source.get("name", "")
        if name == "COMPANY_INVESTOR_RELATIONS":
            return company.get("investor_relations_url", "") or ""
        # default: official website
        return company.get("official_website", "") or ""

    def collect(self, company: dict, source: dict) -> CoverageRow:
        # Provide a clearer skip reason when the company simply didn't supply a URL.
        row = self.new_row(company, source)
        url = self.resolve_url(company, source, row)
        if not url:
            row.source_url = ""
            row.fetch_status = "skipped"
            field = (
                "investor_relations_url"
                if source.get("name") == "COMPANY_INVESTOR_RELATIONS"
                else "official_website"
            )
            row.failure_reason = f"company.{field}_not_provided"
            row.recommended_next_step = f"Add {field} to this company's entry in companies.yaml."
            return row
        return super().collect(company, source)

    def enrich(self, company: dict, source: dict, row: CoverageRow, result: FetchResult) -> None:
        if not result.ok or not result.text:
            return
        row.title = page_title(result.text) or row.title
        sections = find_section_links(result.text, SECTION_KEYWORDS)
        row.set_extracted({"sections_found": sections})
        row.sample_result = ", ".join(sections.keys()) if sections else "homepage reachable; no labeled sections found"
        row.evidence_sentence = self.llm.evidence_sentence(meta_description(result.text), row.query_used)
        row.fetch_status = "success" if sections else "partial"

"""Maps a source `category` to the collector class that handles it.

Adding a new category = add a collector module + one line here. No company- or
source-specific logic lives in this file.
"""

from __future__ import annotations

from collectors.association_collector import AssociationCollector
from collectors.base import BaseCollector
from collectors.company_official_collector import CompanyOfficialCollector
from collectors.disclosure_collector import DisclosureCollector
from collectors.enterprise_relation_collector import EnterpriseRelationCollector
from collectors.industry_chain_collector import IndustryChainCollector
from collectors.investor_interaction_collector import InvestorInteractionCollector
from collectors.local_government_collector import LocalGovernmentCollector
from collectors.market_financial_collector import MarketFinancialCollector
from collectors.news_signal_collector import NewsSignalCollector
from collectors.patent_trademark_collector import PatentTrademarkCollector
from collectors.policy_collector import PolicyCollector
from collectors.research_report_collector import ResearchReportCollector
from collectors.sentiment_collector import SentimentCollector
from collectors.standards_collector import StandardsCollector
from collectors.tender_collector import TenderCollector

CATEGORY_TO_COLLECTOR: dict[str, type[BaseCollector]] = {
    "legal_disclosure": DisclosureCollector,
    "company_official": CompanyOfficialCollector,
    "policy": PolicyCollector,
    "news_signal": NewsSignalCollector,
    "industry_chain": IndustryChainCollector,
    "tender": TenderCollector,
    "patent_trademark": PatentTrademarkCollector,
    "enterprise_relation": EnterpriseRelationCollector,
    "market_financial": MarketFinancialCollector,
    "investor_interaction": InvestorInteractionCollector,
    "sentiment": SentimentCollector,
    "research_report": ResearchReportCollector,
    "standards": StandardsCollector,
    "local_government": LocalGovernmentCollector,
    "association": AssociationCollector,
}


def get_collector(category: str, fetcher, llm) -> BaseCollector:
    """Return a collector instance for `category` (BaseCollector fallback)."""
    cls = CATEGORY_TO_COLLECTOR.get(category, BaseCollector)
    return cls(fetcher=fetcher, llm=llm)

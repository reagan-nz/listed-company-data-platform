"""PDF parsing helpers for official filings (annual/periodic reports).

Tries PyMuPDF (fitz) first, falls back to pdfplumber. Used to locate and
extract disclosure *sections* from official report PDFs:
  - main business segments / major products
  - revenue by segment / region
  - top customers / suppliers (if disclosed)
  - R&D investment, major subsidiaries
  - risk factors, industry discussion, MD&A

Only official statutory filings are processed this way; storage of those is
generally permitted (see sources.yaml legal notes).
"""

from __future__ import annotations

from utils.text_cleaner import clean_text, truncate

# Section anchors -> Chinese headings commonly used in CN periodic reports.
SECTION_ANCHORS: dict[str, list[str]] = {
    "main_business_segments": ["主营业务", "分行业", "业务板块", "经营情况"],
    "major_products": ["主要产品", "产品及用途", "主要产品及服务"],
    "revenue_by_segment": ["分行业", "分产品", "营业收入构成", "分部信息"],
    "revenue_by_region": ["分地区", "境内", "境外", "地区分布"],
    "top_customers": ["前五名客户", "主要客户", "前五大客户"],
    "top_suppliers": ["前五名供应商", "主要供应商", "前五大供应商"],
    "rnd_investment": ["研发投入", "研发费用", "研究与开发"],
    "major_subsidiaries": ["主要控股参股公司", "主要子公司", "重要子公司"],
    "risk_factors": ["风险因素", "可能面对的风险", "风险提示"],
    "industry_discussion": ["行业格局", "行业发展", "所处行业情况", "行业地位"],
    "mda": ["管理层讨论与分析", "经营情况讨论与分析"],
}


def extract_text(pdf_bytes: bytes, max_pages: int = 60) -> str:
    """Return concatenated text from the first `max_pages` pages, or ""."""
    if not pdf_bytes:
        return ""
    text = _extract_with_fitz(pdf_bytes, max_pages)
    if text:
        return text
    return _extract_with_pdfplumber(pdf_bytes, max_pages)


def _extract_with_fitz(pdf_bytes: bytes, max_pages: int) -> str:
    try:
        import fitz  # type: ignore  # PyMuPDF
    except Exception:
        return ""
    try:
        chunks: list[str] = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for i, page in enumerate(doc):
                if i >= max_pages:
                    break
                chunks.append(page.get_text("text"))
        return "\n".join(chunks)
    except Exception:
        return ""


def _extract_with_pdfplumber(pdf_bytes: bytes, max_pages: int) -> str:
    try:
        import io

        import pdfplumber  # type: ignore
    except Exception:
        return ""
    try:
        chunks: list[str] = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= max_pages:
                    break
                chunks.append(page.extract_text() or "")
        return "\n".join(chunks)
    except Exception:
        return ""


def find_sections(text: str, snippet_len: int = 160) -> dict[str, str]:
    """Locate disclosure sections and return a short snippet for each found one."""
    found: dict[str, str] = {}
    if not text:
        return found
    for section, anchors in SECTION_ANCHORS.items():
        for anchor in anchors:
            idx = text.find(anchor)
            if idx != -1:
                snippet = text[idx : idx + snippet_len]
                found[section] = truncate(clean_text(snippet), snippet_len)
                break
    return found

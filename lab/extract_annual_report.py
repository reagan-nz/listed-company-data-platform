"""Plan B: structured extraction from an annual-report PDF.

Design requirements (the moat, made concrete):
  - stable parsing: PyMuPDF text per page (page-number aligned) + pdfplumber tables
  - clear field definitions: lab/field_schema.py
  - page-number alignment: every field carries its source page
  - chunk management + cost control: locate the section, work only on its page(s)
  - repeatable runs: parsed pages cached by content hash (sha256)
  - evidence linking: each field emits {value, evidence_sentence, page, source_url}
  - output validation: schema check + a manual spot-check doc (separate step)

This is a DETERMINISTIC extractor (no LLM/API needed), so runs are repeatable
and free. An optional LLM step can be slotted into `extract_field` later without
changing the contract. COMPANY-AGNOSTIC: company name, stock code, and
source_url are CLI arguments; only generic CN-annual-report knowledge lives here.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.field_schema import (FIELD_SPECS, FieldSpec, detect_profile,  # noqa: E402
                              get_field_specs, is_financial_profile, resolve_profile)
from utils.text_cleaner import clean_text, truncate  # noqa: E402

_SENT_SPLIT = re.compile(r"(?<=[。！？；\n])")
_NUM_RE = re.compile(r"[-+]?\d[\d,]*\.?\d*\s*(?:亿元|万元|亿|万|元|%|％)?")
# Dot-leader runs that mark a table-of-contents line.
_TOC_RE = re.compile(r"(?:\.{4,}|\u00b7{4,}|\u2026{2,}|\uff0e{4,})")
# Generic total/label words used to target numeric values.
_TOTAL_LABELS = ("合计", "总额", "金额", "占营业收入")


# -- parsing (cached by content hash) ---------------------------------------
def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_pages(pdf_path: str, cache_dir: str) -> tuple[list[str], dict]:
    """Return (pages_text[list, 0-based], meta). Cached by sha256."""
    digest = sha256_of(pdf_path)
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{digest}.pages.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data["pages"], {"sha256": digest, "page_count": len(data["pages"]), "cached": True}

    import fitz  # type: ignore

    pages: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pages.append(page.get_text("text"))
    with open(cache_file, "w", encoding="utf-8") as fh:
        json.dump({"sha256": digest, "pages": pages}, fh, ensure_ascii=False)
    return pages, {"sha256": digest, "page_count": len(pages), "cached": False}


# -- location heuristics -----------------------------------------------------
def page_is_toc(text: str) -> bool:
    """True if the page is dominated by table-of-contents dot-leader lines."""
    return len(_TOC_RE.findall(text)) >= 5


def _heading_bonus(text: str, idx: int) -> float:
    """Reward anchors that sit at/near the start of a line (i.e. headings)."""
    line_start = text.rfind("\n", 0, idx)
    col = idx - (line_start + 1)
    if col <= 0:
        return 50.0
    if col <= 2:
        return 30.0
    if col <= 6:
        return 12.0
    return 0.0


@functools.lru_cache(maxsize=256)
def _anchor_regex(anchor: str) -> re.Pattern:
    """Whitespace/newline-tolerant matcher so PDF heading line-wraps still match.

    Allows up to 2 whitespace chars between each character of the anchor, e.g.
    '公司从事的主要业务' will match even if the PDF wrapped it as '公司从事的主要\\n业务'.
    """
    return re.compile(r"[ \t\r\n]{0,2}".join(re.escape(ch) for ch in anchor))


def locate_section(
    pages: list[str], anchors: tuple[str, ...], preferred_pages: set[int] | None = None,
    avoid: tuple[str, ...] = (),
) -> dict | None:
    """Find the BODY occurrence of an anchor, scoring all occurrences by:
      - being in the field's PREFERRED region (MD&A vs notes) - dominant bonus,
      - NOT being on a table-of-contents page (heavy penalty),
      - NOT being immediately followed by an `avoid` token (wrong-occurrence
        signal, e.g. a table column header or the employee-count line),
      - anchor PRIORITY (earlier anchors are more specific - dominant among hits),
      - sitting at a heading boundary (line start) rather than mid-paragraph,
      - a small length / following-text bonus.
    Anchor matching is line-break tolerant (see `_anchor_regex`).
    """
    best = None
    best_score = float("-inf")
    n_anchors = len(anchors)
    for pno, text in enumerate(pages, start=1):
        toc = page_is_toc(text)
        in_region = bool(preferred_pages) and pno in preferred_pages
        for a_idx, anchor in enumerate(anchors):
            for m in _anchor_regex(anchor).finditer(text):
                idx = m.start()
                col = idx - (text.rfind("\n", 0, idx) + 1)
                score = 0.0
                if in_region:
                    score += 200.0
                if toc:
                    score -= 1000.0
                if avoid:
                    after = text[m.end(): m.end() + 30]
                    if any(tok in after for tok in avoid):
                        score -= 130.0
                score += (n_anchors - a_idx) * 8.0   # earlier anchor = more specific
                score += _heading_bonus(text, idx)
                score += len(anchor) * 1.0
                score += min((len(text) - idx) / 1000.0, 5.0)
                if score > best_score:
                    best_score = score
                    best = {"page": pno, "idx": idx, "anchor": anchor,
                            "in_region": in_region, "col": col}
    return best


def _loc_page(pages: list[str], anchors: tuple[str, ...]) -> int | None:
    r = locate_section(pages, anchors)
    return r["page"] if r else None


def compute_regions(pages: list[str]) -> dict[str, set[int]]:
    """Derive page ranges for MD&A and financial notes from section headers.

    MD&A (第三节) is bounded by the next section start (公司治理 / 财务报告);
    notes is from the financial-report section to the end. Falls back to empty
    regions if a boundary cannot be located.
    """
    n = len(pages)
    mda_start = _loc_page(pages, ("管理层讨论与分析", "经营情况讨论与分析"))
    gov_start = _loc_page(pages, ("公司治理",))
    fin_start = _loc_page(pages, ("财务报告", "财务报表附注", "合并财务报表项目注释"))
    regions: dict[str, set[int]] = {}
    if mda_start:
        end = None
        for cand in (gov_start, fin_start):
            if cand and cand > mda_start:
                end = cand
                break
        end = end or (n + 1)
        regions["mda"] = set(range(mda_start, end))
    if fin_start:
        regions["notes"] = set(range(fin_start, n + 1))
    return regions


def glue_numbers(text: str) -> str:
    """Rejoin a single number split across a line break by PyMuPDF wrapping.

    Heal a newline ONLY when the left fragment ends with an INCOMPLETE thousands
    group (comma + 1-2 digits, e.g. "12,00"), which signals a mid-number wrap.
    Complete numbers ("...,756") are left alone, so adjacent table columns on
    separate lines (e.g. "18,606,756 / 18,356,108") are NOT merged.
    """
    return re.sub(r"(,\d{1,2})[ \t]*\n[ \t]*(\d)", r"\1\2", text)


def extract_numeric(window: str, labels: list[str]) -> list[dict]:
    """Return labeled {label, value} pairs, preferring specific/total labels."""
    window = glue_numbers(window)
    out: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for lab in labels:
        for m in re.finditer(re.escape(lab), window):
            after = window[m.end(): m.end() + 24]
            nm = _NUM_RE.search(after)
            if not nm:
                continue
            val = nm.group(0).strip()
            if any(ch.isdigit() for ch in val) and (lab, val) not in seen:
                seen.add((lab, val))
                out.append({"label": lab, "value": val})
            if len(out) >= 8:
                return out
    return out


# R&D numeric extraction: prefer total-amount labels; reject ratio-only, list
# markers, and capitalized-zero-only rows. Company-agnostic template rules.
_RND_AMOUNT_LABELS = (
    "研发投入合计",
    "研发投入总额",
    "费用化研发投入",
    "研发支出金额",
    "研发支出合计",
    "研发支出总额",
    "研发投入金额",
    "研发费用",
)
_RND_GENERIC_LABEL = "研发投入"
_RND_SKIP_LINE_MARKERS = (
    "研发人员情况",
    "研发人员占",
    "研发人员总计",
    "比重较上年发生显著变化",
    "资本化率",
    "变化的原因",
    "教育程度",
)
_RND_INCOME_STMT_MARKERS = (
    "财务费用",
    "管理费用",
    "销售费用",
    "营业成本",
    "税金及附加",
    "资产减值损失",
    "信用减值损失",
)
_RND_RATIO_RE = re.compile(r"[%％]")
_RND_AMT_UNIT_RE = re.compile(r"(?:亿元|万元|千元|元)")


def _numeric_magnitude(val: str) -> float | None:
    s = re.sub(r"[^\d.\-+]", "", val.replace(",", ""))
    if not s or s in (".", "-", "+"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _is_rnd_ratio(val: str) -> bool:
    return bool(_RND_RATIO_RE.search(val)) and not _RND_AMT_UNIT_RE.search(val)


def _is_rnd_list_marker(val: str) -> bool:
    mag = _numeric_magnitude(val)
    if mag is None:
        return False
    if re.fullmatch(r"\s*\(?[123]\)?\s*", val.strip()):
        return True
    if not _RND_AMT_UNIT_RE.search(val) and not _RND_RATIO_RE.search(val):
        if mag == int(mag) and 1 <= mag <= 9 and len(re.sub(r"[^\d]", "", val)) <= 2:
            return True
    return False


def rnd_amount_ok(val: str) -> bool:
    """True when value looks like a substantive R&D money amount (not ratio/list marker)."""
    if not val or _is_rnd_ratio(val) or _is_rnd_list_marker(val):
        return False
    mag = _numeric_magnitude(val)
    if mag is None or mag <= 0:
        return False
    if _RND_AMT_UNIT_RE.search(val):
        return True
    if "," in val:
        return True
    return mag >= 10000


def rnd_investment_plausible(value: dict | None) -> bool:
    if not isinstance(value, dict):
        return False
    return any(rnd_amount_ok(x.get("value") or "") for x in value.get("labeled") or [])


def _looks_like_income_statement_block(window: str) -> bool:
    """Reject P&L expense tables (研发费用 beside 财务费用/管理费用 etc.)."""
    return sum(1 for m in _RND_INCOME_STMT_MARKERS if m in window) >= 2


def extract_rnd_numeric(window: str) -> list[dict]:
    """Extract R&D total amounts; reject ratio-only and capitalized-zero-only hits."""
    if _looks_like_income_statement_block(window):
        return []
    window = glue_numbers(window)
    seen: set[tuple[str, str]] = set()
    results: list[dict] = []

    def try_add(label: str, val: str, line: str) -> None:
        if (label, val) in seen:
            return
        if _is_rnd_list_marker(val) or _is_rnd_ratio(val):
            return
        if "资本化" in line and not rnd_amount_ok(val):
            return
        if not rnd_amount_ok(val):
            return
        seen.add((label, val))
        results.append({"label": label, "value": val})

    lines = [ln.strip() for ln in window.split("\n")]
    for i, line in enumerate(lines):
        if not line:
            continue
        skip_line = any(m in line for m in _RND_SKIP_LINE_MARKERS)
        if "占营业收入" in line or ("比例" in line and "金额" not in line):
            continue

        for lab in _RND_AMOUNT_LABELS:
            if lab not in line:
                continue
            pos = line.find(lab)
            after = line[pos + len(lab):].strip()
            nm = _NUM_RE.search(after)
            if nm:
                try_add(lab, nm.group(0).strip(), line)
            elif not after or after.startswith(("（", "(", "：", ":")):
                for nxt in lines[i + 1: i + 4]:
                    if not nxt or any(m in nxt for m in _RND_SKIP_LINE_MARKERS):
                        break
                    if any(l in nxt for l in _RND_AMOUNT_LABELS):
                        break
                    if "占营业收入" in nxt or ("比例" in nxt and "金额" not in nxt):
                        break
                    nm = _NUM_RE.search(nxt)
                    if nm:
                        try_add(lab, nm.group(0).strip(), line + " " + nxt)
                        break

        if not skip_line and _RND_GENERIC_LABEL in line:
            if "占营业收入" in line or "占研发" in line or "比例" in line:
                continue
            pos = line.find(_RND_GENERIC_LABEL)
            after = line[pos + len(_RND_GENERIC_LABEL):].strip()
            nm = _NUM_RE.search(after)
            if nm:
                try_add(_RND_GENERIC_LABEL, nm.group(0).strip(), line)

    label_rank = {l: i for i, l in enumerate(_RND_AMOUNT_LABELS + (_RND_GENERIC_LABEL,))}
    results.sort(key=lambda x: label_rank.get(x["label"], 99))
    deduped: list[dict] = []
    seen_vals: set[str] = set()
    for item in results:
        if item["value"] in seen_vals:
            continue
        seen_vals.add(item["value"])
        deduped.append(item)
    return deduped[:6]


# A heading is the anchor at/near a line start, OR a line whose only prefix
# before the anchor is CN section numbering + a few descriptive chars, e.g.
# "（五）公司2025 年度可能面临的风险". This rescues real headings that carry a
# descriptive numbering prefix (col>6) without admitting mid-paragraph matches.
_HEADING_PREFIX_RE = re.compile(
    r"^\s*[（(]?[一二三四五六七八九十\d]{1,4}[）)、.\s][\u4e00-\u9fff0-9 ]{0,12}$"
)


def _is_heading(page_text: str, idx: int, col: int) -> bool:
    if col <= 6:
        return True
    line_start = page_text.rfind("\n", 0, idx)
    return bool(_HEADING_PREFIX_RE.match(page_text[line_start + 1: idx]))


def evidence_sentence(page_text: str, idx: int, anchor: str, limit: int = 200) -> str:
    window = page_text[idx: idx + 400]
    for sent in _SENT_SPLIT.split(window):
        if anchor in sent and len(clean_text(sent)) > len(anchor):
            return truncate(clean_text(sent), limit)
    return truncate(clean_text(window), limit)


# -- table extraction --------------------------------------------------------
def extract_table_near(
    pdf_path: str, page_no: int, anchors: tuple[str, ...], table_match: tuple[str, ...] = (),
    table_require: tuple[str, ...] = (), preview_focus: tuple[str, ...] = (),
) -> dict | None:
    """Use pdfplumber to find the BEST table near `page_no`.

    Header-aware + context-guarded:
      - `table_require`: a candidate table MUST contain >=1 of these (e.g. a
        revenue token), which rejects unrelated tables (shareholder lists etc.).
      - `table_match`: prefer the table with the most of these tokens (region vs
        segment). If `table_match` is set, at least ONE must be present, so we
        don't return a pure segment table for the region field.
      - `preview_focus`: CN reports often stack 分行业 / 分产品 / 分地区 into ONE
        table; the row preview would otherwise show the top (分行业) section and
        look wrong for the region field. When set, the preview starts at the
        first row matching one of these tokens, so the evidence reflects the
        field's own section (e.g. the 分地区 rows).
    """
    tokens = table_match or anchors
    try:
        import pdfplumber  # type: ignore
    except Exception:
        return None
    best = None
    best_hits = -1
    try:
        with open(pdf_path, "rb") as fh:
            data = fh.read()
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for cand in (page_no, page_no - 1, page_no + 1, page_no - 2):
                if cand < 1 or cand > len(pdf.pages):
                    continue
                page = pdf.pages[cand - 1]
                for tbl in (page.extract_tables() or []):
                    flat = " ".join(str(c) for row in tbl for c in row if c)
                    if table_require and not any(t in flat for t in table_require):
                        continue  # context guard: not the right kind of table
                    if not any(a in flat for a in anchors) and not any(t in flat for t in tokens):
                        continue
                    hits = sum(1 for t in tokens if t in flat)
                    if hits > best_hits:
                        best_hits = hits
                        start = 0
                        if preview_focus:
                            for ri, row in enumerate(tbl):
                                rowtxt = " ".join(str(c) for c in row if c)
                                if any(tok in rowtxt for tok in preview_focus):
                                    start = ri
                                    break
                        rows = [[truncate(str(c or ""), 40) for c in row[:6]]
                                for row in tbl[start:start + 8]]
                        best = {"table_page": cand, "rows": rows, "n_rows": len(tbl),
                                "match_hits": hits, "preview_from_row": start}
    except Exception:
        return None
    # When table_match is specified, require at least one of those tokens to be
    # present (e.g. don't accept a pure segment table as the region table).
    if best is not None and table_match and best.get("match_hits", 0) < 1:
        return None
    return best


# Revenue table plausibility: require at least one data row (label + numeric value).
_REVENUE_TABLE_HEADER_CELLS = frozenset({
    "分行业", "分产品", "分地区", "分销售模式",
})
_REVENUE_TABLE_HEADER_WORDS = (
    "营业收入", "营业成本", "毛利率", "毛利", "比上年", "增减", "百分点", "比例",
)
_TABLE_NUM_RE = re.compile(r"[-+]?\d[\d,]*\.?\d*")


def _table_cell_text(cell) -> str:
    return str(cell or "").strip()


def _table_meaningful_number(cell: str) -> bool:
    """True if cell contains a revenue/cost/margin-style numeric value."""
    s = _table_cell_text(cell)
    if not s or not any(ch.isdigit() for ch in s):
        return False
    if re.search(r"[%％]", s):
        return bool(_TABLE_NUM_RE.search(s))
    if re.search(r"(?:亿元|万元|千元|元)", s):
        return bool(_TABLE_NUM_RE.search(s))
    m = _TABLE_NUM_RE.search(s.replace(" ", ""))
    if not m:
        return False
    raw = m.group(0).replace(",", "")
    try:
        val = float(raw)
    except ValueError:
        return False
    if "," in m.group(0):
        return True
    if abs(val) >= 100:
        return True
    if "." in raw and val != int(val):
        return True
    return False


def _table_is_header_cell(cell: str) -> bool:
    if not cell:
        return True
    if cell in _REVENUE_TABLE_HEADER_CELLS:
        return True
    if "主营业务分" in cell and "情况" in cell:
        return True
    if not any(ch.isdigit() for ch in cell):
        if any(w in cell for w in _REVENUE_TABLE_HEADER_WORDS):
            return True
    return False


def _table_row_is_data_row(row: list) -> bool:
    """True when row has a non-header label and at least one meaningful numeric cell."""
    cells = [_table_cell_text(c) for c in row]
    if not any(cells):
        return False
    if not any(_table_meaningful_number(c) for c in cells):
        return False
    label_cells = [c for c in cells if c and not _table_is_header_cell(c) and not _table_meaningful_number(c)]
    if label_cells:
        return True
    first = cells[0]
    return bool(first) and not _table_is_header_cell(first)


def revenue_table_plausible(value: dict | None) -> bool:
    """Stricter plausibility for revenue_by_segment / revenue_by_region table previews."""
    if not isinstance(value, dict):
        return False
    rows = value.get("rows")
    if not rows:
        return False
    if value.get("match_hits", 0) < 1:
        return False
    return any(_table_row_is_data_row(row) for row in rows)


_PCT_RE = re.compile(r"\d[\d,]*\.?\d*\s*[%％]")
_AMT_RE = re.compile(r"\d[\d,]*\.?\d*\s*(?:亿元|万元|千元|元)")


def extract_concentration(window: str) -> dict:
    """Prose-first extraction for customer/supplier concentration.

    CN reports often disclose '前五名客户销售额X万元，占年度销售总额Y%' as a
    sentence, not a parseable table. Pull the amount + percentage from prose.
    """
    win = glue_numbers(window)
    amt = _AMT_RE.search(win)
    pct = _PCT_RE.search(win)
    sentence = first_sentence_local(window)
    return {
        "amount": amt.group(0).strip() if amt else "",
        "ratio": pct.group(0).strip() if pct else "",
        "sentence": truncate(clean_text(sentence), 200),
    }


def first_sentence_local(text: str, limit: int = 200) -> str:
    cleaned = clean_text(text)
    parts = re.split(r"(?<=[。；])", cleaned, maxsplit=1)
    return truncate(parts[0] if parts else cleaned, limit)


# -- per-field extraction ----------------------------------------------------
def extract_field(
    spec: FieldSpec, pages: list[str], pdf_path: str, source_url: str,
    regions: dict[str, set[int]] | None = None,
) -> dict:
    out = {
        "field": spec.key,
        "label_cn": spec.label_cn,
        "definition": spec.definition,
        "extraction": spec.extraction,
        "region": spec.region,
        "status": "not_found",
        "in_region": False,
        "value": None,
        "evidence_sentence": "",
        "page": None,
        "anchor_matched": "",
        "source_url": source_url,
    }
    preferred = (regions or {}).get(spec.region)
    loc = locate_section(pages, spec.anchors, preferred, spec.avoid)

    # Sibling-section fallback: when the specific anchor is missing, or it matched
    # but not in-region at a heading boundary, retry with the field's fallback
    # anchors (a known sibling section, e.g. the business-overview narrative that
    # usually describes the company's products). Only swaps in a fallback hit that
    # itself lands well, so it can only add coverage, never weaken a good primary
    # hit. Applies solely to specs that declare `fallback_anchors`.
    if spec.fallback_anchors:
        def _lands_well(l: dict | None) -> bool:
            if not l:
                return False
            return ((bool(l.get("in_region")) or not preferred)
                    and l.get("col", 99) <= 6)

        if not _lands_well(loc):
            floc = locate_section(pages, spec.fallback_anchors, preferred, spec.avoid)
            if _lands_well(floc):
                loc = floc

    if not loc:
        return out
    page_text = pages[loc["page"] - 1]
    in_region = bool(loc.get("in_region"))
    heading = _is_heading(page_text, loc["idx"], loc.get("col", 99))
    out["page"] = loc["page"]
    out["anchor_matched"] = loc["anchor"]
    out["in_region"] = in_region
    out["evidence_sentence"] = evidence_sentence(page_text, loc["idx"], loc["anchor"])

    # Confidence: a hit is "found" only when it is in the preferred region (or no
    # region preference) AND sits at a heading boundary; otherwise "partial".
    located_well = (in_region or not preferred) and heading

    if spec.extraction == "section_snippet":
        raw = page_text[loc["idx"]: loc["idx"] + 320]
        # A heading near the page bottom means the section body continues on the
        # next page; pull in its start so a real section isn't judged "too short".
        if len(clean_text(raw)) < 80 and loc["page"] < len(pages):
            raw = raw + " " + pages[loc["page"]][:320]
        snippet = clean_text(raw)
        out["value"] = truncate(snippet, 320)
        out["status"] = "found" if located_well else "partial"
    elif spec.extraction == "numeric":
        window = page_text[loc["idx"]: loc["idx"] + 600]
        if spec.key == "rnd_investment":
            labeled = extract_rnd_numeric(window)
        else:
            labels = list(dict.fromkeys(list(spec.anchors) + list(_TOTAL_LABELS)))
            labeled = extract_numeric(window, labels)
        out["value"] = {"labeled": labeled, "context": truncate(clean_text(window[:200]), 200)}
        out["status"] = "found" if (labeled and located_well) else ("partial" if labeled else "not_found")
    elif spec.extraction == "concentration":
        window = page_text[loc["idx"]: loc["idx"] + 400]
        conc = extract_concentration(window)
        out["value"] = conc
        out["status"] = "found" if (conc["ratio"] or conc["amount"]) else "partial"
    elif spec.extraction == "table":
        tbl = extract_table_near(pdf_path, loc["page"], spec.anchors, spec.table_match, spec.table_require,
                                 preview_focus=spec.table_match or spec.anchors)
        if tbl:
            out["value"] = tbl
            out["page"] = tbl["table_page"]
            out["status"] = "found" if (in_region or not preferred) else "partial"
        else:
            out["value"] = {"note": "anchor located but no parseable table; snippet fallback",
                            "snippet": truncate(clean_text(page_text[loc["idx"]: loc["idx"] + 240]), 240)}
            out["status"] = "partial"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Annual-report structured extraction (company values via CLI)")
    ap.add_argument("--pdf", required=True, help="path to the annual-report PDF")
    ap.add_argument("--stock-code", required=True)
    ap.add_argument("--company-name", default="")
    ap.add_argument("--short-name", default="")
    ap.add_argument("--exchange", default="")
    ap.add_argument("--source-url", required=True, help="official PDF URL (provenance)")
    ap.add_argument("--report-title", default="", help="e.g. 2024 annual report")
    ap.add_argument("--profile", default="auto",
                    choices=["auto", "industrial", "financial", "bank", "broker", "insurer",
                             "other_financial"],
                    help="field-schema profile; 'auto' stays industrial (financial sub-schemas opt-in)")
    ap.add_argument("--output-dir", default=os.path.join(_PROJECT_ROOT, "outputs", "extraction"))
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"[extract] PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    cache_dir = os.path.join(args.output_dir, ".cache")
    pages, meta = parse_pages(args.pdf, cache_dir)
    print(f"[extract] parsed {meta['page_count']} pages (cached={meta['cached']}) sha256={meta['sha256'][:12]}")

    # Scanned / no-text-layer detection: a long report with almost no extractable
    # text is an image-only PDF (would need OCR). Flag it and short-circuit.
    text_len = sum(len(p) for p in pages)
    text_layer_ok = not (meta["page_count"] >= 15 and text_len < 3000)
    # NOTE: financial auto-detection is intentionally OFF. A single generic
    # "financial" profile regressed on the held-out set (false-positived on firms
    # with finance subsidiaries, e.g. 贵州茅台; and underperformed for brokers).
    # The financial profile is available as an explicit opt-in (--profile financial)
    # for future per-subtype (bank/insurer/broker) work; 'auto' stays industrial.
    suggested = detect_profile(pages, short_name=args.short_name or args.company_name)
    schema_profile = resolve_profile(
        pages,
        short_name=args.short_name or args.company_name,
        explicit="industrial" if args.profile == "auto" else args.profile,
    )
    specs = get_field_specs(schema_profile)
    if is_financial_profile(suggested) and schema_profile == "industrial":
        print(f"[extract] note: text/name suggests {suggested} "
              f"(try --profile {suggested})")
    print(f"[extract] profile={schema_profile} text_layer_ok={text_layer_ok} text_len={text_len}")

    if not text_layer_ok:
        fields = []
        for spec in specs:
            fields.append({"field": spec.key, "label_cn": spec.label_cn, "definition": spec.definition,
                           "extraction": spec.extraction, "region": spec.region, "status": "not_found",
                           "in_region": False, "value": None, "evidence_sentence": "",
                           "page": None, "anchor_matched": "",
                           "source_url": args.source_url, "note": "no_text_layer: scanned PDF, OCR required"})
        regions = {}
    else:
        regions = compute_regions(pages)
        region_info = {k: f"pages {min(v)}-{max(v)}" for k, v in regions.items() if v}
        print(f"[extract] regions: {region_info or 'none detected'}")
        fields = [extract_field(spec, pages, args.pdf, args.source_url, regions) for spec in specs]
    found = sum(1 for f in fields if f["status"] == "found")
    partial = sum(1 for f in fields if f["status"] == "partial")
    missing = sum(1 for f in fields if f["status"] == "not_found")

    out_profile = {
        "company": {
            "company_name": args.company_name,
            "short_name": args.short_name,
            "stock_code": args.stock_code,
            "exchange": args.exchange,
        },
        "source": {
            "report_title": args.report_title,
            "source_url": args.source_url,
            "pdf_sha256": meta["sha256"],
            "page_count": meta["page_count"],
        },
        "schema_profile": schema_profile,
        "suggested_profile": suggested,
        "text_layer_ok": text_layer_ok,
        "extracted_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "field_counts": {"found": found, "partial": partial, "not_found": missing, "total": len(fields)},
        "fields": fields,
    }

    os.makedirs(args.output_dir, exist_ok=True)
    profile_path = os.path.join(args.output_dir, "company_profile.json")
    with open(profile_path, "w", encoding="utf-8") as fh:
        json.dump(out_profile, fh, ensure_ascii=False, indent=2)
    print(f"[extract] wrote {profile_path} (found={found} partial={partial} missing={missing})")

    brief_path = os.path.join(args.output_dir, "company_brief.md")
    with open(brief_path, "w", encoding="utf-8") as fh:
        fh.write(render_brief(out_profile))
    print(f"[extract] wrote {brief_path}")
    return 0


def render_brief(profile: dict) -> str:
    c = profile["company"]
    s = profile["source"]
    name = c.get("short_name") or c.get("company_name") or c.get("stock_code")
    lines: list[str] = []
    a = lines.append
    a(f"# Company Brief: {name} ({c.get('stock_code')})")
    a("")
    a(f"_Source: {s.get('report_title') or 'annual report'} - "
      f"[official PDF]({s.get('source_url')}) | sha256 `{s.get('pdf_sha256','')[:12]}` | "
      f"{s.get('page_count')} pages_")
    a("")
    a("Every field below is evidence-linked: value + the sentence it came from + page number. "
      "Fields not disclosed are shown as such (no invented data).")
    a("")
    fc = profile["field_counts"]
    a(f"Coverage: {fc['found']} found, {fc['partial']} partial, {fc['not_found']} not found (of {fc['total']}).")
    a("")
    for f in profile["fields"]:
        a(f"## {f['label_cn']} ({f['field']}) - {f['status']}")
        if f["status"] == "not_found":
            a("")
            a("- not disclosed / not located")
            a("")
            continue
        val = f["value"]
        if isinstance(val, dict) and "rows" in val:
            a("")
            a(f"- table (page {f['page']}, {val.get('n_rows')} rows):")
            for row in val["rows"]:
                a(f"  - {' | '.join(row)}")
        elif isinstance(val, dict) and "ratio" in val:
            a("")
            a(f"- amount: {val.get('amount') or '(n/a)'}  |  ratio: {val.get('ratio') or '(n/a)'}")
            a(f"- sentence: {val.get('sentence','')}")
        elif isinstance(val, dict) and "labeled" in val:
            a("")
            pairs = val["labeled"]
            if pairs:
                for p in pairs:
                    a(f"- {p['label']}: {p['value']}")
            else:
                a("- (no labeled values parsed)")
            a(f"- context: {val.get('context','')}")
        elif isinstance(val, dict):
            a("")
            a(f"- {val.get('note','')}: {val.get('snippet','')}")
        else:
            a("")
            a(f"- {val}")
        a(f"- evidence (p.{f['page']}): {f['evidence_sentence']}")
        a("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

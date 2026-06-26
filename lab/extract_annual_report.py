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


def locate_candidates(
    pages: list[str], anchors: tuple[str, ...], preferred_pages: set[int] | None = None,
    avoid: tuple[str, ...] = (), limit: int = 8,
) -> list[dict]:
    """Return anchor occurrences scored and sorted descending (best first).

    Scoring matches ``locate_section``: preferred region, TOC penalty, avoid
    tokens, anchor priority, heading boundary, length bonus.
    """
    scored: list[tuple[float, dict]] = []
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
                scored.append((score, {"page": pno, "idx": idx, "anchor": anchor,
                                       "in_region": in_region, "col": col, "score": score}))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]


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
    cands = locate_candidates(pages, anchors, preferred_pages, avoid, limit=1)
    return cands[0] if cands else None


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


_FIN_RATIO_FIELDS = frozenset({
    "npl_ratio",
    "capital_adequacy_ratio",
    "provision_coverage_ratio",
})
_FIN_RATIO_BAD_LABEL_MARKERS = (
    "合计", "总额", "金额", "余额", "不良率增减", "较上年", "变化", "上升", "下降",
)
_FIN_RATIO_INDUSTRY_CONTEXT = (
    "银行业", "行业", "主要风险指标处于合理区间", "商业银行", "世界经济复苏",
    "整体而言", "宏观", "经济复苏", "监管部门推出",
)
_FIN_RATIO_PREFERRED_SHARE_CONTEXT = (
    "优先股", "转为A股", "转为a股", "强制转股", "转股", "触发事件",
    "核心一级资本充足率降至", "恢复到5.125%以上",
)
_FIN_RATIO_CAPITAL_NARRATIVE_REJECT = (
    "营业收入", "净利润", "增幅", "利润表", "加权平均净资产收益率", "总资产收益率",
    "附加资本", "附加杠杆率", "系统重要性银行名单", "名单内第一组",
)
_FIN_RATIO_NPL_ROW_REJECT = (
    "长江三角洲", "珠江三角洲", "环渤海地区", "中部地区", "西部地区", "东北地区",
    "长三角", "浙江省", "江苏省", "北京市", "广东省",
    "制造业", "房地产业", "批发和零售业", "建筑业", "农、林、牧、渔业", "采矿业",
    "交通运输、仓储及邮政业", "信息传输、计算机服务和软件业",
    "信用贷款", "保证贷款", "抵押贷款", "质押贷款",
    "本行境内贷款和垫款", "公司类贷款和垫款",
)
# npl_ratio only: reject delta/comparison wording before the first ratio value, not
# after a valid inline ratio like 不良贷款率1.36%，较上年末下降...
_FIN_RATIO_NPL_DELTA_MARKERS = (
    "较上年", "较年初", "比上年", "下降", "上升", "变化", "增减", "不良率增减",
)
_FIN_RATIO_NPL_STRUCTURAL_REJECT = ("合计", "总额", "金额")
_FIN_RATIO_UNITS = ("元", "万元", "亿元", "千元", "百万元")
_FIN_RATIO_LINE_LOOKAHEAD = 3
_FIN_RATIO_CARRIER_RE = re.compile(r"[-+]?\d[\d,]*\.?\d*\s*[%％]?")
_FIN_RATIO_YEAR_RE = re.compile(r"20\d{2}")
_FIN_RATIO_HEADER_HINTS = ("（%）", "(%)", "％", "%", "指标", "情况", "如下", "如下表")


def _ratio_priority_labels(field_key: str, anchors: tuple[str, ...]) -> tuple[str, ...]:
    if field_key == "npl_ratio":
        pref = ("不良贷款率", "不良贷款比例", "不良率")
    elif field_key == "capital_adequacy_ratio":
        pref = ("资本充足率", "核心一级资本充足率", "一级资本充足率")
    elif field_key == "provision_coverage_ratio":
        pref = ("拨备覆盖率", "贷款损失准备覆盖率")
    else:
        pref = anchors
    seen: set[str] = set()
    ordered: list[str] = []
    for lab in pref + anchors:
        if lab not in seen:
            seen.add(lab)
            ordered.append(lab)
    return tuple(ordered)


def _ratio_is_year_token(val: str) -> bool:
    s = re.sub(r"[^\d]", "", val or "")
    return len(s) == 4 and bool(_FIN_RATIO_YEAR_RE.fullmatch(s))


def _ratio_numeric_ok(val: str, field_key: str, context: str) -> bool:
    s = (val or "").strip()
    if not s or not any(ch.isdigit() for ch in s):
        return False
    if _ratio_is_year_token(s):
        return False
    if any(u in s for u in _FIN_RATIO_UNITS):
        return False
    if "," in s and "%" not in s and "％" not in s:
        return False
    mag = _numeric_magnitude(s)
    if mag is None or mag < 0 or mag > 500:
        return False
    if "%" in s or "％" in s:
        return True
    local_pct = any(h in context for h in ("（%）", "(%)", "%", "％"))
    # Bare numerics are only allowed when the local context clearly signals a
    # ratio header/table instead of an amount/balance row.
    if any(h in context for h in ("（%）", "(%)", "%", "％", "比率", "比例", "指标", "率")):
        if "." not in s and not local_pct:
            return False
        if mag >= 100 and "." not in s:
            return False
        return True
    if field_key == "npl_ratio":
        return False
    return False


def _ratio_bad_anchor_context(field_key: str, label: str, line: str, window: str) -> bool:
    combined = (line or "") + " " + (window or "")
    if any(m in label for m in _FIN_RATIO_BAD_LABEL_MARKERS):
        return True
    if field_key == "npl_ratio":
        if any(m in combined for m in _FIN_RATIO_NPL_ROW_REJECT):
            return True
        if label == "不良率" and "不良率增减" in combined:
            return True
        if any(m in combined for m in _FIN_RATIO_NPL_STRUCTURAL_REJECT):
            return True
        if "余额" in combined and "不良贷款余额" not in combined:
            return True
        w = window or ""
        pre = w
        nm = _FIN_RATIO_CARRIER_RE.search(w)
        if nm:
            pre = w[: nm.start()]
        if any(m in pre for m in _FIN_RATIO_NPL_DELTA_MARKERS):
            return True
    if field_key in ("capital_adequacy_ratio", "provision_coverage_ratio"):
        if any(m in combined for m in _FIN_RATIO_INDUSTRY_CONTEXT):
            return True
    if field_key == "capital_adequacy_ratio" and any(
        m in combined for m in _FIN_RATIO_CAPITAL_NARRATIVE_REJECT
    ):
        return True
    if field_key == "capital_adequacy_ratio" and any(
        m in combined for m in _FIN_RATIO_PREFERRED_SHARE_CONTEXT
    ):
        return True
    return False


def _ratio_header_like(line: str, after: str) -> bool:
    aft = (after or "").strip()
    if not aft:
        return True
    if aft.startswith(("：", ":", "（", "(")):
        return True
    if any(h in line or h in aft for h in _FIN_RATIO_HEADER_HINTS):
        return True
    return False


def _extract_ratio_value_from_text(
    field_key: str,
    label: str,
    text: str,
    context: str,
    *,
    max_chars: int | None = None,
) -> str | None:
    scan = text[:max_chars] if max_chars else text
    accepted: list[tuple[str, int, str]] = []
    for match in _FIN_RATIO_CARRIER_RE.finditer(scan):
        val = match.group(0).strip()
        if not val or not any(ch.isdigit() for ch in val):
            continue
        if _ratio_bad_anchor_context(field_key, label, context, text):
            return None
        if _ratio_numeric_ok(val, field_key, context + " " + text):
            accepted.append((val, match.start(), scan[match.end(): match.end() + 8]))
    if not accepted:
        return None
    pct = [item for item in accepted if ("%" in item[0] or "％" in item[0]) and "百分点" not in item[2]]
    if pct:
        return pct[0][0]
    if field_key == "npl_ratio":
        ranked = sorted(
            accepted,
            key=lambda v: ((_numeric_magnitude(v[0]) or 9999.0), v[1]),
        )
        return ranked[0][0]
    return accepted[0][0]


def extract_financial_ratio_numeric(
    window: str,
    field_key: str,
    anchors: tuple[str, ...],
) -> list[dict]:
    """Bank-only ratio extraction with spaced-label matching and line fallback."""
    if field_key not in _FIN_RATIO_FIELDS:
        return []
    window = glue_numbers(window)
    lines = [ln.strip() for ln in window.split("\n")]
    labels = _ratio_priority_labels(field_key, anchors)
    for label in labels:
        pattern = _anchor_regex(label)
        for i, line in enumerate(lines):
            if not line:
                continue
            merged = " ".join(lines[i: i + 1 + _FIN_RATIO_LINE_LOOKAHEAD])
            for m in pattern.finditer(line):
                after = line[m.end():].strip()
                if _ratio_bad_anchor_context(field_key, label, line, after):
                    continue
                val = _extract_ratio_value_from_text(
                    field_key, label, after, line, max_chars=24,
                )
                if val:
                    return [{"label": label, "value": val}]
                if not _ratio_header_like(line, after):
                    continue
                for j, nxt in enumerate(lines[i + 1: i + 1 + _FIN_RATIO_LINE_LOOKAHEAD], start=1):
                    if not nxt:
                        break
                    if any(_anchor_regex(other).search(nxt) for other in labels):
                        break
                    context = " ".join(lines[i: i + j + 1])
                    val = _extract_ratio_value_from_text(
                        field_key, label, nxt, context,
                    )
                    if val:
                        return [{"label": label, "value": val}]
            mm = pattern.search(merged)
            if not mm:
                continue
            merged_after = merged[mm.end():].strip()
            if _ratio_bad_anchor_context(field_key, label, merged, merged_after):
                continue
            val = _extract_ratio_value_from_text(
                field_key, label, merged_after, merged, max_chars=96,
            )
            if val:
                return [{"label": label, "value": val}]
    return []


_NPL_RATIO_PRIMARY_ANCHORS = ("不良贷款率", "不良贷款比例")
_NPL_RATIO_CROSS_PAGE_RANK = (2, 7)


def _npl_ratio_amount_column_row(window: str) -> bool:
    """True when a label line mixes a comma-amount column with a ratio column."""
    w = glue_numbers(window)
    for line in [ln.strip() for ln in w.split("\n")[:12]]:
        for lab in _NPL_RATIO_PRIMARY_ANCHORS + ("不良率",):
            m = _anchor_regex(lab).search(line)
            if not m:
                continue
            after = line[m.end():]
            if re.search(r"\d{1,3},\d{3}", after) and re.search(r"[\d.]+\s*[%％]", after):
                return True
    return False


def _npl_ratio_kpi_table_window(window: str) -> bool:
    """True when the anchor sits on a multi-column KPI summary row."""
    w = glue_numbers(window)
    flat = w[:200].replace("\n", " ")
    for lab in _NPL_RATIO_PRIMARY_ANCHORS + ("不良率",):
        m = _anchor_regex(lab).search(flat)
        if not m:
            continue
        after = flat[m.end(): m.end() + 120]
        nums = [
            x.group(0).strip()
            for x in _FIN_RATIO_CARRIER_RE.finditer(after)
            if any(ch.isdigit() for ch in x.group(0))
        ]
        ratioish = 0
        for val in nums[:6]:
            if "%" in val or "％" in val:
                ratioish += 1
                continue
            s = re.sub(r"[^\d.\-+]", "", val.replace(",", ""))
            if not s:
                continue
            try:
                mag = float(s)
            except ValueError:
                continue
            if 0 < mag <= 100:
                ratioish += 1
        if ratioish >= 2:
            return True
    return False


def _try_npl_ratio_window(
    pages: list[str],
    cand: dict,
    anchors: tuple[str, ...],
    *,
    use_anchors: tuple[str, ...] | None = None,
) -> list[dict]:
    page_text = pages[cand["page"] - 1]
    window = page_text[cand["idx"]: cand["idx"] + 600]
    if _npl_ratio_amount_column_row(window):
        return []
    return extract_financial_ratio_numeric(
        window, "npl_ratio", use_anchors or anchors,
    )


def _pick_npl_ratio_candidate(
    pages: list[str],
    candidates: list[dict],
    preferred: set[int] | None,
    anchors: tuple[str, ...],
) -> tuple[list[dict], dict]:
    """Multi-pass npl_ratio candidate search with guarded cross-page fallback."""
    if not candidates:
        return [], {}
    chosen = candidates[0]
    base_page = chosen["page"]
    rank_of = {id(c): idx + 1 for idx, c in enumerate(candidates)}
    primary_anchors = tuple(a for a in _NPL_RATIO_PRIMARY_ANCHORS if a in anchors) or anchors

    for cand in candidates:
        if cand["page"] != base_page:
            continue
        labeled = _try_npl_ratio_window(pages, cand, anchors)
        if labeled:
            return labeled, cand

    if preferred:
        cross_page = [
            cand for cand in candidates
            if cand.get("in_region")
            and cand["page"] != base_page
            and _NPL_RATIO_CROSS_PAGE_RANK[0] <= rank_of[id(cand)] <= _NPL_RATIO_CROSS_PAGE_RANK[1]
        ]
        for cand in cross_page:
            labeled = _try_npl_ratio_window(
                pages, cand, anchors, use_anchors=primary_anchors,
            )
            if labeled:
                return labeled, cand

        if not any(c.get("in_region") for c in candidates[:8]):
            for cand in candidates:
                if cand.get("in_region"):
                    continue
                page_text = pages[cand["page"] - 1]
                window = page_text[cand["idx"]: cand["idx"] + 600]
                if not _npl_ratio_kpi_table_window(window):
                    continue
                labeled = _try_npl_ratio_window(pages, cand, anchors)
                if labeled:
                    return labeled, cand

    return [], chosen


# Broker income / margin extraction (#30d) — broker-only spaced-label parsers
# aligned with #30a audit evidence rules. Generic extract_numeric remains unchanged.
_BROKER_SEGMENT_INCOME_FIELDS = frozenset({
    "investment_banking_income",
    "asset_management_income",
})
_BROKER_SEGMENT_SECTION_MARKERS = (
    "主营业务分行业", "分行业情况", "收入和成本分析", "分业务",
    "营业收入", "营业支出", "营业利润率",
)
_BROKER_SEGMENT_HARD_REJECT = (
    "是指", "包括", "主要从事", "业务资格", "荣誉", "排名",
)
_BROKER_SEGMENT_SOFT_REJECT = ("同比", "增长", "下降", "百分点")
_BROKER_AM_REJECT_PAGE = ("注册资本", "总资产", "净资产", "净利润")
_BROKER_COMMA_AMOUNT_RE = re.compile(r"[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?")
_BROKER_IB_INCOME_LABELS = (
    "投资银行业务净收入", "投资银行业务手续费净收入",
    "投资银行业务", "投行业务",
)
_BROKER_AM_INCOME_LABELS = (
    "受托客户资产管理业务净收入", "资产管理业务净收入",
    "资产管理业务", "资管业务",
)
_BROKER_DEEP_IB_LABELS = ("投资银行业务净收入", "投行业务净收入")
_BROKER_DEEP_IB_FEE_CONTEXT = ("手续费及佣金净收入", "手续费及佣金")
_BROKER_DEEP_IB_MIN_MAGNITUDE = 1_000_000_000
_BROKER_MARGIN_LABELS = ("融出资金", "融资融券余额")
_BROKER_MARGIN_CONTEXT = ("非主营业务", "资产、负债情况分析", "资产构成", "占总资产")
_BROKER_MARGIN_REJECT = (
    "融资融券利息收入", "融出资金净增加额", "融出资金净减少额",
    "利息收入", "现金流", "减值", "预期信用",
    "及买入返售", "为人民币", "占比",
)
_BROKER_MARGIN_PAGE_REJECT = ("交易性金融资产",)
_BROKER_ASSET_COMPOSITION_RE = re.compile(
    r"融出\s*资\s*金\s+"
    r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?)\s+(\d+\.\d{2})\s+"
    r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})"
)
_BROKER_MARGIN_ROW_RE = re.compile(
    r"融出\s*资\s*金\s+(\d{1,3}(?:,\d{3})+(?:\.\d+)?)\s+(\d+\.\d{2})"
)


def _spaced_keyword_regex(keyword: str) -> re.Pattern:
    return re.compile(r"\s*".join(re.escape(ch) for ch in keyword))


def _broker_income_labels(field_key: str) -> tuple[str, ...]:
    if field_key == "investment_banking_income":
        return _BROKER_IB_INCOME_LABELS
    if field_key == "asset_management_income":
        return _BROKER_AM_INCOME_LABELS
    return ()


def _page_has_broker_segment_context(page_text: str) -> bool:
    return any(m in page_text for m in _BROKER_SEGMENT_SECTION_MARKERS)


def _page_has_margin_balance_context(page_text: str) -> bool:
    return any(m in page_text for m in _BROKER_MARGIN_CONTEXT)


def _broker_window_is_narrative(window: str) -> bool:
    local = window[:160]
    if any(m in local for m in _BROKER_SEGMENT_HARD_REJECT):
        return True
    if _BROKER_COMMA_AMOUNT_RE.search(local):
        return False
    return any(m in local for m in _BROKER_SEGMENT_SOFT_REJECT)


def extract_broker_segment_income(window: str, page_text: str, field_key: str) -> list[dict]:
    """Parse MD&A broker segment rows with whitespace-tolerant label matching."""
    if not _page_has_broker_segment_context(page_text):
        return []
    if field_key == "asset_management_income" and any(m in page_text for m in _BROKER_AM_REJECT_PAGE):
        return []
    window = glue_numbers(window)
    for lab in _broker_income_labels(field_key):
        for m in _spaced_keyword_regex(lab).finditer(window):
            local = window[max(0, m.start() - 20): m.end() + 100]
            if _broker_window_is_narrative(local):
                continue
            after = window[m.end(): m.end() + 60]
            amt_m = _BROKER_COMMA_AMOUNT_RE.search(after)
            if not amt_m:
                continue
            return [{"label": lab, "value": amt_m.group(0).strip()}]
    return []


def extract_broker_deep_ib_income(
    pages: list[str], regions: dict[str, set[int]] | None,
) -> tuple[list[dict], dict] | None:
    """Notes-only IB net income fallback for large-broker fee-note disclosures."""
    notes = (regions or {}).get("notes") or set()
    search_pages = [p for p in range(1, len(pages) + 1) if p in notes or p >= 80]
    best: tuple[list[dict], dict] | None = None
    for pno in search_pages:
        page_text = pages[pno - 1]
        if not any(m in page_text for m in _BROKER_DEEP_IB_FEE_CONTEXT):
            continue
        for lab in _BROKER_DEEP_IB_LABELS:
            for m in _spaced_keyword_regex(lab).finditer(page_text):
                after = page_text[m.end(): m.end() + 80]
                amt_m = _BROKER_COMMA_AMOUNT_RE.search(after)
                if not amt_m:
                    continue
                val = amt_m.group(0).strip()
                mag = _numeric_magnitude(val)
                if mag is None or mag < _BROKER_DEEP_IB_MIN_MAGNITUDE:
                    continue
                chosen = {
                    "page": pno,
                    "idx": m.start(),
                    "anchor": lab,
                    "in_region": pno in notes,
                    "col": m.start() - (page_text.rfind("\n", 0, m.start()) + 1),
                }
                pair = ([{"label": lab, "value": val}], chosen)
                if best is None or lab == "投资银行业务净收入":
                    best = pair
                    if lab == "投资银行业务净收入":
                        return best
    return best


def extract_broker_margin_balance(page_text: str) -> tuple[list[dict], int | None]:
    """MD&A asset-composition 融出资金 row; intentionally excludes notes search."""
    if not _page_has_margin_balance_context(page_text):
        return [], None
    if any(m in page_text for m in _BROKER_MARGIN_PAGE_REJECT):
        return [], None
    flat = page_text.replace("\n", " ")
    comp = _BROKER_ASSET_COMPOSITION_RE.search(flat)
    if comp:
        for m in re.finditer(r"融出\s*资\s*金", page_text):
            chunk = page_text[m.start(): m.start() + 220]
            if any(r in chunk for r in _BROKER_MARGIN_REJECT):
                continue
            row = _BROKER_MARGIN_ROW_RE.search(chunk.replace("\n", " "))
            if row and row.group(1) == comp.group(1):
                return [{"label": "融出资金", "value": comp.group(1)}], m.start()
    for lab in _BROKER_MARGIN_LABELS:
        for m in _spaced_keyword_regex(lab).finditer(page_text):
            chunk = page_text[m.start(): m.start() + 220]
            if any(r in chunk for r in _BROKER_MARGIN_REJECT):
                continue
            row = _BROKER_MARGIN_ROW_RE.search(chunk.replace("\n", " "))
            if row:
                return [{"label": lab, "value": row.group(1)}], m.start()
    return [], None


def _extract_broker_segment_income_field(
    spec: FieldSpec,
    pages: list[str],
    source_url: str,
    regions: dict[str, set[int]] | None,
    out: dict,
    profile_fields: dict[str, dict] | None = None,
) -> dict:
    if (
        spec.key == "asset_management_income"
        and ((profile_fields or {}).get("brokerage_income") or {}).get("status") == "found"
    ):
        return out
    preferred = (regions or {}).get(spec.region)
    candidates = locate_candidates(pages, spec.anchors, preferred, spec.avoid, limit=8)
    chosen: dict | None = None
    labeled: list[dict] = []
    for cand in candidates:
        if preferred and not cand.get("in_region"):
            continue
        page_text = pages[cand["page"] - 1]
        window = page_text[cand["idx"]: cand["idx"] + 600]
        labeled = extract_broker_segment_income(window, page_text, spec.key)
        if labeled:
            chosen = cand
            break
    if not labeled and spec.key == "investment_banking_income":
        deep = extract_broker_deep_ib_income(pages, regions)
        if deep:
            labeled, chosen = deep
    if not chosen or not labeled:
        return out
    page_text = pages[chosen["page"] - 1]
    window = page_text[chosen["idx"]: chosen["idx"] + 600]
    in_region = bool(chosen.get("in_region"))
    heading = _is_heading(page_text, chosen["idx"], chosen.get("col", 99))
    out["page"] = chosen["page"]
    out["anchor_matched"] = chosen.get("anchor") or labeled[0]["label"]
    out["in_region"] = in_region
    out["evidence_sentence"] = evidence_sentence(page_text, chosen["idx"], out["anchor_matched"])
    located_well = (in_region or not preferred) and heading
    out["source_url"] = source_url
    out["value"] = {"labeled": labeled, "context": truncate(clean_text(window[:200]), 200)}
    out["status"] = "found" if (labeled and located_well) else ("partial" if labeled else "not_found")
    return out


def _extract_broker_margin_balance_field(
    spec: FieldSpec,
    pages: list[str],
    source_url: str,
    regions: dict[str, set[int]] | None,
    out: dict,
) -> dict:
    preferred = (regions or {}).get(spec.region)
    if not preferred:
        return out
    chosen: dict | None = None
    labeled: list[dict] = []
    row_idx: int | None = None
    seen_pages: set[int] = set()
    candidates = locate_candidates(pages, _BROKER_MARGIN_LABELS, preferred, spec.avoid, limit=8)
    for cand in candidates:
        pno = cand["page"]
        if pno in seen_pages:
            continue
        seen_pages.add(pno)
        page_text = pages[pno - 1]
        labeled, row_idx = extract_broker_margin_balance(page_text)
        if labeled:
            chosen = {**cand, "idx": row_idx if row_idx is not None else cand["idx"]}
            break
    if not chosen or not labeled:
        for pno in sorted(preferred):
            if pno in seen_pages:
                continue
            page_text = pages[pno - 1]
            labeled, row_idx = extract_broker_margin_balance(page_text)
            if labeled:
                chosen = {
                    "page": pno,
                    "idx": row_idx or 0,
                    "anchor": labeled[0]["label"],
                    "in_region": True,
                    "col": 0,
                }
                break
    if not chosen or not labeled:
        return out
    page_text = pages[chosen["page"] - 1]
    window = page_text[chosen["idx"]: chosen["idx"] + 600]
    in_region = bool(chosen.get("in_region"))
    heading = _is_heading(page_text, chosen["idx"], chosen.get("col", 99))
    out["page"] = chosen["page"]
    out["anchor_matched"] = chosen.get("anchor") or labeled[0]["label"]
    out["in_region"] = in_region
    out["evidence_sentence"] = evidence_sentence(page_text, chosen["idx"], out["anchor_matched"])
    located_well = (in_region or not preferred) and heading
    out["source_url"] = source_url
    out["value"] = {"labeled": labeled, "context": truncate(clean_text(window[:200]), 200)}
    out["status"] = "found" if (labeled and located_well) else ("partial" if labeled else "not_found")
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


# R&D situation-table path (#32c-R2): scan MD&A 研发投入情况表 blocks with unit
# scaling; merged with anchor baseline via max-rank guard in extract_field().
_RND_TABLE_CTX = (
    "研发投入情况", "研发投入总额", "研发投入合计", "研发支出情况",
    "费用化研发投入", "资本化研发投入", "研发投入情况表",
)
_RND_TOTAL_LABELS = ("研发投入合计", "研发投入总额", "研发支出合计", "研发支出总额", "合计")
_RND_CUMULATIVE_MARKERS = ("累计", "近年来", "过去三年", "截至目前", "近三年")
_STRICT_RND_MIN = 100_000
_RND_LINE_NUM_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


def _detect_rnd_window_unit(window: str) -> str:
    head = window[:220]
    if "百万元" in head:
        return "百万元"
    if "单位：亿元" in head or "单位:亿元" in head or "人民币亿元" in head:
        return "亿元"
    if "单位：万元" in head or "单位:万元" in head or "人民币万元" in head:
        return "万元"
    if "单位：千元" in head or "单位:千元" in head:
        return "千元"
    if "单位：元" in head or "单位:元" in head:
        return "元"
    return ""


def _rnd_amount_to_yuan(val: str, default_unit: str = "") -> float | None:
    mag = _numeric_magnitude(val)
    if mag is None:
        return None
    unit = default_unit
    for u in ("百万元", "亿元", "万元", "千元", "元"):
        if u in val:
            unit = u
            break
    if unit == "亿元":
        return mag * 1e8
    if unit == "万元":
        return mag * 1e4
    if unit == "百万元":
        return mag * 1e6
    if unit == "千元":
        return mag * 1e3
    return mag


def _parse_rnd_line_amount(line: str, label: str, default_unit: str = "") -> tuple[str, float] | None:
    variants = [label, f"本期{label}", "本期费用化研发投入"]
    pos = -1
    matched = label
    for v in variants:
        if v in line:
            pos = line.find(v)
            matched = v
            break
    if pos < 0:
        return None
    after = line[pos + len(matched):]
    m = _RND_LINE_NUM_RE.search(after)
    if not m:
        return None
    raw = m.group(0).strip()
    unit = default_unit
    tail = after[m.end(): m.end() + 8]
    for u in ("百万元", "亿元", "万元", "千元"):
        if u in tail or u in after[max(0, m.start() - 4): m.end() + 8]:
            unit = u
            break
    display = f"{raw} {unit}".strip() if unit and unit not in raw else raw
    yuan = _rnd_amount_to_yuan(display, default_unit)
    if yuan is None or yuan <= 0:
        return None
    if default_unit and unit not in display:
        display = f"{raw} {default_unit}"
        yuan = _rnd_amount_to_yuan(display, default_unit)
    return display, yuan


def _rnd_situation_block_on_page(page_text: str) -> str | None:
    for marker in ("研发投入情况表", "研发支出情况", "(1).研发投入情况表"):
        idx = page_text.find(marker)
        if idx < 0:
            continue
        unit_pos = page_text.rfind("单位", max(0, idx - 150), idx + 80)
        start = unit_pos if unit_pos >= 0 else max(0, idx - 60)
        return page_text[start: idx + 650]
    return None


def _extract_rnd_table_amounts(window: str) -> list[dict]:
    default_unit = _detect_rnd_window_unit(window)
    cut = window
    for stop in ("研发人员情况表", "研发人员情况", "(2).", "（2）"):
        pos = cut.find(stop)
        if pos > 0 and "研发投入合计" in cut[:pos]:
            cut = cut[:pos]
            break
    flat = re.sub(r"\s+", " ", cut.replace("\n", " "))
    found: dict[str, dict] = {}
    labels = (
        "研发投入合计", "费用化研发投入", "资本化研发投入",
        "研发支出合计", "研发投入金额",
    )
    for text in (flat,):
        if "同比增长" in text and "研发投入合计" not in text and "费用化研发投入" not in text:
            continue
        for label in labels:
            if label not in text and f"本期{label}" not in text:
                continue
            parsed = _parse_rnd_line_amount(text, label, default_unit)
            if not parsed:
                continue
            display, yuan = parsed
            if label not in found or label in _RND_TOTAL_LABELS:
                found[label] = {"label": label, "value": display, "_yuan": yuan}
    return list(found.values())


def _labeled_from_rnd_situation_block(block: str) -> list[dict]:
    labeled = _extract_rnd_table_amounts(block)
    if not labeled:
        return []
    exp = next((x for x in labeled if x.get("label") == "费用化研发投入"), None)
    cap = next((x for x in labeled if x.get("label") == "资本化研发投入"), None)
    total = next((x for x in labeled if x.get("label") == "研发投入合计"), None)
    if total:
        return [total]
    if exp and cap:
        ey, cy = exp.get("_yuan") or 0, cap.get("_yuan") or 0
        if ey + cy > 0:
            return [{"label": "研发投入合计", "value": exp["value"], "_yuan": ey + cy,
                     "_display": _format_rnd_audit_value("研发投入合计", exp["value"], ey + cy)}]
    if exp:
        return [exp]
    return labeled[:2]


def _format_rnd_audit_value(label: str, display: str, yuan: float) -> str:
    if yuan >= _STRICT_RND_MIN:
        return f"{yuan:,.0f}"
    if any(u in display for u in ("亿元", "万元", "百万元", "千元")):
        return display
    return display


def _score_rnd_situation_window(window: str, labeled: list[dict], anchor: str) -> float:
    score = 0.0
    ctx = window[:600]
    has_rnd_table = any(k in ctx for k in ("研发投入情况表", "研发支出情况", "费用化研发投入", "研发投入合计"))
    if _looks_like_income_statement_block(ctx) and not has_rnd_table:
        score -= 200.0
    elif _looks_like_income_statement_block(ctx) and has_rnd_table:
        score -= 40.0
    if any(m in ctx for m in _RND_CUMULATIVE_MARKERS):
        score -= 80.0
    for kw in _RND_TABLE_CTX:
        if kw in ctx:
            score += 15.0
    if "研发投入情况" in ctx or "研发支出情况" in ctx:
        score += 80.0
    if "单位：" in ctx or "单位:" in ctx:
        score += 15.0
    if "同比增长" in ctx and "研发投入合计" not in ctx:
        score -= 60.0
    if "单位：万元" in ctx or "单位:万元" in ctx:
        score += 10.0
    for item in labeled:
        lab = item.get("label") or ""
        val = item.get("value") or ""
        if lab in _RND_TOTAL_LABELS or "合计" in lab or "总额" in lab:
            score += 50.0
        if lab == "费用化研发投入":
            score += 5.0
        if lab == "研发费用":
            score -= 30.0
        yuan = _rnd_amount_to_yuan(val) or 0
        if yuan >= _STRICT_RND_MIN:
            score += 20.0
    if anchor in ("研发投入合计", "研发投入总额", "费用化研发投入"):
        score += 12.0
    if anchor == "研发费用":
        score -= 25.0
    return score


def _rnd_field_template(spec: FieldSpec, source_url: str) -> dict:
    return {
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


def extract_rnd_investment_baseline(
    spec: FieldSpec, pages: list[str], source_url: str,
    preferred: set[int] | None,
) -> dict:
    """Anchor-based rnd_investment extraction (pre-#32c-R2 baseline path)."""
    out = _rnd_field_template(spec, source_url)
    candidates = locate_candidates(pages, spec.anchors, preferred, spec.avoid, limit=8)
    if not candidates:
        return out
    chosen = candidates[0]
    page_text = pages[chosen["page"] - 1]
    window = page_text[chosen["idx"]: chosen["idx"] + 600]
    labeled = extract_rnd_numeric(window)
    if not labeled:
        skip_fallback = (
            chosen["anchor"] == "研发投入"
            and "不适用" in window
            and "适用" in window
        )
        if not skip_fallback:
            for cand in candidates[1:]:
                page_text = pages[cand["page"] - 1]
                window = page_text[cand["idx"]: cand["idx"] + 600]
                labeled = extract_rnd_numeric(window)
                if labeled:
                    chosen = cand
                    break
    page_text = pages[chosen["page"] - 1]
    in_region = bool(chosen.get("in_region"))
    heading = _is_heading(page_text, chosen["idx"], chosen.get("col", 99))
    out["page"] = chosen["page"]
    out["anchor_matched"] = chosen["anchor"]
    out["in_region"] = in_region
    out["evidence_sentence"] = evidence_sentence(page_text, chosen["idx"], chosen["anchor"])
    located_well = (in_region or not preferred) and heading
    out["value"] = {"labeled": labeled, "context": truncate(clean_text(window[:200]), 200)}
    out["status"] = "found" if (labeled and located_well) else ("partial" if labeled else "not_found")
    return out


def extract_rnd_situation_table_numeric(
    spec: FieldSpec, pages: list[str], source_url: str,
    regions: dict[str, set[int]] | None = None,
) -> dict | None:
    """Situation-table-first R&D selector (#32c-R2 production helper)."""
    preferred = (regions or {}).get(spec.region)
    best_score = float("-inf")
    best: dict | None = None

    def consider(window: str, page: int, anchor: str, idx: int, page_text: str, bonus: float = 0.0):
        nonlocal best_score, best
        if any(m in window for m in _RND_CUMULATIVE_MARKERS):
            if "费用化研发投入" not in window and "研发投入合计" not in window:
                return
        sit = _labeled_from_rnd_situation_block(window)
        if sit:
            labeled = sit
        else:
            labeled = _extract_rnd_table_amounts(window)
            if not labeled and not _looks_like_income_statement_block(window[:500]):
                labeled = extract_rnd_numeric(window)
        if not labeled:
            return
        total_item = labeled[0]
        yuan = total_item.get("_yuan") or _rnd_amount_to_yuan(total_item.get("value") or "") or 0
        if yuan < 10_000 and "研发投入情况表" not in window:
            return
        out_labeled = [{
            "label": total_item["label"],
            "value": total_item.get("_display") or _format_rnd_audit_value(
                total_item["label"], total_item["value"], total_item.get("_yuan") or 0,
            ),
        }]
        score = _score_rnd_situation_window(window, labeled, anchor) + bonus
        if score <= best_score:
            return
        in_region = page in preferred if preferred else True
        has_total = total_item.get("label") in _RND_TOTAL_LABELS or "合计" in (total_item.get("label") or "")
        if has_total and yuan >= _STRICT_RND_MIN and (in_region or not preferred):
            status = "found"
        elif labeled:
            status = "partial"
        else:
            status = "not_found"
        best_score = score
        best = {
            **_rnd_field_template(spec, source_url),
            "status": status,
            "in_region": in_region,
            "value": {
                "labeled": out_labeled,
                "context": truncate(clean_text(window[:250]), 250),
            },
            "evidence_sentence": evidence_sentence(page_text, idx, anchor),
            "page": page,
            "anchor_matched": anchor,
        }

    scan_pages = sorted(preferred) if preferred else range(1, len(pages) + 1)
    for pno in scan_pages:
        if pno < 1 or pno > len(pages):
            continue
        page_text = pages[pno - 1]
        block = _rnd_situation_block_on_page(page_text)
        if block:
            idx = page_text.find("研发投入情况表")
            if idx < 0:
                idx = page_text.find("研发支出情况")
            consider(block, pno, "研发投入情况表", max(idx, 0), page_text, bonus=120.0)

    candidates = locate_candidates(pages, spec.anchors, preferred, spec.avoid, limit=12)
    for cand in candidates:
        page_text = pages[cand["page"] - 1]
        win_start = max(0, cand["idx"] - 250)
        window = page_text[win_start: cand["idx"] + 800]
        block = _rnd_situation_block_on_page(window) or window
        consider(block, cand["page"], cand["anchor"], cand["idx"], page_text, bonus=0.0)

    return best


def _rnd_strict_rank(label: str) -> int:
    return {
        "usable": 4, "partial": 3, "wrong": 2,
        "not_found_missed": 1, "not_found_unverified": 1, "not_found": 1,
    }.get(label, 0)


def _is_cumulative_narrative_rnd(field: dict) -> bool:
    val = field.get("value")
    ctx = ""
    if isinstance(val, dict):
        ctx = val.get("context") or ""
    ctx += " " + (field.get("evidence_sentence") or "")
    if not any(m in ctx for m in _RND_CUMULATIVE_MARKERS):
        return False
    if "研发投入情况表" in ctx or "费用化研发投入" in ctx:
        return False
    return True


def merge_rnd_investment_with_guard(baseline: dict, situation: dict | None) -> dict:
    """max(baseline, situation-table) guard — never downgrade baseline strict rank."""
    if not situation or situation.get("status") == "not_found" or not situation.get("value"):
        return baseline
    from lab.strict_audit_full_market import strict_audit_field  # lazy: circular import

    base_strict, _ = strict_audit_field(baseline)
    sit_strict, _ = strict_audit_field(situation)
    prod_rank = _rnd_strict_rank(base_strict)
    sit_rank = _rnd_strict_rank(sit_strict)
    sit_eligible = sit_rank >= prod_rank and not _is_cumulative_narrative_rnd(situation)
    if not sit_eligible:
        return baseline
    tie_order = {"baseline": 2, "situation": 1}
    candidates = [
        ("baseline", baseline, base_strict),
        ("situation", situation, sit_strict),
    ]
    source, field, _ = max(
        candidates,
        key=lambda c: (_rnd_strict_rank(c[2]), tie_order.get(c[0], 0)),
    )
    if source == "situation":
        merged = dict(field)
        merged["anchor_matched"] = (field.get("anchor_matched") or "") + " (situation_table)"
        return merged
    return baseline


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


_PREVIEW_ROW_LIMIT = 8
_REVENUE_CONTINUATION_FIELDS = frozenset({"revenue_by_region", "revenue_by_segment"})


def _table_row_joined(row: list) -> str:
    return " ".join(_table_cell_text(c) for c in row)


def _preview_has_revenue_section_header(rows: list, preview_focus: tuple[str, ...]) -> bool:
    markers = tuple(preview_focus) + ("分地区", "分行业", "分产品",
                                      "主营业务分地区", "主营业务分行业", "主营业务分产品")
    for row in rows[:4]:
        rt = _table_row_joined(row)
        if any(m in rt for m in markers):
            return True
    return False


def _reject_continuation_table(flat: str) -> bool:
    if "科目" in flat and ("本期数" in flat or "上年同期" in flat):
        return True
    if "合同标的" in flat and "履行金额" in flat:
        return True
    if "分行业情况" in flat and ("成本构成" in flat or "成本构" in flat):
        return True
    if "主要产品" in flat and ("生产量" in flat or "销售量" in flat):
        return True
    return False


def _continuation_stop_row(row: list, field_key: str) -> bool:
    rt = _table_row_joined(row)
    if not rt.strip():
        return False
    if "分销售模式" in rt or "主营业务分销售" in rt:
        return True
    if any(x in rt for x in ("主要产品", "生产量", "销售量", "库存量", "合同标的", "成本构成")):
        return True
    if field_key == "revenue_by_region":
        if "主营业务分行业" in rt or "主营业务分产品" in rt:
            return True
        compact = rt.replace(" ", "").replace("\n", "")
        if compact in ("分行业", "分产品") or compact.startswith("分行业") and "营业收入" in rt:
            return True
        if compact.startswith("分产品") and "营业收入" in rt:
            return True
    elif field_key == "revenue_by_segment":
        if "主营业务分地区" in rt:
            return True
        compact = rt.replace(" ", "").replace("\n", "")
        if compact.startswith("分地区") and "营业收入" in rt:
            return True
    return False


def _format_preview_row(row: list) -> list:
    return [truncate(str(c or ""), 40) for c in row[:6]]


def _stitch_revenue_table_continuation(
    pdf_path: str,
    tbl: dict,
    field_key: str,
    preview_focus: tuple[str, ...],
) -> dict:
    """Append page N+1 revenue table body when preview on page N is header-only."""
    if field_key not in _REVENUE_CONTINUATION_FIELDS:
        return tbl
    rows = tbl.get("rows") or []
    if any(_table_row_is_data_row(r) for r in rows):
        return tbl
    if not _preview_has_revenue_section_header(rows, preview_focus):
        return tbl

    header_page = tbl.get("table_page")
    if not header_page:
        return tbl
    next_page = header_page + 1

    try:
        import pdfplumber  # type: ignore
    except Exception:
        return tbl

    best_append: list[list] = []
    try:
        with open(pdf_path, "rb") as fh:
            data = fh.read()
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            if next_page < 1 or next_page > len(pdf.pages):
                return tbl
            page = pdf.pages[next_page - 1]
            for raw_tbl in (page.extract_tables() or []):
                flat = " ".join(str(c) for row in raw_tbl for c in row if c)
                if _reject_continuation_table(flat):
                    continue
                append: list[list] = []
                for row in raw_tbl:
                    if _continuation_stop_row(row, field_key):
                        break
                    if _table_row_is_data_row(row):
                        append.append(_format_preview_row(row))
                if len(append) > len(best_append):
                    best_append = append
    except Exception:
        return tbl

    if not best_append:
        return tbl

    combined = list(rows) + best_append
    tbl = dict(tbl)
    tbl["rows"] = combined[:_PREVIEW_ROW_LIMIT]
    tbl["continuation_page"] = next_page
    tbl["stitched"] = True
    return tbl


def _is_region_sales_mode_header_row(row: list) -> bool:
    """Standalone 分销售模式 / 销售模式 subsection header (not a data row)."""
    if _table_row_is_data_row(row):
        return False
    cells = [_table_cell_text(c) for c in row]
    nonempty = [c.replace(" ", "").replace("\n", "") for c in cells if c]
    if not nonempty:
        return False
    first = nonempty[0]
    return first in ("分销售模式", "销售模式")


def _preview_needs_region_trim(rows: list) -> bool:
    """Bleed signature from focus cases: sales-mode section after region rows."""
    if not any(_is_region_sales_mode_header_row(r) for r in rows):
        return False
    has_placeholder = any(
        _table_cell_text(c) in ("--", "—", "－")
        for r in rows for c in r
    )
    has_online_offline = any(
        "线上订单" in _table_row_joined(r) or "线下订单" in _table_row_joined(r)
        for r in rows
    )
    return has_placeholder or has_online_offline


def _is_region_stacked_boundary_row(row: list) -> bool:
    """Next-section header row while previewing revenue_by_region."""
    return _is_region_sales_mode_header_row(row)


def _trim_revenue_stacked_preview(tbl: dict, field_key: str) -> dict:
    """Trim same-page stacked preview before the next subsection header."""
    if field_key != "revenue_by_region":
        return tbl
    rows = tbl.get("rows") or []
    if len(rows) < 2 or not _preview_needs_region_trim(rows):
        return tbl

    trimmed: list[list] = []
    for i, row in enumerate(rows):
        if i > 0 and _is_region_stacked_boundary_row(row):
            break
        trimmed.append(row)

    if len(trimmed) == len(rows):
        return tbl
    out = dict(tbl)
    out["rows"] = trimmed
    out["preview_trimmed"] = True
    return out


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
    profile_fields: dict[str, dict] | None = None,
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

    if spec.extraction == "numeric" and spec.key == "rnd_investment":
        baseline = (
            extract_rnd_investment_baseline(spec, pages, source_url, preferred)
            if loc else _rnd_field_template(spec, source_url)
        )
        situation = extract_rnd_situation_table_numeric(spec, pages, source_url, regions)
        return merge_rnd_investment_with_guard(baseline, situation)

    if not loc:
        return out

    if spec.extraction == "numeric" and spec.key in _FIN_RATIO_FIELDS:
        cand_limit = 12 if spec.key == "npl_ratio" else 8
        candidates = locate_candidates(
            pages, spec.anchors, preferred, spec.avoid, limit=cand_limit,
        )
        if not candidates:
            return out
        chosen = candidates[0]
        base_page = chosen["page"]
        if spec.key == "npl_ratio":
            labeled, chosen = _pick_npl_ratio_candidate(
                pages, candidates, preferred, spec.anchors,
            )
        else:
            labeled = []
            for cand in candidates:
                if cand["page"] != base_page:
                    continue
                page_text = pages[cand["page"] - 1]
                window = page_text[cand["idx"]: cand["idx"] + 600]
                labeled = extract_financial_ratio_numeric(window, spec.key, spec.anchors)
                if labeled:
                    chosen = cand
                    break
        page_text = pages[chosen["page"] - 1]
        window = page_text[chosen["idx"]: chosen["idx"] + 600]
        in_region = bool(chosen.get("in_region"))
        heading = _is_heading(page_text, chosen["idx"], chosen.get("col", 99))
        out["page"] = chosen["page"]
        out["anchor_matched"] = chosen["anchor"]
        out["in_region"] = in_region
        out["evidence_sentence"] = evidence_sentence(page_text, chosen["idx"], chosen["anchor"])
        located_well = (in_region or not preferred) and heading
        out["value"] = {"labeled": labeled, "context": truncate(clean_text(window[:200]), 200)}
        out["status"] = "found" if (labeled and located_well) else ("partial" if labeled else "not_found")
        return out

    if spec.extraction == "numeric" and spec.key in _BROKER_SEGMENT_INCOME_FIELDS:
        return _extract_broker_segment_income_field(
            spec, pages, source_url, regions, out, profile_fields=profile_fields,
        )

    if spec.extraction == "numeric" and spec.key == "margin_lending_balance":
        return _extract_broker_margin_balance_field(spec, pages, source_url, regions, out)

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
        focus = spec.table_match or spec.anchors
        tbl = extract_table_near(pdf_path, loc["page"], spec.anchors, spec.table_match, spec.table_require,
                                 preview_focus=focus)
        if tbl and spec.key in _REVENUE_CONTINUATION_FIELDS:
            tbl = _stitch_revenue_table_continuation(pdf_path, tbl, spec.key, focus)
            tbl = _trim_revenue_stacked_preview(tbl, spec.key)
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

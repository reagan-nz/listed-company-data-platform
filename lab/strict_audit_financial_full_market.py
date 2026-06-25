"""Financial-only automated strict audit for full_market_2024.

Read-only over outputs; does not modify profiles, eval_results, PDFs, or extraction.
Separate from non-financial 11-field strict headline (9.43/11).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import (  # noqa: E402
    _numeric_magnitude,
    _table_row_is_data_row,
    revenue_table_plausible,
    rnd_investment_plausible,
)
from lab.field_schema import FieldSpec, get_field_specs  # noqa: E402

DEFAULT_OUT = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
DEFAULT_YAML = os.path.join(_PROJECT_ROOT, "lab", "eval_companies_full_market_2024.yaml")

SUBTYPE_CAVEAT_CODES = frozenset({"000402", "600816", "600318"})

POINTER_KW = ("详见", "参见", "请见", "见下文", "见本报告", "见上述", "见附注")
FIN_BOILER_KW = (
    "金融工具", "公允价值", "《企业会计准则", "法律法规", "监管要求", "套期保值",
    "免责声明", "本报告内容", "备查文件",
)
LEGAL_DISCLAIMER_KW = ("不承担", "不构成投资建议", "投资者应当")

RATIO_FIELDS = frozenset({
    "npl_ratio", "capital_adequacy_ratio", "provision_coverage_ratio",
    "solvency_ratio", "combined_ratio",
})

AMOUNT_NOISE_LABELS = (
    "页码", "单位", "币种", "人民币", "百万元", "千元", "附注",
)

# Wrong-line-item labels for specific fields (numeric noise).
FIELD_REJECT_LABELS: dict[str, tuple[str, ...]] = {
    "net_interest_income": ("营业收入", "营业总收入", "利润总额"),
    "non_interest_income": ("营业收入", "营业成本"),
    "brokerage_income": ("营业收入", "营业总收入"),
    "premium_income": ("营业总收入", "净利润"),
    "npl_ratio": ("拨备", "覆盖率", "资本充足"),
    "capital_adequacy_ratio": ("不良", "拨备"),
}


@dataclass
class FinAuditRow:
    code: str
    name: str
    board: str
    schema_profile: str
    field: str
    extraction_type: str
    status: str
    proxy_plausible: bool
    strict_label: str
    reason: str
    value_preview: str
    evidence_sentence: str
    page: str
    source_url: str
    subtype_caveat_flag: bool


def _load_meta(yaml_path: str) -> dict[str, dict]:
    data = yaml.safe_load(open(yaml_path, encoding="utf-8")) or {}
    return {str(c["stock_code"]): c for c in data.get("companies", [])}


def _profile_path(out_dir: str, code: str, board: str) -> str | None:
    for rel in (f"{code}/company_profile.json", f"{board}/{code}/company_profile.json"):
        p = os.path.join(out_dir, rel)
        if os.path.isfile(p):
            return p
    return None


def _pdf_path(out_dir: str, code: str, board: str) -> str | None:
    p = os.path.join(out_dir, board, code, f"{code}.pdf")
    return p if os.path.isfile(p) else None


def _field_map(profile: dict) -> dict[str, dict]:
    return {f["field"]: f for f in profile.get("fields", [])}


def _is_pointer_only(text: str) -> bool:
    t = (text or "").strip()
    if len(t) >= 80:
        return False
    return any(p in t for p in POINTER_KW)


def value_preview(field: dict, limit: int = 160) -> str:
    v = field.get("value")
    if v is None:
        return ""
    if isinstance(v, str):
        text = v
    elif isinstance(v, dict) and "labeled" in v:
        pairs = "; ".join(f"{p.get('label')}={p.get('value')}" for p in v.get("labeled", [])[:4])
        text = pairs or v.get("context", "")
    elif isinstance(v, dict) and "ratio" in v:
        text = f"amount={v.get('amount') or 'n/a'} ratio={v.get('ratio') or 'n/a'}"
    elif isinstance(v, dict) and "rows" in v:
        rows = v.get("rows", [])
        head = " / ".join(" | ".join(str(c) for c in r) for r in rows[:2])
        text = f"[table p.{v.get('table_page')} hits={v.get('match_hits')}] {head}"
    else:
        text = str(v)
    text = " ".join(text.split())
    return text[:limit] + ("..." if len(text) > limit else "")


def field_plausible(f: dict) -> bool:
    if f.get("status") != "found":
        return False
    ex = f.get("extraction")
    v = f.get("value")
    if ex == "section_snippet":
        return isinstance(v, str) and len(v) >= 25
    if ex == "numeric":
        if f.get("field") == "rnd_investment":
            return rnd_investment_plausible(v)
        return isinstance(v, dict) and any(
            any(c.isdigit() for c in (x.get("value") or "")) for x in v.get("labeled", [])
        )
    if ex == "concentration":
        return isinstance(v, dict) and bool(v.get("ratio") or v.get("amount"))
    if ex == "table":
        fk = f.get("field")
        if fk in ("revenue_by_region", "revenue_by_segment"):
            return revenue_table_plausible(v)
        return isinstance(v, dict) and bool(v.get("rows")) and v.get("match_hits", 0) >= 1
    return False


def _looks_like_ratio_value(val: str) -> bool:
    s = (val or "").strip()
    if not s or not any(c.isdigit() for c in s):
        return False
    if re.search(r"[%％]", s):
        return True
    mag = _numeric_magnitude(s)
    if mag is None:
        return False
    if mag >= 1_000_000:
        return False
    if any(u in s for u in ("万元", "亿元", "千元", "百万元")):
        return False
    return 0 <= mag <= 500


def _looks_like_amount_value(val: str) -> bool:
    s = (val or "").strip()
    if not s or not any(c.isdigit() for c in s):
        return False
    mag = _numeric_magnitude(s)
    if mag is None:
        return False
    if re.search(r"[%％]", s) and mag <= 100:
        return False
    return mag >= 100 or any(u in s for u in ("万元", "亿元", "千元", "百万元", "元"))


def _anchor_in_text(text: str, anchors: tuple[str, ...]) -> bool:
    t = text or ""
    return any(a in t for a in anchors)


def _pdf_anchor_with_number(pdf_path: str | None, anchors: tuple[str, ...], max_pages: int = 80) -> bool:
    """Conservative missed-disclosure check: anchor + financial-looking number nearby."""
    if not pdf_path or not os.path.isfile(pdf_path):
        return False
    fin_num = re.compile(r"[%％]|(?:万元|亿元|百万元|千元)|\d{1,3}(?:,\d{3})+|\d+\.\d{2,}")
    try:
        import fitz
    except ImportError:
        return False
    try:
        doc = fitz.open(pdf_path)
        n = min(len(doc), max_pages)
        for i in range(n):
            text = doc[i].get_text()
            for a in anchors:
                pos = 0
                while True:
                    idx = text.find(a, pos)
                    if idx < 0:
                        break
                    window = text[idx : idx + 100]
                    if fin_num.search(window):
                        doc.close()
                        return True
                    pos = idx + max(len(a), 1)
        doc.close()
    except Exception:
        return False
    return False


def strict_section_snippet(f: dict, spec: FieldSpec) -> tuple[str, str]:
    st = f.get("status", "not_found")
    if st == "not_found":
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        v = f.get("value") if isinstance(f.get("value"), str) else ""
        if v and len(v) >= 25:
            return "partial", "status=partial with some content"
        return "partial", "status=partial low confidence"
    v = f.get("value")
    if not isinstance(v, str):
        return "wrong", "expected string snippet"
    ev = f.get("evidence_sentence") or ""
    combined = v + ev
    if _is_pointer_only(v) or (_is_pointer_only(ev) and len(v) < 80):
        return "wrong", "pointer-only reference"
    if any(b in combined for b in FIN_BOILER_KW):
        return "wrong", "financial/legal boilerplate"
    if any(b in combined for b in LEGAL_DISCLAIMER_KW):
        return "wrong", "legal disclaimer text"
    anchor_hit = _anchor_in_text(combined, spec.anchors)
    in_reg = f.get("in_region")
    if len(v) >= 80 and in_reg and anchor_hit:
        return "usable", f"substantive in-region snippet with anchor (len={len(v)})"
    if len(v) >= 80 and in_reg:
        return "partial", f"substantive in-region but weak anchor match (len={len(v)})"
    if len(v) >= 80 and not in_reg:
        return "partial", f"substantive but out-of-region (len={len(v)})"
    if len(v) >= 25 and anchor_hit:
        return "partial", f"short snippet with anchor (len={len(v)})"
    if len(v) >= 25:
        return "partial", f"short generic snippet (len={len(v)})"
    return "wrong", f"too short (len={len(v)})"


def strict_financial_numeric(f: dict, spec: FieldSpec, pdf_path: str | None) -> tuple[str, str]:
    st = f.get("status", "not_found")
    fk = f.get("field") or spec.key
    if st == "not_found":
        if _pdf_anchor_with_number(pdf_path, spec.anchors):
            return "not_found_missed", "PDF anchor+digit found but extractor not_found"
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        return "partial", "status=partial"
    val = f.get("value")
    if not isinstance(val, dict):
        return "wrong", "missing numeric value dict"
    labeled = val.get("labeled") or []
    ctx = val.get("context") or ""
    ev = f.get("evidence_sentence") or ""
    if not labeled:
        if _anchor_in_text(ctx + ev, spec.anchors) and any(c.isdigit() for c in ctx):
            return "partial", "context-only numbers without labeled pairs"
        return "wrong", "empty labeled list"
    reject = FIELD_REJECT_LABELS.get(fk, ())
    best: tuple[str, str] | None = None
    for item in labeled:
        lab = (item.get("label") or "").strip()
        num = (item.get("value") or "").strip()
        if not num or not any(c.isdigit() for c in num):
            continue
        if any(r in lab for r in reject):
            best = best or ("wrong", f"wrong-line-item label '{lab}'")
            continue
        if any(r in lab for r in AMOUNT_NOISE_LABELS) and fk not in RATIO_FIELDS:
            continue
        anchor_ok = _anchor_in_text(lab, spec.anchors) or _anchor_in_text(ctx + ev, spec.anchors)
        if not anchor_ok:
            best = best or ("wrong", f"orphan numeric without field anchor (label='{lab}')")
            continue
        if fk in RATIO_FIELDS:
            if not _looks_like_ratio_value(num):
                best = best or ("wrong", f"ratio field with non-ratio value '{num}'")
                continue
            return "usable", f"ratio label '{lab}' value={num}"
        if fk == "risk_control_indicators":
            if _looks_like_ratio_value(num) or _looks_like_amount_value(num):
                return "usable", f"risk indicator '{lab}' value={num}"
            best = best or ("partial", f"risk indicator weak value '{num}'")
            continue
        if _looks_like_amount_value(num):
            if _anchor_in_text(lab, spec.anchors):
                return "usable", f"amount label '{lab}' value={num}"
            return "partial", f"amount with indirect anchor (label='{lab}')"
        if _looks_like_ratio_value(num) and fk not in RATIO_FIELDS:
            best = best or ("wrong", f"amount field with ratio-only value '{num}'")
            continue
        best = best or ("partial", f"numeric present but weak semantics (label='{lab}')")
    if best:
        return best
    return "wrong", "no substantive labeled numeric"


def _table_text_blob(val: dict) -> str:
    rows = val.get("rows") or []
    return " ".join(" ".join(str(c) for c in row) for row in rows)


def _financial_table_plausible(fk: str, val: dict) -> tuple[bool, str]:
    if not isinstance(val, dict):
        return False, "missing table dict"
    rows = val.get("rows") or []
    if not rows:
        return False, "empty rows"
    if val.get("match_hits", 0) < 1:
        return False, "match_hits<1"
    blob = _table_text_blob(val)
    data_rows = [r for r in rows if _table_row_is_data_row(r)]

    if fk in ("loan_structure",):
        if not any(k in blob for k in ("贷款", "垫款", "票据")):
            return False, "missing loan vocabulary"
    elif fk in ("deposit_structure",):
        if not any(k in blob for k in ("存款", "吸收存款")):
            return False, "missing deposit vocabulary"
    elif fk in ("regional_distribution", "revenue_by_region"):
        if not any(k in blob for k in ("地区", "境内", "境外", "区域", "长三角", "环渤海")):
            return False, "missing region vocabulary"
    elif fk in ("revenue_by_segment",):
        if not any(k in blob for k in ("分部", "业务", "收入", "手续费", "险种", "经纪", "投行", "资管")):
            return False, "missing segment vocabulary"
    if len(data_rows) >= 2:
        return True, f"{len(data_rows)} data rows"
    if len(data_rows) == 1:
        return True, "single data row"
    return False, "no data rows in preview"


def strict_financial_table(f: dict, spec: FieldSpec, pdf_path: str | None) -> tuple[str, str]:
    st = f.get("status", "not_found")
    fk = f.get("field") or spec.key
    if st == "not_found":
        if _pdf_anchor_with_number(pdf_path, spec.anchors):
            return "not_found_missed", "PDF table anchor found but extractor not_found"
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        return "partial", "status=partial"
    val = f.get("value")
    if fk in ("revenue_by_region", "revenue_by_segment"):
        ok, detail = (True, "revenue_table_plausible") if revenue_table_plausible(val) else (
            False, "fails revenue_table_plausible",
        )
    else:
        ok, detail = _financial_table_plausible(fk, val if isinstance(val, dict) else {})
    if not ok:
        return "wrong", detail
    rows = (val or {}).get("rows") or []
    data_rows = [r for r in rows if _table_row_is_data_row(r)]
    if len(data_rows) >= 2:
        return "usable", detail
    if len(data_rows) == 1:
        return "partial", f"single data row ({detail})"
    return "wrong", detail


def strict_concentration(f: dict, spec: FieldSpec, pdf_path: str | None) -> tuple[str, str]:
    st = f.get("status", "not_found")
    if st == "not_found":
        if _pdf_anchor_with_number(pdf_path, spec.anchors):
            return "not_found_missed", "PDF concentration anchor found but extractor not_found"
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        return "partial", "status=partial"
    val = f.get("value")
    if not isinstance(val, dict):
        return "wrong", "missing concentration dict"
    ev = f.get("evidence_sentence") or val.get("sentence") or ""
    has_val = bool(val.get("ratio") or val.get("amount"))
    if not has_val:
        return "wrong", "empty ratio/amount"
    if _anchor_in_text(ev, spec.anchors):
        return "usable", "concentration with anchor in evidence"
    return "partial", "ratio/amount without clear anchor keyword"


def strict_audit_field(f: dict, spec: FieldSpec, pdf_path: str | None) -> tuple[str, str]:
    ex = f.get("extraction") or spec.extraction
    if ex == "section_snippet":
        return strict_section_snippet(f, spec)
    if ex == "numeric":
        return strict_financial_numeric(f, spec, pdf_path)
    if ex == "table":
        return strict_financial_table(f, spec, pdf_path)
    if ex == "concentration":
        return strict_concentration(f, spec, pdf_path)
    return "wrong", f"unknown extraction type {ex}"


def _strict_cell_score(label: str, lenient: bool = False) -> float:
    if label == "usable":
        return 1.0
    if label == "partial":
        return 1.0 if lenient else 0.5
    return 0.0


def write_population_csv(path: str, rows: list[FinAuditRow]) -> None:
    fields = [
        "code", "name", "board", "schema_profile", "field", "extraction_type",
        "status", "proxy_plausible", "strict_label", "reason", "value_preview",
        "evidence_sentence", "page", "source_url", "subtype_caveat_flag",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "code": r.code,
                "name": r.name,
                "board": r.board,
                "schema_profile": r.schema_profile,
                "field": r.field,
                "extraction_type": r.extraction_type,
                "status": r.status,
                "proxy_plausible": r.proxy_plausible,
                "strict_label": r.strict_label,
                "reason": r.reason,
                "value_preview": r.value_preview,
                "evidence_sentence": r.evidence_sentence,
                "page": r.page,
                "source_url": r.source_url,
                "subtype_caveat_flag": r.subtype_caveat_flag,
            })


def write_summary(
    path: str,
    rows: list[FinAuditRow],
    eval_fin_ok: list[dict],
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    by_sub: dict[str, list[FinAuditRow]] = defaultdict(list)
    for r in rows:
        by_sub[r.schema_profile].append(r)

    lines: list[str] = []
    a = lines.append
    a("# full_market_2024 Financial Strict Audit Summary")
    a("")
    a(f"_Generated: {ts} | automated financial-only audit (Phase 1A)_")
    a("")
    a("## 1. Population breakdown")
    a("")
    a("| scope | companies | field-cells |")
    a("|---|---:|---:|")
    n_co = len({r.code for r in rows})
    a(f"| ok financial (audited) | {n_co} | {len(rows)} |")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        n = len({r.code for r in sub_rows})
        a(f"| `{sub}` | {n} | {len(sub_rows)} |")
    not_ok = [r for r in eval_fin_ok if r.get("status") != "ok"]
    if not_ok:
        a("")
        a(f"Excluded from audit: {len(not_ok)} financial company(ies) not ok "
          f"({', '.join(r['stock_code'] for r in not_ok)}).")
    a("")
    a("## 2. Strict usable / lenient by subtype")
    a("")
    a("| subtype | fields/co | strict usable | strict lenient | proxy plausible |")
    a("|---|---:|---:|---:|---:|")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        n = len({r.code for r in sub_rows})
        ft = len(sub_rows) / n if n else 0
        strict_u = statistics.mean(_strict_cell_score(r.strict_label) for r in sub_rows)
        strict_l = statistics.mean(_strict_cell_score(r.strict_label, lenient=True) for r in sub_rows)
        proxy = statistics.mean(1.0 if r.proxy_plausible else 0.0 for r in sub_rows)
        a(f"| `{sub}` | {ft:.1f} | **{strict_u * ft:.2f} / {ft:.0f}** | "
          f"{strict_l * ft:.2f} / {ft:.0f} | {proxy * ft:.2f} / {ft:.0f} |")
    a("")
    a("## 3. Proxy vs strict gap by subtype")
    a("")
    a("| subtype | proxy cell-rate | strict usable cell-rate | gap |")
    a("|---|---:|---:|---:|")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        proxy = statistics.mean(1.0 if r.proxy_plausible else 0.0 for r in sub_rows)
        strict_u = statistics.mean(_strict_cell_score(r.strict_label) for r in sub_rows)
        a(f"| `{sub}` | {proxy:.1%} | {strict_u:.1%} | **{proxy - strict_u:.1%}** |")
    a("")
    a("## 4. Top weak fields by subtype")
    a("")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        by_field: dict[str, Counter] = defaultdict(Counter)
        for r in sub_rows:
            by_field[r.field][r.strict_label] += 1
        weak = []
        for fk, cnt in by_field.items():
            n = sum(cnt.values())
            bad = cnt.get("wrong", 0) + cnt.get("partial", 0)
            weak.append((bad / n, fk, cnt))
        weak.sort(reverse=True)
        a(f"### {sub}")
        a("")
        a("| field | usable | partial | wrong | not_found* |")
        a("|---|---:|---:|---:|---:|")
        for rate, fk, cnt in weak[:8]:
            nf = cnt.get("not_found_unverified", 0) + cnt.get("not_found_missed", 0)
            a(f"| `{fk}` | {cnt.get('usable', 0)} | {cnt.get('partial', 0)} | "
              f"{cnt.get('wrong', 0)} | {nf} |")
        a("")
    a("*not_found = not_found_unverified + not_found_missed")
    a("")
    a("## 5. Top suspicious companies")
    a("")
    by_co: dict[str, list[FinAuditRow]] = defaultdict(list)
    for r in rows:
        by_co[r.code].append(r)
    co_scores = []
    for code, crows in by_co.items():
        strict_u = statistics.mean(_strict_cell_score(r.strict_label) for r in crows)
        proxy = statistics.mean(1.0 if r.proxy_plausible else 0.0 for r in crows)
        co_scores.append((strict_u, proxy, code, crows[0].name, crows[0].schema_profile, crows))
    co_scores.sort(key=lambda x: (x[0], x[1]))
    a("| code | name | subtype | strict usable / fields | proxy / fields | caveat |")
    a("|---|---|---|---:|---:|---|")
    for strict_u, proxy, code, name, sub, crows in co_scores[:12]:
        ft = len(crows)
        caveat = "yes" if code in SUBTYPE_CAVEAT_CODES else ""
        a(f"| {code} | {name} | {sub} | {strict_u * ft:.1f}/{ft} | "
          f"{proxy * ft:.1f}/{ft} | {caveat} |")
    a("")
    a("## 6. Subtype caveat companies (stored schema; manual review in Phase 1B)")
    a("")
    a("| code | name | stored schema | note |")
    a("|---|---|---|---|")
    a("| 000402 | 金融街 | broker | Likely real-estate / REIT / developer; not a securities broker |")
    a("| 600816 | 建元信托 | bank | Trust company; likely should be other_financial |")
    a("| 600318 | 新力金融 | bank | Financial holding; subtype unclear |")
    a("")
    a("Automated audit uses **stored** `schema_profile`; caveat flags are informational only.")
    a("")
    a("## 7. Financial audit caveats")
    a("")
    a("- **Not full manual validation** — automated adversarial recheck over stored values.")
    a("- **Not mixed into non-financial headline** — industrial strict usable remains **9.43/11** "
      "(5621 companies); this report is financial-only.")
    a("- **Numeric/table noise likely** — financial fields use generic extractors; strict rules "
      "flag wrong-line-item and orphan numerics but cannot eliminate all false positives.")
    a("- **Phase 1B** — stratified manual PDF calibration worksheet is the next step.")
    a("- **`not_found_missed`** — only assigned when PDF anchor search finds anchor+digit; "
      "conservative to avoid overclaiming.")
    a("")
    a("## 8. Phase 1B manual calibration recommendation")
    a("")
    a("Proceed with worksheet generation. Suggested 30-company sample:")
    a("")
    a("- **Force-include:** 601963, 601375, 601377, 601878, 000402, 600816, 600318")
    a("- **bank (12):** 601398, 601939, 601988, 601328, 601825, 002807, 001227, 601997, "
      "601963, 600318, 601166, 600816")
    a("- **broker (12):** 601901, 002500, 600999, 000776, 601375, 601377, 601878, 600958, "
      "601162, 600030, 002736, 601108")
    a("- **insurer (2):** 601336, 601628 (both)")
    a("- **other_financial (4):** 600927, 001236, 002961, 603093 (all)")
    a("")
    a("Review numeric fields (`net_interest_income`, `npl_ratio`, broker income lines) and "
      "table fields first; treat 000402 as tag review, not broker control.")
    a("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_audit(out_dir: str, yaml_path: str) -> tuple[list[FinAuditRow], list[dict]]:
    meta = _load_meta(yaml_path)
    with open(os.path.join(out_dir, "eval_results.json"), encoding="utf-8") as fh:
        eval_rows = json.load(fh)

    fin_eval = [r for r in eval_rows if r.get("financial")]
    fin_ok = [r for r in fin_eval if r.get("status") == "ok"]

    audit_rows: list[FinAuditRow] = []
    spec_cache: dict[str, dict[str, FieldSpec]] = {}

    for er in fin_ok:
        code = str(er["stock_code"])
        yc = meta.get(code, {})
        board = yc.get("board") or er.get("board", "")
        name = er.get("short_name") or yc.get("short_name", "")
        schema = er.get("schema_profile") or "unknown"
        pp = _profile_path(out_dir, code, board)
        if not pp:
            continue
        profile = json.load(open(pp, encoding="utf-8"))
        schema = profile.get("schema_profile") or schema
        source_url = (profile.get("source") or {}).get("source_url") or er.get("source_url", "")
        pdf_path = _pdf_path(out_dir, code, board)
        fmap = _field_map(profile)

        if schema not in spec_cache:
            spec_cache[schema] = {s.key: s for s in get_field_specs(schema)}
        specs = spec_cache[schema]

        caveat = code in SUBTYPE_CAVEAT_CODES
        eval_fields = er.get("fields") or {}

        for fk, spec in specs.items():
            f = fmap.get(fk)
            if not f:
                f = {
                    "field": fk,
                    "status": "not_found",
                    "extraction": spec.extraction,
                    "value": None,
                }
            proxy = bool((eval_fields.get(fk) or {}).get("plausible"))
            if not eval_fields and f.get("status") == "found":
                proxy = field_plausible(f)
            label, reason = strict_audit_field(f, spec, pdf_path)
            audit_rows.append(
                FinAuditRow(
                    code=code,
                    name=name,
                    board=board,
                    schema_profile=schema,
                    field=fk,
                    extraction_type=f.get("extraction") or spec.extraction,
                    status=f.get("status", "not_found"),
                    proxy_plausible=proxy,
                    strict_label=label,
                    reason=reason,
                    value_preview=value_preview(f),
                    evidence_sentence=(f.get("evidence_sentence") or "")[:200],
                    page=str(f.get("page") or ""),
                    source_url=source_url,
                    subtype_caveat_flag=caveat,
                )
            )
    return audit_rows, fin_eval


def main() -> int:
    ap = argparse.ArgumentParser(description="Financial-only strict audit (read-only)")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--companies-yaml", default=DEFAULT_YAML)
    args = ap.parse_args()

    rows, fin_eval = run_audit(args.out_dir, args.companies_yaml)
    pop_csv = os.path.join(args.out_dir, "financial_audit_population.csv")
    summary_md = os.path.join(args.out_dir, "financial_audit_summary.md")
    write_population_csv(pop_csv, rows)
    write_summary(summary_md, rows, fin_eval)

    print(f"[financial_audit] population rows: {len(rows)}")
    print(f"[financial_audit] wrote {pop_csv}")
    print(f"[financial_audit] wrote {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

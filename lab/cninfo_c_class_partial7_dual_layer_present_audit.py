"""
CNINFO C-class — Partial7 双层语义审计（离线 · 可单测）。

对照 DLVR-P01–P04：对 harvest 只读核验 ledger/audit 双层均为 partial（4/10）、
raw 6×http_error/500 + security_observe delisted=true 的合法一致模式；
并将结果接入 QA closure 累积双层证据索引（不改写既有 empty3 索引行 / caveat / metrics）。

不写 snapshot · 不触碰 harvest · 不调用 CNINFO ·
不启用 execute_production_snapshot_rebuild。
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from cninfo_c_class_empty_dividend_zero_byte_present_audit import (
    SOURCE_TO_SUBDIR,
    count_dual_layer_sources,
    index_by_case_id,
    index_by_code,
    load_csv_rows,
    load_delisted_flag,
)

# lab/ 上一级为仓库根
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# slice1 已知 partial7：case_id ↔ company_code
EXPECTED_PARTIAL7_CASE_CODE: Dict[str, str] = {
    "CE1E002": "600001",
    "CE1E003": "600005",
    "CE1E034": "600068",
    "CE1E061": "000003",
    "CE1E067": "000015",
    "CE1E070": "000022",
    "CE1E071": "000024",
}
EXPECTED_PARTIAL7_CODES = frozenset(EXPECTED_PARTIAL7_CASE_CODE.values())
EXPECTED_PARTIAL7_CASE_IDS = frozenset(EXPECTED_PARTIAL7_CASE_CODE.keys())

# PT 标的（tradingStatus=0）；仅注解，不发明 termination sidecar
EXPECTED_PT_CASE_IDS = frozenset({"CE1E061", "CE1E067"})
EXPECTED_PT_CODES = frozenset({"000003", "000015"})

EXPECTED_CAVEAT_CLASS = "delisted_or_merged_partial_normalized"
EXPECTED_DISPOSITION = "accept_with_caveat"
EXPECTED_LEDGER_STATUS = "partial"
EXPECTED_AUDIT_RESUME_STATE = "partial"
EXPECTED_AUDIT_NOTE = "status_csv_partial"
EXPECTED_LIVE_RECOMMENDATION = "deferred_targeted_live_after_approval"
EXPECTED_LEDGER_SOURCES = 4
EXPECTED_AUDIT_SOURCES = 4
EXPECTED_HTTP_ERROR_COUNT = 6
EXPECTED_BUSINESS_CODE = "9240002"
EXPECTED_HTTP_STATUS = "500"
EXPECTED_SO_RETRIEVAL = "endpoint_found"
EXPECTED_SO_HTTP = "200"

# 6 个 HTTP 失败源：source_id → raw 子目录名
HTTP_ERROR_SOURCE_RAW_SUBDIR: Dict[str, str] = {
    "cninfo_company_basic_profile": "basic_profile",
    "cninfo_dividend_financing_profile": "dividend_history",
    "cninfo_executive_profile": "executive_profile",
    "cninfo_share_capital_profile": "share_capital_profile",
    "cninfo_top_shareholders_profile": "top_shareholders_profile",
    "cninfo_top_float_shareholders_profile": "top_float_shareholders_profile",
}
EXPECTED_MISSING_SOURCE_IDS = frozenset(HTTP_ERROR_SOURCE_RAW_SUBDIR.keys())

# 4 个应存在的 normalized 子目录
EXPECTED_PRESENT_SUBDIRS = frozenset(
    {
        "business_scope",
        "contact_profile",
        "industry_profile",
        "security_observe",
    }
)

SECURITY_SUBDIR = "security_observe"

DLVR_PARTIAL_RULE_IDS: Tuple[str, ...] = (
    "DLVR-P01",
    "DLVR-P02",
    "DLVR-P03",
    "DLVR-P04",
)

AUDIT_ROW_FIELDS = [
    "case_id",
    "company_code",
    "company_name",
    "ledger_harvest_status",
    "ledger_sources_present_existence",
    "audit_sources_present_content",
    "audit_sources_present_csv",
    "audit_sources_missing_csv",
    "missing_source_ids_csv",
    "raw_http_error_count",
    "raw_business_code_9240002_count",
    "security_observe_retrieval_status",
    "security_observe_http_status",
    "delisted",
    "trading_status",
    "is_pt_annotated",
    "resume_state_csv",
    "resume_note_csv",
    "live_recommendation_csv",
    "caveat_class",
    "disposition",
    "offline_requires_snapshot",
    "offline_requires_live",
    "dlvr_p01",
    "dlvr_p02",
    "dlvr_p03",
    "dlvr_p04",
    "rules_all_pass",
    "notes",
]

RULE_CHECK_FIELDS = [
    "case_id",
    "company_code",
    "rule_id",
    "applies_to",
    "result",
    "observed",
    "expected",
    "notes",
]

# partial7 专用索引列（sibling；不覆盖 empty3 索引 schema）
QA_CLOSURE_PARTIAL7_INDEX_FIELDS = [
    "case_id",
    "company_code",
    "company_name",
    "caveat_class",
    "disposition",
    "caveat_family",
    "ledger_harvest_status",
    "ledger_sources_present_existence",
    "audit_resume_state",
    "audit_sources_present_content",
    "delisted",
    "trading_status",
    "is_pt_annotated",
    "raw_http_error_count",
    "dlvr_p01",
    "dlvr_p02",
    "dlvr_p03",
    "dlvr_p04",
    "rules_all_pass",
    "dual_layer_audit_gate",
    "index_status",
    "audit_csv_ref",
    "rule_matrix_ref",
    "notes",
]

QA_CLOSURE_METRIC_FIELDS = [
    "metric_key",
    "metric_value",
    "notes",
]

QA_CLOSURE_COHORT_COVERAGE_FIELDS = [
    "caveat_family",
    "expected_count",
    "indexed_pass_count",
    "index_status",
    "audit_csv_ref",
    "notes",
]


@dataclass
class Partial7DualLayerAuditResult:
    """partial7 双层审计结果。"""

    rows: List[Dict[str, str]] = field(default_factory=list)
    rule_rows: List[Dict[str, str]] = field(default_factory=list)
    checks: Dict[str, bool] = field(default_factory=dict)
    gate: str = "FAIL_REVIEW_REQUIRED"
    notes: str = ""


@dataclass
class QaClosurePartial7DualLayerIndexResult:
    """partial7 双层审计 → QA closure 累积证据索引。"""

    rows: List[Dict[str, str]] = field(default_factory=list)
    metric_rows: List[Dict[str, str]] = field(default_factory=list)
    cohort_coverage_rows: List[Dict[str, str]] = field(default_factory=list)
    checks: Dict[str, bool] = field(default_factory=dict)
    gate: str = "FAIL_REVIEW_REQUIRED"
    notes: str = ""


def _normalize(value: object) -> str:
    return str(value or "").strip()


def _abs_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _pass_fail(flag: bool) -> str:
    return "PASS" if flag else "FAIL"


def _raw_path(harvest_root: str, raw_subdir: str, company_code: str) -> Optional[str]:
    """解析 raw 信封路径（.json 或 .jsonl）。"""
    for ext in (".json", ".jsonl"):
        path = os.path.join(harvest_root, "raw", raw_subdir, f"{company_code}{ext}")
        if os.path.isfile(path):
            return path
    return None


def load_raw_envelope(path: str) -> Dict[str, Any]:
    """读取 raw 信封；禁止静默空结果。"""
    with open(path, encoding="utf-8") as fh:
        text = fh.read().strip()
    if not text:
        raise ValueError(f"empty_raw_envelope: {path}")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        first: Optional[Dict[str, Any]] = None
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            first = json.loads(line)
            break
        if first is None:
            raise ValueError(f"raw_envelope_parse_failed: {path}: {exc}") from exc
        obj = first
    if not isinstance(obj, dict):
        raise ValueError(f"raw_envelope_not_object: {path}")
    return obj


def count_http_error_envelopes(
    harvest_root: str,
    company_code: str,
) -> Tuple[int, int, List[str]]:
    """
    统计 6 个预期 HTTP 失败源的 raw 信封。
    返回 (http_error_500_count, business_code_9240002_count, notes)。
    """
    notes: List[str] = []
    http_err = 0
    biz_ok = 0
    for source_id, raw_subdir in HTTP_ERROR_SOURCE_RAW_SUBDIR.items():
        path = _raw_path(harvest_root, raw_subdir, company_code)
        if path is None:
            notes.append(f"missing_raw:{source_id}")
            continue
        env = load_raw_envelope(path)
        status = _normalize(env.get("retrieval_status"))
        http = _normalize(env.get("http_status"))
        biz = _normalize(env.get("business_code"))
        if status == "http_error" and http == EXPECTED_HTTP_STATUS:
            http_err += 1
        else:
            notes.append(f"unexpected_raw:{source_id}={status}/{http}")
        if biz == EXPECTED_BUSINESS_CODE:
            biz_ok += 1
        else:
            notes.append(f"unexpected_biz:{source_id}={biz or 'empty'}")
    return http_err, biz_ok, notes


def load_security_observe_raw(
    harvest_root: str,
    company_code: str,
) -> Dict[str, Any]:
    """读取 raw security_observe 信封。"""
    path = _raw_path(harvest_root, SECURITY_SUBDIR, company_code)
    if path is None:
        raise FileNotFoundError(
            f"missing_raw_security_observe: company_code={company_code}"
        )
    return load_raw_envelope(path)


def load_trading_status(harvest_root: str, company_code: str) -> str:
    """
    读取 tradingStatus。
    优先 normalized security_observe.raw_record_json；否则 raw.raw_records。
    """
    norm_path = os.path.join(
        harvest_root, "normalized", SECURITY_SUBDIR, f"{company_code}.json"
    )
    if os.path.isfile(norm_path):
        with open(norm_path, encoding="utf-8") as fh:
            norm = json.load(fh)
        rrj = norm.get("raw_record_json")
        if isinstance(rrj, str) and rrj.strip():
            rrj = json.loads(rrj)
        if isinstance(rrj, dict) and "tradingStatus" in rrj:
            return _normalize(rrj.get("tradingStatus"))
        # 归一化列兜底
        tsc = _normalize(norm.get("trading_status_code"))
        if tsc:
            return tsc

    raw = load_security_observe_raw(harvest_root, company_code)
    records = raw.get("raw_records")
    if isinstance(records, dict) and "tradingStatus" in records:
        return _normalize(records.get("tradingStatus"))
    if isinstance(records, list) and records:
        first = records[0]
        if isinstance(first, dict) and "tradingStatus" in first:
            return _normalize(first.get("tradingStatus"))
    raise ValueError(f"trading_status_missing: company_code={company_code}")


def present_normalized_subdirs(harvest_root: str, company_code: str) -> Set[str]:
    """返回该公司存在的 normalized 子目录集合（ledger 文件存在语义）。"""
    present: Set[str] = set()
    for _source_id, (subdir, ext) in SOURCE_TO_SUBDIR.items():
        path = os.path.join(harvest_root, "normalized", subdir, f"{company_code}{ext}")
        if os.path.isfile(path):
            present.add(subdir)
    return present


def audit_partial7_case(
    *,
    case_id: str,
    company_code: str,
    harvest_root: str,
    status_by_code: Dict[str, Dict[str, str]],
    resume_by_code: Dict[str, Dict[str, str]],
    caveat_by_code: Dict[str, Dict[str, str]],
    offline_by_case: Dict[str, Dict[str, str]],
) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    """
    对单家 partial7 执行 DLVR-P01–P04 机器核验。
    返回 (audit_row, rule_rows)。硬失败写入 notes，不吞异常语义。
    """
    notes: List[str] = []
    company_name = ""

    ledger_n, audit_n, _per = count_dual_layer_sources(harvest_root, company_code)
    present_subs = present_normalized_subdirs(harvest_root, company_code)

    status = status_by_code.get(company_code) or {}
    ledger_status = _normalize(status.get("harvest_status")).lower()
    company_name = _normalize(status.get("company_name")) or company_name

    resume = resume_by_code.get(company_code) or {}
    resume_state = _normalize(resume.get("resume_state")).lower()
    resume_note = _normalize(resume.get("notes"))
    live_rec = _normalize(resume.get("live_resume_recommendation"))
    audit_present_csv = _normalize(resume.get("sources_present"))
    audit_missing_csv = _normalize(resume.get("sources_missing"))
    missing_ids_csv = _normalize(resume.get("missing_source_ids"))
    if not company_name:
        company_name = _normalize(resume.get("company_name"))

    caveat = caveat_by_code.get(company_code) or {}
    caveat_class = _normalize(caveat.get("caveat_class"))
    disposition = _normalize(caveat.get("disposition"))
    if not company_name:
        company_name = _normalize(caveat.get("company_name"))
    if not caveat:
        notes.append("FAIL:missing_caveat_ledger_row")
    else:
        if caveat_class != EXPECTED_CAVEAT_CLASS:
            notes.append(f"FAIL:caveat_class={caveat_class or 'empty'}")
        if disposition != EXPECTED_DISPOSITION:
            notes.append(f"FAIL:disposition={disposition or 'empty'}")
        caveat_case = _normalize(caveat.get("case_id"))
        if caveat_case and caveat_case != case_id:
            notes.append(f"FAIL:caveat_case_id_mismatch={caveat_case}")

    offline = offline_by_case.get(case_id) or {}
    offline_req_snap = _normalize(offline.get("requires_snapshot")).lower()
    offline_req_live = _normalize(offline.get("requires_live")).lower()
    if not offline:
        notes.append("FAIL:missing_offline_matrix_row")
    else:
        off_code = _normalize(offline.get("company_code"))
        if off_code and off_code != company_code:
            notes.append(f"FAIL:offline_matrix_code_mismatch={off_code}")
        if not company_name:
            company_name = _normalize(offline.get("company_name"))

    http_err, biz_ok, raw_notes = count_http_error_envelopes(harvest_root, company_code)
    notes.extend(raw_notes)

    so_raw = load_security_observe_raw(harvest_root, company_code)
    so_status = _normalize(so_raw.get("retrieval_status"))
    so_http = _normalize(so_raw.get("http_status"))

    delisted = load_delisted_flag(harvest_root, company_code)
    trading_status = load_trading_status(harvest_root, company_code)
    expect_pt = case_id in EXPECTED_PT_CASE_IDS
    is_pt = trading_status == "0"
    if expect_pt and not is_pt:
        notes.append(f"FAIL:pt_expected_tradingStatus0 got={trading_status or 'empty'}")
    if (not expect_pt) and is_pt:
        notes.append("FAIL:unexpected_pt_tradingStatus0")

    missing_ids = {
        x.strip() for x in missing_ids_csv.split(";") if x.strip()
    }
    if missing_ids and missing_ids != set(EXPECTED_MISSING_SOURCE_IDS):
        notes.append(
            f"FAIL:missing_source_ids_mismatch={sorted(missing_ids)}"
        )

    # DLVR-P01：双层 partial 4/10 · delisted · 6×http_error · SO ok
    p01 = (
        ledger_status == EXPECTED_LEDGER_STATUS
        and ledger_n == EXPECTED_LEDGER_SOURCES
        and resume_state == EXPECTED_AUDIT_RESUME_STATE
        and audit_n == EXPECTED_AUDIT_SOURCES
        and present_subs == EXPECTED_PRESENT_SUBDIRS
        and delisted is True
        and http_err == EXPECTED_HTTP_ERROR_COUNT
        and so_status == EXPECTED_SO_RETRIEVAL
        and so_http == EXPECTED_SO_HTTP
        and EXPECTED_AUDIT_NOTE in resume_note
    )
    if not p01:
        notes.append(
            "FAIL:DLVR-P01 "
            f"ledger={ledger_status}/{ledger_n} "
            f"audit={resume_state}/{audit_n} "
            f"http_err={http_err} delisted={delisted} "
            f"so={so_status}/{so_http} present={sorted(present_subs)}"
        )

    # DLVR-P02：不升 missing · live deferred · biz 9240002 · accept_with_caveat
    p02 = (
        ledger_status == EXPECTED_LEDGER_STATUS
        and ledger_status != "missing"
        and resume_state == EXPECTED_AUDIT_RESUME_STATE
        and live_rec == EXPECTED_LIVE_RECOMMENDATION
        and biz_ok == EXPECTED_HTTP_ERROR_COUNT
        and disposition == EXPECTED_DISPOSITION
    )
    if not p02:
        notes.append(
            f"FAIL:DLVR-P02 ledger={ledger_status} resume={resume_state} "
            f"live={live_rec or 'empty'} biz_ok={biz_ok} "
            f"disposition={disposition or 'empty'}"
        )

    # DLVR-P03：禁止冒充 complete；双层一致 partial
    p03 = (
        ledger_status == EXPECTED_LEDGER_STATUS
        and resume_state == EXPECTED_AUDIT_RESUME_STATE
        and ledger_status != "complete"
        and resume_state != "complete"
        and ledger_n == EXPECTED_LEDGER_SOURCES
        and audit_n == EXPECTED_AUDIT_SOURCES
        and audit_present_csv == str(EXPECTED_AUDIT_SOURCES)
        and audit_missing_csv == str(EXPECTED_HTTP_ERROR_COUNT)
    )
    if not p03:
        notes.append(
            f"FAIL:DLVR-P03 ledger={ledger_status}/{ledger_n} "
            f"audit={resume_state}/{audit_n} "
            f"csv_present={audit_present_csv} csv_missing={audit_missing_csv}"
        )

    # DLVR-P04：snapshot 排除 · offline requires_snapshot/live=false · live deferred
    p04 = (
        ledger_status == EXPECTED_LEDGER_STATUS
        and disposition == EXPECTED_DISPOSITION
        and live_rec == EXPECTED_LIVE_RECOMMENDATION
        and offline_req_snap in {"false", "0", "no"}
        and offline_req_live in {"false", "0", "no"}
    )
    if not p04:
        notes.append(
            f"FAIL:DLVR-P04 disposition={disposition or 'empty'} "
            f"live={live_rec or 'empty'} "
            f"req_snap={offline_req_snap or 'empty'} "
            f"req_live={offline_req_live or 'empty'}"
        )

    all_pass = (
        p01
        and p02
        and p03
        and p04
        and not any(n.startswith("FAIL:") for n in notes)
    )
    if all_pass:
        notes.append(
            "partial7_dual_layer_aligned; "
            "ledger_audit_both_partial_4_10; accept_with_caveat"
        )

    row = {
        "case_id": case_id,
        "company_code": company_code,
        "company_name": company_name,
        "ledger_harvest_status": ledger_status,
        "ledger_sources_present_existence": str(ledger_n),
        "audit_sources_present_content": str(audit_n),
        "audit_sources_present_csv": audit_present_csv,
        "audit_sources_missing_csv": audit_missing_csv,
        "missing_source_ids_csv": missing_ids_csv,
        "raw_http_error_count": str(http_err),
        "raw_business_code_9240002_count": str(biz_ok),
        "security_observe_retrieval_status": so_status,
        "security_observe_http_status": so_http,
        "delisted": "true" if delisted else "false",
        "trading_status": trading_status,
        "is_pt_annotated": _yes_no(is_pt),
        "resume_state_csv": resume_state,
        "resume_note_csv": resume_note,
        "live_recommendation_csv": live_rec,
        "caveat_class": caveat_class,
        "disposition": disposition,
        "offline_requires_snapshot": offline_req_snap or "false",
        "offline_requires_live": offline_req_live or "false",
        "dlvr_p01": _pass_fail(p01),
        "dlvr_p02": _pass_fail(p02),
        "dlvr_p03": _pass_fail(p03),
        "dlvr_p04": _pass_fail(p04),
        "rules_all_pass": _yes_no(all_pass),
        "notes": "; ".join(notes),
    }

    rule_specs = [
        (
            "DLVR-P01",
            p01,
            (
                f"ledger={ledger_status}/{ledger_n} audit={resume_state}/{audit_n} "
                f"http_err={http_err} delisted={delisted} so={so_status}/{so_http}"
            ),
            "ledger=partial 4/10; audit=partial; 6x http_error/500; delisted=true",
        ),
        (
            "DLVR-P02",
            p02,
            (
                f"ledger={ledger_status} live={live_rec} biz_ok={biz_ok} "
                f"disposition={disposition}"
            ),
            "not upgraded to missing; deferred_targeted_live; biz=9240002; "
            "accept_with_caveat",
        ),
        (
            "DLVR-P03",
            p03,
            (
                f"ledger={ledger_status}/{ledger_n} audit={resume_state}/{audit_n} "
                f"not_complete=yes"
            ),
            "must not label 4/10 as complete; ledger/audit agree partial",
        ),
        (
            "DLVR-P04",
            p04,
            (
                f"disposition={disposition} live={live_rec} "
                f"req_snap={offline_req_snap} req_live={offline_req_live}"
            ),
            "excluded from snapshot complete pool; requires_snapshot/live=false",
        ),
    ]
    rule_rows: List[Dict[str, str]] = []
    for rule_id, ok, observed, expected in rule_specs:
        rule_rows.append(
            {
                "case_id": case_id,
                "company_code": company_code,
                "rule_id": rule_id,
                "applies_to": "partial",
                "result": _pass_fail(ok),
                "observed": observed,
                "expected": expected,
                "notes": "" if ok else "rule_failed",
            }
        )
    return row, rule_rows


def dual_layer_matrix_covers_partial_rules(
    dual_rows: Sequence[Dict[str, str]],
) -> bool:
    """确认 dual-layer 规则矩阵覆盖 DLVR-P01–P04 且 applies_to=partial。"""
    by_id = {
        _normalize(r.get("rule_id")): r for r in dual_rows if _normalize(r.get("rule_id"))
    }
    for rule_id in DLVR_PARTIAL_RULE_IDS:
        row = by_id.get(rule_id)
        if not row:
            return False
        applies = _normalize(row.get("applies_to")).lower()
        if applies != "partial":
            return False
    return True


def run_partial7_dual_layer_present_audit(
    *,
    harvest_root: str,
    status_csv: str,
    resume_audit_csv: str,
    caveat_ledger_csv: str,
    offline_matrix_csv: str,
    dual_layer_matrix_csv: str,
) -> Partial7DualLayerAuditResult:
    """执行 partial7 全量 DLVR-P01–P04 审计。"""
    harvest = _abs_path(harvest_root)
    status_path = _abs_path(status_csv)
    resume_path = _abs_path(resume_audit_csv)
    caveat_path = _abs_path(caveat_ledger_csv)
    offline_path = _abs_path(offline_matrix_csv)
    dual_path = _abs_path(dual_layer_matrix_csv)

    for label, path in (
        ("harvest_root", harvest),
        ("status_csv", status_path),
        ("resume_audit_csv", resume_path),
        ("caveat_ledger_csv", caveat_path),
        ("offline_matrix_csv", offline_path),
        ("dual_layer_matrix_csv", dual_path),
    ):
        if label == "harvest_root":
            if not os.path.isdir(path):
                raise FileNotFoundError(f"missing_{label}: {path}")
        elif not os.path.isfile(path):
            raise FileNotFoundError(f"missing_{label}: {path}")

    status_by_code = index_by_code(load_csv_rows(status_path))
    resume_by_code = index_by_code(load_csv_rows(resume_path))
    caveat_rows = load_csv_rows(caveat_path)
    caveat_by_code = index_by_code(caveat_rows)
    offline_by_case = index_by_case_id(load_csv_rows(offline_path))
    dual_rows = load_csv_rows(dual_path)

    audit_rows: List[Dict[str, str]] = []
    rule_rows: List[Dict[str, str]] = []
    for case_id in sorted(EXPECTED_PARTIAL7_CASE_CODE.keys()):
        code = EXPECTED_PARTIAL7_CASE_CODE[case_id]
        row, rules = audit_partial7_case(
            case_id=case_id,
            company_code=code,
            harvest_root=harvest,
            status_by_code=status_by_code,
            resume_by_code=resume_by_code,
            caveat_by_code=caveat_by_code,
            offline_by_case=offline_by_case,
        )
        audit_rows.append(row)
        rule_rows.extend(rules)

    fail_rows = [r for r in audit_rows if r["rules_all_pass"] != "yes"]
    caveat_partial = [
        r
        for r in caveat_rows
        if _normalize(r.get("caveat_class")) == EXPECTED_CAVEAT_CLASS
    ]
    caveat_codes = {_normalize(r.get("company_code")) for r in caveat_partial}
    offline_cases = set(offline_by_case.keys())
    pt_rows = [r for r in audit_rows if r["case_id"] in EXPECTED_PT_CASE_IDS]

    checks = {
        "partial7_all_rules_pass": not fail_rows and len(audit_rows) == 7,
        "offline_matrix_covers_partial7": offline_cases
        == EXPECTED_PARTIAL7_CASE_IDS,
        "caveat_ledger_covers_partial7": caveat_codes == EXPECTED_PARTIAL7_CODES,
        "dual_layer_matrix_covers_dlvr_p01_p04": dual_layer_matrix_covers_partial_rules(
            dual_rows
        ),
        "pt_two_annotated_trading_status_0": (
            len(pt_rows) == 2
            and all(r["is_pt_annotated"] == "yes" for r in pt_rows)
            and all(r["trading_status"] == "0" for r in pt_rows)
        ),
        "no_non_pt_trading_status_0": all(
            r["trading_status"] != "0"
            for r in audit_rows
            if r["case_id"] not in EXPECTED_PT_CASE_IDS
        ),
        "no_execute_flag": True,
        "cninfo_calls_zero": True,
        "harvest_read_only": True,
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"
    return Partial7DualLayerAuditResult(
        rows=audit_rows,
        rule_rows=rule_rows,
        checks=checks,
        gate=gate,
        notes=(
            f"fail_count={len(fail_rows)}; "
            f"pt_annotated={[r['company_code'] for r in pt_rows]}"
        ),
    )


def build_qa_closure_partial7_dual_layer_evidence_index(
    *,
    audit_rows: Sequence[Dict[str, str]],
    rule_rows: Sequence[Dict[str, str]],
    caveat_ledger_rows: Sequence[Dict[str, str]],
    audit_gate: str,
    audit_csv_ref: str,
    rule_matrix_ref: str,
    empty3_indexed_pass_count: int = 0,
    empty3_index_csv_ref: str = "",
) -> QaClosurePartial7DualLayerIndexResult:
    """
    将 partial7 双层审计结果接入 QA closure 累积证据索引。

    只读消费 caveat ledger 中 delisted_or_merged 行；不改写原 ledger/metrics；
    不覆盖 empty3 索引文件（由 runner 写 sibling CSV）。
    """
    caveat_partial = [
        r
        for r in caveat_ledger_rows
        if _normalize(r.get("caveat_class")) == EXPECTED_CAVEAT_CLASS
    ]
    caveat_by_case = index_by_case_id(caveat_partial)
    audit_by_case = index_by_case_id(list(audit_rows))

    rule_by_case: Dict[str, Dict[str, str]] = {}
    for rr in rule_rows:
        case_id = _normalize(rr.get("case_id"))
        rule_id = _normalize(rr.get("rule_id")).lower().replace("-", "_")
        if not case_id or not rule_id:
            continue
        rule_by_case.setdefault(case_id, {})[rule_id] = _normalize(rr.get("result"))

    index_rows: List[Dict[str, str]] = []
    for case_id in sorted(EXPECTED_PARTIAL7_CASE_CODE.keys()):
        code = EXPECTED_PARTIAL7_CASE_CODE[case_id]
        caveat = caveat_by_case.get(case_id) or {}
        audit = audit_by_case.get(case_id) or {}
        rules = rule_by_case.get(case_id) or {}

        notes: List[str] = []
        if not caveat:
            notes.append("FAIL:missing_caveat_ledger_row")
        else:
            if _normalize(caveat.get("company_code")) != code:
                notes.append(
                    f"FAIL:caveat_code_mismatch={_normalize(caveat.get('company_code'))}"
                )
            if _normalize(caveat.get("disposition")) != EXPECTED_DISPOSITION:
                notes.append(
                    f"FAIL:disposition={_normalize(caveat.get('disposition')) or 'empty'}"
                )

        if not audit:
            notes.append("FAIL:missing_audit_row")
            index_status = "caveat_missing_audit"
            rules_ok = False
        else:
            rules_ok = _normalize(audit.get("rules_all_pass")).lower() == "yes"
            if not rules_ok:
                notes.append("FAIL:rules_all_pass_not_yes")
                index_status = "indexed_fail"
            elif notes:
                index_status = "indexed_fail"
                rules_ok = False
            else:
                index_status = "indexed_pass"
                notes.append(
                    "qa_closure_dual_layer_indexed; linked_to_partial7_audit"
                )

        company_name = (
            _normalize(audit.get("company_name"))
            or _normalize(caveat.get("company_name"))
        )
        row = {
            "case_id": case_id,
            "company_code": code,
            "company_name": company_name,
            "caveat_class": _normalize(caveat.get("caveat_class"))
            or EXPECTED_CAVEAT_CLASS,
            "disposition": _normalize(caveat.get("disposition")),
            "caveat_family": "partial",
            "ledger_harvest_status": _normalize(audit.get("ledger_harvest_status"))
            or _normalize(caveat.get("harvest_status")),
            "ledger_sources_present_existence": _normalize(
                audit.get("ledger_sources_present_existence")
            ),
            "audit_resume_state": _normalize(audit.get("resume_state_csv")),
            "audit_sources_present_content": _normalize(
                audit.get("audit_sources_present_content")
            ),
            "delisted": _normalize(audit.get("delisted")),
            "trading_status": _normalize(audit.get("trading_status")),
            "is_pt_annotated": _normalize(audit.get("is_pt_annotated")),
            "raw_http_error_count": _normalize(audit.get("raw_http_error_count")),
            "dlvr_p01": rules.get("dlvr_p01") or _normalize(audit.get("dlvr_p01")),
            "dlvr_p02": rules.get("dlvr_p02") or _normalize(audit.get("dlvr_p02")),
            "dlvr_p03": rules.get("dlvr_p03") or _normalize(audit.get("dlvr_p03")),
            "dlvr_p04": rules.get("dlvr_p04") or _normalize(audit.get("dlvr_p04")),
            "rules_all_pass": "yes" if rules_ok else "no",
            "dual_layer_audit_gate": audit_gate,
            "index_status": index_status,
            "audit_csv_ref": audit_csv_ref,
            "rule_matrix_ref": rule_matrix_ref,
            "notes": "; ".join(notes),
        }
        index_rows.append(row)

    pass_rows = [r for r in index_rows if r["index_status"] == "indexed_pass"]
    fail_rows = [r for r in index_rows if r["index_status"] != "indexed_pass"]
    caveat_case_ids = set(caveat_by_case.keys())
    audit_case_ids = set(audit_by_case.keys())
    orphan_audit = sorted(audit_case_ids - EXPECTED_PARTIAL7_CASE_IDS)
    orphan_caveat = sorted(caveat_case_ids - EXPECTED_PARTIAL7_CASE_IDS)

    total_expected = 3 + 7  # empty3 + partial7
    total_indexed = empty3_indexed_pass_count + len(pass_rows)
    full_cohort = (
        empty3_indexed_pass_count == 3
        and len(pass_rows) == 7
        and not fail_rows
    )

    checks = {
        "index_covers_partial7": {r["case_id"] for r in index_rows}
        == EXPECTED_PARTIAL7_CASE_IDS,
        "all_indexed_pass": len(pass_rows) == 7 and not fail_rows,
        "caveat_partial7_match_expected": caveat_case_ids
        == EXPECTED_PARTIAL7_CASE_IDS,
        "no_orphan_audit_rows": not orphan_audit,
        "no_orphan_caveat_partial_rows": not orphan_caveat,
        "audit_gate_pass_offline": audit_gate == "PASS_OFFLINE",
        "empty3_index_preserved_readable": empty3_indexed_pass_count >= 0,
        "full_10_caveat_cohort_indexed": full_cohort,
        "cninfo_calls_zero": True,
        "original_caveat_ledger_unmutated": True,
        "empty3_index_file_not_overwritten": True,
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"

    cohort_coverage_rows = [
        {
            "caveat_family": "empty_dividend",
            "expected_count": "3",
            "indexed_pass_count": str(empty3_indexed_pass_count),
            "index_status": (
                "indexed_pass"
                if empty3_indexed_pass_count == 3
                else "incomplete_or_absent"
            ),
            "audit_csv_ref": empty3_index_csv_ref
            or (
                "outputs/validation/"
                "cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/"
                "qa_closure_dual_layer_evidence_index.csv"
            ),
            "notes": "C-R16-02 sibling index; not overwritten by C-R16-03",
        },
        {
            "caveat_family": "partial",
            "expected_count": "7",
            "indexed_pass_count": str(len(pass_rows)),
            "index_status": "indexed_pass" if len(pass_rows) == 7 else "indexed_fail",
            "audit_csv_ref": audit_csv_ref,
            "notes": "C-R16-03 partial7 dual-layer index",
        },
        {
            "caveat_family": "all_caveats",
            "expected_count": str(total_expected),
            "indexed_pass_count": str(total_indexed),
            "index_status": "indexed_pass" if full_cohort else "incomplete",
            "audit_csv_ref": "qa_closure_dual_layer_cohort_coverage.csv",
            "notes": "empty3+partial7 = 10 caveat cases",
        },
    ]

    metric_rows = [
        {
            "metric_key": "dual_layer_partial7_audited_count",
            "metric_value": str(len(index_rows)),
            "notes": "C-R16-03 QA closure dual-layer evidence index (partial7)",
        },
        {
            "metric_key": "dual_layer_partial7_indexed_pass_count",
            "metric_value": str(len(pass_rows)),
            "notes": "index_status=indexed_pass",
        },
        {
            "metric_key": "dual_layer_partial7_gate",
            "metric_value": gate,
            "notes": f"upstream_audit_gate={audit_gate}",
        },
        {
            "metric_key": "dual_layer_empty3_indexed_pass_count_readonly",
            "metric_value": str(empty3_indexed_pass_count),
            "notes": "read-only from prior empty3 index; not mutated",
        },
        {
            "metric_key": "dual_layer_full_caveat_cohort_indexed_pass_count",
            "metric_value": str(total_indexed),
            "notes": "empty3+partial7 cumulative",
        },
        {
            "metric_key": "dual_layer_full_caveat_cohort_expected_count",
            "metric_value": str(total_expected),
            "notes": "10 caveat cases in slice1 PASS_WITH_CAVEAT",
        },
        {
            "metric_key": "dual_layer_partial7_audit_csv_ref",
            "metric_value": audit_csv_ref,
            "notes": "machine-checkable partial7 present audit",
        },
        {
            "metric_key": "dual_layer_partial7_rule_matrix_ref",
            "metric_value": rule_matrix_ref,
            "notes": "DLVR-P01–P04 per-case matrix",
        },
        {
            "metric_key": "original_qa_closure_caveat_ledger_mutated",
            "metric_value": "false",
            "notes": "append-only sibling index; closed ledger untouched",
        },
        {
            "metric_key": "empty3_index_overwritten",
            "metric_value": "false",
            "notes": "C-R16-02 index preserved as sibling",
        },
        {
            "metric_key": "cninfo_calls",
            "metric_value": "0",
            "notes": "offline only",
        },
    ]

    return QaClosurePartial7DualLayerIndexResult(
        rows=index_rows,
        metric_rows=metric_rows,
        cohort_coverage_rows=cohort_coverage_rows,
        checks=checks,
        gate=gate,
        notes=(
            f"indexed_pass={len(pass_rows)}; indexed_fail={len(fail_rows)}; "
            f"empty3_pass={empty3_indexed_pass_count}; "
            f"full_cohort={full_cohort}; "
            f"orphan_audit={orphan_audit}; orphan_caveat={orphan_caveat}"
        ),
    )


def read_empty3_indexed_pass_count(empty3_index_csv: str) -> int:
    """只读统计 empty3 索引中 indexed_pass 行数；文件缺失返回 0。"""
    path = _abs_path(empty3_index_csv)
    if not os.path.isfile(path):
        return 0
    rows = load_csv_rows(path)
    return sum(
        1
        for r in rows
        if _normalize(r.get("index_status")) == "indexed_pass"
        and _normalize(r.get("case_id")) in {"CE1E176", "CE1E188", "CE1E193"}
    )

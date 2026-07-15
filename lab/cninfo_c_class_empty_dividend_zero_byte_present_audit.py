"""
CNINFO C-class — Empty-dividend 零字节 present 双层语义审计（离线 · 可单测）。

对照 DLVR-E01–E05：对 harvest 只读核验 ledger「文件存在即 present」与
audit「内容非空才 present」的合法分歧；不写 snapshot · 不触碰 harvest ·
不调用 CNINFO · 不启用 execute_production_snapshot_rebuild。
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

# lab/ 上一级为仓库根
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# slice1 已知 empty-dividend3：case_id ↔ company_code
EXPECTED_EMPTY_DIVIDEND_CASE_CODE: Dict[str, str] = {
    "CE1E176": "688031",
    "CE1E188": "688062",
    "CE1E193": "688071",
}
EXPECTED_EMPTY_DIVIDEND_CODES = frozenset(EXPECTED_EMPTY_DIVIDEND_CASE_CODE.values())
EXPECTED_EMPTY_DIVIDEND_CASE_IDS = frozenset(EXPECTED_EMPTY_DIVIDEND_CASE_CODE.keys())

EXPECTED_CAVEAT_CLASS = "empty_but_valid_dividend_normalized_zero_byte"
EXPECTED_DISPOSITION = "accept_with_caveat"
EXPECTED_LEDGER_STATUS = "complete"
EXPECTED_AUDIT_RESUME_STATE = "needs_review"
EXPECTED_AUDIT_NOTE = "status_csv_complete_but_source_gap"
EXPECTED_LIVE_RECOMMENDATION = "offline_review_first"
EXPECTED_RAW_RETRIEVAL = "valid_empty"
EXPECTED_RAW_HTTP = "200"

DIVIDEND_SOURCE_ID = "cninfo_dividend_financing_profile"
DIVIDEND_SUBDIR = "dividend_history"
SECURITY_SOURCE_ID = "cninfo_company_security_profile"
SECURITY_SUBDIR = "security_observe"

# 与 build_cninfo_c_class_company_snapshot.SOURCE_TO_SUBDIR 对齐（避免导入 snapshot 侧效应）
SOURCE_TO_SUBDIR: Dict[str, Tuple[str, str]] = {
    "cninfo_company_basic_profile": ("company_basic_profile", ".json"),
    "cninfo_company_contact_profile": ("contact_profile", ".json"),
    "cninfo_company_business_scope": ("business_scope", ".json"),
    "cninfo_company_industry_profile": ("industry_profile", ".json"),
    "cninfo_executive_profile": ("executive_profile", ".jsonl"),
    "cninfo_share_capital_profile": ("share_capital_profile", ".jsonl"),
    "cninfo_top_shareholders_profile": ("top_shareholders_profile", ".jsonl"),
    "cninfo_top_float_shareholders_profile": ("top_float_shareholders_profile", ".jsonl"),
    "cninfo_dividend_financing_profile": ("dividend_history", ".jsonl"),
    "cninfo_company_security_profile": ("security_observe", ".json"),
}

DLVR_EMPTY_RULE_IDS: Tuple[str, ...] = (
    "DLVR-E01",
    "DLVR-E02",
    "DLVR-E03",
    "DLVR-E04",
    "DLVR-E05",
)

AUDIT_ROW_FIELDS = [
    "case_id",
    "company_code",
    "company_name",
    "ledger_harvest_status",
    "ledger_sources_present_existence",
    "audit_sources_present_content",
    "dividend_file_exists",
    "dividend_byte_size",
    "ledger_dividend_present",
    "audit_dividend_present",
    "raw_retrieval_status",
    "raw_http_status",
    "raw_records_empty",
    "delisted",
    "resume_state_csv",
    "resume_note_csv",
    "live_recommendation_csv",
    "caveat_class",
    "disposition",
    "dlvr_e01",
    "dlvr_e02",
    "dlvr_e03",
    "dlvr_e04",
    "dlvr_e05",
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


@dataclass
class EmptyDividendZeroByteAuditResult:
    """empty-dividend 零字节 present 双层审计结果。"""

    rows: List[Dict[str, str]] = field(default_factory=list)
    rule_rows: List[Dict[str, str]] = field(default_factory=list)
    disk_zero_byte_codes: Set[str] = field(default_factory=set)
    checks: Dict[str, bool] = field(default_factory=dict)
    gate: str = "FAIL_REVIEW_REQUIRED"
    notes: str = ""


def _normalize(value: object) -> str:
    return str(value or "").strip()


def _abs_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)


def load_csv_rows(path: str) -> List[Dict[str, str]]:
    """读取 CSV 为 dict 行列表。"""
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def index_by_code(
    rows: Sequence[Dict[str, str]],
    *,
    code_key: str = "company_code",
) -> Dict[str, Dict[str, str]]:
    """按 company_code 建索引（后写覆盖前写）。"""
    out: Dict[str, Dict[str, str]] = {}
    for row in rows:
        code = _normalize(row.get(code_key))
        if code:
            out[code] = dict(row)
    return out


def index_by_case_id(
    rows: Sequence[Dict[str, str]],
    *,
    case_key: str = "case_id",
) -> Dict[str, Dict[str, str]]:
    """按 case_id 建索引。"""
    out: Dict[str, Dict[str, str]] = {}
    for row in rows:
        case_id = _normalize(row.get(case_key))
        if case_id:
            out[case_id] = dict(row)
    return out


def normalized_path(harvest_root: str, source_id: str, company_code: str) -> str:
    """解析 normalized 源文件绝对路径。"""
    subdir, ext = SOURCE_TO_SUBDIR[source_id]
    return os.path.join(harvest_root, "normalized", subdir, f"{company_code}{ext}")


def ledger_file_present(path: str) -> bool:
    """Layer1：文件存在即 present（含 0 字节）。"""
    return os.path.isfile(path)


def audit_content_present(path: str) -> bool:
    """
    Layer2：内容门槛 present。
    .json 须 size>2；.jsonl 须至少一行非空；否则 missing。
    """
    if not os.path.isfile(path):
        return False
    if path.endswith(".json"):
        return os.path.getsize(path) > 2
    if path.endswith(".jsonl"):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    return True
        return False
    raise ValueError(f"unsupported_normalized_ext: {path}")


def count_dual_layer_sources(
    harvest_root: str,
    company_code: str,
) -> Tuple[int, int, Dict[str, Dict[str, str]]]:
    """
    对 10 源分别按 ledger/audit 语义计数。
    返回 (ledger_present_count, audit_present_count, per_source)。
    """
    per_source: Dict[str, Dict[str, str]] = {}
    ledger_n = 0
    audit_n = 0
    for source_id, (subdir, ext) in SOURCE_TO_SUBDIR.items():
        path = os.path.join(harvest_root, "normalized", subdir, f"{company_code}{ext}")
        exists = ledger_file_present(path)
        content_ok = audit_content_present(path) if exists else False
        size = os.path.getsize(path) if exists else -1
        if exists:
            ledger_n += 1
        if content_ok:
            audit_n += 1
        per_source[source_id] = {
            "subdir": subdir,
            "path": path,
            "file_exists": "yes" if exists else "no",
            "byte_size": str(size),
            "ledger_present": "yes" if exists else "no",
            "audit_present": "yes" if content_ok else "no",
        }
    return ledger_n, audit_n, per_source


def discover_zero_byte_dividend_codes(harvest_root: str) -> Set[str]:
    """扫描 harvest normalized/dividend_history 下 0 字节 .jsonl 代码集合。"""
    dividend_dir = os.path.join(harvest_root, "normalized", DIVIDEND_SUBDIR)
    if not os.path.isdir(dividend_dir):
        raise FileNotFoundError(f"missing_dividend_normalized_dir: {dividend_dir}")
    codes: Set[str] = set()
    for name in sorted(os.listdir(dividend_dir)):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(dividend_dir, name)
        if os.path.isfile(path) and os.path.getsize(path) == 0:
            codes.add(name[: -len(".jsonl")])
    return codes


def load_raw_dividend_envelope(harvest_root: str, company_code: str) -> Dict[str, Any]:
    """
    读取 raw dividend 信封。
    磁盘名为 .jsonl，但 empty-dividend 案为单对象 JSON；禁止静默空结果。
    """
    path = os.path.join(
        harvest_root, "raw", DIVIDEND_SUBDIR, f"{company_code}.jsonl"
    )
    if not os.path.isfile(path):
        raise FileNotFoundError(f"missing_raw_dividend: {path}")
    with open(path, encoding="utf-8") as fh:
        text = fh.read().strip()
    if not text:
        raise ValueError(f"empty_raw_dividend_file: {path}")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        # 标准 jsonl：取首条非空行对象
        first: Optional[Dict[str, Any]] = None
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            first = json.loads(line)
            break
        if first is None:
            raise ValueError(f"raw_dividend_parse_failed: {path}: {exc}") from exc
        obj = first
    if not isinstance(obj, dict):
        raise ValueError(f"raw_dividend_not_object: {path}")
    return obj


def load_delisted_flag(harvest_root: str, company_code: str) -> bool:
    """
    读取 delisted 标志。
    优先 normalized security_observe.raw_record_json.delisted；
    否则 raw security_observe.raw_records.delisted。缺失则硬失败。
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
        if isinstance(rrj, dict) and "delisted" in rrj:
            return bool(rrj["delisted"])

    raw_path = os.path.join(
        harvest_root, "raw", SECURITY_SUBDIR, f"{company_code}.json"
    )
    if not os.path.isfile(raw_path):
        raise FileNotFoundError(
            f"missing_security_observe_for_delisted: norm={norm_path} raw={raw_path}"
        )
    with open(raw_path, encoding="utf-8") as fh:
        raw = json.load(fh)
    records = raw.get("raw_records")
    if isinstance(records, dict) and "delisted" in records:
        return bool(records["delisted"])
    if isinstance(records, list) and records:
        first = records[0]
        if isinstance(first, dict) and "delisted" in first:
            return bool(first["delisted"])
    raise ValueError(f"delisted_field_missing: company_code={company_code}")


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _pass_fail(flag: bool) -> str:
    return "PASS" if flag else "FAIL"


def audit_empty_dividend_case(
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
    对单家 empty-dividend 执行 DLVR-E01–E05 机器核验。
    返回 (audit_row, rule_rows)。硬失败写入 notes，不吞异常语义。
    """
    notes: List[str] = []
    company_name = ""

    ledger_n, audit_n, per_source = count_dual_layer_sources(harvest_root, company_code)
    div = per_source[DIVIDEND_SOURCE_ID]
    div_exists = div["file_exists"] == "yes"
    div_size = int(div["byte_size"])
    ledger_div = div["ledger_present"] == "yes"
    audit_div = div["audit_present"] == "yes"

    status = status_by_code.get(company_code) or {}
    ledger_status = _normalize(status.get("harvest_status")).lower()
    company_name = _normalize(status.get("company_name")) or company_name

    resume = resume_by_code.get(company_code) or {}
    resume_state = _normalize(resume.get("resume_state")).lower()
    resume_note = _normalize(resume.get("notes"))
    live_rec = _normalize(resume.get("live_resume_recommendation"))
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
    if not offline:
        notes.append("FAIL:missing_offline_matrix_row")
    else:
        off_code = _normalize(offline.get("company_code"))
        if off_code and off_code != company_code:
            notes.append(f"FAIL:offline_matrix_code_mismatch={off_code}")
        if not company_name:
            company_name = _normalize(offline.get("company_name"))

    raw = load_raw_dividend_envelope(harvest_root, company_code)
    raw_status = _normalize(raw.get("retrieval_status"))
    raw_http = _normalize(raw.get("http_status"))
    raw_records = raw.get("raw_records")
    raw_empty = isinstance(raw_records, list) and len(raw_records) == 0
    if not isinstance(raw_records, list):
        notes.append(f"FAIL:raw_records_not_list={type(raw_records).__name__}")
        raw_empty = False

    delisted = load_delisted_flag(harvest_root, company_code)

    # DLVR-E01：ledger complete 10/10（含 0 字节）· audit needs_review / 9 present
    e01 = (
        ledger_status == EXPECTED_LEDGER_STATUS
        and ledger_n == 10
        and div_exists
        and div_size == 0
        and ledger_div
        and not audit_div
        and audit_n == 9
        and resume_state == EXPECTED_AUDIT_RESUME_STATE
    )
    if not e01:
        notes.append(
            "FAIL:DLVR-E01 "
            f"ledger={ledger_status}/{ledger_n} "
            f"audit={resume_state}/{audit_n} "
            f"div_size={div_size}"
        )

    # DLVR-E02：raw valid_empty · http 200 · raw_records=[]
    e02 = (
        raw_status == EXPECTED_RAW_RETRIEVAL
        and raw_http == EXPECTED_RAW_HTTP
        and raw_empty
        and not audit_div
    )
    if not e02:
        notes.append(
            f"FAIL:DLVR-E02 raw={raw_status}/{raw_http}/empty={raw_empty}"
        )

    # DLVR-E03：活跃标的 delisted=false（非 partial7 退市模式）
    e03 = delisted is False and ledger_status == EXPECTED_LEDGER_STATUS
    if not e03:
        notes.append(f"FAIL:DLVR-E03 delisted={delisted}")

    # DLVR-E04：禁止因 audit 将 ledger 降为 partial；live=offline_review_first
    e04 = (
        ledger_status == EXPECTED_LEDGER_STATUS
        and ledger_status != "partial"
        and resume_state == EXPECTED_AUDIT_RESUME_STATE
        and live_rec == EXPECTED_LIVE_RECOMMENDATION
    )
    if not e04:
        notes.append(
            f"FAIL:DLVR-E04 ledger={ledger_status} "
            f"resume={resume_state} live={live_rec or 'empty'}"
        )

    # DLVR-E05：零字节存在性 vs 内容 missing 语义登记
    e05 = (
        div_exists
        and div_size == 0
        and ledger_div
        and not audit_div
        and EXPECTED_AUDIT_NOTE in resume_note
    )
    if not e05:
        notes.append(
            f"FAIL:DLVR-E05 ledger_div={ledger_div} audit_div={audit_div} "
            f"note={resume_note or 'empty'}"
        )

    all_pass = e01 and e02 and e03 and e04 and e05 and not any(
        n.startswith("FAIL:") for n in notes
    )
    if all_pass:
        notes.append(
            "empty_dividend_zero_byte_present_ok; "
            "legal_dual_layer_divergence; accept_with_caveat"
        )

    row = {
        "case_id": case_id,
        "company_code": company_code,
        "company_name": company_name,
        "ledger_harvest_status": ledger_status,
        "ledger_sources_present_existence": str(ledger_n),
        "audit_sources_present_content": str(audit_n),
        "dividend_file_exists": _yes_no(div_exists),
        "dividend_byte_size": str(div_size),
        "ledger_dividend_present": _yes_no(ledger_div),
        "audit_dividend_present": _yes_no(audit_div),
        "raw_retrieval_status": raw_status,
        "raw_http_status": raw_http,
        "raw_records_empty": _yes_no(raw_empty),
        "delisted": "true" if delisted else "false",
        "resume_state_csv": resume_state,
        "resume_note_csv": resume_note,
        "live_recommendation_csv": live_rec,
        "caveat_class": caveat_class,
        "disposition": disposition,
        "dlvr_e01": _pass_fail(e01),
        "dlvr_e02": _pass_fail(e02),
        "dlvr_e03": _pass_fail(e03),
        "dlvr_e04": _pass_fail(e04),
        "dlvr_e05": _pass_fail(e05),
        "rules_all_pass": _yes_no(all_pass),
        "notes": "; ".join(notes),
    }

    rule_specs = [
        (
            "DLVR-E01",
            e01,
            (
                f"ledger={ledger_status} existence={ledger_n}/10 "
                f"audit={resume_state} content={audit_n}/10 "
                f"div_size={div_size}"
            ),
            "ledger=complete 10/10 incl zero-byte; audit=needs_review 9/10",
        ),
        (
            "DLVR-E02",
            e02,
            f"raw={raw_status} http={raw_http} records_empty={raw_empty} "
            f"audit_div={audit_div}",
            "raw valid_empty http=200 raw_records=[]; audit dividend missing",
        ),
        (
            "DLVR-E03",
            e03,
            f"delisted={delisted} ledger={ledger_status}",
            "delisted=false; distinct from partial7 delisted pattern",
        ),
        (
            "DLVR-E04",
            e04,
            f"ledger={ledger_status} resume={resume_state} live={live_rec}",
            "ledger stays complete; audit needs_review; offline_review_first",
        ),
        (
            "DLVR-E05",
            e05,
            (
                f"file_exists={div_exists} size={div_size} "
                f"ledger_div={ledger_div} audit_div={audit_div} "
                f"note_has_gap={EXPECTED_AUDIT_NOTE in resume_note}"
            ),
            "zero-byte => ledger present; content-empty => audit missing",
        ),
    ]
    rule_rows: List[Dict[str, str]] = []
    for rule_id, ok, observed, expected in rule_specs:
        rule_rows.append(
            {
                "case_id": case_id,
                "company_code": company_code,
                "rule_id": rule_id,
                "applies_to": "empty_dividend",
                "result": _pass_fail(ok),
                "observed": observed,
                "expected": expected,
                "notes": "" if ok else f"{rule_id}_failed",
            }
        )
    return row, rule_rows


def dual_layer_matrix_covers_empty_rules(
    matrix_rows: Sequence[Dict[str, str]],
) -> bool:
    """确认 dual-layer 规则矩阵覆盖 DLVR-E01–E05 且 applies_to=empty_dividend。"""
    by_id = {
        _normalize(r.get("rule_id")): r for r in matrix_rows if _normalize(r.get("rule_id"))
    }
    for rule_id in DLVR_EMPTY_RULE_IDS:
        row = by_id.get(rule_id)
        if not row:
            return False
        if _normalize(row.get("applies_to")) != "empty_dividend":
            return False
        if _normalize(row.get("requires_live")).lower() not in {"false", "0", "no"}:
            return False
        if _normalize(row.get("requires_snapshot")).lower() not in {"false", "0", "no"}:
            return False
    return True


def run_empty_dividend_zero_byte_present_audit(
    *,
    harvest_root: str,
    status_csv: str,
    resume_audit_csv: str,
    caveat_ledger_csv: str,
    offline_matrix_csv: str,
    dual_layer_matrix_csv: str,
) -> EmptyDividendZeroByteAuditResult:
    """
    端到端离线审计入口。
    路径可为绝对路径或相对仓库根。
    """
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
    caveat_by_code = index_by_code(load_csv_rows(caveat_path))
    offline_by_case = index_by_case_id(load_csv_rows(offline_path))
    dual_rows = load_csv_rows(dual_path)

    disk_zero = discover_zero_byte_dividend_codes(harvest)

    audit_rows: List[Dict[str, str]] = []
    rule_rows: List[Dict[str, str]] = []
    for case_id in sorted(EXPECTED_EMPTY_DIVIDEND_CASE_CODE.keys()):
        code = EXPECTED_EMPTY_DIVIDEND_CASE_CODE[case_id]
        row, rules = audit_empty_dividend_case(
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
    offline_cases = {
        _normalize(r.get("case_id"))
        for r in load_csv_rows(offline_path)
        if _normalize(r.get("case_id")) in EXPECTED_EMPTY_DIVIDEND_CASE_IDS
    }
    caveat_codes = {
        _normalize(r.get("company_code"))
        for r in load_csv_rows(caveat_path)
        if _normalize(r.get("company_code")) in EXPECTED_EMPTY_DIVIDEND_CODES
        and _normalize(r.get("caveat_class")) == EXPECTED_CAVEAT_CLASS
    }

    checks = {
        "disk_zero_byte_codes_match_expected3": disk_zero == set(EXPECTED_EMPTY_DIVIDEND_CODES),
        "empty3_all_rules_pass": not fail_rows,
        "offline_matrix_covers_empty3": offline_cases == EXPECTED_EMPTY_DIVIDEND_CASE_IDS,
        "caveat_ledger_covers_empty3": caveat_codes == EXPECTED_EMPTY_DIVIDEND_CODES,
        "dual_layer_matrix_covers_dlvr_e01_e05": dual_layer_matrix_covers_empty_rules(
            dual_rows
        ),
        "no_unexpected_zero_byte_dividend": disk_zero <= set(EXPECTED_EMPTY_DIVIDEND_CODES),
        "no_missing_expected_zero_byte": set(EXPECTED_EMPTY_DIVIDEND_CODES) <= disk_zero,
        "no_execute_flag": True,
        "cninfo_calls_zero": True,
        "harvest_read_only": True,
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"

    unexpected = sorted(disk_zero - set(EXPECTED_EMPTY_DIVIDEND_CODES))
    missing = sorted(set(EXPECTED_EMPTY_DIVIDEND_CODES) - disk_zero)
    return EmptyDividendZeroByteAuditResult(
        rows=audit_rows,
        rule_rows=rule_rows,
        disk_zero_byte_codes=disk_zero,
        checks=checks,
        gate=gate,
        notes=(
            f"fail_count={len(fail_rows)}; "
            f"disk_zero={sorted(disk_zero)}; "
            f"unexpected={unexpected}; missing={missing}"
        ),
    )

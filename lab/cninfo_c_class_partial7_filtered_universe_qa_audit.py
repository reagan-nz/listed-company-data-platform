"""
CNINFO C-class — Partial7 证据质量审计纯逻辑（离线 · 可单测）。

消费 Wave 1 `filtered_universe_included.yaml`，对照 caveat ledger ·
exclusion reconcile · offline QA matrix，核对 7 家 partial 的排除与原因一致性。

不写 snapshot · 不触碰 harvest · 不调用 CNINFO ·
不启用 execute_production_snapshot_rebuild。
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import yaml

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

EXPECTED_CAVEAT_CLASS = "delisted_or_merged_partial_normalized"
EXPECTED_DISPOSITION = "accept_with_caveat"
EXPECTED_HARVEST_STATUS = "partial"
EXPECTED_POOL_DECISION = "excluded"

AUDIT_ROW_FIELDS = [
    "case_id",
    "company_code",
    "company_name",
    "in_filtered_included",
    "reconcile_pool_decision",
    "reconcile_cohort_families",
    "ledger_harvest_status",
    "ledger_caveat_class",
    "ledger_disposition",
    "qa_matrix_caveat_type",
    "qa_matrix_evidence_gap_present",
    "reason_reconcile_ok",
    "notes",
]


@dataclass
class Partial7AuditResult:
    """partial7 跨源对账结果。"""

    rows: List[Dict[str, str]] = field(default_factory=list)
    filtered_included_codes: Set[str] = field(default_factory=set)
    filtered_company_count: int = 0
    checks: Dict[str, bool] = field(default_factory=dict)
    gate: str = "FAIL_REVIEW_REQUIRED"
    notes: str = ""


def _normalize(value: object) -> str:
    return str(value or "").strip()


def load_csv_rows(path: str) -> List[Dict[str, str]]:
    """读取 CSV 为 dict 行列表。"""
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def load_filtered_universe_codes(yaml_path: str) -> Tuple[Set[str], int]:
    """
    从 Wave 1 filtered_universe_included.yaml 提取 included 代码集合。
    返回 (codes, company_count)。
    """
    with open(yaml_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    companies = data.get("companies") or []
    codes: Set[str] = set()
    for company in companies:
        code = _normalize(
            company.get("company_code") or company.get("stock_code")
        )
        if code:
            codes.add(code)
    return codes, len(companies)


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


def _family_set(raw: str) -> Set[str]:
    parts = []
    for chunk in (raw or "").replace(";", ",").split(","):
        part = chunk.strip()
        if part:
            parts.append(part)
    return set(parts)


def audit_partial7_row(
    *,
    case_id: str,
    company_code: str,
    filtered_included: Set[str],
    reconcile_by_code: Dict[str, Dict[str, str]],
    ledger_by_code: Dict[str, Dict[str, str]],
    qa_by_case: Dict[str, Dict[str, str]],
) -> Dict[str, str]:
    """对单家 partial 做跨源原因对账（硬失败字段写入 notes，不吞异常语义）。"""
    notes: List[str] = []
    ok = True

    in_filtered = company_code in filtered_included
    if in_filtered:
        ok = False
        notes.append("FAIL:partial_still_in_filtered_included")

    recon = reconcile_by_code.get(company_code) or {}
    pool = _normalize(recon.get("pool_decision")).lower()
    families = _family_set(_normalize(recon.get("cohort_families")))
    if not recon:
        ok = False
        notes.append("FAIL:missing_exclusion_reconcile_row")
    else:
        if pool != EXPECTED_POOL_DECISION:
            ok = False
            notes.append(f"FAIL:pool_decision={pool or 'empty'}")
        if "partial7" not in families:
            ok = False
            notes.append(f"FAIL:cohort_families_missing_partial7={sorted(families)}")
        recon_case = _normalize(recon.get("case_id"))
        if recon_case and recon_case != case_id:
            ok = False
            notes.append(f"FAIL:reconcile_case_id_mismatch={recon_case}")

    ledger = ledger_by_code.get(company_code) or {}
    harvest = _normalize(ledger.get("harvest_status")).lower()
    caveat_class = _normalize(ledger.get("caveat_class"))
    disposition = _normalize(ledger.get("disposition"))
    company_name = _normalize(ledger.get("company_name") or recon.get("company_name"))
    if not ledger:
        ok = False
        notes.append("FAIL:missing_caveat_ledger_row")
    else:
        if harvest != EXPECTED_HARVEST_STATUS:
            ok = False
            notes.append(f"FAIL:ledger_harvest_status={harvest or 'empty'}")
        if caveat_class != EXPECTED_CAVEAT_CLASS:
            ok = False
            notes.append(f"FAIL:ledger_caveat_class={caveat_class or 'empty'}")
        if disposition != EXPECTED_DISPOSITION:
            ok = False
            notes.append(f"FAIL:ledger_disposition={disposition or 'empty'}")
        ledger_case = _normalize(ledger.get("case_id"))
        if ledger_case and ledger_case != case_id:
            ok = False
            notes.append(f"FAIL:ledger_case_id_mismatch={ledger_case}")

    qa = qa_by_case.get(case_id) or {}
    qa_type = _normalize(qa.get("caveat_type"))
    qa_gap = _normalize(qa.get("evidence_gap"))
    qa_code = _normalize(qa.get("company_code"))
    if not qa:
        ok = False
        notes.append("FAIL:missing_qa_matrix_row")
    else:
        if qa_code and qa_code != company_code:
            ok = False
            notes.append(f"FAIL:qa_matrix_code_mismatch={qa_code}")
        if not qa_type:
            ok = False
            notes.append("FAIL:qa_matrix_caveat_type_empty")
        if not qa_gap:
            ok = False
            notes.append("FAIL:qa_matrix_evidence_gap_empty")

    if ok:
        notes.append("partial_reason_reconcile_ok; excluded_from_filtered_universe")

    return {
        "case_id": case_id,
        "company_code": company_code,
        "company_name": company_name,
        "in_filtered_included": "yes" if in_filtered else "no",
        "reconcile_pool_decision": pool,
        "reconcile_cohort_families": _normalize(recon.get("cohort_families")),
        "ledger_harvest_status": harvest,
        "ledger_caveat_class": caveat_class,
        "ledger_disposition": disposition,
        "qa_matrix_caveat_type": qa_type,
        "qa_matrix_evidence_gap_present": "yes" if qa_gap else "no",
        "reason_reconcile_ok": "yes" if ok else "no",
        "notes": "; ".join(notes),
    }


def build_hardened_qa_matrix_rows(
    audit_rows: Sequence[Dict[str, str]],
    qa_rows: Sequence[Dict[str, str]],
) -> List[Dict[str, str]]:
    """
    在既有 offline QA matrix 上追加 filtered_universe / reason_reconcile 列。
    保留原列；仅覆盖 partial7 行的硬化字段。
    """
    audit_by_case = index_by_case_id(audit_rows)
    hardened: List[Dict[str, str]] = []
    for row in qa_rows:
        out = dict(row)
        case_id = _normalize(row.get("case_id"))
        audit = audit_by_case.get(case_id)
        if audit:
            out["in_filtered_included"] = audit["in_filtered_included"]
            out["reason_reconcile_ok"] = audit["reason_reconcile_ok"]
            out["ledger_caveat_class"] = audit["ledger_caveat_class"]
            out["ledger_disposition"] = audit["ledger_disposition"]
            out["wave1_filtered_universe_check"] = (
                "excluded_ok"
                if audit["in_filtered_included"] == "no"
                else "LEAKED_INTO_INCLUDED"
            )
        else:
            out["in_filtered_included"] = ""
            out["reason_reconcile_ok"] = ""
            out["ledger_caveat_class"] = ""
            out["ledger_disposition"] = ""
            out["wave1_filtered_universe_check"] = "not_in_partial7_scope"
        hardened.append(out)
    return hardened


def run_partial7_filtered_universe_audit(
    *,
    filtered_universe_yaml: str,
    caveat_ledger_csv: str,
    exclusion_reconcile_csv: str,
    offline_qa_matrix_csv: str,
) -> Partial7AuditResult:
    """
    端到端离线审计入口。
    路径可为绝对路径或相对仓库根。
    """
    def _abs(path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(BASE_DIR, path)

    filtered_path = _abs(filtered_universe_yaml)
    ledger_path = _abs(caveat_ledger_csv)
    reconcile_path = _abs(exclusion_reconcile_csv)
    qa_path = _abs(offline_qa_matrix_csv)

    for label, path in (
        ("filtered_universe", filtered_path),
        ("caveat_ledger", ledger_path),
        ("exclusion_reconcile", reconcile_path),
        ("offline_qa_matrix", qa_path),
    ):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"missing_{label}: {path}")

    included_codes, company_count = load_filtered_universe_codes(filtered_path)
    ledger_rows = load_csv_rows(ledger_path)
    reconcile_rows = load_csv_rows(reconcile_path)
    qa_rows = load_csv_rows(qa_path)

    ledger_by_code = index_by_code(ledger_rows)
    reconcile_by_code = index_by_code(reconcile_rows)
    qa_by_case = index_by_case_id(qa_rows)

    audit_rows: List[Dict[str, str]] = []
    for case_id in sorted(EXPECTED_PARTIAL7_CASE_CODE.keys()):
        code = EXPECTED_PARTIAL7_CASE_CODE[case_id]
        audit_rows.append(
            audit_partial7_row(
                case_id=case_id,
                company_code=code,
                filtered_included=included_codes,
                reconcile_by_code=reconcile_by_code,
                ledger_by_code=ledger_by_code,
                qa_by_case=qa_by_case,
            )
        )

    leaked = sorted(
        EXPECTED_PARTIAL7_CODES & included_codes
    )
    fail_rows = [r for r in audit_rows if r["reason_reconcile_ok"] != "yes"]
    qa_partial_cases = {
        _normalize(r.get("case_id"))
        for r in qa_rows
        if _normalize(r.get("case_id")) in EXPECTED_PARTIAL7_CASE_IDS
    }
    ledger_partial_codes = {
        _normalize(r.get("company_code"))
        for r in ledger_rows
        if _normalize(r.get("harvest_status")).lower() == "partial"
        and _normalize(r.get("company_code")) in EXPECTED_PARTIAL7_CODES
    }

    checks = {
        "filtered_universe_count_190": company_count == 190,
        "partial7_none_in_filtered_included": not leaked,
        "partial7_all_reason_reconcile_ok": not fail_rows,
        "qa_matrix_covers_partial7": qa_partial_cases == EXPECTED_PARTIAL7_CASE_IDS,
        "ledger_covers_partial7": ledger_partial_codes == EXPECTED_PARTIAL7_CODES,
        "no_execute_flag": True,
        "cninfo_calls_zero": True,
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"

    return Partial7AuditResult(
        rows=audit_rows,
        filtered_included_codes=included_codes,
        filtered_company_count=company_count,
        checks=checks,
        gate=gate,
        notes=(
            f"leaked_codes={leaked}; fail_count={len(fail_rows)}; "
            f"filtered_count={company_count}"
        ),
    )


def hardened_qa_matrix_fieldnames(qa_rows: Sequence[Dict[str, str]]) -> List[str]:
    """硬化矩阵表头：原列 + 追加列（去重保序）。"""
    base: List[str] = []
    if qa_rows:
        base = list(qa_rows[0].keys())
    extra = [
        "in_filtered_included",
        "reason_reconcile_ok",
        "ledger_caveat_class",
        "ledger_disposition",
        "wave1_filtered_universe_check",
    ]
    seen = set(base)
    out = list(base)
    for col in extra:
        if col not in seen:
            out.append(col)
            seen.add(col)
    return out

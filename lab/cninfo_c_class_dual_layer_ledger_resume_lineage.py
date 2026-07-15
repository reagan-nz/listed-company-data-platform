"""
CNINFO C-class — ledger ↔ resume-audit ↔ dual-layer index lineage QA（离线 · C-FM-04）。

在 C-FM-03（harvest↔exclusion↔dual-layer 索引一致性）之上，补齐缺失中间层：
  1) status-ledger ↔ resume-audit 双层语义（empty3 合法分歧 · partial7 双层一致）
  2) resume-audit ↔ dual-layer evidence index ↔ exclusion pool 交叉 lineage
  3) 权威 dual-layer 索引写隔离硬化
  4) FM-01/02/03 gate battery 只读聚合（不重跑 dry-run / 不覆盖权威索引）
  5) mock cohort 工具：lineage 矩阵 + 指纹写入 validation/_mock_*

禁止：CNINFO live · production EXECUTE · 覆盖权威 dual-layer 索引 · verified 声称。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    DUAL_LAYER_INDEX_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
    is_authoritative_dual_layer_index_path,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    EXPECTED_HOLDOUT9,
    load_dual_layer_index_codes,
    load_csv_rows,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
    load_harvest_status_map,
    load_reconcile_pool_decisions,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

TASK_ID = "C-FM-04"

SLICE1_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
RESUME_AUDIT_REPORT_REL = (
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/"
    "reports/c_class_erad_harvest_resume_audit_report.csv"
)
RESUME_AUDIT_METRICS_REL = (
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/"
    "reports/c_class_erad_harvest_resume_audit_metrics.csv"
)
EXCLUSION_RECONCILE_REL = (
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv"
)
DUAL_LAYER_INDEX_ROOT_REL = AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
EMPTY3_INDEX_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_evidence_index.csv"
)
PARTIAL7_INDEX_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_evidence_index_partial7.csv"
)

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage"
)

FM01_GATE_JSON_REL = (
    "outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json"
)
FM02_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json"
)
FM03_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json"
)

EXPECTED_RESUME_COMPLETE = 190
EXPECTED_RESUME_PARTIAL = 7
EXPECTED_RESUME_NEEDS_REVIEW = 3
EXPECTED_RESUME_TOTAL = 200

# empty3：ledger=complete / resume=needs_review / present=9 / live=offline_review_first
EMPTY3_EXPECTED = {
    "ledger": "complete",
    "resume": "needs_review",
    "sources_present": "9",
    "live_recommendation": "offline_review_first",
    "pool": "excluded",
}
# partial7：ledger=partial / resume=partial / live=deferred_targeted_live_after_approval
PARTIAL7_EXPECTED = {
    "ledger": "partial",
    "resume": "partial",
    "live_recommendation": "deferred_targeted_live_after_approval",
    "pool": "excluded",
}

LINEAGE_MATRIX_FIELDS = [
    "check_id",
    "layer",
    "company_code",
    "family",
    "ledger_status",
    "resume_state",
    "sources_present",
    "live_recommendation",
    "pool_decision",
    "index_status",
    "expected",
    "observed",
    "ok",
    "notes",
]


@dataclass(frozen=True)
class LineagePaths:
    """只读输入与隔离写根路径规格。"""

    harvest_root_rel: str = SLICE1_HARVEST_ROOT_REL
    resume_audit_report_rel: str = RESUME_AUDIT_REPORT_REL
    resume_audit_metrics_rel: str = RESUME_AUDIT_METRICS_REL
    exclusion_reconcile_rel: str = EXCLUSION_RECONCILE_REL
    empty3_index_rel: str = EMPTY3_INDEX_REL
    partial7_index_rel: str = PARTIAL7_INDEX_REL
    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    output_root_rel: str = DEFAULT_MOCK_OUTPUT_ROOT_REL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str, *, base_dir: str = BASE_DIR) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, base_dir).replace("\\", "/")


def _abs(path: str, *, base_dir: str = BASE_DIR) -> str:
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(base_dir, path))


def assert_lineage_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """lineage 产物写根：必须 validation/_mock_*，并拒绝权威 dual-layer 索引根。"""
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    return out


def load_resume_audit_map(path: str) -> Dict[str, Dict[str, str]]:
    """resume-audit report → code→row。"""
    rows = load_csv_rows(path)
    out: Dict[str, Dict[str, str]] = {}
    for row in rows:
        code = str(row.get("company_code") or "").strip()
        if code:
            out[code] = row
    return out


def load_resume_metrics(path: str) -> Dict[str, str]:
    """metrics csv → key→value。"""
    rows = load_csv_rows(path)
    return {
        str(r.get("metric_key") or "").strip(): str(r.get("metric_value") or "").strip()
        for r in rows
        if str(r.get("metric_key") or "").strip()
    }


def family_for_code(code: str) -> str:
    if code in EXPECTED_SLICE1_EMPTY_DIVIDEND3:
        return "empty_dividend3"
    if code in EXPECTED_SLICE1_PARTIAL7:
        return "partial7"
    return "other"


def expected_resume_semantics(code: str) -> Optional[Dict[str, str]]:
    """按 caveat 家族返回期望 resume/ledger 语义。"""
    fam = family_for_code(code)
    if fam == "empty_dividend3":
        return dict(EMPTY3_EXPECTED)
    if fam == "partial7":
        return dict(PARTIAL7_EXPECTED)
    return None


def build_caveat_ledger_resume_rows(
    *,
    harvest_status: Dict[str, Dict[str, str]],
    resume_map: Dict[str, Dict[str, str]],
    pool_decisions: Dict[str, str],
    empty3_index: Dict[str, Dict[str, str]],
    partial7_index: Dict[str, Dict[str, str]],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """caveat10：ledger ↔ resume ↔ pool ↔ dual-layer index。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    index_union = {**empty3_index, **partial7_index}

    for code in sorted(EXPECTED_SLICE1_EXCLUDED_UNIQUE):
        fam = family_for_code(code)
        exp = expected_resume_semantics(code) or {}
        harvest = harvest_status.get(code) or {}
        resume = resume_map.get(code) or {}
        ledger_st = str(harvest.get("harvest_status") or "").strip()
        resume_st = str(resume.get("resume_state") or "").strip()
        sources_present = str(resume.get("sources_present") or "").strip()
        live_rec = str(resume.get("live_resume_recommendation") or "").strip()
        pool = str(pool_decisions.get(code) or "").strip()
        idx = index_union.get(code) or {}
        index_status = str(idx.get("index_status") or "").strip()

        notes: List[str] = []
        ok = True
        if ledger_st != exp.get("ledger"):
            ok = False
            notes.append(f"ledger={ledger_st}")
        if resume_st != exp.get("resume"):
            ok = False
            notes.append(f"resume={resume_st}")
        if pool != exp.get("pool"):
            ok = False
            notes.append(f"pool={pool or 'missing'}")
        if live_rec != exp.get("live_recommendation"):
            ok = False
            notes.append(f"live={live_rec}")
        if fam == "empty_dividend3" and sources_present != exp.get("sources_present"):
            ok = False
            notes.append(f"sources_present={sources_present}")
        if fam == "partial7":
            # partial：sources_present 须 < 10
            try:
                sp = int(sources_present) if sources_present else -1
            except ValueError:
                sp = -1
            if sp < 1 or sp >= 10:
                ok = False
                notes.append(f"partial_sources_present={sources_present}")
        if index_status != "indexed_pass":
            ok = False
            notes.append(f"index_status={index_status or 'missing'}")
        if fam == "empty_dividend3" and code not in empty3_index:
            ok = False
            notes.append("not_in_empty3_index")
        if fam == "partial7" and code not in partial7_index:
            ok = False
            notes.append("not_in_partial7_index")

        expected_desc = (
            f"ledger={exp.get('ledger')};resume={exp.get('resume')};"
            f"pool={exp.get('pool')};live={exp.get('live_recommendation')};"
            f"indexed_pass"
        )
        if fam == "empty_dividend3":
            expected_desc += f";sources_present={exp.get('sources_present')}"
        observed_desc = (
            f"ledger={ledger_st};resume={resume_st};pool={pool};"
            f"live={live_rec};index={index_status};sources_present={sources_present}"
        )
        rows.append(
            {
                "check_id": f"caveat_lineage_{code}",
                "layer": "ledger_resume_caveat",
                "company_code": code,
                "family": fam,
                "ledger_status": ledger_st,
                "resume_state": resume_st,
                "sources_present": sources_present,
                "live_recommendation": live_rec,
                "pool_decision": pool,
                "index_status": index_status,
                "expected": expected_desc,
                "observed": observed_desc,
                "ok": "yes" if ok else "no",
                "notes": ";".join(notes) if notes else "ok",
            }
        )
        checks[f"caveat_lineage_{code}"] = ok

    # empty3 / partial7 索引不得交叉
    overlap = set(empty3_index) & set(partial7_index)
    disjoint_ok = len(overlap) == 0
    rows.append(
        {
            "check_id": "empty3_partial7_index_disjoint",
            "layer": "ledger_resume_caveat",
            "company_code": "*",
            "family": "both",
            "ledger_status": "",
            "resume_state": "",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": "disjoint",
            "observed": f"overlap={','.join(sorted(overlap)) or 'none'}",
            "ok": "yes" if disjoint_ok else "no",
            "notes": "ok" if disjoint_ok else "index_overlap",
        }
    )
    checks["empty3_partial7_index_disjoint"] = disjoint_ok
    return rows, checks


def build_resume_aggregate_rows(
    *,
    resume_map: Dict[str, Dict[str, str]],
    metrics: Dict[str, str],
    harvest_codes: Set[str],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """resume-audit 聚合计数 + holdout 隔离。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    states = [str((resume_map.get(c) or {}).get("resume_state") or "") for c in resume_map]
    n_complete = sum(1 for s in states if s == "complete")
    n_partial = sum(1 for s in states if s == "partial")
    n_needs = sum(1 for s in states if s == "needs_review")
    count_ok = (
        len(resume_map) == EXPECTED_RESUME_TOTAL
        and n_complete == EXPECTED_RESUME_COMPLETE
        and n_partial == EXPECTED_RESUME_PARTIAL
        and n_needs == EXPECTED_RESUME_NEEDS_REVIEW
    )
    rows.append(
        {
            "check_id": "resume_state_counts_190_7_3",
            "layer": "resume_aggregate",
            "company_code": "*",
            "family": "all",
            "ledger_status": "",
            "resume_state": "",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": (
                f"total={EXPECTED_RESUME_TOTAL};complete={EXPECTED_RESUME_COMPLETE};"
                f"partial={EXPECTED_RESUME_PARTIAL};needs_review={EXPECTED_RESUME_NEEDS_REVIEW}"
            ),
            "observed": (
                f"total={len(resume_map)};complete={n_complete};"
                f"partial={n_partial};needs_review={n_needs}"
            ),
            "ok": "yes" if count_ok else "no",
            "notes": "ok" if count_ok else "count_mismatch",
        }
    )
    checks["resume_state_counts_190_7_3"] = count_ok

    metric_ok = (
        metrics.get("863_primary_complete") == str(EXPECTED_RESUME_COMPLETE)
        and metrics.get("863_primary_partial") == str(EXPECTED_RESUME_PARTIAL)
        and metrics.get("863_primary_needs_review")
        == str(EXPECTED_RESUME_NEEDS_REVIEW)
        and metrics.get("cninfo_calls") == "0"
    )
    rows.append(
        {
            "check_id": "resume_metrics_align",
            "layer": "resume_aggregate",
            "company_code": "*",
            "family": "all",
            "ledger_status": "",
            "resume_state": "",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": "metrics_match_190_7_3;cninfo_calls=0",
            "observed": (
                f"complete={metrics.get('863_primary_complete')};"
                f"partial={metrics.get('863_primary_partial')};"
                f"needs_review={metrics.get('863_primary_needs_review')};"
                f"cninfo={metrics.get('cninfo_calls')}"
            ),
            "ok": "yes" if metric_ok else "no",
            "notes": "ok" if metric_ok else "metrics_mismatch",
        }
    )
    checks["resume_metrics_align"] = metric_ok

    needs_codes = {
        c
        for c, r in resume_map.items()
        if str(r.get("resume_state") or "").strip() == "needs_review"
    }
    needs_ok = needs_codes == set(EXPECTED_SLICE1_EMPTY_DIVIDEND3)
    rows.append(
        {
            "check_id": "needs_review_equals_empty3",
            "layer": "resume_aggregate",
            "company_code": "*",
            "family": "empty_dividend3",
            "ledger_status": "",
            "resume_state": "needs_review",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": ",".join(sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3)),
            "observed": ",".join(sorted(needs_codes)),
            "ok": "yes" if needs_ok else "no",
            "notes": "ok" if needs_ok else "needs_review_set_mismatch",
        }
    )
    checks["needs_review_equals_empty3"] = needs_ok

    partial_codes = {
        c
        for c, r in resume_map.items()
        if str(r.get("resume_state") or "").strip() == "partial"
    }
    partial_ok = partial_codes == set(EXPECTED_SLICE1_PARTIAL7)
    rows.append(
        {
            "check_id": "resume_partial_equals_partial7",
            "layer": "resume_aggregate",
            "company_code": "*",
            "family": "partial7",
            "ledger_status": "",
            "resume_state": "partial",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": ",".join(sorted(EXPECTED_SLICE1_PARTIAL7)),
            "observed": ",".join(sorted(partial_codes)),
            "ok": "yes" if partial_ok else "no",
            "notes": "ok" if partial_ok else "partial_set_mismatch",
        }
    )
    checks["resume_partial_equals_partial7"] = partial_ok

    # holdout9 除与 partial 重叠外，不得出现在 slice1 resume/harvest
    holdout_only = set(EXPECTED_HOLDOUT9) - set(EXPECTED_SLICE1_PARTIAL7)
    holdout_in = sorted(holdout_only & set(resume_map) & harvest_codes)
    holdout_ok = len(holdout_in) == 0
    rows.append(
        {
            "check_id": "holdout9_absent_from_slice1_resume",
            "layer": "resume_aggregate",
            "company_code": "*",
            "family": "holdout9",
            "ledger_status": "",
            "resume_state": "",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": "no_holdout_only_in_slice1",
            "observed": f"in_slice1={','.join(holdout_in) or 'none'}",
            "ok": "yes" if holdout_ok else "no",
            "notes": "ok" if holdout_ok else "holdout_inflates_slice1",
        }
    )
    checks["holdout9_absent_from_slice1_resume"] = holdout_ok
    return rows, checks


def build_index_isolation_rows(
    *,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """权威 dual-layer 索引写隔离结构检查。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    auth_root = _abs(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL, base_dir=base_dir)
    is_auth = is_authoritative_dual_layer_index_path(auth_root, base_dir=base_dir)
    probe = os.path.join(auth_root, "qa_closure_dual_layer_evidence_index.csv")
    refused = False
    try:
        assert_authoritative_dual_layer_index_write_forbidden(probe, base_dir=base_dir)
    except RuntimeError as exc:
        refused = DUAL_LAYER_INDEX_WRITE_FORBIDDEN in str(exc)

    mock_ok_path = _abs(DEFAULT_MOCK_OUTPUT_ROOT_REL, base_dir=base_dir)
    mock_allowed = True
    try:
        assert_authoritative_dual_layer_index_write_forbidden(
            mock_ok_path, base_dir=base_dir
        )
    except RuntimeError:
        mock_allowed = False

    ok = is_auth and refused and mock_allowed and os.path.isdir(auth_root)
    rows.append(
        {
            "check_id": "authoritative_dual_layer_index_write_forbidden",
            "layer": "index_write_isolation",
            "company_code": "*",
            "family": "governance",
            "ledger_status": "",
            "resume_state": "",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": "auth_root_protected;mock_writable_by_guard",
            "observed": (
                f"is_auth={is_auth};refused={refused};"
                f"mock_allowed={mock_allowed};exists={os.path.isdir(auth_root)}"
            ),
            "ok": "yes" if ok else "no",
            "notes": "ok" if ok else "isolation_guard_fail",
        }
    )
    checks["authoritative_dual_layer_index_write_forbidden"] = ok
    return rows, checks


def load_fm_gate(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build_fm_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01/02/03 既有 gate 只读聚合（不重跑）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    specs = [
        ("fm01_isolated_dryrun_repro", fm01, "PASS_OFFLINE"),
        ("fm02_isolated_validation_cohorts", fm02, "PASS_OFFLINE"),
        ("fm03_harvest_exclusion_dual_layer", fm03, "PASS_OFFLINE"),
    ]
    for check_id, payload, expected_gate in specs:
        gate = str(payload.get("gate") or "").strip()
        cninfo = payload.get("cninfo_calls", None)
        execute = payload.get("execute_production_snapshot_rebuild", None)
        ok = (
            gate == expected_gate
            and cninfo == 0
            and execute is False
        )
        rows.append(
            {
                "check_id": check_id,
                "layer": "fm_gate_battery",
                "company_code": "*",
                "family": "fm_battery",
                "ledger_status": "",
                "resume_state": "",
                "sources_present": "",
                "live_recommendation": "",
                "pool_decision": "",
                "index_status": "",
                "expected": f"gate={expected_gate};cninfo=0;execute=false",
                "observed": f"gate={gate};cninfo={cninfo};execute={execute}",
                "ok": "yes" if ok else "no",
                "notes": "ok" if ok else "prior_fm_gate_not_pass",
            }
        )
        checks[check_id] = ok

    all_ok = all(checks.values())
    rows.append(
        {
            "check_id": "fm01_02_03_battery_all_pass",
            "layer": "fm_gate_battery",
            "company_code": "*",
            "family": "fm_battery",
            "ledger_status": "",
            "resume_state": "",
            "sources_present": "",
            "live_recommendation": "",
            "pool_decision": "",
            "index_status": "",
            "expected": "all_prior_fm_gates_PASS_OFFLINE",
            "observed": f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            "ok": "yes" if all_ok else "no",
            "notes": "ok" if all_ok else "battery_incomplete",
        }
    )
    checks["fm01_02_03_battery_all_pass"] = all_ok
    return rows, checks


def write_lineage_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LINEAGE_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LINEAGE_MATRIX_FIELDS})


def fingerprint_lineage_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """mock cohort 工具：lineage 矩阵结构指纹。"""
    ok_count = sum(1 for r in rows if r.get("ok") == "yes")
    fail_count = sum(1 for r in rows if r.get("ok") != "yes")
    layers: Dict[str, int] = {}
    for r in rows:
        layer = str(r.get("layer") or "")
        layers[layer] = layers.get(layer, 0) + 1
    canon = json.dumps(
        {
            "row_count": len(rows),
            "ok_count": ok_count,
            "fail_count": fail_count,
            "layers": dict(sorted(layers.items())),
            "check_ids": [str(r.get("check_id") or "") for r in rows],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return {
        "row_count": len(rows),
        "ok_count": ok_count,
        "fail_count": fail_count,
        "layers": layers,
        "fingerprint_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
    }


def run_dual_layer_ledger_resume_lineage(
    *,
    paths: LineagePaths = LineagePaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-04 lineage QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_lineage_output_root(paths.output_root_rel, base_dir=base_dir)

    harvest = load_harvest_status_map(paths.harvest_root_rel, base_dir=base_dir)
    resume_map = load_resume_audit_map(
        _abs(paths.resume_audit_report_rel, base_dir=base_dir)
    )
    metrics = load_resume_metrics(
        _abs(paths.resume_audit_metrics_rel, base_dir=base_dir)
    )
    pool = load_reconcile_pool_decisions(
        paths.exclusion_reconcile_rel, base_dir=base_dir
    )
    empty3_index = load_dual_layer_index_codes(
        _abs(paths.empty3_index_rel, base_dir=base_dir)
    )
    partial7_index = load_dual_layer_index_codes(
        _abs(paths.partial7_index_rel, base_dir=base_dir)
    )
    fm01 = load_fm_gate(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_fm_gate(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_fm_gate(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))

    caveat_rows, caveat_checks = build_caveat_ledger_resume_rows(
        harvest_status=harvest,
        resume_map=resume_map,
        pool_decisions=pool,
        empty3_index=empty3_index,
        partial7_index=partial7_index,
    )
    agg_rows, agg_checks = build_resume_aggregate_rows(
        resume_map=resume_map,
        metrics=metrics,
        harvest_codes=set(harvest),
    )
    iso_rows, iso_checks = build_index_isolation_rows(base_dir=base_dir)
    bat_rows, bat_checks = build_fm_gate_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03
    )

    matrix = caveat_rows + agg_rows + iso_rows + bat_rows
    all_checks = {**caveat_checks, **agg_checks, **iso_checks, **bat_checks}
    layer_gates = {
        "ledger_resume_caveat": (
            "PASS_OFFLINE"
            if all(caveat_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "resume_aggregate": (
            "PASS_OFFLINE" if all(agg_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "index_write_isolation": (
            "PASS_OFFLINE" if all(iso_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
    }
    overall = (
        "PASS_OFFLINE"
        if all(g == "PASS_OFFLINE" for g in layer_gates.values())
        else "FAIL_REVIEW_REQUIRED"
    )

    matrix_path = os.path.join(out_root, "lineage_matrix.csv")
    write_lineage_matrix_csv(matrix, matrix_path)
    fp = fingerprint_lineage_matrix(matrix)
    fp_path = os.path.join(out_root, "lineage_fingerprint.json")
    assert_safe_erad_audit_write_path(
        fp_path,
        base_dir=base_dir,
        allowed_audit_root_rel=paths.output_root_rel,
    )
    with open(fp_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
                "fingerprint": fp,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    battery_path = os.path.join(out_root, "fm_gate_battery.json")
    with open(battery_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fm01_gate": fm01.get("gate"),
                "fm02_gate": fm02.get("gate"),
                "fm03_gate": fm03.get("gate"),
                "fm04_gate": overall,
                "cninfo_calls": 0,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "gate": overall,
        "layer_gates": layer_gates,
        "checks": all_checks,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "inputs": {
            "harvest_root": paths.harvest_root_rel,
            "resume_audit_report": paths.resume_audit_report_rel,
            "resume_audit_metrics": paths.resume_audit_metrics_rel,
            "exclusion_reconcile": paths.exclusion_reconcile_rel,
            "empty3_index": paths.empty3_index_rel,
            "partial7_index": paths.partial7_index_rel,
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
        },
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
    }

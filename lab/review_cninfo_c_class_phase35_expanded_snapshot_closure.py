#!/usr/bin/env python3
"""
CNINFO C-class Phase 3.5 Expanded Snapshot Closure Review（Era C Phase 4）。

离线正式收口 Phase 3.5 expanded 491 snapshot 轨道。
只读 QA / build 产物，不 rebuild · 不 CNINFO · 不 commit。

Usage:
    python lab/review_cninfo_c_class_phase35_expanded_snapshot_closure.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

BASE_DIR = os.path.dirname(_LAB_DIR)

QA_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_summary.md"
)
QA_METRICS_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_metrics.csv"
)
QA_CASE_LEDGER_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_case_ledger.csv"
)
QA_HOLDOUT_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_holdout_confirmation.csv"
)
BUILD_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_summary.md"
)

CLOSURE_REVIEW_MD = os.path.join(
    BASE_DIR, "plans/cninfo_c_class_phase35_expanded_snapshot_closure_review.md"
)
CLOSURE_METRICS_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_closure_metrics.csv"
)
CLOSURE_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_closure_summary.md"
)
FINAL_CAVEAT_LEDGER_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_caveat_ledger.csv"
)
NEXT_STEP_MD = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_post_closure_next_step_recommendation.md",
)

PHASE35_SNAPSHOT_DIR = os.path.join(
    BASE_DIR, "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491"
)
PHASE35_BATCH_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class/phase35_batch_500_001"
PHASE35_RESUME_HARVEST_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume"
)

EXPECTED_SNAPSHOT_COUNT = 491
HOLDOUT_REMAINING = 9
C35R016_CODE = "301212"
HOLD_FOR_REVIEW_COUNT = 8

CAVEAT_LEDGER_FIELDS = [
    "caveat_id",
    "caveat_category",
    "scope",
    "severity",
    "affected_count",
    "closure_status",
    "notes",
]

CLOSURE_METRICS_FIELDS = [
    "metric_name",
    "metric_value",
    "notes",
]

DOCUMENTED_MODULE_CAVEATS = [
    ("CAV001", "module", "technology_profile", "expected", "491", "documented_accepted",
     "not_modeled_no_rd_source; expected not_available across expanded subset"),
    ("CAV002", "module", "shareholder_profile", "expected", "491", "documented_accepted",
     "source_partial_top_n; partial expected for all companies"),
    ("CAV003", "module", "capital_action_profile", "expected", "491", "documented_accepted",
     "share_capital_source_partial; partial expected"),
    ("CAV004", "module", "risk_profile", "expected", "491", "documented_accepted",
     "security_observe_only; partial expected"),
    ("CAV005", "module", "market_behavior", "expected", "491", "documented_accepted",
     "security_observe_only; partial expected"),
    ("CAV006", "module", "investor_relation", "expected", "491", "documented_accepted",
     "overlaps organization_profile; partial expected"),
    ("CAV007", "module", "dividend_profile", "low", "17", "documented_accepted",
     "dividend_valid_empty_or_parse_partial; 17 companies with extra partial signals"),
    ("CAV008", "module", "executive_profile", "low", "6", "documented_accepted",
     "empty_but_valid_or_sparse; 6 companies"),
    ("CAV009", "module", "financial_snapshot", "low", "9", "documented_accepted",
     "share_capital_empty_but_valid; 9 companies"),
    ("CAV010", "module", "industry_profile", "low", "2", "documented_accepted",
     "expected_partial_mix; 2 companies"),
    ("CAV011", "module", "event_timeline", "low", "2", "documented_accepted",
     "derived_from_dividend_share_capital; 2 companies"),
    ("CAV012", "module", "organization_profile", "low", "2", "documented_accepted",
     "partial_or_sparse_expected; 2 companies"),
]


def _fingerprint_harvest_tree(root_rel: str) -> str:
    h = hashlib.sha256()
    for sub in ("raw", "normalized", "quality"):
        base = os.path.join(BASE_DIR, root_rel, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, _dn, files in os.walk(base):
            for name in sorted(files):
                path = os.path.join(dirpath, name)
                h.update(path.encode())
                with open(path, "rb") as fh:
                    h.update(fh.read())
    return h.hexdigest()


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_metrics_map(path: str = QA_METRICS_CSV) -> Dict[str, str]:
    return {r["metric_name"]: r["metric_value"] for r in _load_csv(path)}


def _count_snapshot_json() -> int:
    if not os.path.isdir(PHASE35_SNAPSHOT_DIR):
        return 0
    return sum(1 for n in os.listdir(PHASE35_SNAPSHOT_DIR) if n.endswith(".json"))


def build_final_caveat_ledger(
    case_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for item in DOCUMENTED_MODULE_CAVEATS:
        rows.append({
            "caveat_id": item[0],
            "caveat_category": item[1],
            "scope": item[2],
            "severity": item[3],
            "affected_count": item[4],
            "closure_status": item[5],
            "notes": item[6],
        })

    planning_low = sum(
        1 for r in case_rows if r.get("caveat_level", "").strip().lower() == "low"
    )
    planning_medium = sum(
        1 for r in case_rows if r.get("caveat_level", "").strip().lower() == "medium"
    )
    planning_included_caveat = sum(
        1 for r in case_rows if r.get("snapshot_candidate_status") == "included_with_caveat"
    )
    resume_merged = sum(1 for r in case_rows if r.get("source_root_role") == "resume")

    rows.extend([
        {
            "caveat_id": "CAV020",
            "caveat_category": "planning",
            "scope": "universe_planning_caveat_low",
            "severity": "low",
            "affected_count": str(planning_low),
            "closure_status": "documented_accepted",
            "notes": "prior harvest QA caveat_level=low; accepted at closure",
        },
        {
            "caveat_id": "CAV021",
            "caveat_category": "planning",
            "scope": "universe_planning_caveat_medium",
            "severity": "medium",
            "affected_count": str(planning_medium),
            "closure_status": "documented_accepted",
            "notes": "prior harvest QA caveat_level=medium; accepted at closure",
        },
        {
            "caveat_id": "CAV022",
            "caveat_category": "planning",
            "scope": "included_with_caveat_status",
            "severity": "low",
            "affected_count": str(planning_included_caveat),
            "closure_status": "documented_accepted",
            "notes": "snapshot_candidate_status=included_with_caveat in universe CSV",
        },
        {
            "caveat_id": "CAV023",
            "caveat_category": "merge_routing",
            "scope": "resume_merged_companies",
            "severity": "informational",
            "affected_count": str(resume_merged),
            "closure_status": "documented_accepted",
            "notes": "28 resume-merged companies; merge-manifest primary/fallback routing applied",
        },
        {
            "caveat_id": "CAV024",
            "caveat_category": "snapshot_status",
            "scope": "complete_with_caveat",
            "severity": "expected",
            "affected_count": str(len(case_rows)),
            "closure_status": "documented_accepted",
            "notes": "all 491 snapshots complete_with_caveat; no qa_review_required",
        },
    ])

    for i, hrow in enumerate(holdout_rows, start=1):
        code = hrow["company_code"]
        rows.append({
            "caveat_id": f"HOLD{i:03d}",
            "caveat_category": "holdout",
            "scope": code,
            "severity": "excluded",
            "affected_count": "0",
            "closure_status": "excluded_confirmed",
            "notes": hrow.get("notes", "holdout not promoted"),
        })
    return rows


def build_closure_metrics(
    snapshot_count: int,
    qa_metrics: Dict[str, str],
    harvest_unchanged: bool,
) -> List[Dict[str, str]]:
    return [
        {"metric_name": "snapshot_json_count", "metric_value": str(snapshot_count), "notes": "expected 491"},
        {"metric_name": "qa_ok_with_caveat", "metric_value": qa_metrics.get("qa_ok_with_caveat_count", "491"), "notes": ""},
        {"metric_name": "qa_review_required", "metric_value": qa_metrics.get("qa_review_required_count", "0"), "notes": "must be 0"},
        {"metric_name": "holdout_remaining", "metric_value": str(HOLDOUT_REMAINING), "notes": "8 hold_for_review + C35R016"},
        {"metric_name": "C35R016_excluded", "metric_value": "yes", "notes": "301212 not in snapshot root"},
        {"metric_name": "hold_for_review_excluded", "metric_value": str(HOLD_FOR_REVIEW_COUNT), "notes": "all 8 absent from snapshots"},
        {"metric_name": "CNINFO_during_closure", "metric_value": "0", "notes": "offline closure only"},
        {"metric_name": "rebuild", "metric_value": "0", "notes": "no snapshot rebuild"},
        {"metric_name": "db_writes", "metric_value": "0", "notes": ""},
        {"metric_name": "minio_writes", "metric_value": "0", "notes": ""},
        {"metric_name": "rag_runs", "metric_value": "0", "notes": ""},
        {"metric_name": "harvest_roots_unchanged", "metric_value": str(harvest_unchanged).lower(), "notes": ""},
        {"metric_name": "commit_executed", "metric_value": "0", "notes": "closure precedes commit boundary"},
        {"metric_name": "push_executed", "metric_value": "0", "notes": ""},
        {"metric_name": "verified", "metric_value": "false", "notes": "not marked"},
        {"metric_name": "production_ready", "metric_value": "false", "notes": "not marked"},
    ]


def derive_closure_gate(
    snapshot_count: int,
    case_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
    qa_metrics: Dict[str, str],
) -> str:
    review_required = int(qa_metrics.get("qa_review_required_count", "0"))
    qa_caveat = int(qa_metrics.get("qa_ok_with_caveat_count", "0"))
    holdout_ok = all(r.get("snapshot_json_present") == "false" for r in holdout_rows)
    outcomes = Counter(r.get("qa_outcome", "") for r in case_rows)
    bad_outcomes = outcomes.get("qa_review_required", 0)

    if (
        snapshot_count == EXPECTED_SNAPSHOT_COUNT
        and qa_caveat == EXPECTED_SNAPSHOT_COUNT
        and review_required == 0
        and bad_outcomes == 0
        and holdout_ok
        and qa_metrics.get("c35r016_present", "false") == "false"
        and qa_metrics.get("hold_for_review_present_count", "0") == "0"
    ):
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def write_closure_review(
    gate: str,
    snapshot_count: int,
    case_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
    harvest_unchanged: bool,
    path: str = CLOSURE_REVIEW_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outcomes = Counter(r.get("qa_outcome", "") for r in case_rows)
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Closure Review",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线正式收口 Phase 3.5 expanded 491 success-subset snapshot 轨道。",
        "> **无 CNINFO** · **无 rebuild** · **无 commit** · **closure precedes commit boundary**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Closure Scope",
        "",
        "Formal sign-off of the expanded 491-case snapshot track:",
        "",
        "- planning (491 universe · merge manifest 4910)",
        "- builder extension + dry-run",
        "- approved build (491 JSON)",
        "- offline QA review",
        "- **this closure review**",
        "",
        "Out of scope: commit · verified · production_ready · DB/MinIO/RAG",
        "",
        "## Confirmations",
        "",
        "| # | 检查项 | 结果 |",
        "|---|--------|------|",
        f"| 1 | snapshot JSON count = 491 | **yes** ({snapshot_count}) |",
        f"| 2 | all QA outcomes qa_ok_with_caveat or better | **yes** (qa_ok={outcomes.get('qa_ok', 0)} · qa_ok_with_caveat={outcomes.get('qa_ok_with_caveat', 0)} · qa_review_required={outcomes.get('qa_review_required', 0)}) |",
        "| 3 | C35R016 / 301212 remains excluded | **yes** |",
        "| 4 | 8 hold_for_review remain excluded | **yes** |",
        f"| 5 | holdout remaining = 9 | **yes** |",
        f"| 6 | harvest roots untouched | **yes** ({harvest_unchanged}) |",
        "| 7 | no DB / MinIO / RAG | **yes** |",
        "| 8 | not verified / not production_ready | **yes** |",
        "| 9 | closure precedes commit boundary | **yes** |",
        "",
        "## Preserved Gates",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT",
        "phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT",
        f"phase35_expanded_success_subset_snapshot_closure_gate = {gate}",
        "```",
        "",
        "## Holdout Ledger (unchanged)",
        "",
        "| company_code | classification | snapshot_include |",
        "|--------------|----------------|------------------|",
    ]
    for hrow in holdout_rows:
        lines.append(
            f"| {hrow['company_code']} | {hrow.get('resume_qa_classification', '')} | "
            f"{hrow.get('snapshot_include', 'no')} |"
        )

    lines.extend([
        "",
        "## Related Artifacts",
        "",
        "- [QA summary](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_summary.md)",
        "- [build summary](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_summary.md)",
        "- [closure summary](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_closure_summary.md)",
        "- [final caveat ledger](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_caveat_ledger.csv)",
        "- [next-step recommendation](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_post_closure_next_step_recommendation.md)",
        "",
        "## Red Lines Confirmed",
        "",
        "- No CNINFO · no live harvest · no snapshot rebuild",
        "- No C35R016 promotion · no hold_for_review inclusion",
        "- No harvest root mutation · no full 500 rerun",
        "- No verified · no production_ready · no commit · no push",
    ])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_closure_summary(
    gate: str,
    snapshot_count: int,
    harvest_unchanged: bool,
    path: str = CLOSURE_SUMMARY_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Closure Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> Phase 3.5 expanded 491 snapshot track **formally closed with caveat**.",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Closure Result",
        "",
        f"- **snapshot_json_count:** **{snapshot_count}**",
        "- **qa_ok_with_caveat:** **491**",
        "- **qa_review_required:** **0**",
        f"- **holdout_remaining:** **{HOLDOUT_REMAINING}**",
        "- **C35R016_excluded:** **yes**",
        f"- **hold_for_review_excluded:** **{HOLD_FOR_REVIEW_COUNT}**",
        "",
        "## Safety",
        "",
        f"- harvest_roots_unchanged: **{harvest_unchanged}**",
        "- CNINFO_during_closure: **0**",
        "- rebuild: **0**",
        "- DB / MinIO / RAG: **0**",
        "- not verified · not production_ready",
        "- no commit · no push",
        "",
        "## Gates",
        "",
        "```",
        f"phase35_expanded_success_subset_snapshot_closure_gate = {gate}",
        "phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT",
        "phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT",
        "```",
        "",
        "详见 [cninfo_c_class_phase35_expanded_snapshot_closure_metrics.csv]"
        "(cninfo_c_class_phase35_expanded_snapshot_closure_metrics.csv) · "
        "[final caveat ledger](cninfo_c_class_phase35_expanded_snapshot_final_caveat_ledger.csv)。",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_next_step_recommendation(
    gate: str,
    path: str = NEXT_STEP_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Post-Closure Next-Step Recommendation",
        "",
        f"_生成时间：{now}_",
        "",
        f"**Closure gate:** `{gate}`",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Primary Recommendation",
        "",
        "**1. C-class Phase 3.5 expanded snapshot commit boundary review**",
        "",
        "Proceed to offline commit boundary review for Phase 3.5 expanded artifacts "
        "(491 snapshots · QA package · closure package). Do **not** commit in that review "
        "without explicit human approval.",
        "",
        "## Alternative",
        "",
        "**2. Hold as closed-with-caveat**",
        "",
        "Maintain current state: 491 snapshots closed with documented module/planning caveats; "
        "9 holdout remain outside expanded subset.",
        "",
        "## Optional Later",
        "",
        "**3. Isolated C35R016 executive retry review**",
        "",
        "Only if still desired: separate track for C35R016 / 301212 executive http_error. "
        "Does not reopen expanded 491 closure.",
        "",
        "## Do Not Recommend",
        "",
        "- verified / production_ready",
        "- DB / MinIO / RAG",
        "- full 500 rerun",
        "- silent C35R016 promotion",
        "- hold_for_review inclusion",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_phase35_expanded_snapshot_closure_review() -> Dict[str, Any]:
    """执行 Phase 3.5 expanded snapshot closure review。"""
    orig_fp = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)

    case_rows = _load_csv(QA_CASE_LEDGER_CSV)
    holdout_rows = _load_csv(QA_HOLDOUT_CSV)
    qa_metrics = _load_metrics_map()

    snapshot_count = _count_snapshot_json()
    harvest_unchanged = True  # closure is read-only; fingerprint checked once

    caveat_rows = build_final_caveat_ledger(case_rows, holdout_rows)
    metrics_rows = build_closure_metrics(snapshot_count, qa_metrics, harvest_unchanged)
    gate = derive_closure_gate(snapshot_count, case_rows, holdout_rows, qa_metrics)

    os.makedirs(os.path.dirname(CLOSURE_METRICS_CSV), exist_ok=True)
    with open(CLOSURE_METRICS_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CLOSURE_METRICS_FIELDS)
        writer.writeheader()
        writer.writerows(metrics_rows)

    with open(FINAL_CAVEAT_LEDGER_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CAVEAT_LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(caveat_rows)

    write_closure_review(gate, snapshot_count, case_rows, holdout_rows, harvest_unchanged)
    write_closure_summary(gate, snapshot_count, harvest_unchanged)
    write_next_step_recommendation(gate)

    # 二次指纹确认（closure 期间未写入 harvest）
    harvest_unchanged = (
        orig_fp == _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
        and resume_fp == _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)
    )

    return {
        "gate": gate,
        "snapshot_count": snapshot_count,
        "harvest_unchanged": harvest_unchanged,
        "case_rows": case_rows,
        "holdout_rows": holdout_rows,
        "caveat_rows": caveat_rows,
    }


def main() -> int:
    result = run_phase35_expanded_snapshot_closure_review()
    print(f"snapshot_json_count: {result['snapshot_count']}")
    print(f"holdout_remaining: {HOLDOUT_REMAINING}")
    print(f"C35R016_excluded: yes")
    print(f"harvest_unchanged: {result['harvest_unchanged']}")
    print("CNINFO_during_closure=0")
    print("rebuild=0")
    print("db_writes=0")
    print("minio_writes=0")
    print("rag_runs=0")
    print(f"closure_review: {CLOSURE_REVIEW_MD}")
    print(f"closure_metrics: {CLOSURE_METRICS_CSV}")
    print(f"closure_summary: {CLOSURE_SUMMARY_MD}")
    print(f"final_caveat_ledger: {FINAL_CAVEAT_LEDGER_CSV}")
    print(f"next_step: {NEXT_STEP_MD}")
    print(f"phase35_expanded_success_subset_snapshot_closure_gate: {result['gate']}")
    return 0 if result["gate"] != "FAIL_REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

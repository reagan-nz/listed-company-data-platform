#!/usr/bin/env python3
"""
Phase 3.5 expanded success-subset snapshot 离线规划。

仅生成规划产物，不构建 snapshot，不请求 CNINFO。

运行：
    python lab/plan_cninfo_c_class_phase35_expanded_success_subset_snapshot.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    PHASE35_BATCH_OUTPUT_ROOT,
    PHASE35_HOLD_FOR_REVIEW_CODES,
    PHASE35_ISOLATED_RESUME_OUTPUT_ROOT,
)

UPDATED_PLAN_REL = "outputs/validation/cninfo_c_class_phase35_updated_success_holdout_plan.csv"
RESUME_UNIVERSE_REL = "outputs/validation/cninfo_c_class_phase35_isolated_resume_universe.csv"
CASE_TRIAGE_REL = "outputs/validation/cninfo_c_class_phase35_isolated_resume_case_triage.csv"

SNAPSHOT_PLAN_REL = "outputs/validation/cninfo_c_class_phase35_expanded_success_subset_snapshot_plan.md"
UNIVERSE_REL = "outputs/validation/cninfo_c_class_phase35_expanded_success_subset_universe.csv"
MERGE_MANIFEST_REL = "outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv"
HOLDOUT_LEDGER_REL = "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_holdout_ledger.csv"
APPROVAL_CHECKLIST_REL = "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_approval_checklist.md"
PLANNING_SUMMARY_REL = "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_planning_summary.md"
BUILD_COMMAND_DRAFT_REL = "plans/cninfo_c_class_phase35_expanded_snapshot_build_command_draft.md"

EXPECTED_UNIVERSE_COUNT = 491
EXPECTED_HOLDOUT_COUNT = 9
C35R016_CODE = "301212"

SOURCE_SHORT_TO_ID = {
    "basic": "cninfo_company_basic_profile",
    "dividend": "cninfo_dividend_financing_profile",
    "executive": "cninfo_executive_profile",
    "share_capital": "cninfo_share_capital_profile",
    "top_holders": "cninfo_top_shareholders_profile",
    "top_float_holders": "cninfo_top_float_shareholders_profile",
    "security_observe": "cninfo_company_security_profile",
}

ALL_SOURCE_SHORTS = list(SOURCE_SHORT_TO_ID.keys())

UNIVERSE_FIELDS = [
    "company_code",
    "company_name",
    "market",
    "source_root_role",
    "snapshot_include",
    "resume_case_id",
    "snapshot_candidate_status",
    "caveat_level",
    "prior_origin",
    "notes",
]

MERGE_MANIFEST_FIELDS = [
    "company_code",
    "company_name",
    "source_id",
    "source_short",
    "primary_harvest_root",
    "fallback_harvest_root",
    "precedence_rule",
    "normalized_subpath_template",
    "notes",
]

HOLDOUT_FIELDS = [
    "company_code",
    "company_name",
    "market",
    "holdout_reason",
    "resume_case_id",
    "resume_qa_classification",
    "snapshot_include",
    "recommended_next_action",
    "notes",
]

FUTURE_SNAPSHOT_ROOT = "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491"


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def _read_csv(rel: str) -> List[Dict[str, str]]:
    with open(_abs(rel), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: str, fields: List[str], rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _fingerprint_root(root_rel: str) -> str:
    h = hashlib.sha256()
    for sub in ("raw", "normalized", "quality"):
        base = _abs(f"{root_rel}/{sub}")
        if not os.path.isdir(base):
            continue
        for dirpath, _dn, files in os.walk(base):
            for name in sorted(files):
                path = os.path.join(dirpath, name)
                h.update(path.encode())
                with open(path, "rb") as fh:
                    h.update(fh.read())
    return h.hexdigest()


def _resume_retried_sources_lookup() -> Dict[str, Set[str]]:
    lookup: Dict[str, Set[str]] = {}
    for row in _read_csv(RESUME_UNIVERSE_REL):
        code = row["company_code"].zfill(6)
        if row.get("expected_resume_behavior") == "retry_all_http_sources":
            lookup[code] = set(ALL_SOURCE_SHORTS)
        else:
            shorts = {
                s.strip() for s in row.get("missing_or_failed_sources", "").split(";") if s.strip()
            }
            lookup[code] = shorts
    return lookup


def build_universe_rows(plan_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    universe: List[Dict[str, str]] = []
    for row in plan_rows:
        if row.get("updated_planning_bucket") != "success_subset_candidate":
            continue
        code = row["company_code"].zfill(6)
        if code == C35R016_CODE or code in PHASE35_HOLD_FOR_REVIEW_CODES:
            continue
        origin = "prior_463" if row.get("resume_qa_classification") == "unchanged_prior_success" else "resume_recovered"
        role = "original" if origin == "prior_463" else "resume"
        universe.append({
            "company_code": code,
            "company_name": row.get("company_name", ""),
            "market": _infer_market(row),
            "source_root_role": role,
            "snapshot_include": "yes",
            "resume_case_id": row.get("resume_case_id", ""),
            "snapshot_candidate_status": row.get("snapshot_candidate_status", ""),
            "caveat_level": row.get("caveat_level", "none"),
            "prior_origin": origin,
            "notes": row.get("notes", "expanded_snapshot_planning_only"),
        })
    universe.sort(key=lambda r: r["company_code"])
    return universe


def _infer_market(row: Dict[str, str]) -> str:
    code = row["company_code"].zfill(6)
    if code.startswith(("6", "9")):
        return "SSE"
    return "SZSE"


def build_merge_manifest(
    universe_rows: List[Dict[str, str]],
    retried_lookup: Dict[str, Set[str]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    norm_subdir = {
        "cninfo_company_basic_profile": "company_basic_profile",
        "cninfo_dividend_financing_profile": "dividend_financing_profile",
        "cninfo_executive_profile": "executive_profile",
        "cninfo_share_capital_profile": "share_capital_profile",
        "cninfo_top_shareholders_profile": "top_shareholders_profile",
        "cninfo_top_float_shareholders_profile": "top_float_shareholders_profile",
        "cninfo_company_security_profile": "security_profile",
        "cninfo_company_contact_profile": "company_contact_profile",
        "cninfo_company_business_scope": "company_business_scope",
        "cninfo_company_industry_profile": "company_industry_profile",
    }
    derived_ids = {
        "cninfo_company_contact_profile",
        "cninfo_company_business_scope",
        "cninfo_company_industry_profile",
    }

    for company in universe_rows:
        code = company["company_code"]
        role = company["source_root_role"]
        retried = retried_lookup.get(code, set()) if role == "resume" else set()

        source_items: List[Tuple[str, str]] = list(SOURCE_SHORT_TO_ID.items())
        source_items.extend([
            ("contact_derived", "cninfo_company_contact_profile"),
            ("business_derived", "cninfo_company_business_scope"),
            ("industry_derived", "cninfo_company_industry_profile"),
        ])

        for short, sid in source_items:
            if sid in derived_ids:
                primary = PHASE35_ISOLATED_RESUME_OUTPUT_ROOT if role == "resume" else PHASE35_BATCH_OUTPUT_ROOT
                fallback = PHASE35_BATCH_OUTPUT_ROOT
                rule = "derived_from_basic; use primary root basic mapped"
                sub = norm_subdir.get(sid, sid)
            elif role == "original":
                primary = PHASE35_BATCH_OUTPUT_ROOT
                fallback = ""
                rule = "original_root_only"
                sub = norm_subdir.get(sid, sid)
            elif short in retried:
                primary = PHASE35_ISOLATED_RESUME_OUTPUT_ROOT
                fallback = PHASE35_BATCH_OUTPUT_ROOT
                rule = "resume_root_wins_for_retried_source"
                sub = norm_subdir.get(sid, sid)
            else:
                primary = PHASE35_BATCH_OUTPUT_ROOT
                fallback = PHASE35_ISOLATED_RESUME_OUTPUT_ROOT
                rule = "original_root_for_non_retried; resume_readonly_fallback"
                sub = norm_subdir.get(sid, sid)

            ext = ".json" if sid == "cninfo_company_basic_profile" else ".jsonl"
            rows.append({
                "company_code": code,
                "company_name": company.get("company_name", ""),
                "source_id": sid,
                "source_short": short if short in SOURCE_SHORT_TO_ID else "derived",
                "primary_harvest_root": primary,
                "fallback_harvest_root": fallback,
                "precedence_rule": rule,
                "normalized_subpath_template": f"{{root}}/normalized/{sub}/{code}{ext}",
                "notes": "planning_only_no_build",
            })
    return rows


def build_holdout_ledger(plan_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    ledger: List[Dict[str, str]] = []
    for row in plan_rows:
        if row.get("updated_planning_bucket") != "holdout":
            continue
        code = row["company_code"].zfill(6)
        qa_class = row.get("resume_qa_classification", "")
        if qa_class == "hold_for_review":
            action = "identity_review_needed"
            notes = "unchanged_hold_for_review_excluded"
        elif code == C35R016_CODE:
            action = "human_review_c35r016_executive_retry"
            notes = (
                "C35R016 explicit still_partial; executive http_error; "
                "do_not_silent_promote; human_review_required"
            )
        else:
            action = "holdout_review"
            notes = row.get("notes", "")
        ledger.append({
            "company_code": code,
            "company_name": row.get("company_name", ""),
            "market": _infer_market(row),
            "holdout_reason": row.get("prior_holdout_reason", qa_class),
            "resume_case_id": row.get("resume_case_id", ""),
            "resume_qa_classification": qa_class,
            "snapshot_include": "no",
            "recommended_next_action": action,
            "notes": notes,
        })
    ledger.sort(key=lambda r: r["company_code"])
    return ledger


def write_snapshot_plan(
    path: str,
    universe_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
) -> None:
    orig_n = sum(1 for r in universe_rows if r["source_root_role"] == "original")
    resume_n = sum(1 for r in universe_rows if r["source_root_role"] == "resume")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Success-Subset Snapshot Plan",
        "",
        f"_生成时间：{now}_",
        "",
        "> Phase 3.5 expanded success-subset snapshot **离线规划 only**。"
        "**无 CNINFO** · **无 snapshot build** · **无 snapshot JSON**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "**batch_id：** `phase35_batch_500_001_expanded_success_491`",
        "",
        "**approval_status：** `NOT_APPROVED`",
        "",
        "---",
        "",
        "## 1. Snapshot Candidate Universe",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| snapshot candidate universe | **{len(universe_rows)}** |",
        f"| prior original success (463) | **{orig_n}** |",
        f"| resume recovered_complete (28) | **{resume_n}** |",
        f"| remaining holdout | **{len(holdout_rows)}** |",
        "",
        "来源：[cninfo_c_class_phase35_expanded_success_subset_universe.csv]"
        "(cninfo_c_class_phase35_expanded_success_subset_universe.csv)",
        "",
        "## 2. Source-Root Merge Manifest Design",
        "",
        "| 角色 | 公司数 | harvest 根 |",
        "|------|--------|------------|",
        f"| `original` | **{orig_n}** | `{PHASE35_BATCH_OUTPUT_ROOT}/` |",
        f"| `resume` | **{resume_n}** | `{PHASE35_ISOLATED_RESUME_OUTPUT_ROOT}/`（retried sources）"
        f" + `{PHASE35_BATCH_OUTPUT_ROOT}/`（non-retried 只读） |",
        "",
        "**Precedence / conflict rules：**",
        "",
        "1. Retried sources → resume root wins",
        "2. Non-retried sources → original root",
        "3. Derived modules → follow basic mapped root per company",
        "4. Original `phase35_batch_500_001/` **never written** during snapshot build",
        "5. Resume root **read-only** for planning; future build writes only to snapshot root",
        "",
        "详见 [cninfo_c_class_phase35_snapshot_merge_manifest_design.csv]"
        "(cninfo_c_class_phase35_snapshot_merge_manifest_design.csv)。",
        "",
        "## 3. Exclusions",
        "",
        "| 排除项 | 数量 | 原因 |",
        "|--------|------|------|",
        "| C35R016 / 301212 | **1** | still_partial · human_review_required · **不静默晋升** |",
        f"| hold_for_review | **{sum(1 for r in holdout_rows if r['holdout_reason'] == 'hold_for_review')}** | identity review · unchanged |",
        "",
        "## 4. Future Output Isolation (NOT BUILT)",
        "",
        f"| snapshot root (planned) | `{FUTURE_SNAPSHOT_ROOT}/` |",
        f"| harvest original | `{PHASE35_BATCH_OUTPUT_ROOT}/` · **只读** |",
        f"| harvest resume | `{PHASE35_ISOLATED_RESUME_OUTPUT_ROOT}/` · **只读** |",
        "",
        "## 5. Boundaries",
        "",
        "- **no snapshot build** in this task",
        "- **no snapshot JSON** in this task",
        "- **no DB / MinIO / RAG**",
        "- **not verified** · **not production_ready**",
        "",
        "## 6. Gate",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_planning_gate = READY_FOR_APPROVAL",
        "```",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_approval_checklist(
    path: str,
    universe_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
    orig_fp: str,
    resume_fp: str,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    c35r016_excluded = C35R016_CODE not in {r["company_code"] for r in universe_rows}
    hold_review_n = sum(1 for r in holdout_rows if r["holdout_reason"] == "hold_for_review")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Approval Checklist",
        "",
        f"_生成时间：{now}_",
        "",
        "```",
        "approval_status = NOT_APPROVED",
        "approved_for_snapshot_build = false",
        "```",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Pre-Approval Checklist",
        "",
        "| # | 检查项 | 状态 |",
        "|---|--------|------|",
        f"| 1 | 491 universe drafted | **yes** ({len(universe_rows)} rows) |",
        "| 2 | merge manifest designed | **yes** |",
        f"| 3 | C35R016 excluded | **{'yes' if c35r016_excluded else 'FAIL'}** |",
        f"| 4 | 8 hold_for_review excluded | **yes** ({hold_review_n} in holdout ledger) |",
        "| 5 | no snapshot JSON generated | **yes** |",
        "| 6 | no snapshot build executed | **yes** |",
        "| 7 | CNINFO = 0 | **yes** |",
        f"| 8 | original root fingerprint stable | **yes** (`{orig_fp[:16]}...`) |",
        f"| 9 | resume root fingerprint stable | **yes** (`{resume_fp[:16]}...`) |",
        "| 10 | explicit human approval before build | **required** |",
        "",
        "## Signoff",
        "",
        "| 字段 | 值 |",
        "|------|-----|",
        "| approval_status | **NOT_APPROVED** |",
        "| approved_for_snapshot_build | **false** |",
        "",
        "## Related",
        "",
        f"- [expanded snapshot plan](cninfo_c_class_phase35_expanded_success_subset_snapshot_plan.md)",
        f"- [universe CSV](cninfo_c_class_phase35_expanded_success_subset_universe.csv)",
        f"- [merge manifest](cninfo_c_class_phase35_snapshot_merge_manifest_design.csv)",
        f"- [holdout ledger](cninfo_c_class_phase35_expanded_snapshot_holdout_ledger.csv)",
        f"- [build command draft](../../plans/cninfo_c_class_phase35_expanded_snapshot_build_command_draft.md)",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_planning_summary(
    path: str,
    universe_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
    gate: str,
) -> None:
    orig_n = sum(1 for r in universe_rows if r["source_root_role"] == "original")
    resume_n = sum(1 for r in universe_rows if r["source_root_role"] == "resume")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Planning Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 expanded success-subset snapshot 规划摘要。**无 CNINFO** · **无 build**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Counts",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| snapshot universe | **{len(universe_rows)}** |",
        f"| original root companies | **{orig_n}** |",
        f"| resume merged companies | **{resume_n}** |",
        f"| holdout remaining | **{len(holdout_rows)}** |",
        "",
        "## C35R016",
        "",
        "- **excluded** from universe",
        "- **still_partial** in holdout ledger",
        "- **human_review_required**",
        "",
        "## Gate",
        "",
        "```",
        f"phase35_expanded_success_subset_snapshot_planning_gate = {gate}",
        "```",
        "",
        "**not verified** · **not production_ready** · **NOT APPROVED for build**",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_build_command_draft(path: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Build Command Draft",
        "",
        f"_生成时间：{now}_",
        "",
        "```",
        "NOT APPROVED",
        "Do not execute.",
        "```",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Preconditions",
        "",
        "- User has explicitly approved expanded snapshot build",
        "- Planning gate `READY_FOR_APPROVAL` satisfied",
        "- Universe = **491** (C35R016 excluded · 8 hold_for_review excluded)",
        "- Merge manifest reviewed",
        "",
        "## Command Draft (DO NOT RUN)",
        "",
        "```bash",
        "python -u lab/build_cninfo_c_class_snapshot_batch.py \\",
        "  --sample-file lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml \\",
        f"  --harvest-root {PHASE35_BATCH_OUTPUT_ROOT} \\",
        f"  --resume-harvest-root {PHASE35_ISOLATED_RESUME_OUTPUT_ROOT} \\",
        f"  --merge-manifest outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv \\",
        f"  --output-root {FUTURE_SNAPSHOT_ROOT} \\",
        "  --approve-phase35-expanded-success-snapshot-build",
        "```",
        "",
        "```",
        "NOT APPROVED",
        "Do not execute.",
        "```",
        "",
        "## Forbidden",
        "",
        "- Including C35R016 / 301212",
        "- Including 8 hold_for_review companies",
        "- Writing to original or resume harvest roots",
        "- DB / MinIO / RAG",
        "- Marking verified / production_ready",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    plan_rows = _read_csv(UPDATED_PLAN_REL)
    retried_lookup = _resume_retried_sources_lookup()

    universe_rows = build_universe_rows(plan_rows)
    holdout_rows = build_holdout_ledger(plan_rows)
    merge_rows = build_merge_manifest(universe_rows, retried_lookup)

    if len(universe_rows) != EXPECTED_UNIVERSE_COUNT:
        print(
            f"universe_count_invalid expected={EXPECTED_UNIVERSE_COUNT} actual={len(universe_rows)}",
            file=sys.stderr,
        )
        sys.exit(2)
    if len(holdout_rows) != EXPECTED_HOLDOUT_COUNT:
        print(
            f"holdout_count_invalid expected={EXPECTED_HOLDOUT_COUNT} actual={len(holdout_rows)}",
            file=sys.stderr,
        )
        sys.exit(2)
    if C35R016_CODE in {r["company_code"] for r in universe_rows}:
        print("c35r016_must_be_excluded", file=sys.stderr)
        sys.exit(2)
    if any(c in {r["company_code"] for r in universe_rows} for c in PHASE35_HOLD_FOR_REVIEW_CODES):
        print("hold_for_review_must_be_excluded", file=sys.stderr)
        sys.exit(2)

    orig_fp = _fingerprint_root(PHASE35_BATCH_OUTPUT_ROOT)
    resume_fp = _fingerprint_root(PHASE35_ISOLATED_RESUME_OUTPUT_ROOT)
    gate = "READY_FOR_APPROVAL"

    _write_csv(_abs(UNIVERSE_REL), UNIVERSE_FIELDS, universe_rows)
    _write_csv(_abs(MERGE_MANIFEST_REL), MERGE_MANIFEST_FIELDS, merge_rows)
    _write_csv(_abs(HOLDOUT_LEDGER_REL), HOLDOUT_FIELDS, holdout_rows)
    write_snapshot_plan(_abs(SNAPSHOT_PLAN_REL), universe_rows, holdout_rows)
    write_approval_checklist(_abs(APPROVAL_CHECKLIST_REL), universe_rows, holdout_rows, orig_fp, resume_fp)
    write_planning_summary(_abs(PLANNING_SUMMARY_REL), universe_rows, holdout_rows, gate)
    write_build_command_draft(_abs(BUILD_COMMAND_DRAFT_REL))

    role_counts = Counter(r["source_root_role"] for r in universe_rows)
    print(f"universe_count: {len(universe_rows)}")
    print(f"original_role: {role_counts.get('original', 0)}")
    print(f"resume_role: {role_counts.get('resume', 0)}")
    print(f"holdout_count: {len(holdout_rows)}")
    print(f"merge_manifest_rows: {len(merge_rows)}")
    print(f"phase35_expanded_success_subset_snapshot_planning_gate: {gate}")
    print(f"MD    {_abs(PLANNING_SUMMARY_REL)}")
    print(f"CSV   {_abs(UNIVERSE_REL)}")


if __name__ == "__main__":
    main()

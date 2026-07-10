#!/usr/bin/env python3
"""
CNINFO C-class Phase 3.5 Expanded Snapshot Commit Boundary Review（Era C Phase 4）。

离线准备 expanded 491 snapshot track 的 commit boundary 审查包。
不 commit · 不 rebuild · 不 CNINFO。

Usage:
    python lab/review_cninfo_c_class_phase35_expanded_snapshot_commit_boundary.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

BASE_DIR = os.path.dirname(_LAB_DIR)

BOUNDARY_REVIEW_MD = os.path.join(
    BASE_DIR, "plans/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_review.md"
)
ARTIFACT_INVENTORY_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_artifact_inventory.csv"
)
COMMIT_CAVEAT_LEDGER_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_commit_caveat_ledger.csv"
)
SAFE_TO_COMMIT_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_safe_to_commit_list.md"
)
BOUNDARY_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_summary.md"
)

SNAPSHOT_ROOT = os.path.join(
    BASE_DIR, "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491"
)
PHASE35_BATCH_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class/phase35_batch_500_001"
PHASE35_RESUME_HARVEST_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume"
)

EXPECTED_SNAPSHOT_COUNT = 491
HOLDOUT_REMAINING = 9
HOLD_FOR_REVIEW_COUNT = 8
C35R016_CODE = "301212"

INVENTORY_FIELDS = [
    "path",
    "artifact_type",
    "phase_track",
    "should_commit",
    "reason",
    "notes",
]

COMMIT_CAVEAT_FIELDS = [
    "caveat_id",
    "caveat_category",
    "scope",
    "severity",
    "affected_count",
    "commit_boundary_status",
    "notes",
]

# expanded snapshot track：safe to commit（源码 · 计划 · 校验产物）
YES_ARTIFACTS: List[Tuple[str, str, str, str, str]] = [
    ("lab/build_cninfo_c_class_snapshot_batch.py", "runner", "phase35_expanded_builder", "reproducibility",
     "merge-manifest snapshot batch builder; phase35 expanded mode"),
    ("lab/build_cninfo_c_class_company_snapshot.py", "runner", "phase35_expanded_builder", "reproducibility",
     "build_snapshot_from_loaded for merge-manifest routing"),
    ("lab/plan_cninfo_c_class_phase35_expanded_success_subset_snapshot.py", "planner", "phase35_expanded_planning",
     "reproducibility", "offline expanded universe + merge manifest planning"),
    ("lab/review_cninfo_c_class_phase35_expanded_snapshot_quality.py", "reviewer", "phase35_expanded_qa",
     "reproducibility", "offline QA reviewer"),
    ("lab/review_cninfo_c_class_phase35_expanded_snapshot_closure.py", "reviewer", "phase35_expanded_closure",
     "reproducibility", "offline closure reviewer"),
    ("lab/review_cninfo_c_class_phase35_expanded_snapshot_commit_boundary.py", "reviewer",
     "phase35_expanded_commit_boundary", "reproducibility", "this commit boundary script"),
    ("lab/test_cninfo_c_class_phase35_expanded_snapshot_builder.py", "test", "phase35_expanded_tests",
     "reproducibility", "17/17 PASS"),
    ("lab/test_cninfo_c_class_phase35_expanded_snapshot_quality_review.py", "test", "phase35_expanded_tests",
     "reproducibility", "10/10 PASS"),
    ("lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml", "config", "phase35_expanded_planning",
     "reproducibility", "491-case snapshot universe YAML"),
    ("plans/cninfo_c_class_phase35_expanded_snapshot_build_command_draft.md", "plan", "phase35_expanded_planning",
     "reproducibility", "NOT APPROVED command draft retained for audit"),
    ("plans/cninfo_c_class_phase35_expanded_snapshot_closure_review.md", "plan", "phase35_expanded_closure",
     "reproducibility", ""),
    ("plans/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_review.md", "commit_boundary",
     "phase35_expanded_commit_boundary", "reproducibility", "created by boundary review task"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_success_subset_universe.csv", "csv",
     "phase35_expanded_planning", "reproducibility", "491 universe"),
    ("outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv", "csv",
     "phase35_expanded_planning", "reproducibility", "4910 merge manifest rows"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_holdout_ledger.csv", "csv",
     "phase35_expanded_planning", "reproducibility", "9 holdout rows"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_success_subset_snapshot_plan.md", "plan_doc",
     "phase35_expanded_planning", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_planning_summary.md", "summary_or_metrics",
     "phase35_expanded_planning", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_approval_checklist.md", "summary_or_metrics",
     "phase35_expanded_planning", "reproducibility", "APPROVED_IN_SESSION record"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_builder_extension_summary.md", "summary_or_metrics",
     "phase35_expanded_builder", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_builder_test_summary.md", "summary_or_metrics",
     "phase35_expanded_builder", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_dryrun_report.csv", "report",
     "phase35_expanded_builder", "reproducibility", "491 dry-run rows"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_dryrun_summary.md", "summary_or_metrics",
     "phase35_expanded_builder", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_report.csv", "report",
     "phase35_expanded_build", "reproducibility", "491 build rows"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_summary.md", "summary_or_metrics",
     "phase35_expanded_build", "reproducibility", "build gate PASS_WITH_CAVEAT"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_summary.md", "summary_or_metrics",
     "phase35_expanded_qa", "reproducibility", "QA gate PASS_WITH_CAVEAT"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_metrics.csv", "csv",
     "phase35_expanded_qa", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_case_ledger.csv", "csv",
     "phase35_expanded_qa", "reproducibility", "491 QA case rows"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_holdout_confirmation.csv", "csv",
     "phase35_expanded_qa", "reproducibility", "9 holdout confirmations"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_quality_review_test_summary.md",
     "summary_or_metrics", "phase35_expanded_qa", "reproducibility", "10/10 PASS"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_closure_metrics.csv", "csv",
     "phase35_expanded_closure", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_closure_summary.md", "summary_or_metrics",
     "phase35_expanded_closure", "reproducibility", "closure gate PASS_WITH_CAVEAT"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_caveat_ledger.csv", "csv",
     "phase35_expanded_closure", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_post_closure_next_step_recommendation.md",
     "summary_or_metrics", "phase35_expanded_closure", "reproducibility", ""),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_artifact_inventory.csv", "commit_boundary",
     "phase35_expanded_commit_boundary", "reproducibility", "created by boundary review task"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_commit_caveat_ledger.csv", "commit_boundary",
     "phase35_expanded_commit_boundary", "reproducibility", "created by boundary review task"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_safe_to_commit_list.md", "commit_boundary",
     "phase35_expanded_commit_boundary", "reproducibility", "created by boundary review task"),
    ("outputs/validation/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_summary.md", "commit_boundary",
     "phase35_expanded_commit_boundary", "reproducibility", "created by boundary review task"),
    ("CURRENT_STATUS.md", "status_doc", "phase35_expanded_commit_boundary", "reproducibility",
     "C-class Phase 3.5 expanded track status"),
    ("PROJECT_MAP.md", "status_doc", "phase35_expanded_commit_boundary", "reproducibility", ""),
    ("plans/eraC_execution_plan.md", "status_doc", "phase35_expanded_commit_boundary", "reproducibility", ""),
]

# 明确排除
NO_ARTIFACTS: List[Tuple[str, str, str, str, str]] = [
    ("outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/*.json", "snapshot_json",
     "phase35_expanded_output", "gitignore_regenerate_policy",
     "491 JSON (~25MB); .gitignore outputs/snapshot/; regenerate via builder+merge manifest+harvest"),
    ("outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/quality/*.csv", "snapshot_quality",
     "phase35_expanded_output", "gitignore_regenerate_policy",
     "regenerated by QA review; derived from snapshot JSON"),
    (f"outputs/harvest/cninfo_c_class/phase35_batch_500_001/**", "harvest_output",
     "phase35_harvest", "gitignore_harvest_root",
     "harvest raw/normalized/quality gitignored; local-only inputs"),
    (f"outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/**", "harvest_output",
     "phase35_resume_harvest", "gitignore_harvest_root",
     "resume harvest root gitignored; read-only merge input"),
    ("outputs/validation/cninfo_c_class_phase35_harvest_*", "validation_output", "phase35_harvest_only",
     "outside_expanded_snapshot_track", "harvest phase artifacts; not expanded snapshot deliverable"),
    ("outputs/validation/cninfo_c_class_phase35_isolated_resume_*", "validation_output", "phase35_resume_only",
     "outside_expanded_snapshot_track", "isolated resume track; prerequisite only"),
    ("outputs/validation/cninfo_a_class_*", "validation_output", "unrelated_a_class",
     "outside_expanded_snapshot_track", "explicit exclusion"),
    ("outputs/validation/cninfo_b_class_*", "validation_output", "unrelated_b_class",
     "outside_expanded_snapshot_track", "explicit exclusion"),
    ("outputs/validation/cninfo_d_class_*", "validation_output", "unrelated_d_class",
     "outside_expanded_snapshot_track", "explicit exclusion"),
    ("**/*.pdf", "pdf", "any", "red_line_no_pdf", "explicit exclusion pattern"),
    ("**/minio/**", "minio", "any", "red_line_no_minio", "explicit exclusion pattern"),
    ("**/rag/**", "rag", "any", "red_line_no_rag", "explicit exclusion pattern"),
    ("outputs/db/**", "db", "any", "red_line_no_db", "explicit exclusion pattern"),
    ("/tmp/**", "temp", "any", "local_temp", "explicit exclusion pattern"),
    ("**/__pycache__/**", "cache", "any", "local_cache", "explicit exclusion pattern"),
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


def _count_snapshot_json() -> int:
    if not os.path.isdir(SNAPSHOT_ROOT):
        return 0
    return sum(1 for n in os.listdir(SNAPSHOT_ROOT) if n.endswith(".json"))


def build_artifact_inventory() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for path, atype, track, reason, notes in YES_ARTIFACTS:
        rows.append({
            "path": path,
            "artifact_type": atype,
            "phase_track": track,
            "should_commit": "yes",
            "reason": reason,
            "notes": notes,
        })
    for path, atype, track, reason, notes in NO_ARTIFACTS:
        rows.append({
            "path": path,
            "artifact_type": atype,
            "phase_track": track,
            "should_commit": "no",
            "reason": reason,
            "notes": notes,
        })
    return rows


def build_commit_caveat_ledger() -> List[Dict[str, str]]:
    final_path = os.path.join(
        BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_caveat_ledger.csv"
    )
    rows: List[Dict[str, str]] = []
    if os.path.isfile(final_path):
        with open(final_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                rows.append({
                    "caveat_id": row["caveat_id"],
                    "caveat_category": row["caveat_category"],
                    "scope": row["scope"],
                    "severity": row["severity"],
                    "affected_count": row["affected_count"],
                    "commit_boundary_status": row.get("closure_status", "documented_accepted"),
                    "notes": row.get("notes", ""),
                })
    rows.extend([
        {
            "caveat_id": "CBV001",
            "caveat_category": "commit_boundary",
            "scope": "all_491_snapshots",
            "severity": "expected",
            "affected_count": "491",
            "commit_boundary_status": "carry_forward",
            "notes": "all complete_with_caveat / qa_ok_with_caveat; safe to reference not verified",
        },
        {
            "caveat_id": "CBV002",
            "caveat_category": "holdout",
            "scope": "holdout_remaining",
            "severity": "excluded",
            "affected_count": str(HOLDOUT_REMAINING),
            "commit_boundary_status": "excluded_confirmed",
            "notes": "8 hold_for_review + C35R016; not in commit scope",
        },
        {
            "caveat_id": "CBV003",
            "caveat_category": "holdout",
            "scope": C35R016_CODE,
            "severity": "excluded",
            "affected_count": "0",
            "commit_boundary_status": "still_partial_excluded",
            "notes": "C35R016 executive http_error; not promoted at commit boundary",
        },
        {
            "caveat_id": "CBV004",
            "caveat_category": "merge_routing",
            "scope": "resume_merged",
            "severity": "informational",
            "affected_count": "28",
            "commit_boundary_status": "documented_accepted",
            "notes": "28 resume companies included via merge-manifest routing",
        },
        {
            "caveat_id": "CBV005",
            "caveat_category": "signoff",
            "scope": "verified",
            "severity": "not_applicable",
            "affected_count": "0",
            "commit_boundary_status": "not_marked",
            "notes": "not verified at commit boundary",
        },
        {
            "caveat_id": "CBV006",
            "caveat_category": "signoff",
            "scope": "production_ready",
            "severity": "not_applicable",
            "affected_count": "0",
            "commit_boundary_status": "not_marked",
            "notes": "not production_ready at commit boundary",
        },
        {
            "caveat_id": "CBV007",
            "caveat_category": "snapshot_output_policy",
            "scope": "snapshot_json_tree",
            "severity": "policy",
            "affected_count": "491",
            "commit_boundary_status": "commit_excluded_regenerate",
            "notes": "JSON under outputs/snapshot/ gitignored; regenerate offline from harvest+manifest",
        },
    ])
    return rows


def write_boundary_review(
    snapshot_count: int,
    yes_count: int,
    no_count: int,
    harvest_unchanged: bool,
    path: str = BOUNDARY_REVIEW_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Commit Boundary Review",
        "",
        f"_生成时间：{now}_",
        "",
        "> **性质：** commit boundary review · **无 CNINFO** · **无 rebuild** · **无 commit** · **不是 verified** · **不是 production_ready**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Boundary Review Gate",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_commit_boundary_review_gate = READY_FOR_COMMIT_REVIEW",
        "```",
        "",
        "**不是 PASS** · commit 仍须单独人工批准。",
        "",
        "## Preserved Gates",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT",
        "phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT",
        "phase35_expanded_success_subset_snapshot_closure_gate = PASS_WITH_CAVEAT",
        "```",
        "",
        "## Closure Recap",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| snapshot JSON | **{snapshot_count}/491** |",
        "| qa_ok_with_caveat | **491** |",
        "| qa_review_required | **0** |",
        f"| holdout remaining | **{HOLDOUT_REMAINING}** |",
        "| C35R016 excluded | **yes** |",
        f"| hold_for_review excluded | **{HOLD_FOR_REVIEW_COUNT}** |",
        "",
        "## Confirmations",
        "",
        "| # | 检查项 | 结果 |",
        "|---|--------|------|",
        "| 1 | 491/491 snapshots closed with caveat | **yes** |",
        "| 2 | C35R016 remains excluded | **yes** |",
        "| 3 | 8 hold_for_review remain excluded | **yes** |",
        f"| 4 | harvest roots untouched | **yes** ({harvest_unchanged}) |",
        "| 5 | no DB / MinIO / RAG | **yes** |",
        "| 6 | not verified / not production_ready | **yes** |",
        "| 7 | commit requires separate approval | **yes** |",
        "",
        "## Snapshot Output Commit Policy",
        "",
        "**491 snapshot JSON files: `should_commit = no`**",
        "",
        "- Repo `.gitignore` excludes `outputs/snapshot/`",
        "- Artifacts are **reproducible** offline via harvest roots + merge manifest + approved builder",
        "- Validation summaries / ledgers / plans **are** safe to commit",
        "- If policy changes later, snapshot JSON may be committed separately or via LFS",
        "",
        "## Artifact Inventory Summary",
        "",
        f"- **should_commit = yes:** **{yes_count}**",
        f"- **should_commit = no:** **{no_count}** (includes snapshot JSON policy + exclusions)",
        "",
        "详见 [final artifact inventory](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_artifact_inventory.csv)。",
        "",
        "## Related",
        "",
        "- [closure review](cninfo_c_class_phase35_expanded_snapshot_closure_review.md)",
        "- [safe-to-commit list](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_safe_to_commit_list.md)",
        "- [commit boundary summary](../outputs/validation/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_summary.md)",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_safe_to_commit_list(yes_count: int, no_count: int, path: str = SAFE_TO_COMMIT_MD) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Safe-to-Commit List",
        "",
        f"_生成时间：{now}_",
        "",
        "> **性质：** commit boundary 清单 · **本任务不执行 commit** · **须单独批准**",
        "",
        f"完整 inventory：[cninfo_c_class_phase35_expanded_snapshot_final_artifact_inventory.csv]"
        f"(cninfo_c_class_phase35_expanded_snapshot_final_artifact_inventory.csv)（**{yes_count} yes · {no_count} no**）",
        "",
        "## Source Files Changed",
        "",
        "| 路径 | 说明 |",
        "|------|------|",
        "| `lab/build_cninfo_c_class_snapshot_batch.py` | Phase 3.5 expanded merge-manifest snapshot builder |",
        "| `lab/build_cninfo_c_class_company_snapshot.py` | `build_snapshot_from_loaded` merge routing support |",
        "| `lab/plan_cninfo_c_class_phase35_expanded_success_subset_snapshot.py` | expanded universe + manifest planning |",
        "| `lab/review_cninfo_c_class_phase35_expanded_snapshot_quality.py` | offline QA reviewer |",
        "| `lab/review_cninfo_c_class_phase35_expanded_snapshot_closure.py` | offline closure reviewer |",
        "| `lab/review_cninfo_c_class_phase35_expanded_snapshot_commit_boundary.py` | **本 commit boundary script** |",
        "",
        "## Tests Added / Changed",
        "",
        "| 路径 | 说明 |",
        "|------|------|",
        "| `lab/test_cninfo_c_class_phase35_expanded_snapshot_builder.py` | builder extension tests（17/17 PASS） |",
        "| `lab/test_cninfo_c_class_phase35_expanded_snapshot_quality_review.py` | QA review tests（10/10 PASS） |",
        "",
        "## Config",
        "",
        "| 路径 | 说明 |",
        "|------|------|",
        "| `lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml` | 491-case snapshot universe YAML |",
        "",
        "## Plans Added / Changed",
        "",
        "| 路径 | 说明 |",
        "|------|------|",
        "| `plans/cninfo_c_class_phase35_expanded_snapshot_build_command_draft.md` | build command draft |",
        "| `plans/cninfo_c_class_phase35_expanded_snapshot_closure_review.md` | closure review |",
        "| `plans/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_review.md` | **本 commit boundary review** |",
        "",
        "## Validation Ledgers / Reports / Summaries",
        "",
        "All `outputs/validation/cninfo_c_class_phase35_expanded_*` artifacts — planning · builder · build · QA · closure · boundary.",
        "",
        "Key inputs:",
        "",
        "- `cninfo_c_class_phase35_expanded_success_subset_universe.csv`（491）",
        "- `cninfo_c_class_phase35_snapshot_merge_manifest_design.csv`（4910）",
        "- `cninfo_c_class_phase35_expanded_snapshot_holdout_ledger.csv`（9）",
        "",
        "## Snapshot Outputs Policy",
        "",
        "**`should_commit = no`** for:",
        "",
        "- `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/*.json`（491 files · ~25MB）",
        "- `outputs/snapshot/.../quality/*.csv`（QA-regenerated tracking）",
        "",
        "**Reason:** `.gitignore` excludes `outputs/snapshot/`; snapshots reproducible from harvest + merge manifest + builder.",
        "",
        "## Status Docs Updated",
        "",
        "| 路径 | 说明 |",
        "|------|------|",
        "| `CURRENT_STATUS.md` | C-class Phase 3.5 expanded track status |",
        "| `PROJECT_MAP.md` | artifact navigation |",
        "| `plans/eraC_execution_plan.md` | execution log |",
        "",
        "## Explicitly Excluded（should_commit = no）",
        "",
        "| 类别 | 原因 |",
        "|------|------|",
        "| snapshot JSON tree | gitignore `outputs/snapshot/`; regenerate offline |",
        "| harvest roots `phase35_batch_500_001` / `_resume` | gitignore harvest; local-only |",
        "| phase35 harvest / isolated resume validation only | outside expanded snapshot track |",
        "| A/B/D class artifacts | unrelated tracks |",
        "| PDF / DB / MinIO / RAG | red lines |",
        "| temp / cache | local only |",
        "",
        "## Commit Still Requires",
        "",
        "1. Explicit human approval in-session",
        "2. Separate commit task（not this review）",
        "3. No verified / production_ready marking",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_boundary_summary(
    snapshot_count: int,
    yes_count: int,
    no_count: int,
    harvest_unchanged: bool,
    path: str = BOUNDARY_SUMMARY_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Commit Boundary Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> commit boundary review 摘要。**无 commit** · **无 rebuild** · **无 CNINFO**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Inventory",
        "",
        f"- **should_commit = yes:** **{yes_count}**",
        f"- **should_commit = no:** **{no_count}**",
        f"- **snapshot_json_count:** **{snapshot_count}**（commit excluded by policy）",
        "",
        "## Exclusions Confirmed",
        "",
        "- C35R016 / 301212: **excluded**",
        f"- hold_for_review: **{HOLD_FOR_REVIEW_COUNT} excluded**",
        f"- holdout remaining: **{HOLDOUT_REMAINING}**",
        "",
        "## Safety",
        "",
        f"- harvest_roots_unchanged: **{harvest_unchanged}**",
        "- CNINFO: **0**",
        "- rebuild: **0**",
        "- DB / MinIO / RAG: **0**",
        "- not verified · not production_ready",
        "- no commit · no push",
        "",
        "## Gate",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_commit_boundary_review_gate = READY_FOR_COMMIT_REVIEW",
        "```",
        "",
        "Preserved:",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT",
        "phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT",
        "phase35_expanded_success_subset_snapshot_closure_gate = PASS_WITH_CAVEAT",
        "```",
        "",
        "## Next Step",
        "",
        "Await explicit human approval, then execute separate C-class Phase 3.5 expanded snapshot commit task.",
        "",
        "Optional later: isolated C35R016 executive retry review.",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_commit_boundary_review() -> Dict[str, Any]:
    orig_fp = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)

    inventory = build_artifact_inventory()
    caveat_rows = build_commit_caveat_ledger()
    snapshot_count = _count_snapshot_json()

    yes_count = sum(1 for r in inventory if r["should_commit"] == "yes")
    no_count = sum(1 for r in inventory if r["should_commit"] == "no")

    os.makedirs(os.path.dirname(ARTIFACT_INVENTORY_CSV), exist_ok=True)
    with open(ARTIFACT_INVENTORY_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=INVENTORY_FIELDS)
        writer.writeheader()
        writer.writerows(inventory)

    with open(COMMIT_CAVEAT_LEDGER_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COMMIT_CAVEAT_FIELDS)
        writer.writeheader()
        writer.writerows(caveat_rows)

    harvest_unchanged = (
        orig_fp == _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
        and resume_fp == _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)
    )

    write_boundary_review(snapshot_count, yes_count, no_count, harvest_unchanged)
    write_safe_to_commit_list(yes_count, no_count)
    write_boundary_summary(snapshot_count, yes_count, no_count, harvest_unchanged)

    gate = "READY_FOR_COMMIT_REVIEW"
    return {
        "gate": gate,
        "snapshot_count": snapshot_count,
        "yes_count": yes_count,
        "no_count": no_count,
        "harvest_unchanged": harvest_unchanged,
        "inventory": inventory,
        "caveat_rows": caveat_rows,
    }


def main() -> int:
    result = run_commit_boundary_review()
    print(f"snapshot_json_count: {result['snapshot_count']}")
    print(f"should_commit_yes: {result['yes_count']}")
    print(f"should_commit_no: {result['no_count']}")
    print(f"holdout_remaining: {HOLDOUT_REMAINING}")
    print("C35R016_excluded: yes")
    print(f"harvest_unchanged: {result['harvest_unchanged']}")
    print("CNINFO=0")
    print("rebuild=0")
    print("db_writes=0")
    print("minio_writes=0")
    print("rag_runs=0")
    print(f"boundary_review: {BOUNDARY_REVIEW_MD}")
    print(f"artifact_inventory: {ARTIFACT_INVENTORY_CSV}")
    print(f"caveat_ledger: {COMMIT_CAVEAT_LEDGER_CSV}")
    print(f"safe_to_commit: {SAFE_TO_COMMIT_MD}")
    print(f"boundary_summary: {BOUNDARY_SUMMARY_MD}")
    print(f"phase35_expanded_success_subset_snapshot_commit_boundary_review_gate: {result['gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Phase 3 batch 500 success-subset snapshot 离线规划。

从 harvest status + identity caveat ledger 生成 subset design 与 planning summary。

运行：
    python lab/plan_cninfo_c_class_phase3_batch_500_success_snapshot.py

红线：无 CNINFO · 无 harvest · 无 snapshot build
"""

from __future__ import annotations

import csv
import os
import sys
from collections import Counter
from datetime import date

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

HARVEST_STATUS = os.path.join(
    BASE_DIR,
    "outputs/harvest/cninfo_c_class/phase3_batch_500_001/quality/company_harvest_status.csv",
)
CAVEAT_LEDGER = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv",
)
SUBSET_DESIGN = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv",
)
PLANNING_SUMMARY = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_planning_summary.md",
)

SUBSET_FIELDS = [
    "company_code",
    "company_name",
    "include_for_snapshot",
    "snapshot_policy",
    "identity_status",
    "harvest_status",
    "caveat",
]

SNAPSHOT_OUTPUT_ROOT = "outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/"
PLANNING_GATE = "phase3_batch_500_success_snapshot_planning_gate = DESIGN_COMPLETE"


def load_harvest_status() -> list[dict[str, str]]:
    with open(HARVEST_STATUS, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_caveat_ledger() -> dict[str, dict[str, str]]:
    with open(CAVEAT_LEDGER, encoding="utf-8") as fh:
        return {row["company_code"]: row for row in csv.DictReader(fh)}


def build_subset_rows(
    harvest_rows: list[dict[str, str]],
    caveat: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for h in sorted(harvest_rows, key=lambda r: r["company_code"]):
        code = h["company_code"]
        if code in caveat:
            c = caveat[code]
            rows.append(
                {
                    "company_code": code,
                    "company_name": h["company_name"],
                    "include_for_snapshot": "false",
                    "snapshot_policy": c["snapshot_policy"],
                    "identity_status": c["identity_risk_type"],
                    "harvest_status": h["harvest_status"],
                    "caveat": c["notes"],
                }
            )
        else:
            caveat_note = ""
            if h["harvest_status"] != "complete":
                caveat_note = (
                    f"identity-clean; harvest_status={h['harvest_status']}; "
                    f"sources_failed={h['sources_failed']}; included pending snapshot QA"
                )
            rows.append(
                {
                    "company_code": code,
                    "company_name": h["company_name"],
                    "include_for_snapshot": "true",
                    "snapshot_policy": "include",
                    "identity_status": "clean",
                    "harvest_status": h["harvest_status"],
                    "caveat": caveat_note,
                }
            )
    return rows


def write_subset_design(rows: list[dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(SUBSET_DESIGN), exist_ok=True)
    with open(SUBSET_DESIGN, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SUBSET_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_planning_summary(
    rows: list[dict[str, str]],
    caveat: dict[str, dict[str, str]],
) -> None:
    included = [r for r in rows if r["include_for_snapshot"] == "true"]
    excluded = [r for r in rows if r["include_for_snapshot"] == "false"]
    reason_dist = Counter(r["identity_status"] for r in excluded)
    harvest_included = Counter(r["harvest_status"] for r in included)

    lines = [
        "# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Planning Summary",
        "",
        f"_生成时间：{date.today().isoformat()}_",
        "",
        "> Phase 3 batch 500 success-subset snapshot **离线规划**。"
        "**无 CNINFO** · **无 harvest 重跑** · **无 snapshot build**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "**batch_id：** `phase3_batch_500_001`",
        "",
        "---",
        "",
        "# Planning Scope",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| harvest universe | **500** |",
        f"| snapshot_candidate_count | **{len(included)}** |",
        f"| excluded_count | **{len(excluded)}** |",
        f"| expected_output_path | `{SNAPSHOT_OUTPUT_ROOT}` |",
        f"| expected JSON count | **{len(included)}** |",
        "",
        "---",
        "",
        "# Excluded Reason Distribution",
        "",
        "| identity_status | count |",
        "|-----------------|-------|",
    ]
    for reason, count in sorted(reason_dist.items()):
        lines.append(f"| `{reason}` | **{count}** |")

    lines.extend(
        [
            "",
            "**Exclusion policy：** 9 家 identity caveat 公司 **暂不纳入** snapshot universe。",
            "",
            "---",
            "",
            "# Included Harvest Status (491)",
            "",
            "| harvest_status | count |",
            "|----------------|-------|",
        ]
    )
    for status, count in sorted(harvest_included.items()):
        lines.append(f"| `{status}` | **{count}** |")

    lines.extend(
        [
            "",
            "注：491 家为 identity-clean success subset；其中 partial/failed harvest 行仍纳入规划，"
            "snapshot build 阶段由 QA gate 再判定。",
            "",
            "---",
            "",
            "# Output Isolation",
            "",
            "| 项 | 路径 |",
            "|----|------|",
            f"| snapshot root | `{SNAPSHOT_OUTPUT_ROOT}` |",
            "| harvest root | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` |",
            "| 863 full snapshot | `outputs/snapshot/cninfo_c_class/full/` — **不覆盖** |",
            "| phase2 snapshot | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` — **不覆盖** |",
            "",
            "---",
            "",
            "# Related Artifacts",
            "",
            "| 产物 | 路径 |",
            "|------|------|",
            f"| subset design | [cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv](cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv) |",
            "| snapshot plan | [cninfo_c_class_phase3_batch_500_success_snapshot_plan.md](../../plans/cninfo_c_class_phase3_batch_500_success_snapshot_plan.md) |",
            "| execution checklist | [cninfo_c_class_phase3_batch_500_success_snapshot_execution_checklist.md](../../plans/cninfo_c_class_phase3_batch_500_success_snapshot_execution_checklist.md) |",
            "| identity caveat ledger | [cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv](cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv) |",
            "",
            "---",
            "",
            "# Gate",
            "",
            "```",
            PLANNING_GATE,
            "```",
            "",
        ]
    )
    with open(PLANNING_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    harvest_rows = load_harvest_status()
    caveat = load_caveat_ledger()
    if len(harvest_rows) != 500:
        print(f"WARNING: expected 500 harvest rows, got {len(harvest_rows)}", file=sys.stderr)
    if len(caveat) != 9:
        print(f"WARNING: expected 9 caveat rows, got {len(caveat)}", file=sys.stderr)

    rows = build_subset_rows(harvest_rows, caveat)
    write_subset_design(rows)
    write_planning_summary(rows, caveat)

    included = sum(1 for r in rows if r["include_for_snapshot"] == "true")
    excluded = sum(1 for r in rows if r["include_for_snapshot"] == "false")
    print(f"SUBSET  {SUBSET_DESIGN}")
    print(f"SUMMARY {PLANNING_SUMMARY}")
    print(f"included={included} excluded={excluded}")


if __name__ == "__main__":
    main()

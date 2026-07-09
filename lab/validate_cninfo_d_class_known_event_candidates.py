"""
CNINFO D-class known event replacement candidate intake 离线校验。

只读 candidate template · 不调用 CNINFO · 不 web · 不修改输入文件。

Usage:
    python lab/validate_cninfo_d_class_known_event_candidates.py
    python lab/validate_cninfo_d_class_known_event_candidates.py \\
        --input outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_INPUT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_known_event_replacement_candidate_template.csv",
)
DEFAULT_REPORT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_known_event_candidate_validation_report.csv",
)
DEFAULT_SUMMARY = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_known_event_candidate_validation_summary.md",
)

STATUS_WAITING = "WAITING_FOR_HUMAN_INPUT"
STATUS_VALIDATED = "HUMAN_CANDIDATE_VALIDATED"
STATUS_REJECTED = "REJECTED"

INTAKE_GATE_WAITING = "WAITING_FOR_HUMAN_INPUT"
INTAKE_GATE_VALIDATED = "HUMAN_CANDIDATE_VALIDATED"

SLOT_PAIRING = {
    "DLC003R": ("DLC003", "restricted_shares_unlock"),
    "DLC006R": ("DLC006", "shareholder_change"),
}

ALLOWED_EVIDENCE_TYPES = {
    "regulatory_disclosure",
    "unlock_schedule_record",
    "shareholder_change_announcement",
    "internal_research_note",
    "prior_validation_record",
}

EVIDENCE_FIELDS = (
    "event_evidence_type",
    "event_evidence_description",
    "event_date_or_period",
    "source_reference",
)

REPORT_COLUMNS = [
    "replacement_case_id",
    "replaces_case_id",
    "component",
    "check_id",
    "check_status",
    "message",
]


def _is_true(val: str) -> bool:
    return str(val).strip().lower() in ("true", "yes", "1")


def _empty(val: Any) -> bool:
    return val is None or str(val).strip() == ""


def load_candidates(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_row(row: Dict[str, str]) -> List[Dict[str, str]]:
    """返回该校验行的 check 结果列表。"""
    rid = str(row.get("replacement_case_id", "")).strip()
    checks: List[Dict[str, str]] = []

    def add(check_id: str, ok: bool, message: str) -> None:
        checks.append(
            {
                "replacement_case_id": rid,
                "replaces_case_id": str(row.get("replaces_case_id", "")).strip(),
                "component": str(row.get("component", "")).strip(),
                "check_id": check_id,
                "check_status": "PASS" if ok else "FAIL",
                "message": message,
            }
        )

    if rid not in SLOT_PAIRING:
        add("R001_replacement_case_id", False, f"unknown replacement_case_id:{rid}")
        return checks

    expected_replaces, expected_component = SLOT_PAIRING[rid]
    add(
        "R002_replaces_case_id",
        str(row.get("replaces_case_id", "")).strip() == expected_replaces,
        f"expected replaces_case_id={expected_replaces}",
    )
    add(
        "R003_component",
        str(row.get("component", "")).strip() == expected_component,
        f"expected component={expected_component}",
    )
    add(
        "R004_required_behavior",
        str(row.get("required_behavior", "")).strip() == "captured_normal",
        "required_behavior must be captured_normal",
    )

    for field in ("company_code", "company_name"):
        if _empty(row.get(field)):
            add(f"R005_{field}", False, f"missing {field}")
        else:
            add(f"R005_{field}", True, f"{field} present")

    for field in EVIDENCE_FIELDS:
        if _empty(row.get(field)):
            add(f"R006_{field}", False, f"missing {field}")
        else:
            add(f"R006_{field}", True, f"{field} present")

    etype = str(row.get("event_evidence_type", "")).strip()
    if _empty(etype):
        add("R007_event_evidence_type", False, "missing event_evidence_type")
    elif etype not in ALLOWED_EVIDENCE_TYPES:
        add("R007_event_evidence_type", False, f"disallowed type:{etype}")
    else:
        add("R007_event_evidence_type", True, f"type={etype}")

    hp = row.get("human_provided", "")
    cs = str(row.get("candidate_status", "")).strip()
    any_filled = any(not _empty(row.get(f)) for f in ("company_code", "company_name") + EVIDENCE_FIELDS)

    if _empty(row.get("company_code")) and _empty(row.get("company_name")) and not any_filled:
        add("R008_human_provided", True, "waiting for human input")
        add("R009_candidate_status", cs == "candidate_required", "expected candidate_required while empty")
    else:
        add("R008_human_provided", _is_true(hp), "human_provided must be true after input")
        add(
            "R009_candidate_status",
            cs == "human_candidate_provided",
            "candidate_status must be human_candidate_provided after input",
        )

    return checks


def validate_duplicate_codes(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []
    codes: Dict[str, List[str]] = {}
    for row in rows:
        rid = str(row.get("replacement_case_id", "")).strip()
        code = str(row.get("company_code", "")).strip()
        if code:
            codes.setdefault(code, []).append(rid)

    for code, rids in codes.items():
        if len(rids) > 1:
            justified = any(
                "explicitly justified" in str(row.get("notes", "")).lower()
                or "duplicate_justified" in str(row.get("notes", "")).lower()
                for row in rows
                if str(row.get("company_code", "")).strip() == code
            )
            for rid in rids:
                row = next(r for r in rows if r.get("replacement_case_id") == rid)
                checks.append(
                    {
                        "replacement_case_id": rid,
                        "replaces_case_id": str(row.get("replaces_case_id", "")).strip(),
                        "component": str(row.get("component", "")).strip(),
                        "check_id": "R010_duplicate_company_code",
                        "check_status": "PASS" if justified else "FAIL",
                        "message": f"duplicate company_code={code} across {','.join(rids)}",
                    }
                )
    return checks


def compute_overall_status(rows: List[Dict[str, str]], all_checks: List[Dict[str, str]]) -> str:
    if not rows:
        return STATUS_REJECTED

    any_waiting = False
    for row in rows:
        if _empty(row.get("company_code")) and _empty(row.get("company_name")):
            any_waiting = True

    fails = [c for c in all_checks if c["check_status"] == "FAIL"]
    if any_waiting:
        return STATUS_WAITING

    if fails:
        return STATUS_REJECTED
    return STATUS_VALIDATED


def write_report(checks: List[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(checks)


def write_summary(
    rows: List[Dict[str, str]],
    checks: List[Dict[str, str]],
    overall: str,
    path: str,
) -> None:
    fail_count = sum(1 for c in checks if c["check_status"] == "FAIL")
    pass_count = sum(1 for c in checks if c["check_status"] == "PASS")
    intake_gate = INTAKE_GATE_WAITING if overall == STATUS_WAITING else (
        INTAKE_GATE_VALIDATED if overall == STATUS_VALIDATED else "REJECTED"
    )

    lines = [
        "# CNINFO D 类 Known Event Candidate Intake Validation Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 离线 intake 校验 · **CNINFO calls = 0** · **输入文件未修改**",
        "",
        "## Result",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| candidate_validation_status | **{overall}** |",
        f"| intake_gate | **d_class_known_event_candidate_intake_gate = {intake_gate}** |",
        f"| candidates | {len(rows)} |",
        f"| checks PASS | {pass_count} |",
        f"| checks FAIL | {fail_count} |",
        f"| CNINFO calls | **0** |",
        "",
        "## Per-Case",
        "",
        "| replacement_case_id | company_code | candidate_status | human_provided |",
        "|---------------------|--------------|------------------|----------------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('replacement_case_id', '')} | {row.get('company_code', '') or '(empty)'} | "
            f"{row.get('candidate_status', '')} | {row.get('human_provided', '')} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "```text",
            f"d_class_known_event_candidate_intake_gate = {intake_gate}",
            "```",
            "",
            "**不是 PASS** · **不是 ready_for_live** · **不是 verified**",
            "",
        ]
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def validate_candidates(input_path: str) -> Tuple[str, List[Dict[str, str]], List[Dict[str, str]]]:
    rows = load_candidates(input_path)
    all_checks: List[Dict[str, str]] = []
    for row in rows:
        all_checks.extend(validate_row(row))
    all_checks.extend(validate_duplicate_codes(rows))
    overall = compute_overall_status(rows, all_checks)
    return overall, rows, all_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="D-class known event candidate intake 离线校验")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--summary", default=DEFAULT_SUMMARY)
    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not os.path.isfile(args.input):
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        return 2

    overall, rows, checks = validate_candidates(args.input)
    write_report(checks, args.report)
    write_summary(rows, checks, overall, args.summary)

    print(f"candidate_validation_status={overall}")
    print(f"intake_gate=d_class_known_event_candidate_intake_gate={INTAKE_GATE_WAITING if overall == STATUS_WAITING else INTAKE_GATE_VALIDATED if overall == STATUS_VALIDATED else 'REJECTED'}")
    print(f"cninfo_calls=0")
    print(f"report={args.report}")
    print(f"summary={args.summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

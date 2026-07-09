"""
CNINFO D-class Phase 1 freeze v1 offline lint.

Validates freeze v1 field catalog, registry draft annotations, DC001-DC007 fixtures,
required/removed/future fields, enums, quality policy mapping, and lineage fields.
No CNINFO requests.

Usage:
    python lab/lint_cninfo_d_class_phase1_freeze_v1.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Set

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELD_MATRIX = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_phase1_field_decision_matrix.csv"
)
FIELD_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_phase1_freeze_v1_field_catalog.csv"
)
REGISTRY_YAML = os.path.join(BASE_DIR, "config", "cninfo_d_class_source_registry_draft.yaml")
QUALITY_POLICY = os.path.join(BASE_DIR, "plans", "cninfo_d_class_event_quality_policy.md")
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "d_class", "phase1")
SUMMARY_MD = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_phase1_freeze_v1_lint_summary.md",
)

PHASE1_COMPONENTS = frozenset({
    "margin_trading",
    "block_trade",
    "restricted_shares_unlock",
    "disclosure_schedule",
    "equity_pledge",
    "shareholder_change",
    "executive_shareholding",
})

READY_CASE_FIXTURES: Dict[str, str] = {
    "DC001.json": "margin_trading",
    "DC002.json": "block_trade",
    "DC003.json": "restricted_shares_unlock",
    "DC004.json": "equity_pledge",
    "DC005.json": "shareholder_change",
    "DC006.json": "executive_shareholding",
    "DC007.json": "equity_pledge",
}

READY_CASE_TYPES = {
    "DC001.json": "empty_but_valid",
    "DC002.json": "captured_normal",
    "DC003.json": "captured_normal",
    "DC004.json": "empty_but_valid",
    "DC005.json": "captured_normal",
    "DC006.json": "captured_normal",
    "DC007.json": "needs_review",
}

REMOVED_FIELDS = frozenset({"verified_flag", "testing_stable_sample_flag"})
FUTURE_FIELDS = frozenset({"buyer", "seller", "pledge_status"})

QUALITY_STATUS_ENUM = frozenset({"pass", "caveat", "blocked", "needs_review"})
EVENT_STATUS_ENUM = frozenset({"captured", "empty_but_valid", "failed", "pending"})
LINEAGE_STATUS_ENUM = frozenset({"discovered", "linked", "needs_review", "stale"})

LINEAGE_REQUIRED = frozenset({
    "registry_source_id",
    "fetch_time",
    "raw_record_hash",
})

ENVELOPE_REQUIRED = frozenset({
    "event_id",
    "company_code",
    "event_type",
    "event_time",
    "source_endpoint",
    "source_record_id",
    "event_status",
    "quality_status",
})

EMPTY_BUT_VALID_QUALITY = frozenset({"pass", "caveat"})
CAPTURED_QUALITY = frozenset({"pass", "caveat", "needs_review"})

EXPECTED_FIELD_COUNTS = {
    "required": 49,
    "recommended": 25,
    "future": 3,
    "removed": 2,
    "total": 79,
}

TOTAL_CHECKS = 12


@dataclass
class LintResult:
    rule_id: str
    description: str
    passed: bool
    detail: str


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_fixture(name: str) -> dict:
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _all_fixture_files() -> List[str]:
    names: List[str] = []
    for fname in os.listdir(FIXTURES_DIR):
        if fname.endswith(".json"):
            names.append(fname)
    return sorted(names)


def _required_fields_by_component(matrix_rows: List[dict]) -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = defaultdict(set)
    for row in matrix_rows:
        if row["decision"] == "required":
            out[row["component"]].add(row["field_name"])
    return out


def check_field_catalog_counts(catalog_rows: List[dict]) -> LintResult:
    level_counts = Counter(r["level"] for r in catalog_rows)
    ok = (
        len(catalog_rows) == EXPECTED_FIELD_COUNTS["total"]
        and level_counts["required"] == EXPECTED_FIELD_COUNTS["required"]
        and level_counts["recommended"] == EXPECTED_FIELD_COUNTS["recommended"]
        and level_counts["future"] == EXPECTED_FIELD_COUNTS["future"]
        and level_counts["removed"] == EXPECTED_FIELD_COUNTS["removed"]
    )
    return LintResult(
        "R-D-FV1-001",
        "freeze v1 field catalog counts match matrix",
        ok,
        f"rows={len(catalog_rows)} levels={dict(level_counts)}",
    )


def check_catalog_matrix_alignment(catalog_rows: List[dict], matrix_rows: List[dict]) -> LintResult:
    catalog_keys = {(r["component"], r["field_name"]) for r in catalog_rows}
    matrix_keys = {(r["component"], r["field_name"]) for r in matrix_rows}
    missing = matrix_keys - catalog_keys
    extra = catalog_keys - matrix_keys
    ok = not missing and not extra
    return LintResult(
        "R-D-FV1-002",
        "field catalog aligns with decision matrix",
        ok,
        f"missing={len(missing)} extra={len(extra)}",
    )


def check_removed_fields_absent() -> LintResult:
    offenders: List[str] = []
    for fname in _all_fixture_files():
        data = _load_fixture(fname)
        blob = json.dumps(data, ensure_ascii=False)
        for field in REMOVED_FIELDS:
            if f'"{field}"' in blob:
                offenders.append(f"{fname}:{field}")
    ok = not offenders
    return LintResult(
        "R-D-FV1-003",
        "removed fields absent from all fixtures",
        ok,
        f"offenders={offenders}" if offenders else "none",
    )


def check_future_fields_absent() -> LintResult:
    offenders: List[str] = []
    for fname in _all_fixture_files():
        data = _load_fixture(fname)
        for comp_key, payload in data.items():
            if comp_key.startswith("_") or comp_key == "market_event":
                continue
            if not isinstance(payload, dict):
                continue
            for field in FUTURE_FIELDS:
                if field in payload and payload[field] is not None:
                    offenders.append(f"{fname}:{comp_key}.{field}")
    ok = not offenders
    return LintResult(
        "R-D-FV1-004",
        "future fields absent from all fixtures",
        ok,
        f"offenders={offenders}" if offenders else "none",
    )


def check_ready_case_fixtures_exist() -> LintResult:
    missing = [
        name for name in READY_CASE_FIXTURES if not os.path.isfile(os.path.join(FIXTURES_DIR, name))
    ]
    ok = not missing
    return LintResult(
        "R-D-FV1-005",
        "DC001-DC007 ready-case fixtures exist",
        ok,
        f"missing={missing}" if missing else "count=7",
    )


def check_required_fields_on_captured(matrix_rows: List[dict]) -> LintResult:
    required_by_comp = _required_fields_by_component(matrix_rows)
    failures: List[str] = []
    for fname, comp in READY_CASE_FIXTURES.items():
        data = _load_fixture(fname)
        env = data.get("market_event", {})
        if env.get("event_status") != "captured":
            continue
        payload = data.get(comp, {})
        missing = required_by_comp.get(comp, set()) - set(payload.keys())
        if missing:
            failures.append(f"{fname}:missing={sorted(missing)}")
        env_missing = ENVELOPE_REQUIRED - set(env.keys())
        if env_missing:
            failures.append(f"{fname}:envelope_missing={sorted(env_missing)}")
    ok = not failures
    return LintResult(
        "R-D-FV1-006",
        "captured fixtures include component required fields",
        ok,
        "; ".join(failures) if failures else "all captured cases ok",
    )


def check_empty_but_valid_quality_policy() -> LintResult:
    failures: List[str] = []
    for fname, case_type in READY_CASE_TYPES.items():
        if case_type != "empty_but_valid":
            continue
        data = _load_fixture(fname)
        env = data.get("market_event", {})
        comp = READY_CASE_FIXTURES[fname]
        payload = data.get(comp, {})
        if env.get("event_status") != "empty_but_valid":
            failures.append(f"{fname}:event_status")
        if env.get("quality_status") not in EMPTY_BUT_VALID_QUALITY:
            failures.append(f"{fname}:envelope_quality")
        if payload.get("quality_status") not in EMPTY_BUT_VALID_QUALITY:
            failures.append(f"{fname}:payload_quality")
        if payload.get("company_code") != env.get("company_code"):
            failures.append(f"{fname}:company_code_mismatch")
    ok = not failures
    return LintResult(
        "R-D-FV1-007",
        "empty_but_valid fixtures follow quality policy",
        ok,
        f"fail={failures}" if failures else "DC001+DC004 ok",
    )


def check_enum_validity() -> LintResult:
    failures: List[str] = []
    for fname in READY_CASE_FIXTURES:
        data = _load_fixture(fname)
        env = data.get("market_event", {})
        comp = READY_CASE_FIXTURES[fname]
        payload = data.get(comp, {})
        if env.get("event_status") not in EVENT_STATUS_ENUM:
            failures.append(f"{fname}:event_status")
        if env.get("quality_status") not in QUALITY_STATUS_ENUM:
            failures.append(f"{fname}:envelope_quality_status")
        if payload.get("quality_status") not in QUALITY_STATUS_ENUM:
            failures.append(f"{fname}:payload_quality_status")
        lineage = env.get("lineage") or {}
        if lineage.get("lineage_status") and lineage["lineage_status"] not in LINEAGE_STATUS_ENUM:
            failures.append(f"{fname}:lineage_status")
    ok = not failures
    return LintResult(
        "R-D-FV1-008",
        "event/quality/lineage enums valid on ready cases",
        ok,
        f"fail={failures}" if failures else "all valid",
    )


def check_lineage_fields() -> LintResult:
    failures: List[str] = []
    for fname in READY_CASE_FIXTURES:
        data = _load_fixture(fname)
        env = data.get("market_event", {})
        lineage = env.get("lineage") or {}
        missing = LINEAGE_REQUIRED - set(lineage.keys())
        if missing:
            failures.append(f"{fname}:missing={sorted(missing)}")
        expected_source = READY_CASE_FIXTURES[fname]
        if lineage.get("registry_source_id") != expected_source:
            failures.append(f"{fname}:registry_source_id")
    ok = not failures
    return LintResult(
        "R-D-FV1-009",
        "lineage required fields valid on ready cases",
        ok,
        "; ".join(failures) if failures else "all ok",
    )


def check_registry_phase1_mapping() -> LintResult:
    with open(REGISTRY_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    freeze = data.get("phase1_freeze_v1") or {}
    failures: List[str] = []
    if not freeze.get("implemented"):
        failures.append("phase1_freeze_v1.implemented")
    if freeze.get("implementation_gate") != "PASS_OFFLINE":
        failures.append("implementation_gate")
    if freeze.get("cninfo_called") is not False:
        failures.append("cninfo_called")
    if freeze.get("quality_policy_ref") != "plans/cninfo_d_class_event_quality_policy.md":
        failures.append("quality_policy_ref")
    catalog_ref = freeze.get("field_catalog_ref", "")
    if "cninfo_d_class_phase1_freeze_v1_field_catalog.csv" not in catalog_ref:
        failures.append("field_catalog_ref")
    components = freeze.get("components") or {}
    for comp in PHASE1_COMPONENTS:
        if comp not in components:
            failures.append(f"missing_component:{comp}")
    for src in data.get("sources", []):
        sid = src.get("source_id")
        if sid not in PHASE1_COMPONENTS:
            continue
        p1 = src.get("phase1_freeze_v1") or {}
        if p1.get("phase1_status") != "freeze_v1_implemented_offline":
            failures.append(f"{sid}:phase1_status")
        if p1.get("component") != sid:
            failures.append(f"{sid}:component")
    ok = not failures
    return LintResult(
        "R-D-FV1-010",
        "registry phase1_freeze_v1 mapping valid",
        ok,
        f"fail={failures}" if failures else "registry ok",
    )


def check_needs_review_case() -> LintResult:
    data = _load_fixture("DC007.json")
    env = data.get("market_event", {})
    payload = data.get("equity_pledge", {})
    ok = (
        env.get("event_status") == "captured"
        and env.get("quality_status") == "needs_review"
        and payload.get("quality_status") == "needs_review"
        and (env.get("lineage") or {}).get("lineage_status") == "needs_review"
    )
    return LintResult(
        "R-D-FV1-011",
        "DC007 needs_review case valid",
        ok,
        "DC007 captured+needs_review" if ok else "DC007 policy mismatch",
    )


def check_cninfo_not_called() -> LintResult:
    offenders: List[str] = []
    for fname in _all_fixture_files():
        data = _load_fixture(fname)
        meta = data.get("_fixture_meta", {})
        if meta.get("cninfo_called") is not False:
            offenders.append(fname)
    ok = not offenders
    return LintResult(
        "R-D-FV1-012",
        "all fixtures declare cninfo_called=false",
        ok,
        f"offenders={offenders}" if offenders else "cninfo_called=0",
    )


def _write_summary(results: List[LintResult], passed: int) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# CNINFO D-class Phase 1 Freeze v1 Lint Summary",
        "",
        f"_Generated: {ts}_",
        "",
        f"**Gate:** `d_class_phase1_freeze_v1_lint_gate = {'PASS' if passed == TOTAL_CHECKS else 'FAIL'}`",
        f"**Checks:** {passed}/{TOTAL_CHECKS} PASS",
        "**CNINFO calls:** 0",
        "",
        "| Rule | Description | Result | Detail |",
        "|------|-------------|--------|--------|",
    ]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"| {r.rule_id} | {r.description} | {status} | {r.detail} |")
    lines.extend(["", "---", "", "Offline only; no live; no harvest."])
    os.makedirs(os.path.dirname(SUMMARY_MD), exist_ok=True)
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    if not os.path.isfile(QUALITY_POLICY):
        print(f"ERROR: missing {QUALITY_POLICY}", file=sys.stderr)
        return 1

    catalog_rows = _read_csv(FIELD_CATALOG)
    matrix_rows = _read_csv(FIELD_MATRIX)

    results = [
        check_field_catalog_counts(catalog_rows),
        check_catalog_matrix_alignment(catalog_rows, matrix_rows),
        check_removed_fields_absent(),
        check_future_fields_absent(),
        check_ready_case_fixtures_exist(),
        check_required_fields_on_captured(matrix_rows),
        check_empty_but_valid_quality_policy(),
        check_enum_validity(),
        check_lineage_fields(),
        check_registry_phase1_mapping(),
        check_needs_review_case(),
        check_cninfo_not_called(),
    ]

    passed = sum(1 for r in results if r.passed)
    _write_summary(results, passed)

    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"[{mark}] {r.rule_id}: {r.description} — {r.detail}")

    gate = "PASS" if passed == TOTAL_CHECKS else "FAIL"
    print(f"\nd_class_phase1_freeze_v1_lint_gate = {gate}")
    print(f"checks: {passed}/{TOTAL_CHECKS}")
    return 0 if passed == TOTAL_CHECKS else 1


if __name__ == "__main__":
    sys.exit(main())

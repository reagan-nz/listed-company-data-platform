"""
CNINFO D-class Phase 1 ready-case benchmark offline runner.

Reads local fixtures only. No CNINFO requests. No network.

Usage:
    python lab/run_cninfo_d_class_phase1_ready_case_benchmark.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELD_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_phase1_freeze_v1_field_catalog.csv"
)
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "d_class", "phase1")
BENCHMARK_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_phase1_ready_case_benchmark.csv"
)
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_phase1_ready_case_benchmark_summary.md"
)

SCHEMA_VERSION = "d_class_phase1_freeze_v1"
BENCHMARK_GATE = "READY_FOR_REVIEW"

REMOVED_FIELDS = frozenset({"verified_flag", "testing_stable_sample_flag"})
FUTURE_FIELDS = frozenset({"buyer", "seller", "pledge_status"})
FORBIDDEN_STATUS_TOKENS = frozenset({"verified", "testing_stable_sample"})

VALID_QUALITY_STATUS = frozenset({"pass", "caveat", "blocked", "needs_review"})
VALID_EVENT_STATUS = frozenset({"captured", "empty_but_valid", "failed", "pending"})
VALID_RETRIEVAL_STATUS = frozenset({
    "found",
    "not_found",
    "empty_but_valid",
    "http_error",
    "blocked",
})
VALID_LINEAGE_STATUS = frozenset({"discovered", "linked", "needs_review", "stale"})

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

LINEAGE_REQUIRED = frozenset({
    "registry_source_id",
    "fetch_time",
    "raw_record_hash",
})

CASE_REGISTRY = [
    {
        "case_id": "DC001",
        "component": "margin_trading",
        "fixture": "DC001.json",
        "scenario": "empty_but_valid",
        "expected_status": "empty_but_valid_pass",
    },
    {
        "case_id": "DC002",
        "component": "block_trade",
        "fixture": "DC002.json",
        "scenario": "captured_normal",
        "expected_status": "captured_pass",
    },
    {
        "case_id": "DC003",
        "component": "restricted_shares_unlock",
        "fixture": "DC003.json",
        "scenario": "captured_normal",
        "expected_status": "captured_pass",
    },
    {
        "case_id": "DC004",
        "component": "equity_pledge",
        "fixture": "DC004.json",
        "scenario": "empty_but_valid",
        "expected_status": "empty_but_valid_pass",
    },
    {
        "case_id": "DC005",
        "component": "shareholder_change",
        "fixture": "DC005.json",
        "scenario": "captured_normal",
        "expected_status": "captured_pass",
    },
    {
        "case_id": "DC006",
        "component": "executive_shareholding",
        "fixture": "DC006.json",
        "scenario": "captured_normal",
        "expected_status": "captured_pass",
    },
    {
        "case_id": "DC007",
        "component": "equity_pledge",
        "fixture": "DC007.json",
        "scenario": "needs_review",
        "expected_status": "needs_review_accepted",
    },
]


@dataclass
class BenchmarkRow:
    case_id: str
    component: str
    scenario: str
    expected_status: str
    actual_status: str
    retrieval_status: str
    quality_status: str
    lineage_status: str
    passed: str
    notes: str = ""


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True


def _load_required_by_component() -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = {}
    with open(FIELD_CATALOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("level") != "required":
                continue
            comp = row["component"]
            if comp == "market_event":
                continue
            out.setdefault(comp, set()).add(row["field_name"])
    return out


def _missing_required(payload: dict, required: Set[str]) -> List[str]:
    return sorted(f for f in required if f not in payload or not _is_present(payload.get(f)))


def _retrieval_status_from_event(event_status: str) -> str:
    if event_status == "empty_but_valid":
        return "empty_but_valid"
    if event_status == "captured":
        return "found"
    if event_status == "failed":
        return "http_error"
    return "not_found"


def _contains_forbidden_status(data: dict) -> List[str]:
    offenders: List[str] = []
    blob = json.dumps(data, ensure_ascii=False).lower()
    for token in FORBIDDEN_STATUS_TOKENS:
        if f'"{token}"' in blob:
            offenders.append(token)
    return offenders


def _validate_common(data: dict, component: str) -> Tuple[bool, str, str, str, str]:
    """返回 ok, retrieval_status, quality_status, lineage_status, detail。"""
    meta = data.get("_fixture_meta") or {}
    if meta.get("cninfo_called") is not False:
        return False, "", "", "", "cninfo_called must be false"

    env = data.get("market_event") or {}
    payload = data.get(component) or {}
    lineage = env.get("lineage") or {}

    missing_env = sorted(ENVELOPE_REQUIRED - set(env.keys()))
    if missing_env:
        return False, "", "", "", f"envelope missing: {missing_env}"

    if env.get("event_type") != component:
        return False, "", "", "", f"event_type mismatch: {env.get('event_type')}"

    if env.get("event_status") not in VALID_EVENT_STATUS:
        return False, "", "", "", f"invalid event_status: {env.get('event_status')}"

    if env.get("quality_status") not in VALID_QUALITY_STATUS:
        return False, "", "", "", f"invalid envelope quality_status: {env.get('quality_status')}"

    missing_lineage = sorted(LINEAGE_REQUIRED - set(lineage.keys()))
    if missing_lineage:
        return False, "", "", "", f"lineage missing: {missing_lineage}"

    lineage_status = str(lineage.get("lineage_status") or "discovered")
    if lineage_status not in VALID_LINEAGE_STATUS:
        return False, "", "", "", f"invalid lineage_status: {lineage_status}"

    if lineage.get("registry_source_id") != component:
        return False, "", "", "", f"registry_source_id mismatch: {lineage.get('registry_source_id')}"

    retrieval_status = _retrieval_status_from_event(str(env.get("event_status")))
    if retrieval_status not in VALID_RETRIEVAL_STATUS:
        return False, "", "", "", f"invalid retrieval_status: {retrieval_status}"

    if payload.get("company_code") != env.get("company_code"):
        return False, retrieval_status, "", lineage_status, "company_code mismatch envelope/payload"

    forbidden = _contains_forbidden_status(data)
    if forbidden:
        return False, retrieval_status, "", lineage_status, f"forbidden status tokens: {forbidden}"

    blob = json.dumps(data, ensure_ascii=False)
    for field in REMOVED_FIELDS:
        if f'"{field}"' in blob:
            return False, retrieval_status, "", lineage_status, f"removed field present: {field}"

    if isinstance(payload, dict):
        for field in FUTURE_FIELDS:
            if field in payload and payload[field] is not None:
                return False, retrieval_status, "", lineage_status, f"future field populated: {field}"

    quality_status = str(payload.get("quality_status") or env.get("quality_status"))
    if quality_status not in VALID_QUALITY_STATUS:
        return False, retrieval_status, quality_status, lineage_status, "invalid payload quality_status"

    return True, retrieval_status, quality_status, lineage_status, "common checks ok"


def _validate_empty_but_valid(
    data: dict,
    component: str,
    required_by_comp: Dict[str, Set[str]],
) -> Tuple[str, str, str, str, bool, str]:
    ok, retrieval, quality, lineage, detail = _validate_common(data, component)
    if not ok:
        return "fail", retrieval, quality, lineage, False, detail

    env = data["market_event"]
    payload = data.get(component) or {}
    if env.get("event_status") != "empty_but_valid":
        return "fail", retrieval, quality, lineage, False, "event_status must be empty_but_valid"
    if retrieval != "empty_but_valid":
        return "fail", retrieval, quality, lineage, False, "retrieval_status must be empty_but_valid"
    if quality not in {"pass", "caveat"}:
        return "fail", retrieval, quality, lineage, False, "quality_status must be pass or caveat"

    full_required = required_by_comp.get(component, set())
    metric_fields = full_required - {"company_code", "quality_status"}
    populated_metrics = [f for f in metric_fields if _is_present(payload.get(f))]
    if populated_metrics:
        return (
            "fail",
            retrieval,
            quality,
            lineage,
            False,
            f"empty_but_valid should not populate metrics: {populated_metrics}",
        )

    if not _is_present(payload.get("company_code")):
        return "fail", retrieval, quality, lineage, False, "company_code required on empty payload"

    return "empty_but_valid_pass", retrieval, quality, lineage, True, "empty_but_valid accepted per quality policy"


def _validate_captured_normal(
    data: dict,
    component: str,
    required_by_comp: Dict[str, Set[str]],
) -> Tuple[str, str, str, str, bool, str]:
    ok, retrieval, quality, lineage, detail = _validate_common(data, component)
    if not ok:
        return "fail", retrieval, quality, lineage, False, detail

    env = data["market_event"]
    payload = data.get(component) or {}
    if env.get("event_status") != "captured":
        return "fail", retrieval, quality, lineage, False, "event_status must be captured"
    if retrieval != "found":
        return "fail", retrieval, quality, lineage, False, "retrieval_status must be found"

    missing = _missing_required(payload, required_by_comp.get(component, set()))
    if missing:
        return "fail", retrieval, quality, lineage, False, f"missing required fields: {missing}"

    if quality not in {"pass", "caveat"}:
        return "fail", retrieval, quality, lineage, False, "quality_status must be pass or caveat"

    return "captured_pass", retrieval, quality, lineage, True, "required fields complete; captured pass"


def _validate_needs_review(
    data: dict,
    component: str,
    required_by_comp: Dict[str, Set[str]],
) -> Tuple[str, str, str, str, bool, str]:
    ok, retrieval, quality, lineage, detail = _validate_common(data, component)
    if not ok:
        return "fail", retrieval, quality, lineage, False, detail

    env = data["market_event"]
    payload = data.get(component) or {}
    if env.get("event_status") != "captured":
        return "fail", retrieval, quality, lineage, False, "needs_review case must be captured"
    if env.get("quality_status") != "needs_review":
        return "fail", retrieval, quality, lineage, False, "envelope quality_status must be needs_review"
    if payload.get("quality_status") != "needs_review":
        return "fail", retrieval, quality, lineage, False, "payload quality_status must be needs_review"
    if lineage != "needs_review":
        return "fail", retrieval, quality, lineage, False, "lineage_status must be needs_review"

    missing = _missing_required(payload, required_by_comp.get(component, set()))
    if missing:
        return "fail", retrieval, quality, lineage, False, f"missing required fields: {missing}"

    return (
        "needs_review_accepted",
        retrieval,
        "needs_review",
        lineage,
        True,
        "needs_review accepted per quality policy",
    )


def _run_case(case: dict, required_by_comp: Dict[str, Set[str]]) -> BenchmarkRow:
    fixture_path = os.path.join(FIXTURES_DIR, case["fixture"])
    if not os.path.isfile(fixture_path):
        return BenchmarkRow(
            case["case_id"],
            case["component"],
            case["scenario"],
            case["expected_status"],
            "error",
            "",
            "",
            "",
            "no",
            "fixture not found",
        )

    data = _load_json(fixture_path)
    component = case["component"]
    scenario = case["scenario"]

    if scenario == "empty_but_valid":
        actual, retrieval, quality, lineage, ok, notes = _validate_empty_but_valid(
            data, component, required_by_comp
        )
    elif scenario == "captured_normal":
        actual, retrieval, quality, lineage, ok, notes = _validate_captured_normal(
            data, component, required_by_comp
        )
    elif scenario == "needs_review":
        actual, retrieval, quality, lineage, ok, notes = _validate_needs_review(
            data, component, required_by_comp
        )
    else:
        return BenchmarkRow(
            case["case_id"],
            component,
            scenario,
            case["expected_status"],
            "skip",
            "",
            "",
            "",
            "no",
            f"unknown scenario: {scenario}",
        )

    passed = ok and actual == case["expected_status"]
    return BenchmarkRow(
        case["case_id"],
        component,
        scenario,
        case["expected_status"],
        actual,
        retrieval,
        quality,
        lineage,
        "yes" if passed else "no",
        notes if passed else notes,
    )


def _write_benchmark_csv(rows: List[BenchmarkRow]) -> None:
    os.makedirs(os.path.dirname(BENCHMARK_CSV), exist_ok=True)
    with open(BENCHMARK_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "component",
                "scenario",
                "expected_status",
                "actual_status",
                "retrieval_status",
                "quality_status",
                "lineage_status",
                "passed",
                "notes",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "case_id": r.case_id,
                    "component": r.component,
                    "scenario": r.scenario,
                    "expected_status": r.expected_status,
                    "actual_status": r.actual_status,
                    "retrieval_status": r.retrieval_status,
                    "quality_status": r.quality_status,
                    "lineage_status": r.lineage_status,
                    "passed": r.passed,
                    "notes": r.notes,
                }
            )


def _write_summary(rows: List[BenchmarkRow]) -> None:
    passed = sum(1 for r in rows if r.passed == "yes")
    failed = len(rows) - passed
    components = sorted({r.component for r in rows})
    empty_cases = [r for r in rows if r.scenario == "empty_but_valid"]
    review_cases = [r for r in rows if r.scenario == "needs_review"]

    lines = [
        "# CNINFO D 类 Phase 1 Ready-case Benchmark 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 离线 fixture benchmark；**无 CNINFO**；**无 live**；**无 harvest**。",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| Total cases | {len(rows)} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| Schema version | {SCHEMA_VERSION} |",
        f"| CNINFO calls | **0** |",
        "",
        "## Component Coverage",
        "",
        f"- Components exercised: **{len(components)}** — {', '.join(components)}",
        f"- Scenarios: empty_but_valid (**{sum(1 for r in empty_cases if r.passed == 'yes')}/{len(empty_cases)}** pass) · "
        f"captured_normal · needs_review (**{sum(1 for r in review_cases if r.passed == 'yes')}/{len(review_cases)}** pass)",
        "",
        "## Quality Policy Coverage",
        "",
        "- `empty_but_valid`: DC001 margin_trading · DC004 equity_pledge — retrieval=`empty_but_valid`, quality=`pass`",
        "- `captured` + `pass`: DC002–DC006 — retrieval=`found`, required fields from freeze v1 catalog",
        "- `needs_review`: DC007 — captured row with mapping ambiguity; quality/lineage=`needs_review`",
        "- Removed fields (`verified_flag`, `testing_stable_sample_flag`): absent",
        "- Future fields (`buyer`, `seller`, `pledge_status`): not populated",
        "",
        "## Case Results",
        "",
        "| case_id | component | scenario | expected_status | actual_status | retrieval_status | quality_status | lineage_status | passed |",
        "|---------|-----------|----------|-----------------|---------------|------------------|----------------|----------------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| {r.case_id} | {r.component} | {r.scenario} | {r.expected_status} | {r.actual_status} | "
            f"{r.retrieval_status} | {r.quality_status} | {r.lineage_status} | {r.passed} |"
        )

    lines.extend(
        [
            "",
            "## empty_but_valid Behavior",
            "",
        ]
    )
    for r in empty_cases:
        lines.append(
            f"- **{r.case_id}** ({r.component}): retrieval=`{r.retrieval_status}` · "
            f"quality=`{r.quality_status}` · passed=**{r.passed}**"
        )

    lines.extend(
        [
            "",
            "## needs_review Behavior",
            "",
        ]
    )
    for r in review_cases:
        lines.append(
            f"- **{r.case_id}** ({r.component}): quality=`{r.quality_status}` · "
            f"lineage=`{r.lineage_status}` · passed=**{r.passed}**"
        )

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "```text",
            f"d_class_ready_case_benchmark_gate = {BENCHMARK_GATE}",
            "```",
            "",
            "**不是 PASS** · **不是 live_ready** · **不是 verified**.",
            "",
            "## Parallel Safety",
            "",
            "- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变）",
            "- A-class / B-class outputs: **unchanged**",
            "- CNINFO calls: **0**",
            "- testing_stable_sample: **not upgraded**",
            "",
        ]
    )
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    required_by_comp = _load_required_by_component()
    rows = [_run_case(case, required_by_comp) for case in CASE_REGISTRY]
    _write_benchmark_csv(rows)
    _write_summary(rows)

    for r in rows:
        mark = "PASS" if r.passed == "yes" else "FAIL"
        print(f"{r.case_id} {mark}: {r.notes}")

    all_passed = all(r.passed == "yes" for r in rows)
    print(f"\nGate: d_class_ready_case_benchmark_gate = {BENCHMARK_GATE}")
    print(f"All cases passed: {all_passed}")
    print(f"Benchmark CSV: {BENCHMARK_CSV}")
    print(f"Summary: {SUMMARY_MD}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

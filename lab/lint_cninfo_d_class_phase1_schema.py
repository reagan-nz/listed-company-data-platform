"""
CNINFO D-class Phase 1 schema freeze offline lint.

Validates field decision matrix, phase1 fixtures, event envelope relations,
source endpoint mapping, and quality_status enums. No CNINFO requests.

Usage:
    python lab/lint_cninfo_d_class_phase1_schema.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELD_MATRIX = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_phase1_field_decision_matrix.csv"
)
REGISTRY_YAML = os.path.join(BASE_DIR, "config", "cninfo_d_class_source_registry_draft.yaml")
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "d_class", "phase1")
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_phase1_schema_lint_summary.md"
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

EXPECTED_FIXTURES: Dict[str, str] = {
    "margin_trading_fixture.json": "margin_trading",
    "block_trade_fixture.json": "block_trade",
    "restricted_unlock_fixture.json": "restricted_shares_unlock",
}

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

QUALITY_STATUS_ENUM = frozenset({"pass", "caveat", "blocked", "needs_review"})
EVENT_STATUS_ENUM = frozenset({"captured", "empty_but_valid", "failed", "pending"})

COMPONENT_REQUIRED_FIELDS: Dict[str, Set[str]] = {
    "margin_trading": {
        "company_code",
        "trade_date",
        "financing_balance",
        "margin_balance",
        "total_margin_balance",
        "source_endpoint",
        "retrieval_time",
        "quality_status",
    },
    "block_trade": {
        "company_code",
        "trade_date",
        "transaction_price",
        "transaction_volume",
        "transaction_amount",
        "source_endpoint",
        "quality_status",
    },
    "restricted_shares_unlock": {
        "company_code",
        "unlock_date",
        "unlock_amount",
        "unlock_ratio",
        "quality_status",
    },
}

SOURCE_ENDPOINT_BY_COMPONENT: Dict[str, str] = {
    "margin_trading": "https://www.cninfo.com.cn/data20/marginTrading/detailList",
    "block_trade": "https://www.cninfo.com.cn/data20/ints/statistics",
    "restricted_shares_unlock": "https://www.cninfo.com.cn/data20/liftBan/detail",
    "disclosure_schedule": "https://www.cninfo.com.cn/new/information/getPrbookInfo",
    "equity_pledge": "https://www.cninfo.com.cn/data20/equityPledge/list",
    "shareholder_change": "https://www.cninfo.com.cn/data20/shareholeder/detail",
    "executive_shareholding": "https://www.cninfo.com.cn/data20/leader/detail",
}

FORBIDDEN_FIELD_NAMES = frozenset({"verified", "verified_flag", "testing_stable_sample_flag"})

TOTAL_CHECKS = 10


@dataclass
class LintResult:
    rule_id: str
    description: str
    passed: bool
    detail: str


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_registry_endpoints() -> Dict[str, str]:
    with open(REGISTRY_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    out: Dict[str, str] = {}
    for src in data.get("sources", []):
        sid = src.get("source_id")
        url = (src.get("api") or {}).get("url")
        if sid and url:
            out[sid] = url
    return out


def check_field_matrix_components(rows: List[dict]) -> LintResult:
    components = {r["component"] for r in rows if r["component"] != "market_event"}
    missing = PHASE1_COMPONENTS - components
    ok = not missing
    return LintResult(
        "R-D-P1-001",
        "field matrix covers all 7 Phase1 components",
        ok,
        f"missing={sorted(missing)}" if missing else f"components={len(PHASE1_COMPONENTS)}",
    )


def check_quality_status_on_components(rows: List[dict]) -> LintResult:
  failures: List[str] = []
  for comp in PHASE1_COMPONENTS:
      qs = [r for r in rows if r["component"] == comp and r["field_name"] == "quality_status"]
      if not qs or qs[0]["decision"] != "required":
          failures.append(comp)
  ok = not failures
  return LintResult(
      "R-D-P1-002",
      "quality_status required on all 7 components",
      ok,
      f"fail={failures}" if failures else "all required",
  )


def check_forbidden_fields(rows: List[dict]) -> LintResult:
    bad = [r["field_name"] for r in rows if r["field_name"] in FORBIDDEN_FIELD_NAMES and r["decision"] != "removed"]
    ok = not bad
    return LintResult(
        "R-D-P1-003",
        "no verified/testing_stable_sample fields in contract",
        ok,
        f"bad={bad}" if bad else "none",
    )


def check_fixture_files_exist() -> LintResult:
    missing = [name for name in EXPECTED_FIXTURES if not os.path.isfile(os.path.join(FIXTURES_DIR, name))]
    ok = not missing
    return LintResult(
        "R-D-P1-004",
        "phase1 fixture files exist",
        ok,
        f"missing={missing}" if missing else f"count={len(EXPECTED_FIXTURES)}",
    )


def _load_fixture(name: str) -> dict:
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_envelope_required_fields() -> LintResult:
    failures: List[str] = []
    for fname, comp in EXPECTED_FIXTURES.items():
        data = _load_fixture(fname)
        env = data.get("market_event", {})
        missing = ENVELOPE_REQUIRED - set(env.keys())
        if missing:
            failures.append(f"{fname}:missing={sorted(missing)}")
        if env.get("event_type") != comp:
            failures.append(f"{fname}:event_type_mismatch")
    ok = not failures
    return LintResult(
        "R-D-P1-005",
        "market_event envelope required fields present",
        ok,
        "; ".join(failures) if failures else "3/3 fixtures ok",
    )


def check_component_required_fields() -> LintResult:
    failures: List[str] = []
    for fname, comp in EXPECTED_FIXTURES.items():
        if comp not in COMPONENT_REQUIRED_FIELDS:
            continue
        data = _load_fixture(fname)
        payload = data.get(comp, {})
        missing = COMPONENT_REQUIRED_FIELDS[comp] - set(payload.keys())
        if missing:
            failures.append(f"{comp}:missing={sorted(missing)}")
    ok = not failures
    return LintResult(
        "R-D-P1-006",
        "component required fields present in fixtures",
        ok,
        "; ".join(failures) if failures else "3 fixture payloads ok",
    )


def check_event_object_relation() -> LintResult:
    failures: List[str] = []
    date_key = {
        "margin_trading": "trade_date",
        "block_trade": "trade_date",
        "restricted_shares_unlock": "unlock_date",
    }
    for fname, comp in EXPECTED_FIXTURES.items():
        data = _load_fixture(fname)
        env = data["market_event"]
        payload = data[comp]
        if env["company_code"] != payload.get("company_code"):
            failures.append(f"{comp}:company_code_mismatch")
        dk = date_key[comp]
        if env["event_time"] != payload.get(dk):
            failures.append(f"{comp}:event_time_mismatch")
        if payload.get("quality_status") and env["quality_status"] != payload["quality_status"]:
            failures.append(f"{comp}:quality_status_mismatch")
        if payload.get("source_endpoint") and env["source_endpoint"] != payload["source_endpoint"]:
            failures.append(f"{comp}:source_endpoint_mismatch")
    ok = not failures
    return LintResult(
        "R-D-P1-007",
        "event envelope aligns with component payload",
        ok,
        "; ".join(failures) if failures else "relations valid",
    )


def check_quality_status_enum() -> LintResult:
    failures: List[str] = []
    for fname in EXPECTED_FIXTURES:
        data = _load_fixture(fname)
        env_qs = data["market_event"].get("quality_status")
        if env_qs not in QUALITY_STATUS_ENUM:
            failures.append(f"{fname}:envelope={env_qs}")
        comp = EXPECTED_FIXTURES[fname]
        comp_qs = data[comp].get("quality_status")
        if comp_qs and comp_qs not in QUALITY_STATUS_ENUM:
            failures.append(f"{fname}:component={comp_qs}")
    ok = not failures
    return LintResult(
        "R-D-P1-008",
        "quality_status enum valid",
        ok,
        "; ".join(failures) if failures else f"enum={sorted(QUALITY_STATUS_ENUM)}",
    )


def check_event_status_enum() -> LintResult:
    failures: List[str] = []
    for fname in EXPECTED_FIXTURES:
        es = _load_fixture(fname)["market_event"].get("event_status")
        if es not in EVENT_STATUS_ENUM:
            failures.append(f"{fname}={es}")
    ok = not failures
    return LintResult(
        "R-D-P1-009",
        "event_status enum valid",
        ok,
        "; ".join(failures) if failures else f"enum={sorted(EVENT_STATUS_ENUM)}",
    )


def check_source_mapping(registry_urls: Dict[str, str]) -> LintResult:
    failures: List[str] = []
    for comp, expected in SOURCE_ENDPOINT_BY_COMPONENT.items():
        reg = registry_urls.get(comp)
        if reg != expected:
            failures.append(f"{comp}:registry={reg}")
    for fname, comp in EXPECTED_FIXTURES.items():
        env_url = _load_fixture(fname)["market_event"]["source_endpoint"]
        if env_url != SOURCE_ENDPOINT_BY_COMPONENT[comp]:
            failures.append(f"fixture:{comp}")
    ok = not failures
    return LintResult(
        "R-D-P1-010",
        "source endpoint mapping matches registry and fixtures",
        ok,
        "; ".join(failures) if failures else "7 registry + 3 fixtures aligned",
    )


def _write_summary(results: List[LintResult], passed: int) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# CNINFO D 类 Phase 1 Schema Lint 摘要",
        "",
        f"_生成时间：{ts}_",
        "",
        "> **性质：** 离线 lint；CNINFO 请求 **0**",
        "",
        "## 结果",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| checks | {len(results)} |",
        f"| pass | {passed} |",
        f"| fail | {len(results) - passed} |",
        f"| gate | **`d_class_phase1_schema_lint_gate = {'PASS' if passed == len(results) else 'FAIL'}`** |",
        "",
        "## 规则明细",
        "",
        "| rule_id | description | pass | detail |",
        "|---------|-------------|------|--------|",
    ]
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        lines.append(f"| {r.rule_id} | {r.description} | {mark} | {r.detail} |")
    lines.extend(["", "## 红线", "", "- **CNINFO calls = 0**", "- **no live / harvest / PDF**", ""])
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    rows = _read_csv(FIELD_MATRIX)
    registry_urls = _load_registry_endpoints()

    results = [
        check_field_matrix_components(rows),
        check_quality_status_on_components(rows),
        check_forbidden_fields(rows),
        check_fixture_files_exist(),
        check_envelope_required_fields(),
        check_component_required_fields(),
        check_event_object_relation(),
        check_quality_status_enum(),
        check_event_status_enum(),
        check_source_mapping(registry_urls),
    ]

    passed = sum(1 for r in results if r.passed)
    _write_summary(results, passed)

    print(f"D-class Phase1 schema lint: {passed}/{len(results)} PASS")
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"  [{mark}] {r.rule_id}: {r.description} — {r.detail}")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

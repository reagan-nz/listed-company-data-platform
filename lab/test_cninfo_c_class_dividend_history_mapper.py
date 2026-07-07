"""
CNINFO C-class dividend_history mapper fixture tests（无网络）。

运行：
    python lab/test_cninfo_c_class_dividend_history_mapper.py

输出：
    outputs/validation/cninfo_c_class_dividend_history_mapper_test_summary.md
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_mappers import map_dividend_history  # noqa: E402

BASE_DIR = os.path.dirname(_LAB_DIR)
FIXTURES_PATH = os.path.join(
    BASE_DIR,
    "fixtures",
    "c_class",
    "dividend_history",
    "dividend_history_mapper_fixtures.json",
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_dividend_history_mapper_test_summary.md",
)


def _load_fixtures() -> List[Dict[str, Any]]:
    with open(FIXTURES_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    return data["fixtures"]


def _run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    expect = case["expect"]
    result = map_dividend_history(
        raw_input=case["raw_records"],
        company_code=case["company_code"],
        company_name=case.get("company_name", ""),
    )
    event = result["dividend_history"][0] if result["dividend_history"] else {}

    checks: List[str] = []
    ok = True

    if result["dividend_parse_status"] != expect["dividend_parse_status"]:
        ok = False
        checks.append(
            f"company parse_status: got {result['dividend_parse_status']} "
            f"expected {expect['dividend_parse_status']}"
        )
    if result["record_count"] != expect["event_count"]:
        ok = False
        checks.append(
            f"event_count: got {result['record_count']} expected {expect['event_count']}"
        )
    if "dividend_method" in expect and event.get("dividend_method") != expect["dividend_method"]:
        ok = False
        checks.append(
            f"dividend_method: got {event.get('dividend_method')} expected {expect['dividend_method']}"
        )
    if "cash_dividend_per_share" in expect:
        got = event.get("cash_dividend_per_share")
        exp = expect["cash_dividend_per_share"]
        if got is None or abs(got - exp) > 1e-9:
            ok = False
            checks.append(f"cash_dividend_per_share: got {got} expected {exp}")
    if "stock_dividend_ratio" in expect:
        got = event.get("stock_dividend_ratio")
        exp = expect["stock_dividend_ratio"]
        if got is None or abs(got - exp) > 1e-9:
            ok = False
            checks.append(f"stock_dividend_ratio: got {got} expected {exp}")
    if "transfer_ratio" in expect:
        got = event.get("transfer_ratio")
        exp = expect["transfer_ratio"]
        if got is None or abs(got - exp) > 1e-9:
            ok = False
            checks.append(f"transfer_ratio: got {got} expected {exp}")

    if expect["event_count"] == 1:
        if not event.get("dividend_plan_text_raw"):
            ok = False
            checks.append("missing dividend_plan_text_raw on event")
        if result["source_evidence"]["source_id"] != "cninfo_dividend_financing_profile":
            ok = False
            checks.append("source_evidence.source_id mismatch")

    return {
        "case_id": case["case_id"],
        "description": case["description"],
        "pass": ok,
        "checks": checks,
        "result_snapshot": {
            "dividend_parse_status": result["dividend_parse_status"],
            "record_count": result["record_count"],
            "first_event": event,
        },
    }


def write_summary(results: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    lines = [
        "# CNINFO C-Class dividend_history Mapper Test Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        "**fixture-only**（无 CNINFO 请求）",
        "",
        f"## Result: **{passed}/{total} PASS**",
        "",
        "| case_id | description | result |",
        "|---------|-------------|--------|",
    ]
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        lines.append(f"| `{r['case_id']}` | {r['description']} | **{status}** |")

    lines.extend(["", "## Details", ""])
    for r in results:
        lines.append(f"### `{r['case_id']}` — {r['description']}")
        lines.append("")
        lines.append(f"- **result:** {'PASS' if r['pass'] else 'FAIL'}")
        if r["checks"]:
            for c in r["checks"]:
                lines.append(f"- {c}")
        else:
            lines.append("- all checks passed")
        lines.append("")

    lines.extend([
        "## Caveats",
        "",
        "- mapper 实现：`lab/cninfo_c_class_mappers.py` · `map_dividend_history()`",
        "- harvest 入口：`lab/harvest_cninfo_c_class.py`（import）",
        "- **no verified** · **no harvest execution**",
        "",
    ])

    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    fixtures = _load_fixtures()
    results = [_run_case(c) for c in fixtures]
    write_summary(results)
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    print(f"SUMMARY  dividend_history_mapper_tests  pass={passed}/{total}")
    for r in results:
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"  {r['case_id']}: {mark}")
    print(f"MD    {SUMMARY_PATH}")
    if passed != total:
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
CNINFO C-class basic profile mapper fixture tests（无网络）。

运行：
    python lab/test_cninfo_c_class_mappers.py

覆盖 establishment_date（F010D）映射五类场景。
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_mappers import map_company_basic_profile  # noqa: E402


def _basic_raw(f010d: Any = "__MISSING__", *, include_basic: bool = True) -> Dict[str, Any]:
  """构造 minimal raw_record；f010d=__MISSING__ 表示不含 F010D 键。"""
  basic: Dict[str, Any] = {
      "ASECCODE": "000001",
      "ASECNAME": "测试公司",
      "ORGNAME": "测试公司股份有限公司",
      "F006D": "1991-04-03",
  }
  if f010d != "__MISSING__":
      basic["F010D"] = f010d
  raw: Dict[str, Any] = {"listingInformation": [{"SECCODE": "000001"}]}
  if include_basic:
      raw["basicInformation"] = [basic]
  return raw


CASES: List[Dict[str, Any]] = [
    {
        "case_id": "case_1_normal_date",
        "raw": _basic_raw("1990-09-01"),
        "expect": {
            "establishment_date": "1990-09-01",
            "establishment_date_parse_status": "parsed",
        },
    },
    {
        "case_id": "case_2_null",
        "raw": _basic_raw(None),
        "expect": {
            "establishment_date": None,
            "establishment_date_parse_status": "null_but_valid",
        },
    },
    {
        "case_id": "case_3_empty_string",
        "raw": _basic_raw(""),
        "expect": {
            "establishment_date": None,
            "establishment_date_parse_status": "null_but_valid",
        },
    },
    {
        "case_id": "case_4_nonstandard_date",
        "raw": _basic_raw("约1990年"),
        "expect": {
            "establishment_date": "约1990年",
            "establishment_date_parse_status": "needs_review",
            "establishment_date_field_quality": "nonstandard_date",
        },
    },
    {
        "case_id": "case_5_missing_f010d",
        "raw": _basic_raw(),
        "expect": {
            "establishment_date": None,
            "establishment_date_parse_status": "null_but_valid",
        },
    },
]


def _run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = map_company_basic_profile(
        case["raw"],
        company_code="000001",
        company_name="测试公司",
    )
    assert result is not None, "mapper 不应因 establishment_date 失败返回 None"
    expect = case["expect"]
    checks: List[str] = []
    ok = True
    for key, expected in expect.items():
        got = result.get(key)
        if got != expected:
            ok = False
            checks.append(f"{key}: got {got!r} expected {expected!r}")
    return {
        "case_id": case["case_id"],
        "pass": ok,
        "checks": checks,
    }


def main() -> int:
    results = [_run_case(c) for c in CASES]
    failed = [r for r in results if not r["pass"]]
    for row in results:
        status = "PASS" if row["pass"] else "FAIL"
        print(f"{row['case_id']}: {status}")
        for msg in row["checks"]:
            print(f"  - {msg}")
    print(f"\nTotal: {len(results)} | PASS: {len(results) - len(failed)} | FAIL: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

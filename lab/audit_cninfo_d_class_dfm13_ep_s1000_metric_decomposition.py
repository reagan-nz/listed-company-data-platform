#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-FM-13（equity_pledge further-scale S1000，DEP501-1500）指标解构离线审计。

目的：
不新增任何 CNINFO 请求；仅读取已存在的 D-FM-13 live 产物（live_report.csv +
live_snapshots/*.json + 冻结的 s50/s200 already-live 结果），把原始
"1000/1000 excellence" 单一指标拆解为可追溯的分类计数，纠正
SYNTHETIC_PADDED_EMPTY 被计为 hit 的膨胀问题。

分类规则（每条记录只归入其中一类）：
- REAL_FOUND：record_count > 0，company_name 非 empty_control_* 占位符。
- ENDPOINT_CONFIRMED_EMPTY：record_count == 0，且 company_code 有可验证的、
  非序列占位符命名的目标身份来源（当前 D-FM-13 数据中未观察到此类记录）。
- SYNTHETIC_PADDED_EMPTY：record_count == 0 且 company_name 匹配
  `empty_control_<code>` 占位符命名规则（runner 用连续 SECCODE 序列填充，
  未针对该 company 发起过任何专门请求）。
- CACHED_RESULT：命中来自既有缓存快照而非本次共享探针（当前未观察到）。
- REQUEST_FAILED：retrieval_status 标记失败/超时（当前未观察到）。
- UNMAPPED_OR_UNQUERIED：无法证明该 target 曾被请求/响应覆盖（本审计中与
  SYNTHETIC_PADDED_EMPTY 为同一人群，因为 867 条 empty_control_* 记录既是
  占位符也从未被单独查询——两个标签均适用，本脚本分别输出两个计数但不重复计入
  best-estimate 汇总，以 SYNTHETIC_PADDED_EMPTY 为主分类）。

这是一次离线审计脚本，不发起任何新的 CNINFO 请求。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from typing import Any, Dict, List, Set

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_LIVE_REPORT = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_d_class_equity_pledge_further_scale_s1000/"
    "reports/d_class_equity_pledge_further_scale_s1000_live_report.csv",
)

KNOWN_POSITIVE_REPORTS = [
    os.path.join(
        BASE_DIR,
        "outputs/validation/cninfo_d_class_equity_pledge_further_scale/"
        "reports/d_class_equity_pledge_further_scale_live_report.csv",
    ),
    os.path.join(
        BASE_DIR,
        "outputs/validation/cninfo_d_class_equity_pledge_further_scale_s200/"
        "reports/d_class_equity_pledge_further_scale_s200_live_report.csv",
    ),
]


def _read_rows(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _is_synthetic_placeholder(company_name: str) -> bool:
    return bool(company_name) and company_name.startswith("empty_control_")


def load_known_positive_codes() -> Set[str]:
    codes: Set[str] = set()
    for path in KNOWN_POSITIVE_REPORTS:
        for row in _read_rows(path):
            try:
                record_count = int(row.get("record_count") or 0)
            except ValueError:
                record_count = 0
            if record_count > 0:
                codes.add(str(row.get("company_code", "")))
    return codes


def decompose(live_report_path: str = DEFAULT_LIVE_REPORT) -> Dict[str, Any]:
    rows = _read_rows(live_report_path)
    target_count = len(rows)

    real_found = 0
    endpoint_confirmed_empty = 0
    synthetic_padded_empty = 0
    cached_result = 0
    request_failed = 0
    unmapped_or_unqueried = 0

    for row in rows:
        try:
            record_count = int(row.get("record_count") or 0)
        except ValueError:
            record_count = 0
        company_name = row.get("company_name") or ""
        retrieval_status = (row.get("retrieval_status") or "").strip()

        if retrieval_status in {"failed", "http_error", "timeout"}:
            request_failed += 1
            continue

        if record_count > 0 and not _is_synthetic_placeholder(company_name):
            real_found += 1
            continue

        if record_count == 0 and _is_synthetic_placeholder(company_name):
            synthetic_padded_empty += 1
            unmapped_or_unqueried += 1
            continue

        if record_count == 0:
            # 非占位符命名但仍为空：视为端点确认空（本数据集中未观察到此类行）。
            endpoint_confirmed_empty += 1
            continue

        # record_count > 0 但命名仍是占位符：不应发生，归类为需人工复核。
        cached_result += 1

    response_mapped_count = real_found + endpoint_confirmed_empty
    request_coverage_count = 10  # 共享 tdate_daily 多日联合探针的真实请求数（非按公司计数）

    known_positive_codes = load_known_positive_codes()
    target_codes = {row.get("company_code", "") for row in rows}
    known_positive_tested = known_positive_codes & target_codes
    known_positive_found = {
        row.get("company_code", "")
        for row in rows
        if row.get("company_code", "") in known_positive_codes
        and int(row.get("record_count") or 0) > 0
    }

    real_found_rate = (real_found / target_count) if target_count else 0.0
    endpoint_confirmed_empty_rate = (endpoint_confirmed_empty / target_count) if target_count else 0.0
    synthetic_padding_rate = (synthetic_padded_empty / target_count) if target_count else 0.0
    evidence_traceability_rate = (response_mapped_count / target_count) if target_count else 0.0

    if known_positive_tested:
        known_positive_recall = len(known_positive_found) / len(known_positive_tested)
    else:
        known_positive_recall = None  # DATA_COVERAGE_UNVERIFIED：本轮目标未覆盖任何已知正例

    if request_failed > 0:
        status = "FAIL_REVIEW_REQUIRED"
    elif known_positive_recall is None:
        status = "DATA_COVERAGE_UNVERIFIED"
    elif known_positive_recall >= 0.95 and synthetic_padding_rate <= 0.10:
        status = "DATA_COVERAGE_PASS"
    else:
        status = "PASS_WITH_CAVEAT"

    return {
        "source_report": os.path.relpath(live_report_path, BASE_DIR),
        "target_count": target_count,
        "request_coverage_count": request_coverage_count,
        "response_mapped_count": response_mapped_count,
        "real_found_count": real_found,
        "endpoint_confirmed_empty_count": endpoint_confirmed_empty,
        "synthetic_padded_empty_count": synthetic_padded_empty,
        "cached_count": cached_result,
        "request_failed_count": request_failed,
        "unmapped_or_unqueried_count": unmapped_or_unqueried,
        "real_found_rate": round(real_found_rate, 4),
        "endpoint_confirmed_empty_rate": round(endpoint_confirmed_empty_rate, 4),
        "synthetic_padding_rate": round(synthetic_padding_rate, 4),
        "evidence_traceability_rate": round(evidence_traceability_rate, 4),
        "known_positive_tested": len(known_positive_tested),
        "known_positive_found": len(known_positive_found),
        "known_positive_recall": (
            round(known_positive_recall, 4) if known_positive_recall is not None else None
        ),
        "status": status,
        "note": (
            "known_positive_tested=0 because s50/s200 found codes were explicitly "
            "excluded from the S1000 target universe (no leakage); this means "
            "recall cannot be measured from this run's own data -> "
            "DATA_COVERAGE_UNVERIFIED, not a manufactured PASS."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-report", default=DEFAULT_LIVE_REPORT)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    result = decompose(args.live_report)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-FM-22：executive_shareholding_summary bounded endpoint probe。

规则：
  - 仅探 H1 `data20/leader/summary`；失败再 H2 `data20/leader/statistics`
  - 硬顶 CNINFO ≤ 2（prefer ≤ 2）
  - 默认 dry-run（CNINFO=0）；live 须 --live + 显式 approve flag
  - 不写 FIA / ES detail / AT / SD 既有 live 根
  - 不 reopen DLC006R · 不写 registry testing_stable · 不 verified
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

TASK_ID = "D-FM-22"
COMPONENT = "executive_shareholding_summary"
MAX_CNINFO = 2
HARD_CAP = 2
REQUEST_TIMEOUT = 10
SLEEP_SECONDS = 0.6

H1_URL = "https://www.cninfo.com.cn/data20/leader/summary"
H2_URL = "https://www.cninfo.com.cn/data20/leader/statistics"
PAGE_URL = (
    "https://www.cninfo.com.cn/new/commonUrl?url=data/person-stock-data-tables"
)
# 与 sibling executive_shareholding / leader/detail 默认查询对称
DEFAULT_PARAMS = {"timeMark": "oneMonth", "varyType": "b"}

DEFAULT_OUTPUT_DIR = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_executive_shareholding_summary_endpoint_probe",
)

# 禁止写入的既有 live 根（相对 repo）
PROTECTED_LIVE_ROOTS = (
    "outputs/validation/cninfo_d_class_executive_shareholding_first_slice",
    "outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice",
    "outputs/validation/cninfo_d_class_fund_industry_allocation_dfia005_single_probe",
    "outputs/validation/cninfo_d_class_abnormal_trading_first_slice",
    "outputs/validation/cninfo_d_class_shareholder_data_first_slice",
)

AJAX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/ess-endpoint-probe"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": PAGE_URL,
}

GATE_PASS = "PASS_WITH_CAVEAT"
GATE_FAIL = "FAIL_REVIEW_REQUIRED"
GATE_PARTIAL = "PASS_OFFLINE_ENDPOINT_REACHABLE"
LIVE_GATE = "NOT_APPROVED"  # first-slice live 未批准；本任务仅 endpoint probe


def _ensure_output_dir(path: str) -> str:
    out = os.path.abspath(path)
    # 硬拒绝写入受保护 live 根
    for protected in PROTECTED_LIVE_ROOTS:
        abs_p = os.path.abspath(os.path.join(_BASE_DIR, protected))
        if out == abs_p or out.startswith(abs_p + os.sep):
            raise SystemExit(f"ERROR: refuse_write_protected_live_root:{protected}")
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.join(out, "reports"), exist_ok=True)
    os.makedirs(os.path.join(out, "probe_captures"), exist_ok=True)
    return out


def _write_csv(path: str, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _extract_records(payload: Any) -> Tuple[List[Any], str]:
    """尝试从常见 CNINFO data20 形状提取 records。"""
    if not isinstance(payload, dict):
        return [], "non_dict_payload"
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("records"), list):
        return data["records"], "data.records"
    if isinstance(payload.get("records"), list):
        return payload["records"], "records"
    if isinstance(data, list):
        return data, "data"
    return [], "no_records_path"


def _classify_response(
    http_status: int,
    payload: Any,
    parse_error: str,
) -> Tuple[str, int, str, List[str]]:
    """
    返回 (classification, record_count, records_path, sample_keys)。
    classification:
      confirmed_with_records | confirmed_empty_valid |
      reachable_shape_review | rejected | invalid_payload
    """
    if http_status == 0:
        return "rejected", 0, "", []
    if http_status == 404:
        return "rejected", 0, "", []
    if http_status == 429:
        return "rejected", 0, "", []
    if http_status != 200:
        return "rejected", 0, "", []
    if parse_error:
        return "invalid_payload", 0, "", []
    records, path = _extract_records(payload)
    sample_keys: List[str] = []
    if records and isinstance(records[0], dict):
        sample_keys = sorted(str(k) for k in records[0].keys())
    if path == "no_records_path":
        # HTTP 200 JSON 但非预期 records 形状 — URL 可达，语义待审
        top_keys = sorted(str(k) for k in payload.keys()) if isinstance(payload, dict) else []
        return "reachable_shape_review", 0, "", top_keys
    if len(records) == 0:
        return "confirmed_empty_valid", 0, path, sample_keys
    return "confirmed_with_records", len(records), path, sample_keys


def _post_query(
    session: requests.Session,
    url: str,
    params: Dict[str, str],
) -> Tuple[int, Any, str, str]:
    """POST with query params（与 sibling leader/detail params_location=query 一致）。"""
    try:
        resp = session.post(url, params=params, headers=AJAX_HEADERS, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        return 0, None, f"network_error:{exc}", ""
    body_text = resp.text[:4000] if resp.text else ""
    if resp.status_code != 200:
        return resp.status_code, None, f"http_{resp.status_code}", body_text[:500]
    try:
        return resp.status_code, resp.json(), "", body_text
    except json.JSONDecodeError:
        return resp.status_code, None, "invalid_json", body_text[:500]


def run_dry_run(output_dir: str) -> int:
    """离线 dry-run：写出探针计划 · CNINFO=0。"""
    out = _ensure_output_dir(output_dir)
    plan = {
        "task_id": TASK_ID,
        "component": COMPONENT,
        "mode": "dry_run",
        "cninfo_budget": MAX_CNINFO,
        "hard_cap": HARD_CAP,
        "probe_sequence": [
            {
                "order": 1,
                "hyp_id": "H1",
                "method": "POST",
                "url": H1_URL,
                "params": DEFAULT_PARAMS,
                "params_location": "query",
            },
            {
                "order": 2,
                "hyp_id": "H2",
                "method": "POST",
                "url": H2_URL,
                "params": DEFAULT_PARAMS,
                "params_location": "query",
                "condition": "only_if_H1_rejected_or_invalid",
            },
        ],
        "protected_live_roots_not_mutated": list(PROTECTED_LIVE_ROOTS),
        "registry_write": False,
        "verified_claim": False,
    }
    plan_path = os.path.join(out, "reports", "ess_endpoint_probe_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(
        f"mode=ess_endpoint_probe_dry_run cninfo_calls=0 "
        f"planned_cninfo_budget={MAX_CNINFO} plan={plan_path}"
    )
    return 0


def execute_live_probe(
    output_dir: str,
    session: Optional[requests.Session] = None,
) -> int:
    """执行 H1→(fail)H2 有界探针 · 硬顶 CNINFO≤2。"""
    out = _ensure_output_dir(output_dir)
    sess = session or requests.Session()
    cninfo_calls = 0
    attempts: List[Dict[str, Any]] = []

    sequence = [
        ("H1", H1_URL),
        ("H2", H2_URL),
    ]

    final_class = "unprobed"
    final_hyp = ""
    final_url = ""
    final_records_path = ""
    final_record_count = 0
    final_sample_keys: List[str] = []
    stop_reason = ""

    for hyp_id, url in sequence:
        if cninfo_calls >= HARD_CAP:
            stop_reason = "hard_cap_reached"
            break
        http_status, payload, parse_error, body_snippet = _post_query(
            sess, url, DEFAULT_PARAMS
        )
        cninfo_calls += 1
        time.sleep(SLEEP_SECONDS)
        classification, rec_count, rec_path, sample_keys = _classify_response(
            http_status, payload, parse_error
        )
        attempt = {
            "hyp_id": hyp_id,
            "url": url,
            "params": dict(DEFAULT_PARAMS),
            "http_status": http_status,
            "classification": classification,
            "record_count": rec_count,
            "records_path": rec_path,
            "sample_keys": sample_keys,
            "parse_error": parse_error,
            "cninfo_call_index": cninfo_calls,
        }
        attempts.append(attempt)

        # 落盘捕获（截断）— 仅本探针根
        capture = {
            "task_id": TASK_ID,
            "hyp_id": hyp_id,
            "url": url,
            "params": dict(DEFAULT_PARAMS),
            "http_status": http_status,
            "classification": classification,
            "record_count": rec_count,
            "records_path": rec_path,
            "sample_keys": sample_keys,
            "parse_error": parse_error,
            "payload_truncated": None,
            "body_snippet": body_snippet[:800] if parse_error else "",
        }
        if isinstance(payload, dict):
            # 截断 records 样本，避免巨大落盘
            truncated = dict(payload)
            data = truncated.get("data")
            if isinstance(data, dict) and isinstance(data.get("records"), list):
                truncated = {
                    **truncated,
                    "data": {
                        **data,
                        "records": data["records"][:5],
                        "_records_truncated": True,
                        "_records_total_observed": len(data["records"]),
                    },
                }
            capture["payload_truncated"] = truncated
        cap_path = os.path.join(out, "probe_captures", f"{hyp_id.lower()}_capture.json")
        with open(cap_path, "w", encoding="utf-8") as f:
            json.dump(capture, f, ensure_ascii=False, indent=2)
            f.write("\n")

        final_class = classification
        final_hyp = hyp_id
        final_url = url
        final_records_path = rec_path
        final_record_count = rec_count
        final_sample_keys = sample_keys

        # H1 成功或可达 → 不再烧 H2
        if classification in (
            "confirmed_with_records",
            "confirmed_empty_valid",
            "reachable_shape_review",
        ):
            stop_reason = f"stop_after_{hyp_id}_{classification}"
            break
        # H1 rejected/invalid → 继续 H2（若预算允许）
        if hyp_id == "H1":
            continue
        stop_reason = f"stop_after_{hyp_id}_{classification}"

    # gate 判定
    if final_class == "confirmed_with_records":
        gate = GATE_PASS
        endpoint_status = "confirmed_candidate"
        caveat = "records_present_ui_field_mapping_pending; NOT verified"
    elif final_class == "confirmed_empty_valid":
        gate = GATE_PASS
        endpoint_status = "confirmed_candidate_empty"
        caveat = "empty_but_valid_structure; UI field mapping pending; NOT verified"
    elif final_class == "reachable_shape_review":
        gate = GATE_PARTIAL
        endpoint_status = "reachable_shape_review"
        caveat = "http_200_json_but_records_path_unexpected; DevTools_or_shape_review"
    else:
        gate = GATE_FAIL
        endpoint_status = "unconfirmed_probe_failed"
        caveat = "H1_and_or_H2_rejected_or_invalid; optional_DevTools"

    # report csv
    report_rows = []
    for a in attempts:
        report_rows.append(
            {
                "task_id": TASK_ID,
                "hyp_id": a["hyp_id"],
                "url": a["url"],
                "timeMark": DEFAULT_PARAMS["timeMark"],
                "varyType": DEFAULT_PARAMS["varyType"],
                "http_status": str(a["http_status"]),
                "classification": a["classification"],
                "record_count": str(a["record_count"]),
                "records_path": a["records_path"],
                "sample_keys": "|".join(a["sample_keys"]),
                "parse_error": a["parse_error"],
                "cninfo_call_index": str(a["cninfo_call_index"]),
            }
        )
    report_path = os.path.join(out, "reports", "ess_endpoint_probe_live_report.csv")
    _write_csv(
        report_path,
        report_rows,
        [
            "task_id",
            "hyp_id",
            "url",
            "timeMark",
            "varyType",
            "http_status",
            "classification",
            "record_count",
            "records_path",
            "sample_keys",
            "parse_error",
            "cninfo_call_index",
        ],
    )

    result = {
        "task_id": TASK_ID,
        "component": COMPONENT,
        "mode": "live",
        "cninfo_calls": cninfo_calls,
        "hard_cap": HARD_CAP,
        "final_hyp": final_hyp,
        "final_url": final_url,
        "final_classification": final_class,
        "endpoint_status": endpoint_status,
        "record_count": final_record_count,
        "records_path": final_records_path,
        "sample_keys": final_sample_keys,
        "probe_gate": gate,
        "live_gate": LIVE_GATE,
        "caveat": caveat,
        "stop_reason": stop_reason,
        "attempts": attempts,
        "protected_live_roots_mutated": False,
        "registry_write": False,
        "verified_claim": False,
    }
    result_path = os.path.join(out, "reports", "ess_endpoint_probe_live_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    summary_md = os.path.join(out, "reports", "ess_endpoint_probe_live_summary.md")
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write(
            "\n".join(
                [
                    "# CNINFO D 类 executive_shareholding_summary — Endpoint Probe Live",
                    "",
                    f"_生成时间：{ts} · {TASK_ID}_",
                    "",
                    f"> **性质：** bounded H1→H2 endpoint probe · **CNINFO≤{HARD_CAP}** · "
                    f"**live_gate={LIVE_GATE}** · **NOT verified** · **NOT production_ready**",
                    "",
                    "## Result",
                    "",
                    "| 项 | 值 |",
                    "|----|-----|",
                    f"| final_hyp | **{final_hyp or '—'}** |",
                    f"| final_url | `{final_url or '—'}` |",
                    f"| classification | `{final_class}` |",
                    f"| endpoint_status | **{endpoint_status}** |",
                    f"| records | **{final_record_count}** |",
                    f"| records_path | `{final_records_path or '—'}` |",
                    f"| sample_keys | `{('|'.join(final_sample_keys)) or '—'}` |",
                    f"| CNINFO calls | **{cninfo_calls}** |",
                    f"| stop_reason | `{stop_reason}` |",
                    f"| caveat | `{caveat}` |",
                    "",
                    "## Attempts",
                    "",
                ]
            )
        )
        for a in attempts:
            f.write(
                f"- **{a['hyp_id']}** `{a['url']}` · http={a['http_status']} · "
                f"`{a['classification']}` · records={a['record_count']} · "
                f"path=`{a['records_path'] or '—'}`\n"
            )
        f.write(
            "\n".join(
                [
                    "",
                    "## Gates",
                    "",
                    "```text",
                    f"d_class_executive_shareholding_summary_endpoint_probe_gate = {gate}",
                    f"endpoint_status = {endpoint_status}",
                    f"cninfo_calls = {cninfo_calls}",
                    f"live_gate = {LIVE_GATE}",
                    "```",
                    "",
                    "## Explicit Non-Claims",
                    "",
                    "- 不 claim verified / production_ready / bare PASS",
                    "- 不写入 registry `testing_stable_sample`",
                    "- 不 mutate FIA / ES detail / AT / SD live 根",
                    "- 不 reopen DLC006R",
                    "",
                ]
            )
            + "\n"
        )

    print(
        f"mode=ess_endpoint_probe_live gate={gate} "
        f"endpoint_status={endpoint_status} classification={final_class} "
        f"cninfo_calls={cninfo_calls} hyp={final_hyp}",
        flush=True,
    )
    print(f"live_report={report_path}")
    print(f"live_summary={summary_md}")
    print(f"live_result={result_path}")
    return 0 if gate in (GATE_PASS, GATE_PARTIAL) else 1


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="ESS bounded endpoint probe H1→H2 (CNINFO≤2)"
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="离线计划 · CNINFO=0")
    mode.add_argument("--live", action="store_true", help="真实探针 · CNINFO≤2")
    p.add_argument(
        "--approve-d-class-executive-shareholding-summary-endpoint-probe",
        action="store_true",
        help="standing capital 显式批准本 endpoint probe live",
    )
    p.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.dry_run:
        return run_dry_run(args.output_dir)
    if args.live:
        if not args.approve_d_class_executive_shareholding_summary_endpoint_probe:
            print(
                "ERROR: approve_d_class_executive_shareholding_summary_endpoint_probe_required",
                file=sys.stderr,
            )
            return 2
        return execute_live_probe(args.output_dir)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

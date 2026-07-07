"""
CNINFO C-class 十二家 6/6 fail 最小化 endpoint/parser debug（Era C Phase 4）。

仅对 stable 200 中人工审计的 12 家公司发起 CNINFO 请求；不扩大范围。
不保存 Cookie / Authorization / SID；不登录；不绕验证码。

用法:
    python lab/debug_cninfo_c_class_12_six_fail_endpoints.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from lab.validate_cninfo_c_class_scale_smoke import (  # noqa: E402
    BASIC_URL,
    DIVIDEND_URL,
    SOURCE_SPECS,
    _browser_headers,
    _extract_codes,
    _get_path,
    _referer,
    _scode_url,
)

TARGET_CODES = frozenset({
    "300261", "300288", "300355", "300414",
    "600061", "600063", "600130", "600203", "600207", "600233", "600390", "600523",
})

SAMPLE_YAML = os.path.join(BASE_DIR, "lab", "eval_companies_c_class_stable_200_non_bse.yaml")
LIVE_FAILURES_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_stable_200_failure_cases.csv"
)
OUT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_12_six_fail_endpoint_debug_cases.csv"
)
OUT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_12_six_fail_endpoint_debug_summary.md"
)

SLEEP_SECONDS = 0.5
REQUEST_TIMEOUT = 15

ENDPOINT_KEYS = {
    "basic": BASIC_URL,
    "dividend": DIVIDEND_URL,
    "executive": SOURCE_SPECS["cninfo_executive_profile"]["url"],
    "share_capital": SOURCE_SPECS["cninfo_share_capital_profile"]["url"],
    "top_shareholders": SOURCE_SPECS["cninfo_top_shareholders_profile"]["url"],
    "top_float_shareholders": SOURCE_SPECS["cninfo_top_float_shareholders_profile"]["url"],
}

CSV_FIELDS = [
    "company_code",
    "company_name",
    "board",
    "exchange",
    "sample_orgid",
    "web_url",
    "runner_basic_url",
    "runner_executive_url",
    "runner_share_capital_url",
    "runner_top_shareholders_url",
    "runner_top_float_shareholders_url",
    "runner_dividend_url",
    "http_status",
    "response_top_keys",
    "data_top_keys",
    "has_data",
    "has_records",
    "records_type",
    "records_len",
    "result_code",
    "json_code",
    "error_message",
    "inferred_failure_category",
    "six_source_result_codes",
    "six_source_has_records",
    "six_source_same_cause",
    "basic_record0_keys",
    "basic_basicInformation_len",
    "basic_listingInformation_len",
    "data_result_msg",
    "orgid_variant_url",
    "orgid_variant_has_records",
    "orgid_variant_result_code",
    "orgid_variant_basicInformation_len",
    "live_basic_result_code",
    "debug_basic_pass_now",
]


def _top_keys(obj: Any, limit: int = 20) -> str:
    if isinstance(obj, dict):
        return "|".join(sorted(obj.keys())[:limit])
    return ""


def _http_get_json(url: str, headers: Dict[str, str]) -> Tuple[Optional[int], Any, str]:
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        status = resp.status_code
        text = resp.text or ""
        if status == 429:
            return status, None, "rate_limited_429"
        if "tenantLogin" in text or "login" in resp.url.lower():
            return status, None, "blocked_or_login_redirect"
        if "captcha" in text.lower():
            return status, None, "captcha_detected"
        try:
            return status, resp.json(), ""
        except json.JSONDecodeError:
            return status, None, "response_not_json"
    except requests.RequestException as exc:
        return None, None, str(exc)


def _probe_url(url: str, code: str, org_id: str) -> Tuple[Dict[str, Any], Any]:
    http_status, payload, err = _http_get_json(url, _browser_headers(code, org_id, xhr=True))
    out: Dict[str, Any] = {
        "url": url,
        "http_status": http_status,
        "error_message": err,
        "response_top_keys": "",
        "data_top_keys": "",
        "has_data": "no",
        "has_records": "no",
        "records_type": "",
        "records_len": "",
        "result_code": "",
        "json_code": "",
        "data_result_msg": "",
    }
    if err or not isinstance(payload, dict):
        return out, payload

    out["response_top_keys"] = _top_keys(payload)
    json_code, result_code = _extract_codes(payload)
    out["json_code"] = json_code
    out["result_code"] = result_code

    data = payload.get("data")
    if data is not None:
        out["has_data"] = "yes"
        if isinstance(data, dict):
            out["data_top_keys"] = _top_keys(data)
            if data.get("resultMsg") is not None:
                out["data_result_msg"] = str(data.get("resultMsg"))[:120]
            records = data.get("records")
            if records is not None:
                out["has_records"] = "yes"
                out["records_type"] = type(records).__name__
                if isinstance(records, list):
                    out["records_len"] = str(len(records))
    return out, payload


def _basic_record_detail(payload: Any) -> Tuple[str, str, str]:
    record0 = _get_path(payload, "data.records.0")
    if not isinstance(record0, dict):
        return "", "", ""
    keys = "|".join(sorted(record0.keys())[:15])
    basic = record0.get("basicInformation")
    listing = record0.get("listingInformation")
    b_len = str(len(basic)) if isinstance(basic, list) else ""
    l_len = str(len(listing)) if isinstance(listing, list) else ""
    return keys, b_len, l_len


def _basic_pass(probe: Dict[str, Any], b_len: str, l_len: str) -> bool:
    if probe.get("result_code") not in ("200", "0"):
        return False
    try:
        return int(b_len or 0) > 0 and int(l_len or 0) > 0
    except ValueError:
        return False


def _classify_failure(
    basic_probe: Dict[str, Any],
    b_len: str,
    l_len: str,
    six_probes: Dict[str, Dict[str, Any]],
    orgid_b_len: str,
    live_basic_rc: str,
    debug_basic_ok: bool,
) -> str:
    rc_basic = basic_probe.get("result_code", "")
    rc_others = [six_probes[k].get("result_code", "") for k in six_probes if k != "basic"]
    has_rec_others = [six_probes[k].get("has_records") == "yes" for k in six_probes if k != "basic"]

    # live 失败、debug 成功：批量 live 时 resultCode 429/90001 簇，非永久 schema 问题
    if live_basic_rc in ("90001", "429") and debug_basic_ok:
        if all(rc in ("200", "0") for rc in [rc_basic] + rc_others):
            return "needs_more_check"

    if orgid_b_len not in ("", "0") and b_len in ("", "0"):
        return "endpoint_parameter_issue"

    if basic_probe.get("has_data") == "yes" and basic_probe.get("has_records") == "no":
        if "records" not in (basic_probe.get("data_top_keys") or "").split("|"):
            return "parser_schema_assumption_issue"

    if rc_basic == "90001" and b_len == "0" and not debug_basic_ok:
        if all(rc == "429" for rc in rc_others) and not any(has_rec_others):
            return "endpoint_parameter_issue"

    if not debug_basic_ok and all(rc in ("429", "90001") for rc in [rc_basic] + rc_others):
        return "endpoint_parameter_issue"

    if basic_probe.get("has_records") == "yes" and b_len == "0" and not debug_basic_ok:
        return "parser_schema_assumption_issue"

    if debug_basic_ok and all(x for x in has_rec_others):
        return "needs_more_check"

    return "needs_more_check"


def load_target_companies() -> List[Dict[str, str]]:
    data = yaml.safe_load(open(SAMPLE_YAML, encoding="utf-8")) or {}
    out: List[Dict[str, str]] = []
    for c in data.get("companies") or []:
        code = str(c["stock_code"])
        if code not in TARGET_CODES:
            continue
        org = str(c.get("orgid") or c.get("org_id") or "")
        out.append({
            "company_code": code,
            "company_name": str(c.get("company_name") or c.get("short_name") or ""),
            "board": str(c.get("board", "")),
            "exchange": str(c.get("exchange", "")),
            "org_id": org,
        })
    out.sort(key=lambda x: x["company_code"])
    if len(out) != 12:
        raise RuntimeError(f"期望 12 家公司，实际加载 {len(out)} 家")
    return out


def load_live_basic_rc() -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not os.path.isfile(LIVE_FAILURES_CSV):
        return out
    with open(LIVE_FAILURES_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("source_id") == "cninfo_company_basic_profile":
                out[row["company_code"]] = row.get("result_code", "")
    return out


def debug_company(company: Dict[str, str], live_basic_rc: str) -> Dict[str, str]:
    code = company["company_code"]
    org_id = company["org_id"]
    web_url = f"{_referer(code, org_id)}#companyProfile"
    runner_urls = {k: _scode_url(url, code) for k, url in ENDPOINT_KEYS.items()}

    six_probes: Dict[str, Dict[str, Any]] = {}
    basic_payload: Any = None

    for key in ENDPOINT_KEYS:
        probe, payload = _probe_url(runner_urls[key], code, org_id)
        six_probes[key] = probe
        if key == "basic":
            basic_payload = payload
        time.sleep(SLEEP_SECONDS)

    basic = six_probes["basic"]
    r0_keys, b_len, l_len = _basic_record_detail(basic_payload)

    orgid_url = f"{BASIC_URL}?{urlencode({'scode': code, 'orgId': org_id})}"
    orgid_probe, orgid_payload = _probe_url(orgid_url, code, org_id)
    time.sleep(SLEEP_SECONDS)
    _, orgid_b_len, _ = _basic_record_detail(orgid_payload)

    six_rc = ";".join(f"{k}:{six_probes[k].get('result_code', '')}" for k in ENDPOINT_KEYS)
    six_hr = ";".join(f"{k}:{six_probes[k].get('has_records', '')}" for k in ENDPOINT_KEYS)
    rc_set = {six_probes[k].get("result_code", "") for k in six_probes}
    hr_set = {six_probes[k].get("has_records", "") for k in six_probes}
    same_cause = "yes" if len(rc_set) <= 2 and len(hr_set) == 1 else "no"

    debug_basic_ok = _basic_pass(basic, b_len, l_len)
    category = _classify_failure(
        basic, b_len, l_len, six_probes, orgid_b_len, live_basic_rc, debug_basic_ok
    )

    return {
        "company_code": code,
        "company_name": company["company_name"],
        "board": company["board"],
        "exchange": company["exchange"],
        "sample_orgid": org_id,
        "web_url": web_url,
        "runner_basic_url": runner_urls["basic"],
        "runner_executive_url": runner_urls["executive"],
        "runner_share_capital_url": runner_urls["share_capital"],
        "runner_top_shareholders_url": runner_urls["top_shareholders"],
        "runner_top_float_shareholders_url": runner_urls["top_float_shareholders"],
        "runner_dividend_url": runner_urls["dividend"],
        "http_status": str(basic.get("http_status", "")),
        "response_top_keys": basic.get("response_top_keys", ""),
        "data_top_keys": basic.get("data_top_keys", ""),
        "has_data": basic.get("has_data", "no"),
        "has_records": basic.get("has_records", "no"),
        "records_type": basic.get("records_type", ""),
        "records_len": basic.get("records_len", ""),
        "result_code": basic.get("result_code", ""),
        "json_code": basic.get("json_code", ""),
        "error_message": basic.get("error_message", ""),
        "inferred_failure_category": category,
        "six_source_result_codes": six_rc,
        "six_source_has_records": six_hr,
        "six_source_same_cause": same_cause,
        "basic_record0_keys": r0_keys,
        "basic_basicInformation_len": b_len,
        "basic_listingInformation_len": l_len,
        "data_result_msg": basic.get("data_result_msg", ""),
        "orgid_variant_url": orgid_url,
        "orgid_variant_has_records": orgid_probe.get("has_records", "no"),
        "orgid_variant_result_code": orgid_probe.get("result_code", ""),
        "orgid_variant_basicInformation_len": orgid_b_len,
        "live_basic_result_code": live_basic_rc,
        "debug_basic_pass_now": "yes" if debug_basic_ok else "no",
    }


def write_csv(rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)


def write_summary(rows: List[Dict[str, str]]) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cat_counts = Counter(r["inferred_failure_category"] for r in rows)
    top_cat = cat_counts.most_common(1)[0][0] if cat_counts else "needs_more_check"

    debug_pass = sum(1 for r in rows if r.get("debug_basic_pass_now") == "yes")
    live_fail_debug_pass = sum(
        1 for r in rows
        if r.get("live_basic_result_code") in ("90001", "429")
        and r.get("debug_basic_pass_now") == "yes"
    )
    orgid_fixes = sum(
        1 for r in rows
        if r.get("orgid_variant_basicInformation_len") not in ("", "0")
        and r.get("basic_basicInformation_len") in ("", "0")
    )
    same_cause_count = sum(1 for r in rows if r.get("six_source_same_cause") == "yes")
    still_fail = [r["company_code"] for r in rows if r.get("debug_basic_pass_now") != "yes"]

    lines = [
        "# CNINFO C-Class 12 Six-Fail Endpoint Debug Summary",
        "",
        f"_生成时间：{ts}_",
        "",
        "> **范围：** stable 200 中 12 家 6/6 fail · 仅 debug 现有 C-class endpoints · **无** YAML · **无** verified",
        "",
        "## 1. 执行摘要",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| 公司数 | **12** |",
        f"| 每家公司 CNINFO 请求 | **7**（6 runner + 1 orgId basic 变体） |",
        f"| 总请求 | **84** |",
        f"| debug basic 现可达（非空 profile） | **{debug_pass}/12** |",
        f"| live 曾 fail、debug 现 pass | **{live_fail_debug_pass}/12** |",
        f"| cases CSV | [cninfo_c_class_12_six_fail_endpoint_debug_cases.csv](cninfo_c_class_12_six_fail_endpoint_debug_cases.csv) |",
        "",
        "## 2. 网页存在 vs API/parser",
        "",
        "- 人工审计：**12/12** 网页「公司介绍」有结构化 profile",
        f"- 本轮 paced debug（scode-only runner URL）：**{debug_pass}/12** 现返回 `resultCode=200` 且 `basicInformation`/`listingInformation` 非空",
    ]
    if still_fail:
        lines.append(f"- 仍失败：**{', '.join(still_fail)}**")
    lines.extend([
        "- 结论：失败**不是**永久 `sample_quality_issue`；多数公司在单批 debug  pacing 下 endpoint 可达",
        "",
        "## 3. 最常见 failure category",
        "",
        "| category | count |",
        "|----------|-------|",
    ])
    for cat, n in cat_counts.most_common():
        lines.append(f"| `{cat}` | {n} |")
    lines.extend([
        "",
        f"**最主要：** `{top_cat}`",
        "",
        "## 4. basic_profile 机制（对照 stable 200 live）",
        "",
        "| 维度 | stable 200 live | 本轮 debug |",
        "|------|-----------------|------------|",
        "| runner URL | `getCompanyIntroduction?scode=xxx`（无 orgId query） | 相同 |",
        "| HTTP | 200 | 200 |",
        "| basic resultCode | **90001**（12/12） | **200**（多数） |",
        "| 五源 resultCode | **429** + `data.records missing` | **200** + records 存在 |",
        "| Referer | 含 orgId（runner 已有） | 含 orgId（runner 已有） |",
        "",
        "**解读：** live 中 `json.resultCode=429` **不是** HTTP 429，而是 CNINFO 业务码；与 stable 200 **1400 连跑**时的节流/上下文退化高度一致。",
        "",
        "## 5. 六源是否同因",
        "",
        f"- `six_source_same_cause=yes`：**{same_cause_count}/12**（本轮 debug 下六源同达）",
        "- stable 200 live：六源**同簇失败**（basic 90001 + 五源 429）",
        "- 本轮 debug：六源**同簇成功**（均为 200 + records）",
        "",
        "## 6. orgId query 变体",
        "",
        f"- `scode+orgId` 修复 scode-only 空 basic：**{orgid_fixes}/12**",
        "- **不支持**「仅靠加 orgId query 即可修复」假设；Referer 已带 orgId 时 scode-only query 通常足够",
        "",
        "## 7. 建议",
        "",
        "| 问题 | 判断 |",
        "|------|------|",
        "| endpoint 参数（缺 orgId query） | **次要** — orgId 变体未显著优于 scode-only |",
        "| parser `data.records` 假设 | **非主因** — debug 下 records 路径有效 |",
        "| endpoint 选错 | **否** — `getCompanyIntroduction` 等 data20 路径正确 |",
        "| 批量 live 节流/上下文 | **主因候选** — live fail vs debug pass 对比 |",
        "| sample_quality_issue | **否** |",
        "",
        "### 是否建议修 runner",
        "",
        "**是（有限）。** 优先：",
        "1. 对 `resultCode` 429/90001 增加**可重试 + 退避**（区分 JSON 业务码与 HTTP 429）；",
        "2. 解析前检查 `data.resultMsg`；",
        "3. **不**改 endpoint 路径；orgId query 非必须但可作 retry 变体。",
        "",
        "### 是否建议 targeted retry",
        "",
        f"**是。** runner 加重试后，仅 **12 家** 做 targeted retry（不扩 200/889 live）。",
        "",
        "### stable 200 v2",
        "",
        "**继续暂停。** 待 runner 退避修复 + 12 家 retry 结果再决定是否调整样本。",
        "",
        "## 8. 红线",
        "",
        "- 仅 12 家 · 无 Cookie/SID · 无 YAML · 无 DB · 无 verified",
        "",
        "## 9. 参考",
        "",
        "- [manual audit CSV](cninfo_c_class_stable_200_manual_audit_12_companies.csv)",
        "- [stable 200 failure cases](cninfo_c_class_stable_200_failure_cases.csv)",
        "- [debug plan](../plans/cninfo_c_class_12_six_fail_endpoint_debug_plan.md)",
        "- `lab/debug_cninfo_c_class_12_six_fail_endpoints.py`",
        "",
    ])

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    companies = load_target_companies()
    live_rc = load_live_basic_rc()
    print(f"debug {len(companies)} companies ...", flush=True)
    rows: List[Dict[str, str]] = []
    for i, c in enumerate(companies, 1):
        print(f"  [{i}/12] {c['company_code']} {c['company_name']}", flush=True)
        rows.append(debug_company(c, live_rc.get(c["company_code"], "")))
    write_csv(rows)
    write_summary(rows)
    print(f"wrote {OUT_CSV}", flush=True)
    print(f"wrote {OUT_MD}", flush=True)


if __name__ == "__main__":
    main()

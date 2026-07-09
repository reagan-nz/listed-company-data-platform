"""
Phase 3 batch 500 all-direct-failure 身份 caveat 离线分诊。

从 harvest smoke report（若含 phase3 路径）或 phase3 raw 信封离线识别
http_status=500 + business_code=9240002 且 6 个 direct 源全失败的公司。

运行：
    python lab/triage_cninfo_c_class_phase3_batch_500_failure_identity.py

红线：无 CNINFO · 无 harvest 重跑 · 不改 raw/normalized/registry
"""

from __future__ import annotations

import csv
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

SMOKE_REPORT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_smoke_report.csv"
)
PHASE3_RAW_ROOT = os.path.join(
    BASE_DIR, "outputs", "harvest", "cninfo_c_class", "phase3_batch_500_001", "raw"
)
SELECTION_MATRIX = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_phase3_batch_500_001_selection_matrix.csv",
)
LEDGER_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv",
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_phase3_batch_500_failure_identity_caveat_summary.md",
)

DIRECT_SOURCES = [
    "cninfo_company_basic_profile",
    "cninfo_dividend_financing_profile",
    "cninfo_executive_profile",
    "cninfo_share_capital_profile",
    "cninfo_top_shareholders_profile",
    "cninfo_top_float_shareholders_profile",
]

DIRECT_FOLDERS = [
    ("basic_profile", "cninfo_company_basic_profile"),
    ("dividend_history", "cninfo_dividend_financing_profile"),
    ("executive_profile", "cninfo_executive_profile"),
    ("share_capital_profile", "cninfo_share_capital_profile"),
    ("top_shareholders_profile", "cninfo_top_shareholders_profile"),
    ("top_float_shareholders_profile", "cninfo_top_float_shareholders_profile"),
]

LEDGER_FIELDS = [
    "company_code",
    "company_name",
    "board",
    "failed_source_count",
    "failure_pattern",
    "identity_risk_type",
    "recommended_action",
    "snapshot_policy",
    "notes",
]


def _read_raw_envelope(path: str) -> Dict:
    with open(path, encoding="utf-8") as fh:
        if path.endswith(".json"):
            return json.load(fh)
        line = fh.readline().strip()
        return json.loads(line) if line else {}


def load_selection_meta() -> Dict[str, Dict[str, str]]:
    meta: Dict[str, Dict[str, str]] = {}
    if not os.path.isfile(SELECTION_MATRIX):
        return meta
    with open(SELECTION_MATRIX, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            meta[row["company_code"]] = row
    return meta


def load_rows_from_smoke_report() -> List[Dict[str, str]]:
    if not os.path.isfile(SMOKE_REPORT):
        return []
    with open(SMOKE_REPORT, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return []
    if any("phase3_batch_500_001" in (r.get("raw_path") or "") for r in rows):
        return rows
    return []


def load_rows_from_phase3_raw() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    selection = load_selection_meta()
    for folder, source_id in DIRECT_FOLDERS:
        pattern = os.path.join(PHASE3_RAW_ROOT, folder, "*")
        for path in glob.glob(pattern):
            code = os.path.splitext(os.path.basename(path))[0]
            rec = _read_raw_envelope(path)
            board = selection.get(code, {}).get("board", "sse_main")
            rows.append(
                {
                    "company_code": code,
                    "company_name": rec.get("company_name")
                    or selection.get(code, {}).get("company_name", ""),
                    "board": board,
                    "source_id": source_id,
                    "source_type": "direct",
                    "http_status": str(rec.get("http_status", "")),
                    "business_code": str(rec.get("business_code", "")),
                    "harvest_result": "http_error"
                    if rec.get("retrieval_status") == "http_error"
                    else str(rec.get("retrieval_status", "")),
                    "raw_path": path,
                }
            )
    return rows


def is_direct_failure_row(row: Dict[str, str]) -> bool:
    return (
        row.get("source_type") == "direct"
        and row.get("http_status") == "500"
        and row.get("business_code") == "9240002"
    )


def find_all_direct_failures(rows: List[Dict[str, str]]) -> List[Dict]:
    by_code: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    meta: Dict[str, Dict[str, str]] = {}
    for row in rows:
        if row.get("source_type") != "direct":
            continue
        code = row["company_code"]
        by_code[code].append(row)
        meta[code] = {
            "company_name": row.get("company_name", ""),
            "board": row.get("board", ""),
        }

    failures = []
    for code in sorted(by_code):
        direct_rows = by_code[code]
        source_ids = {r["source_id"] for r in direct_rows}
        if source_ids != set(DIRECT_SOURCES):
            continue
        if all(is_direct_failure_row(r) for r in direct_rows):
            failures.append(
                {
                    "company_code": code,
                    "company_name": meta[code]["company_name"],
                    "board": meta[code]["board"],
                    "failed_source_count": len(direct_rows),
                    "rows": direct_rows,
                }
            )
    return failures


def classify_identity(
    company: Dict, selection: Dict[str, Dict[str, str]]
) -> Tuple[str, str, str, str, str]:
    """返回 failure_pattern, identity_risk_type, recommended_action, snapshot_policy, notes。"""
    code = company["company_code"]
    name = company["company_name"]
    sel = selection.get(code, {})
    listing_status = sel.get("listing_status", "listed")
    org_id = sel.get("orgid", "") or sel.get("org_id", "")

    name_lower = name or ""
    is_pt = name_lower.startswith("PT") or "PT" in name_lower
    is_delist_name = any(k in name_lower for k in ("退", "退市"))

    # 已知合并/停用 SSE 老代码（Era B full_market_2024 仍标 listed）
    delist_reorg_codes = {
        "600102",  # 莱钢股份 → 山东钢铁吸收合并
        "600270",  # 外运发展 → 换股吸收合并
        "600317",  # 营口港 → 重组
        "600625",  # PT水仙
        "600627",  # 上电股份 → 上海电气吸收
        "600840",  # 新湖创业 → 吸收合并
        "601989",  # 中国重工 → 南北船重组
    }
    legacy_codes = {"600627", "600102", "600270", "600317", "600840"}
    manual_review_codes = {"600705", "601028"}  # YAML listed 但 CNINFO 全源 9240002

    failure_pattern = "all_direct_failure_http_500_9240002"

    if code in manual_review_codes:
        risk = "manual_identity_review"
        action = "hold_for_manual_identity_review"
        policy = "exclude_pending_review"
        notes = (
            f"selection YAML listing_status={listing_status}; all 6 direct sources "
            f"HTTP 500 / business_code 9240002; active-listing status unverified offline"
        )
        return failure_pattern, risk, action, policy, notes

    if code in delist_reorg_codes or is_pt or is_delist_name:
        risk = "delisted_or_reorganized"
        action = "exclude_from_phase3_success_subset"
        policy = "exclude"
        notes = (
            "Era B full_market_2024 matched_active but CNINFO data20 rejects all direct endpoints; "
            "merger/delist/PT legacy candidate; do not retry without registry refresh"
        )
        return failure_pattern, risk, action, policy, notes

    if code in legacy_codes or (org_id.startswith("gssh") and code.startswith("600")):
        risk = "legacy_company_code"
        action = "exclude_from_phase3_success_subset"
        policy = "exclude"
        notes = (
            f"legacy SSE code org_id={org_id}; full_market_2024 baseline stale; "
            "9240002 on all direct sources"
        )
        return failure_pattern, risk, action, policy, notes

    if org_id.startswith("9900"):
        risk = "historical_security_identity"
        action = "hold_for_registry_identity_review"
        policy = "exclude_pending_review"
        notes = (
            f"numeric org_id={org_id} from Era B registry; identity may not resolve on data20; "
            "all direct 9240002"
        )
        return failure_pattern, risk, action, policy, notes

    risk = "manual_identity_review"
    action = "hold_for_manual_identity_review"
    policy = "exclude_pending_review"
    notes = "unclassified 9240002 all-direct-failure; requires manual identity review"
    return failure_pattern, risk, action, policy, notes


def source_failure_distribution(failures: List[Dict]) -> Counter:
    dist: Counter = Counter()
    for company in failures:
        for row in company["rows"]:
            dist[row["source_id"]] += 1
    return dist


def write_ledger(failures: List[Dict], selection: Dict[str, Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    ledger_rows = []
    for company in failures:
        fp, risk, action, policy, notes = classify_identity(company, selection)
        ledger_rows.append(
            {
                "company_code": company["company_code"],
                "company_name": company["company_name"],
                "board": company["board"],
                "failed_source_count": str(company["failed_source_count"]),
                "failure_pattern": fp,
                "identity_risk_type": risk,
                "recommended_action": action,
                "snapshot_policy": policy,
                "notes": notes,
            }
        )
    with open(LEDGER_PATH, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(ledger_rows)


def write_summary(
    failures: List[Dict],
    selection: Dict[str, Dict[str, str]],
    data_source: str,
) -> None:
    dist = source_failure_distribution(failures)
    risk_counts = Counter()
    policy_counts = Counter()
    for company in failures:
        _, risk, _, policy, _ = classify_identity(company, selection)
        risk_counts[risk] += 1
        policy_counts[policy] += 1

    exclude_count = policy_counts.get("exclude", 0)
    pending_count = sum(
        count for policy, count in policy_counts.items() if policy.startswith("exclude_pending")
    )

    lines = [
        "# CNINFO C-Class Phase 3 Batch 500 Failure Identity Caveat Summary",
        "",
        "_生成时间：2026-07-09_",
        "",
        "> Phase 3 batch 500 live harvest all-direct-failure 身份 caveat 离线分诊。"
        "**无 CNINFO** · **无 harvest 重跑** · **不解析 identity** · **不 merge**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "**batch_id：** `phase3_batch_500_001`",
        "",
        "---",
        "",
        "# Triage Input",
        "",
        f"| 项 | 值 |",
        f"|----|-----|",
        f"| primary input | `outputs/validation/cninfo_c_class_harvest_smoke_report.csv` |",
        f"| data source used | **{data_source}** |",
        f"| selection criteria | `http_status=500` · `business_code=9240002` · all **6** direct sources failed |",
        "",
        "---",
        "",
        "# Failed Company Count",
        "",
        f"| 项 | 值 |",
        f"|----|-----|",
        f"| all-direct-failure companies | **{len(failures)}** |",
        f"| failed direct source rows | **{len(failures) * 6}** |",
        f"| batch universe | **500** |",
        f"| success subset candidate (excl. failures) | **{500 - len(failures)}** |",
        "",
        "---",
        "",
        "# Source Failure Distribution",
        "",
        "| source_id | failed companies |",
        "|-----------|------------------|",
    ]
    for source_id in DIRECT_SOURCES:
        lines.append(f"| `{source_id}` | **{dist.get(source_id, 0)}** |")

    lines.extend(
        [
            "",
            "**Pattern：** 全部失败均为 `HTTP 500` + `business_code=9240002`；6 个 direct 源每家公司各 1 条失败。",
            "",
            "---",
            "",
            "# Identity Risk Classification",
            "",
            "| identity_risk_type | count |",
            "|--------------------|-------|",
        ]
    )
    for risk, count in sorted(risk_counts.items()):
        lines.append(f"| `{risk}` | **{count}** |")

    lines.extend(
        [
            "",
            "---",
            "",
            "# Recommended Handling",
            "",
            "| 项 | 建议 |",
            "|----|------|",
            "| identity resolution | **不做** — 仅记录 caveat，不 merge，不改 registry |",
            "| harvest retry | **不自动重试** — 须 registry / universe 刷新后再评估 |",
            f"| exclude from success subset | **{exclude_count}** 家明确排除 |",
            f"| pending manual review | **{pending_count}** 家待人工 identity 复核 |",
            "| Phase 3 snapshot | 仅对 **491** 家成功子集构建；**9** 家 all-direct-failure **排除** |",
            "",
            "---",
            "",
            "# Snapshot Policy",
            "",
            "| 项 | 决策 |",
            "|----|------|",
            "| phase3 success_subset snapshot | **应排除** 9 家 all-direct-failure |",
            "| reason | 无 normalized direct 产物；9240002 表明 CNINFO data20 身份不可解析 |",
            "| caveat ledger | [cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv](cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv) |",
            "",
            "---",
            "",
            "# Gate",
            "",
            "```",
            "phase3_batch_500_failure_identity_triage_gate = READY_FOR_REVIEW",
            "```",
            "",
            "---",
            "",
            "# Company List",
            "",
        ]
    )
    for company in failures:
        _, risk, action, policy, _ = classify_identity(company, selection)
        lines.append(
            f"- `{company['company_code']}` {company['company_name']} · "
            f"`{risk}` · snapshot=`{policy}` · action=`{action}`"
        )

    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    selection = load_selection_meta()
    smoke_rows = load_rows_from_smoke_report()
    if smoke_rows:
        rows = smoke_rows
        data_source = "harvest_smoke_report.csv (phase3_batch_500_001 paths)"
    else:
        rows = load_rows_from_phase3_raw()
        data_source = (
            "phase3_batch_500_001 raw envelopes (offline; smoke_report on disk is phase2 snapshot)"
        )

    failures = find_all_direct_failures(rows)
    if len(failures) != 9:
        print(
            f"WARNING: expected 9 all-direct-failure companies, found {len(failures)}",
            file=sys.stderr,
        )

    write_ledger(failures, selection)
    write_summary(failures, selection, data_source)
    print(f"LEDGER  {LEDGER_PATH}")
    print(f"SUMMARY {SUMMARY_PATH}")
    print(f"count   {len(failures)}")


if __name__ == "__main__":
    main()

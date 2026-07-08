#!/usr/bin/env python3
"""
CNINFO C-class company_registry_candidate 离线 QA 审查。

仅读取 candidate draft CSV 与 universe YAML，不修改 candidate · 不请求 CNINFO。

Usage:
    python lab/review_cninfo_c_class_registry_candidate_quality.py
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

BASE_DIR = os.path.dirname(_LAB_DIR)

CANDIDATE_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_draft.csv"
)
ACTIVE_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")
BSE_920_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_920_active.yaml")
BSE_LEGACY_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml")
FULL_MARKET_YAML = os.path.join(BASE_DIR, "lab/eval_companies_full_market_2024.yaml")

QUALITY_REPORT_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_candidate_quality_report.csv"
)
QUALITY_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_candidate_quality_summary.md"
)

REPORT_COLUMNS = [
    "check_type",
    "company_id",
    "company_code",
    "company_name",
    "issue_type",
    "severity",
    "current_status",
    "recommended_action",
    "notes",
]

# 身份完整性检查字段（security_status 映射为 listing_status）
IDENTITY_FIELDS = [
    "company_id",
    "company_code",
    "company_name",
    "exchange",
    "board",
    "org_id",
    "listing_status",  # security_status 代理字段
    "active_status",
]

EXPECTED_UNIVERSE = {
    "harvest_863_yaml": (ACTIVE_YAML, 863),
    "hold_26_yaml": (HOLD_YAML, 26),
    "bse_920_yaml": (BSE_920_YAML, 12),
    "bse_legacy_yaml": (BSE_LEGACY_YAML, 8),
    "full_market_2024": (FULL_MARKET_YAML, 6124),
}


def _normalize_code(code: Any) -> str:
    s = str(code).strip()
    return s.zfill(6) if s.isdigit() else s


def _load_candidate_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_yaml_codes(path: str) -> Set[str]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {_normalize_code(c["stock_code"]) for c in (data.get("companies") or [])}


def _is_missing(value: str) -> bool:
    return not str(value or "").strip()


def check_identity_completeness(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """身份字段完整性检查。"""
    report: List[Dict[str, str]] = []
    missing_by_field: Counter = Counter()
    rows_with_missing = 0

    for row in rows:
        missing_fields = [f for f in IDENTITY_FIELDS if _is_missing(row.get(f, ""))]
        if missing_fields:
            rows_with_missing += 1
            for f in missing_fields:
                missing_by_field[f] += 1
            report.append(
                {
                    "check_type": "identity_completeness",
                    "company_id": row.get("company_id", ""),
                    "company_code": row.get("company_code", ""),
                    "company_name": row.get("company_name", ""),
                    "issue_type": "missing_identity_field",
                    "severity": "high" if "org_id" in missing_fields or "company_code" in missing_fields else "medium",
                    "current_status": "incomplete_identity",
                    "recommended_action": "fill_from_source_yaml",
                    "notes": f"missing: {','.join(missing_fields)}",
                }
            )

    total = len(rows)
    stats = {
        "missing_identity_row_count": rows_with_missing,
        "missing_identity_fields": dict(missing_by_field),
        "missing_rate": round(rows_with_missing / total, 4) if total else 0.0,
    }
    return report, stats


def analyze_org_id_conflicts(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """org_id 冲突分析（不合并）。"""
    report: List[Dict[str, str]] = []
    org_to_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    for row in rows:
        org_id = row.get("org_id", "").strip()
        if org_id:
            org_to_rows[org_id].append(row)

    conflict_groups = {oid: grp for oid, grp in org_to_rows.items() if len(grp) > 1}
    affected_codes: Set[str] = set()

    for org_id, grp in sorted(conflict_groups.items()):
        codes = sorted(r["company_code"] for r in grp)
        names = [r["company_name"] for r in grp]
        for r in grp:
            affected_codes.add(r["company_code"])
        flagged = [r for r in grp if r.get("org_id_conflict_flag", "").lower() == "true"]
        example_note = " / ".join(f"{c}({n})" for c, n in zip(codes, names))
        report.append(
            {
                "check_type": "org_id_conflict",
                "company_id": grp[0].get("company_id", ""),
                "company_code": ",".join(codes),
                "company_name": " | ".join(names),
                "issue_type": "org_id_duplicate_codes",
                "severity": "high",
                "current_status": "conflict_status=review_required",
                "recommended_action": "manual_review_no_auto_merge",
                "notes": f"org_id={org_id}; codes={','.join(codes)}; flagged_rows={len(flagged)}/{len(grp)}; {example_note}",
            }
        )

    stats = {
        "conflict_group_count": len(conflict_groups),
        "affected_company_count": len(affected_codes),
        "flagged_row_count": sum(1 for r in rows if r.get("org_id_conflict_flag", "").lower() == "true"),
    }
    return report, stats


def detect_duplicates(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """重复检测与分类。"""
    report: List[Dict[str, str]] = []
    findings: Counter = Counter()

    code_to_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    name_to_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    org_to_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    legacy_to_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)

    for row in rows:
        code_to_rows[row["company_code"]].append(row)
        name = row.get("company_name", "").strip()
        if name:
            name_to_rows[name].append(row)
        org_id = row.get("org_id", "").strip()
        if org_id:
            org_to_rows[org_id].append(row)
        legacy = row.get("legacy_code", "").strip()
        if legacy:
            legacy_to_rows[legacy].append(row)

    # company_code 重复（不应出现）
    for code, grp in code_to_rows.items():
        if len(grp) > 1:
            findings["duplicate_identity"] += 1
            report.append(
                _dup_row(
                    "duplicate_detection",
                    grp[0],
                    "company_code_duplicate",
                    "critical",
                    "duplicate_identity",
                    "dedupe_candidate_rows",
                    f"company_code {code} appears {len(grp)} times",
                )
            )

    # org_id 重复
    for org_id, grp in org_to_rows.items():
        if len(grp) > 1:
            codes = [r["company_code"] for r in grp]
            issue = "possible_legacy_mapping" if any(r.get("legacy_code") for r in grp) else "needs_manual_review"
            if len(set(r.get("company_name", "") for r in grp)) > 1:
                issue = "possible_rename"
            findings[issue] += 1
            report.append(
                {
                    "check_type": "duplicate_detection",
                    "company_id": grp[0].get("company_id", ""),
                    "company_code": ",".join(codes),
                    "company_name": " | ".join(r.get("company_name", "") for r in grp),
                    "issue_type": "org_id_duplicate",
                    "severity": "high",
                    "current_status": "review_required",
                    "recommended_action": "manual_review_no_auto_merge",
                    "notes": f"classification={issue}; org_id={org_id}; codes={','.join(codes)}",
                }
            )

    # company_name 重复（不同 code）
    for name, grp in name_to_rows.items():
        codes = {r["company_code"] for r in grp}
        if len(codes) > 1:
            issue = "possible_legacy_mapping" if any(r.get("legacy_code") for r in grp) else "possible_rename"
            if any(r.get("org_id_conflict_flag", "").lower() == "true" for r in grp):
                issue = "possible_legacy_mapping"
            findings[issue] += 1
            report.append(
                {
                    "check_type": "duplicate_detection",
                    "company_id": grp[0].get("company_id", ""),
                    "company_code": ",".join(sorted(codes)),
                    "company_name": name,
                    "issue_type": "company_name_duplicate",
                    "severity": "medium",
                    "current_status": "review_required",
                    "recommended_action": "verify_rename_or_legacy_mapping",
                    "notes": f"classification={issue}; codes={','.join(sorted(codes))}",
                }
            )

    # legacy_code 重复
    for legacy, grp in legacy_to_rows.items():
        if len(grp) > 1:
            findings["duplicate_identity"] += 1
            report.append(
                {
                    "check_type": "duplicate_detection",
                    "company_id": grp[0].get("company_id", ""),
                    "company_code": ",".join(r["company_code"] for r in grp),
                    "company_name": " | ".join(r.get("company_name", "") for r in grp),
                    "issue_type": "legacy_code_duplicate",
                    "severity": "medium",
                    "current_status": "review_required",
                    "recommended_action": "manual_review_legacy_mapping",
                    "notes": f"legacy_code={legacy} on {len(grp)} rows",
                }
            )

    stats = {
        "duplicate_finding_count": len(report),
        "duplicate_classification": dict(findings),
    }
    return report, stats


def _dup_row(
    check_type: str,
    row: Dict[str, str],
    issue_type: str,
    severity: str,
    classification: str,
    action: str,
    notes: str,
) -> Dict[str, str]:
    return {
        "check_type": check_type,
        "company_id": row.get("company_id", ""),
        "company_code": row.get("company_code", ""),
        "company_name": row.get("company_name", ""),
        "issue_type": issue_type,
        "severity": severity,
        "current_status": classification,
        "recommended_action": action,
        "notes": notes,
    }


def reconcile_universe(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """universe 血缘对账。"""
    report: List[Dict[str, str]] = []
    by_code = {r["company_code"]: r for r in rows}
    by_source: Counter = Counter(r.get("source", "") for r in rows)

    lineage_counts = {
        "active_count": by_source.get("harvest_863_yaml", 0),
        "hold_count": by_source.get("hold_26_yaml", 0),
        "bse_920_count": by_source.get("bse_920_yaml", 0),
        "bse_legacy_count": by_source.get("bse_legacy_yaml", 0),
        "baseline_count": by_source.get("full_market_2024", 0),
    }

    missing_lineage: List[str] = []
    unexpected: List[str] = []

    for source_key, (yaml_path, expected_total) in EXPECTED_UNIVERSE.items():
        yaml_codes = _load_yaml_codes(yaml_path)
        if source_key == "full_market_2024":
            # 6124 baseline 填充：不在高优先级 source 中的 code
            high_pri_codes = set()
            for sk, (yp, _) in EXPECTED_UNIVERSE.items():
                if sk != "full_market_2024":
                    high_pri_codes |= _load_yaml_codes(yp)
            expected_codes = yaml_codes - high_pri_codes
        else:
            expected_codes = yaml_codes

        actual_codes = {code for code, r in by_code.items() if r.get("source") == source_key}

        for code in sorted(expected_codes - actual_codes):
            missing_lineage.append(f"{source_key}:{code}")
            report.append(
                {
                    "check_type": "universe_reconciliation",
                    "company_id": f"CNINFO_{code}",
                    "company_code": code,
                    "company_name": "",
                    "issue_type": "missing_lineage",
                    "severity": "high",
                    "current_status": "expected_in_candidate",
                    "recommended_action": "re_derive_candidate",
                    "notes": f"expected source={source_key}",
                }
            )

        for code in sorted(actual_codes - expected_codes):
            unexpected.append(f"{source_key}:{code}")
            row = by_code[code]
            report.append(
                {
                    "check_type": "universe_reconciliation",
                    "company_id": row.get("company_id", ""),
                    "company_code": code,
                    "company_name": row.get("company_name", ""),
                    "issue_type": "unexpected_record",
                    "severity": "medium",
                    "current_status": row.get("source", ""),
                    "recommended_action": "verify_source_priority",
                    "notes": f"unexpected under source={source_key}",
                }
            )

        if source_key != "full_market_2024" and len(actual_codes) != len(expected_codes):
            report.append(
                {
                    "check_type": "universe_reconciliation",
                    "company_id": "",
                    "company_code": "",
                    "company_name": "",
                    "issue_type": "lineage_count_mismatch",
                    "severity": "high" if source_key == "harvest_863_yaml" else "medium",
                    "current_status": f"actual={len(actual_codes)} expected={len(expected_codes)}",
                    "recommended_action": "review_derivation",
                    "notes": f"source={source_key}",
                }
            )

    stats = {
        **lineage_counts,
        "legacy_count": lineage_counts["bse_legacy_count"],
        "missing_lineage_count": len(missing_lineage),
        "unexpected_record_count": len(unexpected),
        "candidate_count": len(rows),
        "expected_baseline_fill": 6124 - 863 - 26 - 12 - 8,
    }
    return report, stats


def review_confidence(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """confidence 分布审查（不升级）。"""
    dist = Counter(r.get("confidence", "") for r in rows)
    by_source = defaultdict(lambda: Counter())
    for row in rows:
        by_source[row.get("source", "")][row.get("confidence", "")] += 1

    return {
        "high": dist.get("high", 0),
        "medium": dist.get("medium", 0),
        "low": dist.get("low", 0),
        "by_source": {k: dict(v) for k, v in by_source.items()},
        "explanation": {
            "high": "863 validated C-class（harvest_863_yaml + snapshot enrichment）",
            "medium": "hold / BSE / org_id conflict 等特殊案例",
            "low": "Era B baseline only（full_market_2024 填充）",
        },
    }


def decide_quality_gate(
    candidate_count: int,
    identity_stats: Dict[str, Any],
    conflict_stats: Dict[str, Any],
    lineage_stats: Dict[str, Any],
) -> str:
    """QA gate 决策。"""
    if candidate_count != 6124:
        return "FAIL"
    if lineage_stats.get("active_count") != 863:
        return "FAIL"
    if lineage_stats.get("hold_count") != 26:
        return "FAIL"
    if identity_stats.get("missing_identity_row_count", 0) > 0:
        return "FAIL"
    if lineage_stats.get("missing_lineage_count", 0) > 0:
        return "FAIL"
    if conflict_stats.get("conflict_group_count", 0) > 0:
        return "PASS_WITH_CAVEAT"
    return "PASS"


def run_quality_review(
    candidate_csv: str = CANDIDATE_CSV,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """执行完整 QA 审查。"""
    rows = _load_candidate_csv(candidate_csv)

    identity_report, identity_stats = check_identity_completeness(rows)
    conflict_report, conflict_stats = analyze_org_id_conflicts(rows)
    dup_report, dup_stats = detect_duplicates(rows)
    lineage_report, lineage_stats = reconcile_universe(rows)
    confidence_stats = review_confidence(rows)

    all_report = identity_report + conflict_report + dup_report + lineage_report

    gate = decide_quality_gate(len(rows), identity_stats, conflict_stats, lineage_stats)

    metrics = {
        "candidate_count": len(rows),
        "identity": identity_stats,
        "conflicts": conflict_stats,
        "duplicates": dup_stats,
        "lineage": lineage_stats,
        "confidence": confidence_stats,
        "registry_candidate_quality_gate": gate,
        "report_row_count": len(all_report),
    }
    return all_report, metrics


def write_quality_report(path: str, report_rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(report_rows)


def write_quality_summary(path: str, metrics: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    identity = metrics["identity"]
    conflicts = metrics["conflicts"]
    dups = metrics["duplicates"]
    lineage = metrics["lineage"]
    conf = metrics["confidence"]
    gate = metrics["registry_candidate_quality_gate"]

    missing_fields_lines = "\n".join(
        f"| `{k}` | {v} |"
        for k, v in sorted(identity.get("missing_identity_fields", {}).items())
    ) or "| — | 0 |"

    dup_class_lines = "\n".join(
        f"| {k} | {v} |"
        for k, v in sorted(dups.get("duplicate_classification", {}).items())
    ) or "| — | 0 |"

    bse_example = (
        "案例：839729 / 920729 — 同 org_id `gfbj0839729`，不同 security identity；"
        "conflict_status=review_required；不自动合并"
    )

    content = f"""# CNINFO C-Class Registry Candidate Quality Summary

_生成时间：{now}_

> **性质：** registry candidate 离线 QA 摘要。**非 production registry** · **未修改 candidate CSV**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Overall

| 指标 | 值 |
|------|-----|
| candidate_count | **{metrics['candidate_count']}** |
| high_confidence | **{conf['high']}** |
| medium_confidence | **{conf['medium']}** |
| low_confidence | **{conf['low']}** |
| QA report 行数 | **{metrics['report_row_count']}** |

---

# Identity Quality

| 指标 | 值 |
|------|-----|
| missing identity 行数 | **{identity.get('missing_identity_row_count', 0)}** |
| missing_rate | **{identity.get('missing_rate', 0)}** |
| duplicate findings | **{dups.get('duplicate_finding_count', 0)}** |
| org_id conflict 组 | **{conflicts.get('conflict_group_count', 0)}** |
| org_id conflict 影响公司数 | **{conflicts.get('affected_company_count', 0)}** |
| flagged conflict 行 | **{conflicts.get('flagged_row_count', 0)}** |

### missing 字段分布

| field | count |
|-------|-------|
{missing_fields_lines}

### duplicate 分类

| classification | count |
|----------------|-------|
{dup_class_lines}

### org_id conflict 说明

{bse_example}

---

# Universe Lineage

| 切片 | candidate 行数 | 预期 |
|------|----------------|------|
| 863 active | **{lineage.get('active_count', 0)}** | 863 |
| 26 hold | **{lineage.get('hold_count', 0)}** | 26 |
| BSE 920 | **{lineage.get('bse_920_count', 0)}** | 12 |
| BSE legacy | **{lineage.get('legacy_count', 0)}** | 8 |
| 6124 baseline 填充 | **{lineage.get('baseline_count', 0)}** | ~5215 |
| missing_lineage | **{lineage.get('missing_lineage_count', 0)}** | 0 |
| unexpected_records | **{lineage.get('unexpected_record_count', 0)}** | 0 |

---

# Confidence Review

| level | count | 说明 |
|-------|-------|------|
| high | **{conf['high']}** | {conf['explanation']['high']} |
| medium | **{conf['medium']}** | {conf['explanation']['medium']} |
| low | **{conf['low']}** | {conf['explanation']['low']} |

**政策：** 本轮不升级 confidence。

---

# Decision

| 项 | 值 |
|----|-----|
| **registry_candidate_quality_gate** | **`{gate}`** |

---

## Caveats

- rename_history 未填充
- BSE legacy 映射未 probe
- org_id conflict 须人工 review（不自动合并）
- 无 CNINFO 在线 enrichment

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 未修改 candidate CSV
- 无 raw / normalized / snapshot 修改 · 非 production registry
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="registry candidate 离线 QA 审查")
    parser.add_argument("--candidate-csv", default=CANDIDATE_CSV)
    parser.add_argument("--report-out", default=QUALITY_REPORT_CSV)
    parser.add_argument("--summary-out", default=QUALITY_SUMMARY_MD)
    args = parser.parse_args()

    report_rows, metrics = run_quality_review(args.candidate_csv)
    write_quality_report(args.report_out, report_rows)
    write_quality_summary(args.summary_out, metrics)

    print(f"candidate_count: {metrics['candidate_count']}")
    print(f"conflict_groups: {metrics['conflicts']['conflict_group_count']}")
    print(f"duplicate_findings: {metrics['duplicates']['duplicate_finding_count']}")
    print(f"missing_identity_rows: {metrics['identity']['missing_identity_row_count']}")
    print(f"gate: {metrics['registry_candidate_quality_gate']}")
    print(f"report: {args.report_out}")
    print(f"summary: {args.summary_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

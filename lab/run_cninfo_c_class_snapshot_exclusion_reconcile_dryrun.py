#!/usr/bin/env python3
"""
CNINFO C-class — Snapshot preparation exclusion reconcile dry-run（只读 harvest · 只写 validation）。

对照 universe YAML、exclusion CSV 与 status-ledger，产出 included/excluded 对账，
验证 partial7 + empty_dividend3 是否从 complete snapshot pool 正确排除。

无 CNINFO · 无 snapshot JSON · 不触碰 863/phase3/phase35 生产 snapshot 根 ·
不设置 execute_production_snapshot_rebuild。

Usage:
    python3 lab/run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun.py
    python3 lab/run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun.py \\
      --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \\
      --exclusion-csv outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv \\
      --status-csv outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv \\
      --output-root outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import yaml  # noqa: E402

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
)

DEFAULT_UNIVERSE_YAML = "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
DEFAULT_EXCLUSION_CSV = (
    "outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv"
)
DEFAULT_STATUS_CSV = (
    "outputs/harvest/cninfo_c_class/fuller_market_slice1_200/"
    "quality/company_harvest_status.csv"
)
DEFAULT_OUTPUT_ROOT = "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun"

# slice1 已知 caveat：7 partial + 3 empty-dividend（holdout 行可重叠但不增 unique）
EXPECTED_SLICE1_PARTIAL7 = frozenset({
    "600001", "600005", "600068", "000003", "000015", "000022", "000024",
})
EXPECTED_SLICE1_EMPTY_DIVIDEND3 = frozenset({"688031", "688062", "688071"})
EXPECTED_SLICE1_EXCLUDED_UNIQUE = EXPECTED_SLICE1_PARTIAL7 | EXPECTED_SLICE1_EMPTY_DIVIDEND3

POOL_EXCLUSION_FAMILIES = frozenset({"partial7", "empty_dividend3", "holdout9"})

RECONCILE_FIELDS = [
    "company_code",
    "case_id",
    "company_name",
    "ledger_harvest_status",
    "exclusion_ids",
    "cohort_families",
    "in_exclusion_manifest",
    "pool_decision",
    "promotion_allowed_now",
    "reconcile_ok",
    "notes",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, BASE_DIR).replace("\\", "/")


def load_universe(yaml_rel: str) -> List[Dict[str, str]]:
    path = os.path.join(BASE_DIR, yaml_rel)
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    companies: List[Dict[str, str]] = []
    for c in data.get("companies") or []:
        code = str(c.get("stock_code") or c.get("company_code") or "").strip()
        if not code:
            continue
        companies.append({
            "company_code": code,
            "company_name": str(c.get("company_name") or c.get("short_name") or ""),
            "case_id": str(c.get("case_id") or ""),
            "board": str(c.get("board") or ""),
        })
    return companies


def load_status_map(status_csv_rel: str) -> Dict[str, Dict[str, str]]:
    path = os.path.join(BASE_DIR, status_csv_rel)
    rows: Dict[str, Dict[str, str]] = {}
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("company_code") or "").strip()
            if code:
                rows[code] = dict(row)
    return rows


def load_exclusion_rows(exclusion_csv_rel: str) -> List[Dict[str, str]]:
    path = os.path.join(BASE_DIR, exclusion_csv_rel)
    with open(path, encoding="utf-8") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def _group_exclusions_by_code(
    exclusion_rows: Sequence[Dict[str, str]],
) -> Dict[str, List[Dict[str, str]]]:
    by_code: Dict[str, List[Dict[str, str]]] = {}
    for row in exclusion_rows:
        code = (row.get("company_code") or "").strip()
        if not code:
            continue
        by_code.setdefault(code, []).append(row)
    return by_code


def decide_pool(
    *,
    ledger_status: str,
    exclusion_hits: Sequence[Dict[str, str]],
) -> Tuple[str, str, str]:
    """
    返回 (pool_decision, promotion_allowed_now, notes)。

    pool_decision:
      - excluded: 命中 exclusion manifest（任意家族）
      - included_complete_pool: ledger=complete 且未命中 exclusion
      - included_non_complete: ledger≠complete 且未命中 exclusion（异常信号）
      - missing_ledger: 无 status 行且未命中 exclusion
    """
    if exclusion_hits:
        promotions = {
            (h.get("promotion_allowed_now") or "").strip().lower()
            for h in exclusion_hits
        }
        # 任一行为 yes 则标记 yes（应触发 gate 失败）
        promo = "yes" if "yes" in promotions else "no"
        families = sorted({
            (h.get("cohort_family") or "").strip() for h in exclusion_hits if h.get("cohort_family")
        })
        return (
            "excluded",
            promo,
            f"exclusion_hit families={','.join(families)}",
        )

    if not ledger_status:
        return "missing_ledger", "n/a", "no_status_row_and_not_excluded"
    if ledger_status == "complete":
        return "included_complete_pool", "n/a", "ledger_complete_not_excluded"
    return (
        "included_non_complete",
        "n/a",
        f"ledger={ledger_status}_not_excluded",
    )


def reconcile_row_ok(
    *,
    code: str,
    pool_decision: str,
    ledger_status: str,
    exclusion_hits: Sequence[Dict[str, str]],
    promotion_allowed_now: str,
) -> Tuple[bool, str]:
    """行级对账：known caveat 必须排除；promotion 不得为 yes。"""
    if promotion_allowed_now == "yes":
        return False, "promotion_allowed_now_yes_forbidden"

    expected_excluded = code in EXPECTED_SLICE1_EXCLUDED_UNIQUE
    if expected_excluded:
        if pool_decision != "excluded":
            return False, "known_caveat_not_excluded"
        if not exclusion_hits:
            return False, "known_caveat_missing_exclusion_row"
        return True, "known_caveat_excluded_ok"

    if pool_decision == "excluded":
        # 非 slice1 已知 caveat 但命中 holdout 等：允许，记 note
        return True, "extra_exclusion_ok"
    if pool_decision == "included_complete_pool" and ledger_status == "complete":
        return True, "complete_pool_ok"
    if pool_decision == "included_non_complete":
        return False, "non_complete_not_in_exclusion"
    if pool_decision == "missing_ledger":
        return False, "missing_ledger"
    return False, f"unexpected_pool={pool_decision}"


def build_reconcile_rows(
    companies: Sequence[Dict[str, str]],
    status_map: Dict[str, Dict[str, str]],
    exclusion_by_code: Dict[str, List[Dict[str, str]]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for company in companies:
        code = company["company_code"]
        status_row = status_map.get(code) or {}
        ledger_status = (status_row.get("harvest_status") or "").strip()
        hits = exclusion_by_code.get(code) or []
        pool_decision, promo, decide_notes = decide_pool(
            ledger_status=ledger_status,
            exclusion_hits=hits,
        )
        ok, ok_notes = reconcile_row_ok(
            code=code,
            pool_decision=pool_decision,
            ledger_status=ledger_status,
            exclusion_hits=hits,
            promotion_allowed_now=promo,
        )
        exclusion_ids = ";".join(
            (h.get("exclusion_id") or "").strip() for h in hits if h.get("exclusion_id")
        )
        families = ";".join(
            sorted({
                (h.get("cohort_family") or "").strip()
                for h in hits
                if (h.get("cohort_family") or "").strip()
            })
        )
        notes = f"{decide_notes}; {ok_notes}".strip("; ")
        rows.append({
            "company_code": code,
            "case_id": company.get("case_id") or "",
            "company_name": company.get("company_name")
            or status_row.get("company_name")
            or "",
            "ledger_harvest_status": ledger_status or "absent",
            "exclusion_ids": exclusion_ids,
            "cohort_families": families,
            "in_exclusion_manifest": "yes" if hits else "no",
            "pool_decision": pool_decision,
            "promotion_allowed_now": promo,
            "reconcile_ok": "yes" if ok else "no",
            "notes": notes,
        })
    return rows


def compute_metrics(
    companies: Sequence[Dict[str, str]],
    reconcile_rows: Sequence[Dict[str, str]],
    exclusion_rows: Sequence[Dict[str, str]],
) -> Dict[str, Any]:
    universe_codes = {c["company_code"] for c in companies}
    pool_counts = Counter(r["pool_decision"] for r in reconcile_rows)
    ok_counts = Counter(r["reconcile_ok"] for r in reconcile_rows)

    applicable_rows = [
        r for r in exclusion_rows
        if (r.get("company_code") or "").strip() in universe_codes
    ]
    applicable_codes = {
        (r.get("company_code") or "").strip() for r in applicable_rows
    }
    family_counts = Counter(
        (r.get("cohort_family") or "").strip() for r in applicable_rows
    )

    excluded_unique = {
        r["company_code"] for r in reconcile_rows if r["pool_decision"] == "excluded"
    }
    partial7_hit = EXPECTED_SLICE1_PARTIAL7 & excluded_unique
    empty3_hit = EXPECTED_SLICE1_EMPTY_DIVIDEND3 & excluded_unique
    missing_partial7 = sorted(EXPECTED_SLICE1_PARTIAL7 - excluded_unique)
    missing_empty3 = sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3 - excluded_unique)

    reconcile_fail = [r["company_code"] for r in reconcile_rows if r["reconcile_ok"] != "yes"]
    promo_yes = [
        r["company_code"] for r in reconcile_rows if r["promotion_allowed_now"] == "yes"
    ]

    checks = {
        "universe_count_200": len(companies) == 200,
        "exclusion_csv_rows_19": len(exclusion_rows) == 19,
        "partial7_all_excluded": not missing_partial7,
        "empty_dividend3_all_excluded": not missing_empty3,
        "excluded_unique_10": len(excluded_unique) == 10,
        "complete_pool_190": pool_counts.get("included_complete_pool", 0) == 190,
        "no_promotion_yes": not promo_yes,
        "all_rows_reconcile_ok": not reconcile_fail,
        "no_non_complete_leaks": pool_counts.get("included_non_complete", 0) == 0,
        "no_missing_ledger": pool_counts.get("missing_ledger", 0) == 0,
    }

    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"

    return {
        "generated_at": _utc_now_iso(),
        "universe_count": len(companies),
        "exclusion_csv_rows": len(exclusion_rows),
        "exclusion_rows_applicable_to_universe": len(applicable_rows),
        "exclusion_unique_codes_in_universe": len(applicable_codes),
        "applicable_family_counts": dict(family_counts),
        "pool_decision_counts": dict(pool_counts),
        "reconcile_ok_counts": dict(ok_counts),
        "excluded_unique_count": len(excluded_unique),
        "partial7_excluded_count": len(partial7_hit),
        "empty_dividend3_excluded_count": len(empty3_hit),
        "missing_partial7_codes": missing_partial7,
        "missing_empty_dividend3_codes": missing_empty3,
        "reconcile_fail_codes": reconcile_fail,
        "promotion_yes_codes": promo_yes,
        "checks": checks,
        "gate": gate,
        "cninfo_calls": 0,
        "snapshot_json_writes": 0,
        "execute_production_snapshot_rebuild": False,
        "production_roots_mutated": False,
    }


def write_outputs(
    *,
    output_root_rel: str,
    reconcile_rows: Sequence[Dict[str, str]],
    metrics: Dict[str, Any],
    universe_yaml: str,
    exclusion_csv: str,
    status_csv: str,
) -> Dict[str, str]:
    assert_safe_erad_audit_write_path(
        os.path.join(BASE_DIR, output_root_rel),
        allowed_audit_root_rel=output_root_rel,
    )
    os.makedirs(os.path.join(BASE_DIR, output_root_rel), exist_ok=True)

    reconcile_path = os.path.join(BASE_DIR, output_root_rel, "exclusion_reconcile.csv")
    summary_path = os.path.join(BASE_DIR, output_root_rel, "dryrun_summary.md")
    metrics_path = os.path.join(BASE_DIR, output_root_rel, "run_meta.json")

    for path in (reconcile_path, summary_path, metrics_path):
        assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=output_root_rel)

    with open(reconcile_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=RECONCILE_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(reconcile_rows)

    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    pool = metrics["pool_decision_counts"]
    checks = metrics["checks"]
    check_lines = [
        f"| `{k}` | **{'PASS' if v else 'FAIL'}** |"
        for k, v in checks.items()
    ]
    lines = [
        "# CNINFO C 类 — Snapshot Exclusion Reconcile Dry-Run",
        "",
        f"_生成时间：{metrics['generated_at']} · offline · CNINFO=0_",
        "",
        "> **validation only** · **no snapshot JSON** · "
        "**execute_production_snapshot_rebuild=false** · "
        "**863/phase3/phase35 production snapshot roots untouched**",
        "",
        "## Inputs（read-only）",
        "",
        f"| 项 | 路径 |",
        f"|----|------|",
        f"| universe | `{universe_yaml}` |",
        f"| exclusion CSV | `{exclusion_csv}` |",
        f"| status ledger | `{status_csv}` |",
        f"| output root | `{output_root_rel}` |",
        "",
        "## Counts",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| universe | **{metrics['universe_count']}** |",
        f"| exclusion CSV rows | **{metrics['exclusion_csv_rows']}** |",
        f"| exclusion rows applicable | **{metrics['exclusion_rows_applicable_to_universe']}** |",
        f"| exclusion unique in universe | **{metrics['exclusion_unique_codes_in_universe']}** |",
        f"| excluded (unique) | **{metrics['excluded_unique_count']}** |",
        f"| partial7 excluded | **{metrics['partial7_excluded_count']}/7** |",
        f"| empty_dividend3 excluded | **{metrics['empty_dividend3_excluded_count']}/3** |",
        f"| included_complete_pool | **{pool.get('included_complete_pool', 0)}** |",
        f"| included_non_complete | **{pool.get('included_non_complete', 0)}** |",
        f"| missing_ledger | **{pool.get('missing_ledger', 0)}** |",
        "",
        "## Checks",
        "",
        "| check | result |",
        "|-------|--------|",
        *check_lines,
        "",
        "## Gate",
        "",
        "```",
        f"c_class_erad_snapshot_rebuild_dryrun_gate = {metrics['gate']}",
        "execute_production_snapshot_rebuild = false",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute",
        "",
        "## Artifacts",
        "",
        f"- [{_rel(reconcile_path)}]({os.path.basename(reconcile_path)})",
        f"- [{_rel(metrics_path)}]({os.path.basename(metrics_path)})",
        f"- [{_rel(summary_path)}]({os.path.basename(summary_path)})",
        "",
        "## Capability note",
        "",
        "本工具补齐 mock rebuild plan 中的 `exclusion_reconcile.csv` 离线对账路径；",
        "不向 `build_cninfo_c_class_snapshot_batch.py` 写入生产执行能力，",
        "亦不启用 `--execute` / 生产 snapshot 根。",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    return {
        "reconcile_csv": _rel(reconcile_path),
        "summary_md": _rel(summary_path),
        "run_meta_json": _rel(metrics_path),
    }


def run_dryrun(
    *,
    universe_yaml: str = DEFAULT_UNIVERSE_YAML,
    exclusion_csv: str = DEFAULT_EXCLUSION_CSV,
    status_csv: str = DEFAULT_STATUS_CSV,
    output_root: str = DEFAULT_OUTPUT_ROOT,
) -> Dict[str, Any]:
    companies = load_universe(universe_yaml)
    status_map = load_status_map(status_csv)
    exclusion_rows = load_exclusion_rows(exclusion_csv)
    exclusion_by_code = _group_exclusions_by_code(exclusion_rows)

    # 校验 exclusion 家族白名单（防止脏行 silently 进入）
    bad_families = sorted({
        (r.get("cohort_family") or "").strip()
        for r in exclusion_rows
        if (r.get("cohort_family") or "").strip() not in POOL_EXCLUSION_FAMILIES
    })
    if bad_families:
        raise RuntimeError(f"unknown_exclusion_cohort_family: {bad_families}")

    reconcile_rows = build_reconcile_rows(companies, status_map, exclusion_by_code)
    metrics = compute_metrics(companies, reconcile_rows, exclusion_rows)
    paths = write_outputs(
        output_root_rel=output_root,
        reconcile_rows=reconcile_rows,
        metrics=metrics,
        universe_yaml=universe_yaml,
        exclusion_csv=exclusion_csv,
        status_csv=status_csv,
    )
    metrics["artifacts"] = paths
    return metrics


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="C-class snapshot exclusion reconcile dry-run（validation only）"
    )
    parser.add_argument("--universe-yaml", default=DEFAULT_UNIVERSE_YAML)
    parser.add_argument("--exclusion-csv", default=DEFAULT_EXCLUSION_CSV)
    parser.add_argument("--status-csv", default=DEFAULT_STATUS_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)

    result = run_dryrun(
        universe_yaml=args.universe_yaml,
        exclusion_csv=args.exclusion_csv,
        status_csv=args.status_csv,
        output_root=args.output_root,
    )
    print(f"mode: snapshot_exclusion_reconcile_dryrun")
    print(f"gate: {result['gate']}")
    print(f"universe: {result['universe_count']}")
    print(f"excluded_unique: {result['excluded_unique_count']}")
    print(f"complete_pool: {result['pool_decision_counts'].get('included_complete_pool', 0)}")
    print(f"cninfo_calls: {result['cninfo_calls']}")
    print(f"snapshot_json_writes: {result['snapshot_json_writes']}")
    print(f"execute_production_snapshot_rebuild: {result['execute_production_snapshot_rebuild']}")
    for key, path in (result.get("artifacts") or {}).items():
        print(f"{key}: {path}")
    return 0 if result["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())

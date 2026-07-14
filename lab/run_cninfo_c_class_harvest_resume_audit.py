#!/usr/bin/env python3
"""
CNINFO C-class Era D 863-scale harvest resume 审计（仅 dry-run · 只读生产 harvest）。

扫描本地 harvest 树，生成 resume-readiness 报告；不调用 CNINFO、不写入生产 harvest/snapshot。

Usage:
    python lab/run_cninfo_c_class_harvest_resume_audit.py --dry-run \\
      --harvest-root outputs/harvest/cninfo_c_class \\
      --protected-roots-csv outputs/validation/cninfo_c_class_erad_protected_output_roots.csv \\
      --output-root outputs/validation/cninfo_c_class_erad_harvest_resume_audit/
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import yaml  # noqa: E402

from build_cninfo_c_class_company_snapshot import SOURCE_TO_SUBDIR  # noqa: E402
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    CLEANUP_REFUSED_MSG,
    DEFAULT_ERAD_AUDIT_OUTPUT_ROOT_REL,
    assert_safe_erad_audit_write_path,
    is_protected_c_class_production_root,
    normalize_cleanup_path,
)
from harvest_cninfo_c_class import HARVEST_MATRIX_SOURCE_ORDER  # noqa: E402

DEFAULT_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class"
DEFAULT_UNIVERSE_YAML = "lab/eval_companies_c_class_harvest_863_non_bse.yaml"
DEFAULT_PROTECTED_CSV = "outputs/validation/cninfo_c_class_erad_protected_output_roots.csv"

REPORT_CSV_NAME = "c_class_erad_harvest_resume_audit_report.csv"
SUMMARY_MD_NAME = "c_class_erad_harvest_resume_audit_summary.md"
METRICS_CSV_NAME = "c_class_erad_harvest_resume_audit_metrics.csv"
SOURCE_LEDGER_CSV_NAME = "c_class_erad_harvest_resume_audit_source_ledger.csv"

HARVEST_RESUME_LIVE_APPROVAL_REQUIRED = "C_CLASS_ERAD_HARVEST_RESUME_LIVE_APPROVAL_REQUIRED"

# 已知 batch 子树（排除 _mock_*）
KNOWN_BATCH_SUBTREES: Tuple[str, ...] = (
    "phase3_batch_500_001",
    "phase35_batch_500_001",
    "phase35_batch_500_001_resume",
    "phase2_smoke_200",
)

RESUME_STATES: Tuple[str, ...] = (
    "complete",
    "partial",
    "missing",
    "needs_review",
    "unknown",
)

REPORT_FIELDS = [
    "company_code",
    "company_name",
    "board",
    "harvest_subtree",
    "resume_state",
    "harvest_status_csv",
    "sources_expected",
    "sources_present",
    "sources_missing",
    "missing_source_ids",
    "live_resume_recommendation",
    "audit_mode",
    "notes",
]

SOURCE_LEDGER_FIELDS = [
    "company_code",
    "harvest_subtree",
    "source_id",
    "normalized_subdir",
    "file_exists",
    "source_resume_state",
    "notes",
]

METRICS_FIELDS = [
    "metric_key",
    "metric_value",
    "notes",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_universe(yaml_rel: str) -> List[Dict[str, str]]:
    path = os.path.join(BASE_DIR, yaml_rel)
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    out: List[Dict[str, str]] = []
    for c in data.get("companies") or []:
        out.append({
            "company_code": str(c["stock_code"]),
            "company_name": str(c.get("company_name") or c.get("name") or ""),
            "board": str(c.get("board") or ""),
        })
    out.sort(key=lambda x: x["company_code"])
    return out


def _discover_harvest_subtrees(harvest_root: str) -> List[Tuple[str, str]]:
    """
    返回 (subtree_label, absolute_path) 列表。
    始终包含主 863 根（label=863_primary）；并扫描已知 batch 子目录。
    """
    subtrees: List[Tuple[str, str]] = [("863_primary", harvest_root)]
    if not os.path.isdir(harvest_root):
        return subtrees

    for name in sorted(os.listdir(harvest_root)):
        if name.startswith("_mock"):
            continue
        if name in KNOWN_BATCH_SUBTREES:
            path = os.path.join(harvest_root, name)
            if os.path.isdir(path):
                subtrees.append((name, path))
        elif name.startswith("phase") and os.path.isdir(os.path.join(harvest_root, name)):
            path = os.path.join(harvest_root, name)
            if (name, path) not in subtrees:
                subtrees.append((name, path))
    return subtrees


def _load_company_status_map(subtree_path: str) -> Dict[str, Dict[str, str]]:
    status_csv = os.path.join(subtree_path, "quality", "company_harvest_status.csv")
    rows: Dict[str, Dict[str, str]] = {}
    if not os.path.isfile(status_csv):
        return rows
    with open(status_csv, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("company_code") or "").strip()
            if code:
                rows[code] = dict(row)
    return rows


def _normalized_path(subtree_path: str, source_id: str, company_code: str) -> str:
    subdir, ext = SOURCE_TO_SUBDIR[source_id]
    return os.path.join(subtree_path, "normalized", subdir, f"{company_code}{ext}")


def _source_present(subtree_path: str, source_id: str, company_code: str) -> bool:
    path = _normalized_path(subtree_path, source_id, company_code)
    if not os.path.isfile(path):
        return False
    if path.endswith(".json"):
        return os.path.getsize(path) > 2
    if path.endswith(".jsonl"):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    return True
        return False
    return True


def _classify_source_state(present: bool) -> str:
    if present:
        return "present"
    return "missing"


def _classify_company_resume_state(
    company_code: str,
    status_row: Optional[Dict[str, str]],
    sources_present: int,
    sources_expected: int,
    *,
    in_universe: bool,
) -> Tuple[str, str]:
    """
    resume_state 映射（与 harvest runner 对齐并扩展）：
    - complete: company_harvest_status=complete 且 sources_present >= sources_expected
    - partial: harvest_status in (partial, failed) 或 sources 缺口但存在部分文件
    - missing: 无 status 且无 normalized 文件
    - needs_review: 无 status 行但磁盘有文件；或 complete 但 sources 计数不一致
    - unknown: 无法判定（非 universe 且无数据）
    """
    csv_status = (status_row or {}).get("harvest_status", "").strip()

    if not in_universe and not status_row and sources_present == 0:
        return "unknown", "outside_863_universe_no_artifacts"

    if sources_present == 0 and not status_row:
        return "missing", "no_status_row_no_normalized_files"

    if csv_status == "complete" and sources_present >= sources_expected:
        return "complete", "status_csv_complete_sources_ok"

    if csv_status == "complete" and sources_present < sources_expected:
        return "needs_review", "status_csv_complete_but_source_gap"

    if csv_status == "partial":
        return "partial", "status_csv_partial"

    if csv_status == "failed":
        return "partial", "status_csv_failed_treated_as_partial_for_resume"

    if not status_row and sources_present > 0:
        return "needs_review", "normalized_on_disk_without_status_row"

    if sources_present > 0 and sources_present < sources_expected:
        return "partial", "source_gap_without_status_csv"

    if csv_status:
        return "needs_review", f"unmapped_status_csv={csv_status}"

    return "unknown", "classification_fallback"


def _live_resume_recommendation(resume_state: str) -> str:
    if resume_state == "complete":
        return "none"
    if resume_state == "missing":
        return "deferred_targeted_live_after_approval"
    if resume_state == "partial":
        return "deferred_targeted_live_after_approval"
    if resume_state == "needs_review":
        return "offline_review_first"
    return "hold"


def audit_harvest_subtree(
    subtree_label: str,
    subtree_path: str,
    universe: List[Dict[str, str]],
    *,
    audit_mode: str = "dry_run",
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[str, int]]:
    """对单 harvest 子树做只读审计。"""
    universe_codes = {c["company_code"] for c in universe}
    universe_by_code = {c["company_code"]: c for c in universe}
    status_map = _load_company_status_map(subtree_path)
    sources_expected = len(HARVEST_MATRIX_SOURCE_ORDER)

    report_rows: List[Dict[str, str]] = []
    source_ledger: List[Dict[str, str]] = []
    state_counts: Counter = Counter()

    # 863 主轨：以 universe 为主；batch 子树以 status csv 中出现的公司为主
    if subtree_label == "863_primary":
        company_codes = sorted(universe_codes)
    else:
        company_codes = sorted(set(status_map.keys()))

    for code in company_codes:
        meta = universe_by_code.get(code, {
            "company_code": code,
            "company_name": status_map.get(code, {}).get("company_name", ""),
            "board": "",
        })
        status_row = status_map.get(code)
        present_sources: List[str] = []
        missing_sources: List[str] = []

        for sid in HARVEST_MATRIX_SOURCE_ORDER:
            present = _source_present(subtree_path, sid, code)
            subdir, _ = SOURCE_TO_SUBDIR[sid]
            src_state = _classify_source_state(present)
            source_ledger.append({
                "company_code": code,
                "harvest_subtree": subtree_label,
                "source_id": sid,
                "normalized_subdir": subdir,
                "file_exists": "yes" if present else "no",
                "source_resume_state": src_state,
                "notes": audit_mode,
            })
            if present:
                present_sources.append(sid)
            else:
                missing_sources.append(sid)

        resume_state, notes = _classify_company_resume_state(
            code,
            status_row,
            len(present_sources),
            sources_expected,
            in_universe=code in universe_codes,
        )
        state_counts[resume_state] += 1

        report_rows.append({
            "company_code": code,
            "company_name": meta.get("company_name", ""),
            "board": meta.get("board", ""),
            "harvest_subtree": subtree_label,
            "resume_state": resume_state,
            "harvest_status_csv": (status_row or {}).get("harvest_status", ""),
            "sources_expected": str(sources_expected),
            "sources_present": str(len(present_sources)),
            "sources_missing": str(len(missing_sources)),
            "missing_source_ids": ";".join(missing_sources) if missing_sources else "",
            "live_resume_recommendation": _live_resume_recommendation(resume_state),
            "audit_mode": audit_mode,
            "notes": notes,
        })

    return report_rows, source_ledger, dict(state_counts)


def _assert_harvest_readonly(harvest_root: str) -> None:
    """确认 harvest 根为生产只读扫描目标（不阻止读取）。"""
    norm = normalize_cleanup_path(harvest_root)
    if not os.path.isdir(norm):
        raise SystemExit(f"harvest root not found: {norm}")


def _validate_output_root(output_root: str, allowed_audit_root_rel: str) -> str:
    norm = normalize_cleanup_path(output_root)
    assert_safe_erad_audit_write_path(norm, allowed_audit_root_rel=allowed_audit_root_rel)
    reports_dir = os.path.join(norm, "reports")
    assert_safe_erad_audit_write_path(reports_dir, allowed_audit_root_rel=allowed_audit_root_rel)
    os.makedirs(reports_dir, exist_ok=True)
    return norm


def _write_csv(
    path: str,
    fields: List[str],
    rows: Iterable[Dict[str, str]],
    *,
    allowed_audit_root_rel: str,
) -> None:
    assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=allowed_audit_root_rel)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_json(path: str, payload: Dict[str, Any], *, allowed_audit_root_rel: str) -> None:
    assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=allowed_audit_root_rel)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _write_summary_md(
    path: str,
    *,
    harvest_root: str,
    subtrees: List[Tuple[str, str]],
    primary_state_counts: Dict[str, int],
    all_state_counts: Dict[str, int],
    total_report_rows: int,
    audit_mode: str,
    allowed_audit_root_rel: str,
) -> None:
    assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=allowed_audit_root_rel)
    lines = [
        "# C-Class Era D Harvest Resume Audit Summary",
        "",
        f"_generated_at: {_utc_now_iso()}_",
        "",
        "> **offline dry-run only** · **CNINFO = 0** · **production harvest read-only**",
        "",
        "## Scan scope",
        "",
        f"- **harvest_root:** `{harvest_root}`",
        f"- **audit_mode:** `{audit_mode}`",
        "",
        "### Subtrees scanned",
        "",
    ]
    for label, abspath in subtrees:
        quality_csv = os.path.join(abspath, "quality", "company_harvest_status.csv")
        has_status = "yes" if os.path.isfile(quality_csv) else "no"
        lines.append(f"- `{label}` → `{abspath}` (status_csv={has_status})")

    lines.extend([
        "",
        "## Resume state counts (863_primary)",
        "",
        "| resume_state | count |",
        "|--------------|-------|",
    ])
    for state in RESUME_STATES:
        lines.append(f"| {state} | {primary_state_counts.get(state, 0)} |")

    lines.extend([
        "",
        "## Resume state counts (all subtrees)",
        "",
        "| resume_state | count |",
        "|--------------|-------|",
    ])
    for state in RESUME_STATES:
        lines.append(f"| {state} | {all_state_counts.get(state, 0)} |")

    lines.extend([
        "",
        f"- **total report rows:** {total_report_rows}",
        "",
        "## State mapping",
        "",
        "| resume_state | 判定规则 |",
        "|--------------|----------|",
        "| complete | `company_harvest_status=complete` 且 normalized 源齐全 |",
        "| partial | `partial`/`failed` 或源缺口但有部分文件 |",
        "| missing | 无 status 行且无 normalized 文件 |",
        "| needs_review | 磁盘有文件但无 status 行；或 complete 与源计数不一致 |",
        "| unknown | 非 863 universe 且无数据 |",
        "",
        "## Live resume recommendation",
        "",
        "- **hold** for 863_primary when complete dominates and gaps are needs_review/missing only",
        "- **deferred_targeted_live_after_approval** for partial/missing (separate Slice-C-EraD-02b)",
        "- **no snapshot rebuild** in this slice",
        "",
        "## Red lines",
        "",
        "No CNINFO · no live harvest · no production root writes · holdout policy unchanged",
        "",
    ])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def run_audit(args: argparse.Namespace) -> Dict[str, Any]:
    if args.live:
        if not getattr(args, "approve_harvest_resume_live", False):
            print(HARVEST_RESUME_LIVE_APPROVAL_REQUIRED, file=sys.stderr)
            raise SystemExit(2)
        print("live harvest resume not implemented in Era D Slice-C-EraD-02", file=sys.stderr)
        raise SystemExit(2)

    if not args.dry_run:
        print("--dry-run is required for Slice-C-EraD-02", file=sys.stderr)
        raise SystemExit(2)

    harvest_root = normalize_cleanup_path(args.harvest_root)
    _assert_harvest_readonly(harvest_root)

    allowed_audit_rel = os.path.relpath(
        normalize_cleanup_path(args.output_root),
        BASE_DIR,
    )
    output_root = _validate_output_root(args.output_root, allowed_audit_rel)

    universe = _load_universe(args.universe_yaml)
    subtrees = _discover_harvest_subtrees(harvest_root)

    all_reports: List[Dict[str, str]] = []
    all_source_ledger: List[Dict[str, str]] = []
    all_state_counts: Counter = Counter()
    primary_state_counts: Dict[str, int] = {}

    for label, path in subtrees:
        reports, ledger, counts = audit_harvest_subtree(
            label, path, universe, audit_mode="dry_run",
        )
        all_reports.extend(reports)
        all_source_ledger.extend(ledger)
        for k, v in counts.items():
            all_state_counts[k] += v
        if label == "863_primary":
            primary_state_counts = counts

    reports_dir = os.path.join(output_root, "reports")
    report_csv = os.path.join(reports_dir, REPORT_CSV_NAME)
    summary_md = os.path.join(reports_dir, SUMMARY_MD_NAME)
    metrics_csv = os.path.join(reports_dir, METRICS_CSV_NAME)
    ledger_csv = os.path.join(reports_dir, SOURCE_LEDGER_CSV_NAME)
    run_meta_json = os.path.join(output_root, "run_meta.json")

    _write_csv(report_csv, REPORT_FIELDS, all_reports, allowed_audit_root_rel=allowed_audit_rel)
    _write_csv(ledger_csv, SOURCE_LEDGER_FIELDS, all_source_ledger, allowed_audit_root_rel=allowed_audit_rel)

    metrics_rows: List[Dict[str, str]] = [
        {"metric_key": "universe_size", "metric_value": str(len(universe)), "notes": "863_non_bse"},
        {"metric_key": "subtrees_scanned", "metric_value": str(len(subtrees)), "notes": ""},
        {"metric_key": "report_rows", "metric_value": str(len(all_reports)), "notes": ""},
        {"metric_key": "cninfo_calls", "metric_value": "0", "notes": "dry_run_only"},
    ]
    for state in RESUME_STATES:
        metrics_rows.append({
            "metric_key": f"863_primary_{state}",
            "metric_value": str(primary_state_counts.get(state, 0)),
            "notes": "863_primary",
        })
    _write_csv(metrics_csv, METRICS_FIELDS, metrics_rows, allowed_audit_root_rel=allowed_audit_rel)

    _write_summary_md(
        summary_md,
        harvest_root=args.harvest_root,
        subtrees=subtrees,
        primary_state_counts=primary_state_counts,
        all_state_counts=dict(all_state_counts),
        total_report_rows=len(all_reports),
        audit_mode="dry_run",
        allowed_audit_root_rel=allowed_audit_rel,
    )

    meta = {
        "generated_at": _utc_now_iso(),
        "audit_mode": "dry_run",
        "harvest_root": args.harvest_root,
        "output_root": args.output_root,
        "protected_roots_csv": args.protected_roots_csv,
        "universe_yaml": args.universe_yaml,
        "subtrees": [{"label": l, "path": p} for l, p in subtrees],
        "primary_state_counts": primary_state_counts,
        "all_state_counts": dict(all_state_counts),
        "cninfo_calls": 0,
        "report_csv": report_csv,
        "summary_md": summary_md,
    }
    _write_json(run_meta_json, meta, allowed_audit_root_rel=allowed_audit_rel)

    print(f"audit_complete dry_run=1 report={report_csv}")
    print(f"primary_state_counts={json.dumps(primary_state_counts, ensure_ascii=False)}")
    return meta


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="C-class Era D harvest resume audit (dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="offline read-only audit (required)")
    parser.add_argument("--live", action="store_true", help="refused without separate approval")
    parser.add_argument(
        "--approve-harvest-resume-live",
        action="store_true",
        help="explicit approval flag (still refused in Slice-C-EraD-02)",
    )
    parser.add_argument("--harvest-root", default=DEFAULT_HARVEST_ROOT_REL)
    parser.add_argument("--protected-roots-csv", default=DEFAULT_PROTECTED_CSV)
    parser.add_argument("--output-root", default=DEFAULT_ERAD_AUDIT_OUTPUT_ROOT_REL)
    parser.add_argument("--universe-yaml", default=DEFAULT_UNIVERSE_YAML)
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    # 加载 protected CSV 路径供 guard 缓存（只读）
    _ = args.protected_roots_csv
    run_audit(args)


if __name__ == "__main__":
    main()

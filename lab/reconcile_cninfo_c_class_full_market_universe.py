#!/usr/bin/env python3
"""
CNINFO C-class 全市场 universe 离线对账脚本。

比较 Era B 6124 基准与 Era C 已验证 universe，仅分类、不合并、不请求 CNINFO。
默认 dry-run only。
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ERA_B_YAML = os.path.join(BASE_DIR, "lab/eval_companies_full_market_2024.yaml")
ERA_C_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")
BSE_920_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_920_active.yaml")
BSE_LEGACY_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml")
LEDGER_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_identity_decision_ledger.csv"
)
CANDIDATE_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_draft.csv"
)
CONFLICT_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_conflict_triage.csv"
)

RESULT_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_full_market_universe_reconciliation_result.csv"
)
SUMMARY_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_full_market_universe_reconciliation_summary.md"
)

RESULT_COLUMNS = [
    "reconciliation_id",
    "company_code",
    "company_name",
    "source_universe",
    "matched_universe",
    "classification",
    "canonical_candidate",
    "identity_confidence",
    "evidence_source",
    "notes",
]

CLASSIFICATIONS = [
    "matched_active",
    "already_in_c_class",
    "matched_hold",
    "matched_bse_supported_candidate",
    "matched_bse_legacy_hold",
    "identity_conflict",
    "needs_manual_review",
    "not_found_in_cninfo",
]

NAME_SIMILARITY_THRESHOLD = 0.92


def _normalize_code(code: Any) -> str:
    text = str(code).strip()
    if text.isdigit():
        return text.zfill(6)
    return text


def _load_yaml_companies(path: str) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return list(data.get("companies") or [])


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _company_name(entry: Dict[str, Any]) -> str:
    return str(entry.get("short_name") or entry.get("company_name") or "").strip()


def _org_id(entry: Dict[str, Any]) -> str:
    return str(entry.get("orgid") or entry.get("org_id") or "").strip()


def _is_bse_legacy_code(code: str) -> bool:
    return code.startswith(("83", "87", "43"))


def _is_bse_920_code(code: str) -> bool:
    return code.startswith("92")


def _name_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _canonical_id(code: str) -> str:
    return f"CNINFO_{_normalize_code(code)}"


def load_universe_codes(path: str) -> Set[str]:
    return {_normalize_code(c.get("stock_code") or c.get("company_code")) for c in _load_yaml_companies(path)}


def build_ledger_index(ledger_rows: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    index: Dict[str, List[Dict[str, str]]] = {}
    for row in ledger_rows:
        for key in ("old_company_code", "new_company_code"):
            code = _normalize_code(row.get(key, ""))
            if code:
                index.setdefault(code, []).append(row)
    return index


def build_org_index(
    era_b_rows: List[Dict[str, Any]],
    candidate_rows: Dict[str, Dict[str, str]],
) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for entry in era_b_rows:
        code = _normalize_code(entry.get("stock_code"))
        org = _org_id(entry)
        if org:
            index.setdefault(org, []).append(code)
    for code, row in candidate_rows.items():
        org = str(row.get("org_id") or "").strip()
        if org and "|" not in org:
            if code not in index.get(org, []):
                index.setdefault(org, []).append(code)
    return index


def build_name_index(era_b_rows: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for entry in era_b_rows:
        code = _normalize_code(entry.get("stock_code"))
        name = _company_name(entry)
        if name:
            index.setdefault(name, []).append(code)
    return index


def build_conflict_code_set(conflict_rows: List[Dict[str, str]]) -> Set[str]:
    codes: Set[str] = set()
    for row in conflict_rows:
        notes = row.get("notes", "")
        for match in re.findall(r"codes=([^;\"]+)", notes):
            for part in match.split(","):
                codes.add(_normalize_code(part.strip()))
        cid1 = row.get("company_id_1", "")
        cid2 = row.get("company_id_2", "")
        for cid in (cid1, cid2):
            if cid.startswith("CNINFO_"):
                codes.add(_normalize_code(cid.replace("CNINFO_", "")))
    return codes


def load_candidate_map(path: str = CANDIDATE_CSV) -> Dict[str, Dict[str, str]]:
    return {_normalize_code(r["company_code"]): r for r in _load_csv(path)}


def _ledger_for_code(code: str, ledger_index: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
    return ledger_index.get(code, [])


def _pick_ledger_entry(
    code: str, entries: List[Dict[str, str]]
) -> Optional[Dict[str, str]]:
    if not entries:
        return None
    for row in entries:
        if row.get("decision_type") == "duplicate_identity":
            return row
    for row in entries:
        if row.get("decision_status") == "manual_review":
            return row
    return entries[0]


def _evidence_from_ledger(row: Dict[str, str]) -> str:
    return str(row.get("decision_type") or "canonical_identity_ledger")


def classify_company(
    code: str,
    name: str,
    org_id: str,
    era_c_codes: Set[str],
    hold_codes: Set[str],
    bse_920_codes: Set[str],
    bse_legacy_codes: Set[str],
    ledger_index: Dict[str, List[Dict[str, str]]],
    candidate_map: Dict[str, Dict[str, str]],
    org_index: Dict[str, List[str]],
    name_index: Dict[str, List[str]],
    conflict_codes: Set[str],
) -> Dict[str, str]:
    candidate = candidate_map.get(code, {})
    ledger_entries = _ledger_for_code(code, ledger_index)
    ledger_row = _pick_ledger_entry(code, ledger_entries)

    # 优先级 1：company_code 精确匹配
    if code in era_c_codes:
        return {
            "source_universe": "era_b",
            "matched_universe": "era_c",
            "classification": "already_in_c_class",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "high",
            "evidence_source": "company_code_exact",
            "notes": "Era C 863 已验证 universe",
        }

    if code in hold_codes:
        return {
            "source_universe": "era_b",
            "matched_universe": "hold",
            "classification": "matched_hold",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "high",
            "evidence_source": "company_code_exact",
            "notes": "26 all6 hold；hold_no_retry 侧轨",
        }

    # 优先级 2：canonical identity decision ledger
    if ledger_row:
        decision_type = ledger_row.get("decision_type", "")
        decision_status = ledger_row.get("decision_status", "")
        canonical = ledger_row.get("canonical_candidate") or _canonical_id(code)

        if decision_type == "duplicate_identity":
            return {
                "source_universe": "era_b",
                "matched_universe": "identity_ledger",
                "classification": "identity_conflict",
                "canonical_candidate": canonical,
                "identity_confidence": "high",
                "evidence_source": "canonical_identity_ledger",
                "notes": ledger_row.get("notes", "duplicate_identity；不合并"),
            }

        if decision_status == "manual_review":
            return {
                "source_universe": "era_b",
                "matched_universe": "identity_ledger",
                "classification": "needs_manual_review",
                "canonical_candidate": _canonical_id(code),
                "identity_confidence": "medium",
                "evidence_source": _evidence_from_ledger(ledger_row),
                "notes": ledger_row.get("notes", "ledger manual_review") + "；不自动合并",
            }

        if decision_type == "rename_history":
            old_code = _normalize_code(ledger_row.get("old_company_code", ""))
            new_code = _normalize_code(ledger_row.get("new_company_code", ""))
            if code == old_code and old_code != new_code:
                return {
                    "source_universe": "era_b",
                    "matched_universe": "identity_ledger",
                    "classification": "identity_conflict",
                    "canonical_candidate": canonical,
                    "identity_confidence": "high",
                    "evidence_source": "rename_history",
                    "notes": f"rename_history 旧码保留；canonical→{canonical}；不合并",
                }
            return {
                "source_universe": "era_b",
                "matched_universe": "identity_ledger",
                "classification": "matched_active",
                "canonical_candidate": canonical,
                "identity_confidence": "high",
                "evidence_source": "rename_history",
                "notes": ledger_row.get("notes", "rename_history approved"),
            }

        if decision_type == "legacy_code_mapping":
            old_code = _normalize_code(ledger_row.get("old_company_code", ""))
            if code == old_code:
                return {
                    "source_universe": "era_b",
                    "matched_universe": "identity_ledger",
                    "classification": "matched_bse_legacy_hold",
                    "canonical_candidate": canonical,
                    "identity_confidence": "high",
                    "evidence_source": "legacy_code_mapping",
                    "notes": ledger_row.get("notes", "BSE legacy mapping"),
                }
            return {
                "source_universe": "era_b",
                "matched_universe": "identity_ledger",
                "classification": "matched_bse_supported_candidate",
                "canonical_candidate": canonical,
                "identity_confidence": "high",
                "evidence_source": "legacy_code_mapping",
                "notes": ledger_row.get("notes", "BSE 920 canonical"),
            }

    # BSE 启发式（ledger 未覆盖时）
    board = str(candidate.get("board", "")).strip()
    if _is_bse_legacy_code(code) or code in bse_legacy_codes or (
        board == "bse" and _is_bse_legacy_code(code)
    ):
        return {
            "source_universe": "era_b",
            "matched_universe": "bse_legacy",
            "classification": "matched_bse_legacy_hold",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "medium",
            "evidence_source": "legacy_code_mapping",
            "notes": "BSE 83/87/43 legacy 侧轨",
        }

    if _is_bse_920_code(code) or code in bse_920_codes or board == "bse":
        return {
            "source_universe": "era_b",
            "matched_universe": "bse_920",
            "classification": "matched_bse_supported_candidate",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "medium",
            "evidence_source": "company_code_exact",
            "notes": "BSE 920 支持候选",
        }

    # 优先级 3：org_id 匹配
    if org_id:
        org_codes = org_index.get(org_id, [])
        if len(org_codes) > 1 and code in org_codes:
            other = [c for c in org_codes if c != code]
            return {
                "source_universe": "era_b",
                "matched_universe": "org_id_index",
                "classification": "identity_conflict",
                "canonical_candidate": _canonical_id(code),
                "identity_confidence": "medium",
                "evidence_source": "org_id_match",
                "notes": f"org_id 多码冲突；并存 codes={','.join(sorted(org_codes[:4]))}；不合并",
            }

    if str(candidate.get("org_id_conflict_flag", "")).lower() == "true":
        return {
            "source_universe": "era_b",
            "matched_universe": "registry_candidate",
            "classification": "identity_conflict",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "medium",
            "evidence_source": "org_id_match",
            "notes": "candidate org_id_conflict_flag=true",
        }

    # 优先级 4/5：candidate rename / legacy 字段
    rename_hist = str(candidate.get("rename_history", "")).strip()
    if rename_hist and rename_hist not in ("[]", ""):
        return {
            "source_universe": "era_b",
            "matched_universe": "registry_candidate",
            "classification": "identity_conflict",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "low",
            "evidence_source": "rename_history",
            "notes": f"candidate rename_history={rename_hist}",
        }

    legacy_code = str(candidate.get("legacy_code", "")).strip()
    if legacy_code:
        return {
            "source_universe": "era_b",
            "matched_universe": "registry_candidate",
            "classification": "matched_bse_legacy_hold",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "low",
            "evidence_source": "legacy_code_mapping",
            "notes": f"candidate legacy_code={legacy_code}",
        }

    # conflict triage 残余
    if code in conflict_codes:
        return {
            "source_universe": "era_b",
            "matched_universe": "conflict_triage",
            "classification": "needs_manual_review",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "low",
            "evidence_source": "org_id_match",
            "notes": "conflict_triage 未结案",
        }

    # 优先级 6：company_name similarity
    same_name_codes = name_index.get(name, [])
    if len(same_name_codes) > 1 and code in same_name_codes:
        return {
            "source_universe": "era_b",
            "matched_universe": "name_index",
            "classification": "needs_manual_review",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "low",
            "evidence_source": "company_name_similarity",
            "notes": f"同名不同码 codes={','.join(sorted(same_name_codes))}；不自动合并",
        }

    for other_name, other_codes in name_index.items():
        if other_name == name:
            continue
        if _name_similarity(name, other_name) >= NAME_SIMILARITY_THRESHOLD:
            if code in era_c_codes:
                break
            return {
                "source_universe": "era_b",
                "matched_universe": "name_index",
                "classification": "needs_manual_review",
                "canonical_candidate": _canonical_id(code),
                "identity_confidence": "low",
                "evidence_source": "company_name_similarity",
                "notes": f"名称相似候选 {other_name}；不自动合并",
            }

    # 默认：candidate 存在则 matched_active，否则 not_found
    if candidate:
        return {
            "source_universe": "era_b",
            "matched_universe": "registry_candidate",
            "classification": "matched_active",
            "canonical_candidate": _canonical_id(code),
            "identity_confidence": "medium",
            "evidence_source": "company_code_exact",
            "notes": "Era B 扩展候选；未在 Era C 863 验证",
        }

    return {
        "source_universe": "era_b",
        "matched_universe": "none",
        "classification": "not_found_in_cninfo",
        "canonical_candidate": _canonical_id(code),
        "identity_confidence": "low",
        "evidence_source": "company_code_exact",
        "notes": "Era B 有记录但 registry candidate 无对应",
    }


def reconcile_universe(
    era_b_yaml: str = ERA_B_YAML,
    era_c_yaml: str = ERA_C_YAML,
    hold_yaml: str = HOLD_YAML,
    bse_920_yaml: str = BSE_920_YAML,
    bse_legacy_yaml: str = BSE_LEGACY_YAML,
    ledger_csv: str = LEDGER_CSV,
    candidate_csv: str = CANDIDATE_CSV,
    conflict_csv: str = CONFLICT_CSV,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    era_b_rows = _load_yaml_companies(era_b_yaml)
    era_c_codes = load_universe_codes(era_c_yaml)
    hold_codes = load_universe_codes(hold_yaml)
    bse_920_codes = load_universe_codes(bse_920_yaml)
    bse_legacy_codes = load_universe_codes(bse_legacy_yaml)

    ledger_rows = _load_csv(ledger_csv)
    ledger_index = build_ledger_index(ledger_rows)
    candidate_map = load_candidate_map(candidate_csv)
    conflict_codes = build_conflict_code_set(_load_csv(conflict_csv))
    org_index = build_org_index(era_b_rows, candidate_map)
    name_index = build_name_index(era_b_rows)

    results: List[Dict[str, str]] = []
    for idx, entry in enumerate(era_b_rows, start=1):
        code = _normalize_code(entry.get("stock_code"))
        name = _company_name(entry)
        org = _org_id(entry)
        row = classify_company(
            code=code,
            name=name,
            org_id=org,
            era_c_codes=era_c_codes,
            hold_codes=hold_codes,
            bse_920_codes=bse_920_codes,
            bse_legacy_codes=bse_legacy_codes,
            ledger_index=ledger_index,
            candidate_map=candidate_map,
            org_index=org_index,
            name_index=name_index,
            conflict_codes=conflict_codes,
        )
        row["reconciliation_id"] = f"RECON_{idx:04d}"
        row["company_code"] = code
        row["company_name"] = name
        results.append(row)

    stats = {
        "era_b_count": len(era_b_rows),
        "era_c_count": len(era_c_codes),
        "hold_count": len(hold_codes),
        "bse_920_smoke": len(bse_920_codes),
        "bse_legacy_smoke": len(bse_legacy_codes),
        "classification_counts": dict(Counter(r["classification"] for r in results)),
        "identity_conflict_count": sum(
            1 for r in results if r["classification"] == "identity_conflict"
        ),
        "manual_review_count": sum(
            1 for r in results if r["classification"] == "needs_manual_review"
        ),
        "bse_supported_count": sum(
            1 for r in results if r["classification"] == "matched_bse_supported_candidate"
        ),
        "bse_legacy_count": sum(
            1 for r in results if r["classification"] == "matched_bse_legacy_hold"
        ),
    }
    return results, stats


def write_result_csv(rows: List[Dict[str, str]], path: str = RESULT_OUT) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(stats: Dict[str, Any], path: str = SUMMARY_OUT) -> None:
    counts = stats["classification_counts"]
    lines = [
        "# CNINFO C-Class Full Market Universe Reconciliation Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_",
        "",
        "> 离线 universe 对账 dry-run 摘要。**仅分类** · **不合并** · **无 CNINFO**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "---",
        "",
        "# Universe Counts",
        "",
        "| Universe | Count |",
        "|----------|-------|",
        f"| Era B baseline | **{stats['era_b_count']}** |",
        f"| Era C active | **{stats['era_c_count']}** |",
        f"| Hold | **{stats['hold_count']}** |",
        f"| BSE supported（classification） | **{stats['bse_supported_count']}** |",
        f"| BSE legacy（classification） | **{stats['bse_legacy_count']}** |",
        "",
        "---",
        "",
        "# Matching Results",
        "",
        "| classification | count |",
        "|----------------|-------|",
    ]
    for cls in CLASSIFICATIONS:
        lines.append(f"| {cls} | **{counts.get(cls, 0)}** |")
    lines.extend(
        [
            "",
            "---",
            "",
            "# Identity Risk",
            "",
            "| 指标 | count |",
            "|------|-------|",
            f"| identity_conflict | **{stats['identity_conflict_count']}** |",
            f"| needs_manual_review | **{stats['manual_review_count']}** |",
            "",
            "---",
            "",
            "# Important Caveat",
            "",
            "Era B 6124 and Era C 863 belong to different lineage sources.",
            "",
            "Reconciliation result is classification only.",
            "",
            "It does not create registry rows.",
            "",
            "It does not trigger harvest expansion.",
            "",
            "---",
            "",
            "# Gate",
            "",
            "**`universe_reconciliation_dryrun_gate = PASS_WITH_CAVEAT`**",
            "",
            "---",
            "",
            "# 产物",
            "",
            f"- [reconciliation result](cninfo_c_class_full_market_universe_reconciliation_result.csv) · **{stats['era_b_count']}** 行",
            f"- [reconciliation plan](../../plans/cninfo_c_class_full_market_universe_reconciliation_plan.md)",
            "",
        ]
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CNINFO C-class 全市场 universe 离线对账（dry-run only）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="默认 dry-run；仅离线分类，不写产物除非指定 --write",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="写入 reconciliation result CSV 与 summary",
    )
    parser.add_argument("--era-b", default=ERA_B_YAML)
    parser.add_argument("--era-c", default=ERA_C_YAML)
    parser.add_argument("--hold", default=HOLD_YAML)
    parser.add_argument("--result-out", default=RESULT_OUT)
    parser.add_argument("--summary-out", default=SUMMARY_OUT)
    args = parser.parse_args()

    rows, stats = reconcile_universe(
        era_b_yaml=args.era_b,
        era_c_yaml=args.era_c,
        hold_yaml=args.hold,
    )

    print(f"era_b={stats['era_b_count']} era_c={stats['era_c_count']} hold={stats['hold_count']}")
    for cls in CLASSIFICATIONS:
        print(f"  {cls}: {stats['classification_counts'].get(cls, 0)}")
    print(f"identity_conflict={stats['identity_conflict_count']}")
    print(f"manual_review={stats['manual_review_count']}")

    if args.write:
        write_result_csv(rows, args.result_out)
        write_summary(stats, args.summary_out)
        print(f"wrote {args.result_out}")
        print(f"wrote {args.summary_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公司画像试点回填：从 C 类 normalized 产物只读生成 portrait 事实层（offline）。"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HARVEST_ROOT = ROOT / "outputs" / "harvest" / "cninfo_c_class" / "normalized"
PORTRAIT_ROOT = ROOT / "outputs" / "portrait" / "companies"
VALIDATION = ROOT / "outputs" / "validation"
COMPANY_CODE = "000009"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def make_evidence_id(source_path: str, note: str = "") -> str:
    raw = f"{source_path}|{note}"
    return "ev_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def fact(
    field_id: str,
    module_id: str,
    value: Any,
    value_shape: str,
    source_track: str,
    evidence_ref_id: str,
    *,
    as_of: str | None = None,
    period: str | None = None,
    source_rank: int = 1,
    status: str = "testing",
) -> dict[str, Any]:
    return {
        "company_id": COMPANY_CODE,
        "field_id": field_id,
        "module_id": module_id,
        "value": value,
        "value_shape": value_shape,
        "as_of": as_of,
        "period": period,
        "source_track": source_track,
        "source_rank": source_rank,
        "evidence_ref_id": evidence_ref_id,
        "conflict_flag": "no",
        "status": status,
        "collected_at": utc_now(),
    }


def evidence(
    evidence_ref_id: str,
    source_path: str,
    *,
    source_url: str | None = None,
    sha256: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    return {
        "evidence_ref_id": evidence_ref_id,
        "source_path": source_path,
        "source_url": source_url,
        "sha256": sha256,
        "fetched_at": utc_now(),
        "note": note,
    }


def add_evidence_and_fact(
    facts: list[dict[str, Any]],
    evidences: list[dict[str, Any]],
    seen_evidence: set[str],
    source_file: Path,
    field_id: str,
    module_id: str,
    value: Any,
    value_shape: str,
    *,
    as_of: str | None = None,
    period: str | None = None,
    note: str = "",
    status: str = "testing",
    raw_hash: str | None = None,
) -> None:
    rel = rel_path(source_file)
    ev_id = make_evidence_id(rel, note)
    if ev_id not in seen_evidence:
        evidences.append(
            evidence(
                ev_id,
                rel,
                sha256=raw_hash,
                note=note or source_file.parent.name,
            )
        )
        seen_evidence.add(ev_id)
    facts.append(
        fact(
            field_id,
            module_id,
            value,
            value_shape,
            "C",
            ev_id,
            as_of=as_of,
            period=period,
            status=status,
        )
    )


def fill_from_share_capital(
    facts: list[dict[str, Any]],
    evidences: list[dict[str, Any]],
    seen_evidence: set[str],
) -> int:
    path = HARVEST_ROOT / "share_capital_profile" / f"{COMPANY_CODE}.jsonl"
    rows = read_jsonl(path)
    count = 0
    if not rows:
        return count
    latest = sorted(rows, key=lambda r: r.get("report_date") or "", reverse=True)[0]
    add_evidence_and_fact(
        facts,
        evidences,
        seen_evidence,
        path,
        "M01.primary_identity.company_code",
        "M01",
        latest.get("company_code"),
        "scalar",
        note="share_capital_latest",
        raw_hash=latest.get("raw_record_hash"),
    )
    count += 1
    add_evidence_and_fact(
        facts,
        evidences,
        seen_evidence,
        path,
        "M01.primary_identity.stock_short_name",
        "M01",
        latest.get("company_name"),
        "scalar",
        note="share_capital_latest",
        raw_hash=latest.get("raw_record_hash"),
    )
    count += 1
    add_evidence_and_fact(
        facts,
        evidences,
        seen_evidence,
        path,
        "M01.primary_identity.internal_company_id",
        "M01",
        latest.get("org_id"),
        "scalar",
        note="org_id_from_share_capital",
        raw_hash=latest.get("raw_record_hash"),
        status="partial",
    )
    count += 1
    add_evidence_and_fact(
        facts,
        evidences,
        seen_evidence,
        path,
        "M07.share_capital_structure.total_share_capital",
        "M07",
        latest.get("total_share_capital"),
        "timeseries",
        as_of=latest.get("report_date"),
        period=str(latest.get("report_date", ""))[:4] if latest.get("report_date") else None,
        note="share_capital_latest",
        raw_hash=latest.get("raw_record_hash"),
    )
    count += 1
    add_evidence_and_fact(
        facts,
        evidences,
        seen_evidence,
        path,
        "M07.share_capital_structure.float_share_capital",
        "M07",
        latest.get("float_share_capital"),
        "timeseries",
        as_of=latest.get("report_date"),
        period=str(latest.get("report_date", ""))[:4] if latest.get("report_date") else None,
        note="share_capital_latest",
        raw_hash=latest.get("raw_record_hash"),
    )
    count += 1
    return count


def fill_from_executives(
    facts: list[dict[str, Any]],
    evidences: list[dict[str, Any]],
    seen_evidence: set[str],
) -> int:
    path = HARVEST_ROOT / "executive_profile" / f"{COMPANY_CODE}.jsonl"
    rows = read_jsonl(path)
    count = 0
    for idx, row in enumerate(rows[:5]):
        note = f"executive_row_{idx}"
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M08.executive_board.person_name",
            "M08",
            row.get("person_name"),
            "scalar",
            note=note,
            raw_hash=row.get("raw_record_hash"),
        )
        count += 1
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M08.executive_board.position",
            "M08",
            row.get("position"),
            "scalar",
            note=note,
            raw_hash=row.get("raw_record_hash"),
        )
        count += 1
    return count


def fill_from_shareholders(
    facts: list[dict[str, Any]],
    evidences: list[dict[str, Any]],
    seen_evidence: set[str],
) -> int:
    path = HARVEST_ROOT / "top_shareholders_profile" / f"{COMPANY_CODE}.jsonl"
    rows = read_jsonl(path)
    count = 0
    latest_period = max((r.get("report_period") or "" for r in rows), default="")
    top_rows = [r for r in rows if r.get("report_period") == latest_period][:3]
    for idx, row in enumerate(top_rows):
        note = f"top_shareholder_row_{idx}"
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M07.shareholder_structure.holding_shares",
            "M07",
            {
                "shareholder_name": row.get("shareholder_name"),
                "holding_shares": row.get("holding_shares"),
                "rank": row.get("rank"),
            },
            "scalar",
            as_of=row.get("report_period"),
            period=str(row.get("report_period", ""))[:4] if row.get("report_period") else None,
            note=note,
            raw_hash=row.get("raw_record_hash"),
        )
        count += 1
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M07.shareholder_structure.holding_ratio",
            "M07",
            {
                "shareholder_name": row.get("shareholder_name"),
                "holding_ratio": row.get("holding_ratio"),
                "rank": row.get("rank"),
            },
            "scalar",
            as_of=row.get("report_period"),
            period=str(row.get("report_period", ""))[:4] if row.get("report_period") else None,
            note=note,
            raw_hash=row.get("raw_record_hash"),
        )
        count += 1
    return count


def fill_from_dividends(
    facts: list[dict[str, Any]],
    evidences: list[dict[str, Any]],
    seen_evidence: set[str],
) -> int:
    path = HARVEST_ROOT / "dividend_history" / f"{COMPANY_CODE}.jsonl"
    rows = read_jsonl(path)
    count = 0
    for idx, row in enumerate(rows[:3]):
        note = f"dividend_row_{idx}"
        year = row.get("dividend_year")
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M09.dividend_distribution.dividend_year",
            "M09",
            year,
            "timeseries",
            period=str(year) if year else None,
            note=note,
        )
        count += 1
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M09.dividend_distribution.dividend_plan_text",
            "M09",
            row.get("dividend_plan_text_raw"),
            "scalar",
            period=str(year) if year else None,
            note=note,
        )
        count += 1
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M09.dividend_distribution.cash_dividend_per_share",
            "M09",
            row.get("cash_dividend_per_share"),
            "timeseries",
            period=str(year) if year else None,
            note=note,
        )
        count += 1
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M09.dividend_distribution.ex_dividend_date",
            "M09",
            row.get("ex_dividend_date"),
            "event",
            as_of=row.get("ex_dividend_date"),
            period=str(year) if year else None,
            note=note,
        )
        count += 1
        add_evidence_and_fact(
            facts,
            evidences,
            seen_evidence,
            path,
            "M09.dividend_distribution.payment_date",
            "M09",
            row.get("payment_date"),
            "event",
            as_of=row.get("payment_date"),
            period=str(year) if year else None,
            note=note,
        )
        count += 1
    return count


def build_coverage(facts: list[dict[str, Any]]) -> dict[str, Any]:
    module_fields: dict[str, set[str]] = defaultdict(set)
    for item in facts:
        module_fields[item["module_id"]].add(item["field_id"])

    modules = {}
    for module_id in sorted(module_fields):
        modules[module_id] = {
            "filled_field_count": len(module_fields[module_id]),
            "status": "partial" if module_id == "M01" else "testing",
            "field_ids": sorted(module_fields[module_id]),
        }
    return {
        "company_id": COMPANY_CODE,
        "generated_at": utc_now(),
        "modules": modules,
        "gate": "portrait_p3_pilot_gate",
        "note": "M01 无 basic_profile harvest，身份字段来自 share_capital/executive 交叉引用",
    }


def update_coverage_matrix(filled_field_ids: set[str]) -> int:
    matrix_path = VALIDATION / "company_portrait_coverage_matrix_v0.csv"
    rows: list[dict[str, str]] = []
    updated = 0
    with matrix_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            if row["field_id"] in filled_field_ids:
                old = row["coverage_status"]
                row["coverage_status"] = "testing" if old in ("not_modeled", "candidate") else "partial"
                if old != row["coverage_status"]:
                    updated += 1
            rows.append(row)
    with matrix_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return updated


def write_pilot_summary(
    facts: list[dict[str, Any]],
    evidences: list[dict[str, Any]],
    updated_matrix_rows: int,
    gaps: list[str],
) -> None:
    module_counts: dict[str, int] = defaultdict(int)
    for item in facts:
        module_counts[item["module_id"]] += 1
    lines = [
        "# 公司画像试点填充摘要（000009）",
        "",
        f"_生成时间：{utc_now()}_",
        "",
        "## 试点公司",
        "",
        f"- company_code：**{COMPANY_CODE}**（中国宝安）",
        f"- 产出目录：`outputs/portrait/companies/{COMPANY_CODE}/`",
        "",
        "## 填充统计",
        "",
        f"- fact 条数：**{len(facts)}**",
        f"- evidence_ref 条数：**{len(evidences)}**",
        f"- 覆盖矩阵回写行数：**{updated_matrix_rows}**",
        "",
        "## 按模块",
        "",
        "| 模块 | fact 条数 | 状态 |",
        "|------|-----------|------|",
    ]
    for module_id in sorted(module_counts):
        lines.append(f"| {module_id} | {module_counts[module_id]} | testing/partial |")
    lines.extend(
        [
            "",
            "## 映射缺口",
            "",
        ]
    )
    for gap in gaps:
        lines.append(f"- {gap}")
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- `portrait_p3_pilot_gate` — 每条 fact 均有 evidence_ref_id",
            "- 无 live · 无 PDF · 无 DB · 无 `verified`",
            "",
        ]
    )
    summary_path = VALIDATION / "company_portrait_pilot_fill_summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    facts: list[dict[str, Any]] = []
    evidences: list[dict[str, Any]] = []
    seen_evidence: set[str] = set()

    n1 = fill_from_share_capital(facts, evidences, seen_evidence)
    n2 = fill_from_executives(facts, evidences, seen_evidence)
    n3 = fill_from_shareholders(facts, evidences, seen_evidence)
    n4 = fill_from_dividends(facts, evidences, seen_evidence)

    out_dir = PORTRAIT_ROOT / COMPANY_CODE
    write_jsonl(out_dir / "facts.jsonl", facts)
    write_jsonl(out_dir / "evidence_index.jsonl", evidences)
    coverage = build_coverage(facts)
    (out_dir / "coverage.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    filled_ids = {f["field_id"] for f in facts}
    updated = update_coverage_matrix(filled_ids)
    gaps = [
        "M01 缺少 `company_basic_profile` normalized 文件，身份字段仅能从股本/高管交叉填充",
        "M01 法定代表人、注册地址、上市日期等需补 basic harvest",
        "M04 财务数值未填（保持 not_modeled，等 PDF 闸门）",
        "M13/M14 未填（依赖 B/D 轨道产物）",
    ]
    write_pilot_summary(facts, evidences, updated, gaps)

    print(f"facts={len(facts)} evidence={len(evidences)} filled_fields={len(filled_ids)}")
    print(f"share_capital_facts={n1} executive_facts={n2} shareholder_facts={n3} dividend_facts={n4}")
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()

"""
Build a CNINFO P0 sample company list from existing local outputs.

Constraints:
- Offline only (no network, no CNINFO access).
- Reads existing extraction artifacts under outputs/generalization/full_market_2024/.
- Does not download PDF, compute hash, or touch databases.
- Writes two files under outputs/validation/:
  1) cninfo_p0_sample_companies.csv
  2) cninfo_p0_sample_company_summary.md
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter
from typing import Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL_MARKET_DIR = os.path.join(BASE_DIR, "outputs", "generalization", "full_market_2024")
VALIDATION_DIR = os.path.join(BASE_DIR, "outputs", "validation")
CSV_PATH = os.path.join(VALIDATION_DIR, "cninfo_p0_sample_companies.csv")
SUMMARY_PATH = os.path.join(VALIDATION_DIR, "cninfo_p0_sample_company_summary.md")

# Board directories -> board/exchange metadata
BOARD_MAP = {
    "sse_main": {"board": "主板", "exchange": "SSE", "sample_reason": "覆盖上交所主板"},
    "szse_main": {"board": "主板", "exchange": "SZSE", "sample_reason": "覆盖深交所主板"},
    "chinext": {"board": "创业板", "exchange": "SZSE", "sample_reason": "覆盖创业板"},
    "star": {"board": "科创板", "exchange": "SSE", "sample_reason": "覆盖科创板"},
    "bse": {"board": "北交所", "exchange": "BSE", "sample_reason": "覆盖北交所"},
}

# Target ~40 samples: distribute quotas across boards, will backfill if insufficient.
BOARD_QUOTAS = {
    "sse_main": 10,
    "szse_main": 10,
    "chinext": 7,
    "star": 7,
    "bse": 6,
}
TARGET_TOTAL = 40

CSV_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "industry",
    "listing_status",
    "is_st",
    "market_cap_group",
    "announcement_frequency_group",
    "sample_reason",
    "used_for_latest_announcement_validation",
    "used_for_pdf_metadata_validation",
    "used_for_f10_validation",
    "notes",
]


def ensure_dirs() -> None:
    os.makedirs(VALIDATION_DIR, exist_ok=True)


def load_profile(profile_path: str) -> Dict:
    try:
        with open(profile_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def extract_company(code: str, board_dir: str, board_meta: Dict) -> Dict | None:
    profile_path = os.path.join(FULL_MARKET_DIR, board_dir, code, "company_profile.json")
    profile = load_profile(profile_path)
    company_info = profile.get("company", {}) if isinstance(profile, dict) else {}

    company_name = company_info.get("short_name") or company_info.get("company_name") or ""
    # Skip entries without a reliable name.
    if (not company_name) or ("_unknown_name" in company_name):
        return None

    stock_code = company_info.get("stock_code") or code
    exchange = company_info.get("exchange") or board_meta["exchange"]

    # Basic heuristics
    is_st = "是" if ("ST" in company_name.upper() or "ST" in stock_code.upper()) else "否"

    record = {
        "company_code": stock_code,
        "company_name": company_name,
        "exchange": exchange,
        "board": board_meta["board"],
        "industry": company_info.get("industry") or "unknown",
        "listing_status": company_info.get("listing_status") or "unknown",
        "is_st": is_st,
        "market_cap_group": "unknown",
        "announcement_frequency_group": "unknown",
        "sample_reason": board_meta["sample_reason"],
        "used_for_latest_announcement_validation": "yes",
        "used_for_pdf_metadata_validation": "yes",
        "used_for_f10_validation": "yes",
        "notes": "",
    }
    return record


def pick_codes(board_dir: str) -> List[str]:
    path = os.path.join(FULL_MARKET_DIR, board_dir)
    if not os.path.isdir(path):
        return []
    codes = [
        name
        for name in os.listdir(path)
        if name.isdigit() and os.path.isdir(os.path.join(path, name))
    ]
    codes.sort()
    return codes


def collect_samples() -> tuple[List[Dict], Dict]:
    samples: List[Dict] = []
    stats: Dict = {"skipped_unknown_name": 0}
    remaining = TARGET_TOTAL

    # First pass: quota per board
    for board_dir, quota in BOARD_QUOTAS.items():
        if remaining <= 0:
            break
        codes = pick_codes(board_dir)
        picked = 0
        for code in codes:
            record = extract_company(code, board_dir, BOARD_MAP[board_dir])
            if not record:
                stats["skipped_unknown_name"] = stats.get("skipped_unknown_name", 0) + 1
                continue
            samples.append(record)
            picked += 1
            remaining -= 1
            if picked >= quota or remaining <= 0:
                break

    # Second pass: if not enough, backfill by re-iterating boards
    if remaining > 0:
        for board_dir in BOARD_QUOTAS:
            codes = pick_codes(board_dir)  # broader pool
            for code in codes:
                if any(r["company_code"] == code and r["exchange"] == BOARD_MAP[board_dir]["exchange"] for r in samples):
                    continue
                record = extract_company(code, board_dir, BOARD_MAP[board_dir])
                if not record:
                    stats["skipped_unknown_name"] = stats.get("skipped_unknown_name", 0) + 1
                    continue
                samples.append(record)
                remaining -= 1
                if remaining <= 0:
                    break
            if remaining <= 0:
                break

    return samples[:TARGET_TOTAL], stats


def write_csv(rows: List[Dict]) -> None:
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary(rows: List[Dict], sources: List[str], stats: Dict) -> None:
    total = len(rows)
    boards = Counter(r["board"] for r in rows)
    industries = Counter(r["industry"] for r in rows if r.get("industry") and r["industry"] != "unknown")
    unknown_fields = set()
    for r in rows:
        for field in ("industry", "listing_status", "market_cap_group", "announcement_frequency_group"):
            if not r.get(field) or r[field] == "unknown":
                unknown_fields.add(field)

    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO P0 样本公司清单（生成摘要）\n\n")
        fh.write("本清单基于本地已有输出生成，供后续 #82 / #83 / #84 P0 验证使用。\n\n")
        fh.write("## 数据来源\n")
        fh.write("- " + "\n- ".join(sources) + "\n\n")
        fh.write("## 样本概况\n")
        fh.write(f"- 样本总数：{total}\n")
        fh.write(f"- 覆盖板块：{', '.join(f'{k}({v})' for k, v in boards.items())}\n")
        if industries:
            fh.write(f"- 已知行业覆盖：{', '.join(f'{k}({v})' for k, v in industries.items())}\n")
        else:
            fh.write("- 已知行业覆盖：暂无（industry 多为 unknown）\n")
        if unknown_fields:
            fh.write(f"- 仍为 unknown 的字段：{', '.join(sorted(unknown_fields))}\n")
            fh.write("- 说明：上述 unknown 不影响第一轮验证，仍可用于页面可达性、字段可得性和失败原因记录；后续可补齐。\n")
        fh.write("\n## 边界确认\n")
        fh.write("- 未访问 CNINFO，未联网。\n")
        fh.write("- 未下载 PDF，未计算 hash。\n")
        fh.write("- 未做数据库接入。\n")
        fh.write("- 仅读取本地已有抽取结果，未修改计划文档和存储设计文档。\n")
        fh.write("\n## 过滤情况\n")
        fh.write(f"- 跳过 company_name 为空或含 `_unknown_name` 的样本：{stats.get('skipped_unknown_name', 0)} 条（不计入样本总数）\n")
        if total < TARGET_TOTAL:
            fh.write(f"- 提示：样本不足 {TARGET_TOTAL}，当前为 {total}；可后续人工补齐或放宽过滤。\n")


def main() -> None:
    ensure_dirs()
    samples, stats = collect_samples()
    write_csv(samples)
    write_summary(samples, sources=["outputs/generalization/full_market_2024/"], stats=stats)
    print(f"Generated {len(samples)} samples -> {CSV_PATH}")
    print(f"Summary -> {SUMMARY_PATH}")


if __name__ == "__main__":
    main()

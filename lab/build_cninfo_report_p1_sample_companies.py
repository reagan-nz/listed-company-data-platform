"""
构建 CNINFO A 类报告 P1 扩展样本公司清单（离线）。

从本地全市场公司列表按 exchange/board 分层抽样，目标 200 家（每层 40）。
不联网、不补 orgId、不伪造 cninfo_org_id。

用法：
    python lab/build_cninfo_report_p1_sample_companies.py
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML required: pip install pyyaml") from exc

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")

FULL_MARKET_YAML = os.path.join(BASE_DIR, "lab", "eval_companies_full_market_2024.yaml")
P0_SAMPLE_CSV = os.path.join(OUT_DIR, "cninfo_p0_sample_companies.csv")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_report_p1_sample_companies.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_report_p1_sample_companies_summary.md")

TARGET_PER_LAYER = 40

# sample_layer → (exchange, board 中文)
LAYER_META: Dict[str, Tuple[str, str]] = {
    "sse_main": ("SSE", "主板"),
    "szse_main": ("SZSE", "主板"),
    "chinext": ("SZSE", "创业板"),
    "star": ("SSE", "科创板"),
    "bse": ("BSE", "北交所"),
}

CSV_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "sample_layer",
    "sample_reason",
    "source_file",
    "is_p0_overlap",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_code(code: str) -> str:
    return str(code or "").strip().zfill(6) if str(code or "").strip().isdigit() else str(code or "").strip()


def infer_layer_from_code(code: str) -> Optional[str]:
    c = normalize_code(code)
    if not c.isdigit():
        if c.startswith("920"):
            return "bse"
        return None
    if c.startswith(("600", "601", "603", "605")):
        return "sse_main"
    if c.startswith(("000", "001", "002", "003")):
        return "szse_main"
    if c.startswith("300"):
        return "chinext"
    if c.startswith("688"):
        return "star"
    if c.startswith(("430", "83", "87")) or c.startswith("920"):
        return "bse"
    return None


def is_excluded_name(short_name: str) -> bool:
    name = (short_name or "").strip()
    if not name:
        return False
    upper = name.upper()
    if "退" in name:
        return True
    if upper.startswith("*ST") or upper.startswith("ST") or "ST" in upper:
        return True
    return False


def load_p0_codes() -> set[str]:
    if not os.path.isfile(P0_SAMPLE_CSV):
        return set()
    codes: set[str] = set()
    with open(P0_SAMPLE_CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = normalize_code(row.get("company_code", ""))
            if code:
                codes.add(code)
    return codes


def load_full_market() -> List[Dict]:
    with open(FULL_MARKET_YAML, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return list(data.get("companies") or [])


def evenly_sample(candidates: List[Dict], n: int) -> List[Dict]:
    if len(candidates) <= n:
        return list(candidates)
    step = len(candidates) / n
    picked: List[Dict] = []
    seen: set[str] = set()
    for i in range(n):
        idx = min(int(i * step), len(candidates) - 1)
        code = normalize_code(candidates[idx].get("stock_code", ""))
        if code in seen:
            continue
        seen.add(code)
        picked.append(candidates[idx])
    # backfill if duplicates collapsed picks
    if len(picked) < n:
        for c in candidates:
            code = normalize_code(c.get("stock_code", ""))
            if code in seen:
                continue
            seen.add(code)
            picked.append(c)
            if len(picked) >= n:
                break
    return picked[:n]


def build_layer_pools(companies: List[Dict]) -> Dict[str, List[Dict]]:
    pools: Dict[str, List[Dict]] = {k: [] for k in LAYER_META}
    for c in companies:
        board = (c.get("board") or "").strip()
        if board not in LAYER_META:
            continue
        if is_excluded_name(c.get("short_name") or ""):
            continue
        code = normalize_code(c.get("stock_code", ""))
        inferred = infer_layer_from_code(code)
        if inferred and inferred != board:
            continue
        pools[board].append(c)
    for layer in pools:
        pools[layer].sort(key=lambda x: normalize_code(x.get("stock_code", "")))
    return pools


def row_from_company(company: Dict, layer: str, p0_codes: set[str]) -> Dict:
    exchange, board_cn = LAYER_META[layer]
    code = normalize_code(company.get("stock_code", ""))
    return {
        "company_code": code,
        "company_name": (company.get("short_name") or "").strip(),
        "exchange": exchange,
        "board": board_cn,
        "sample_layer": layer,
        "sample_reason": f"P1 stratified sample; layer={layer}; evenly spaced by stock_code",
        "source_file": os.path.relpath(FULL_MARKET_YAML, BASE_DIR),
        "is_p0_overlap": "yes" if code in p0_codes else "no",
    }


def write_csv(rows: List[Dict]) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_summary(
    rows: List[Dict],
    pools: Dict[str, List[Dict]],
    layer_picked: Dict[str, int],
    p0_codes: set[str],
) -> None:
    layer_counter = Counter(r["sample_layer"] for r in rows)
    exchange_counter = Counter(r["exchange"] for r in rows)
    board_counter = Counter(r["board"] for r in rows)
    p0_overlap = sum(1 for r in rows if r.get("is_p0_overlap") == "yes")

    lines = [
        "# CNINFO A 类报告 P1 扩展样本摘要",
        "",
        f"- 生成时间：{now_iso()}",
        f"- 脚本：`lab/build_cninfo_report_p1_sample_companies.py`",
        f"- 计划文档：[cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md)",
        "",
        "## 1. 输入来源",
        "",
        f"- 主列表：`{os.path.relpath(FULL_MARKET_YAML, BASE_DIR)}`",
        f"- P0 对照：`{os.path.relpath(P0_SAMPLE_CSV, BASE_DIR)}`（{len(p0_codes)} 家）",
        "",
        "## 2. 抽样规则",
        "",
        "- 按 `board` 字段分 5 层，每层目标 40 家，层内按 `stock_code` 排序后等距抽取",
        "- 排除简称含 ST / *ST / 退 的公司",
        "- 代码段推断与 YAML `board` 不一致的条目跳过",
        "- **不联网；不写入 orgId**",
        "",
        "## 3. 样本规模",
        "",
        f"- **总样本数：{len(rows)}**（目标 200 = 5 × 40）",
        f"- 与 P0 重叠：**{p0_overlap}** 家（`is_p0_overlap=yes`）",
        "",
        "## 4. 各层样本数",
        "",
        "| sample_layer | exchange | board | 目标 | 已抽 | 池内可用 | 是否足额 |",
        "|--------------|----------|-------|------|------|----------|----------|",
    ]
    for layer, (ex, bd) in LAYER_META.items():
        target = TARGET_PER_LAYER
        picked = layer_counter.get(layer, 0)
        available = len(pools.get(layer, []))
        ok = "是" if picked >= target else f"否（仅 {picked}/{target}）"
        lines.append(f"| {layer} | {ex} | {bd} | {target} | {picked} | {available} | {ok} |")

    lines.extend(
        [
            "",
            "## 5. 按 exchange / board",
            "",
            "### exchange",
            "",
        ]
    )
    for ex, cnt in sorted(exchange_counter.items()):
        lines.append(f"- {ex}：{cnt}")
    lines.extend(["", "### board", ""])
    for bd, cnt in sorted(board_counter.items()):
        lines.append(f"- {bd}：{cnt}")

    short_layers = [layer for layer in LAYER_META if layer_counter.get(layer, 0) < TARGET_PER_LAYER]
    lines.extend(["", "## 6. 不足层说明", ""])
    if short_layers:
        for layer in short_layers:
            lines.append(f"- `{layer}`：仅抽到 {layer_counter.get(layer, 0)}/{TARGET_PER_LAYER}")
    else:
        lines.append("- 五层均达到目标 40 家。")

    lines.extend(
        [
            "",
            "## 7. 后续步骤",
            "",
            "1. **扩展 identity mapping**：为 P1 200 家生成 `cninfo_report_p1_identity_mapping.csv`",
            "   - 可参考 YAML 中已有 `orgid`（不伪造；无 orgId 标 `needs_orgid_mapping`）",
            "   - 创业板注意：F10 `gssh*` 对公告查询可能无效，需 numeric orgId（见 P0 诊断）",
            "2. **运行 P1 coverage**（本地、合规网络）：",
            "   ```bash",
            "   python lab/validate_cninfo_report_coverage.py \\",
            "     --input-mapping outputs/validation/cninfo_report_p1_identity_mapping.csv \\",
            "     --output-prefix outputs/validation/cninfo_report_p1_coverage \\",
            "     --sample-csv outputs/validation/cninfo_report_p1_sample_companies.csv",
            "   ```",
            "3. 对比 P0 baseline（113/120 = 94.17%），评估跨板块稳定性",
            "",
            "## 8. 边界",
            "",
            "- 未下载/解析 PDF；未接数据库；未写 verified",
            "- 本 CSV **不是** coverage 分母文件；coverage 以 mapping CSV 中 `mapped` 公司为准",
            "",
        ]
    )

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    companies = load_full_market()
    p0_codes = load_p0_codes()
    pools = build_layer_pools(companies)

    rows: List[Dict] = []
    layer_picked: Dict[str, int] = {}
    for layer in LAYER_META:
        picked = evenly_sample(pools[layer], TARGET_PER_LAYER)
        layer_picked[layer] = len(picked)
        for c in picked:
            rows.append(row_from_company(c, layer, p0_codes))

    rows.sort(key=lambda r: (r["sample_layer"], r["company_code"]))
    write_csv(rows)
    write_summary(rows, pools, layer_picked, p0_codes)
    print(f"Wrote {len(rows)} companies -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    main()

"""
A-class basic_profile 覆盖扩展（纯离线 · CNINFO = 0）。

用途：
1. 扫描 C-class 侧已落盘但未并入 canonical normalized 的 latent profiles
2. 在 A 轨独立 overlay 目录建立 symlink 并集（不 mutate C harvest 根）
3. 输出覆盖矩阵，供 listing-aware 下一片 cohort 扩大分母

禁止：CNINFO live、伪造 listing_date、写入 C-class harvest 根、
      mutate 封闭 S1–S6 live 权威报告。
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import cninfo_a_class_listing_period_gate as listing_period_gate

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)

DEFAULT_CANON_PROFILE_DIR = listing_period_gate.DEFAULT_PROFILE_DIR

# 只读扫描：侧批 normalized profiles（不得写入这些目录）
DEFAULT_LATENT_PROFILE_DIRS: Tuple[str, ...] = (
    os.path.join(
        _BASE_DIR,
        "outputs",
        "harvest",
        "cninfo_c_class",
        "phase35_batch_500_001",
        "normalized",
        "company_basic_profile",
    ),
    os.path.join(
        _BASE_DIR,
        "outputs",
        "harvest",
        "cninfo_c_class",
        "phase35_batch_500_001_resume",
        "normalized",
        "company_basic_profile",
    ),
    os.path.join(
        _BASE_DIR,
        "outputs",
        "harvest",
        "cninfo_c_class",
        "phase2_smoke_200",
        "normalized",
        "company_basic_profile",
    ),
    os.path.join(
        _BASE_DIR,
        "outputs",
        "harvest",
        "cninfo_c_class",
        "fuller_market_slice1_200",
        "normalized",
        "company_basic_profile",
    ),
    os.path.join(
        _BASE_DIR,
        "outputs",
        "harvest",
        "cninfo_c_class",
        "phase3_batch_500_001",
        "normalized",
        "company_basic_profile",
    ),
)

DEFAULT_OVERLAY_DIR = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

DEFAULT_COVERAGE_MATRIX_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_matrix_fm06_20260715.csv",
)

DEFAULT_COVERAGE_SUMMARY_MD = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_fm06_20260715.md",
)

MATRIX_COLUMNS = [
    "company_code",
    "in_canon",
    "in_latent",
    "overlay_source",
    "source_path",
    "has_listing_date",
    "prefix3",
]


@dataclass(frozen=True)
class ProfileSourceHit:
    """单码 profile 来源。"""

    company_code: str
    path: str
    origin: str  # canon | latent


@dataclass(frozen=True)
class CoverageBuildResult:
    """覆盖构建结果。"""

    overlay_dir: str
    canon_count: int
    latent_only_count: int
    union_count: int
    symlink_count: int
    matrix_rows: int
    cninfo_calls: int = 0


def normalize_code(code: str) -> str:
    """规范化证券代码。"""
    return listing_period_gate.normalize_code(code)


def code_prefix3(company_code: str) -> str:
    """三位码前缀（用于浓度/多样性统计）。"""
    code = normalize_code(company_code)
    return code[:3] if len(code) >= 3 else code


def _profile_has_listing_date(path: str) -> bool:
    """读取 profile 是否含可用上市日（不伪造）。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    ld, _src = listing_period_gate._extract_listing_date_from_profile(data)
    return ld is not None


def discover_profile_path_map(
    *,
    canon_dir: str = DEFAULT_CANON_PROFILE_DIR,
    latent_dirs: Sequence[str] = DEFAULT_LATENT_PROFILE_DIRS,
) -> Dict[str, ProfileSourceHit]:
    """
    发现 code→profile 路径并集。

    canonical 优先；latent 仅补充 canon 缺失码。不写入任何源目录。
    """
    path_map: Dict[str, ProfileSourceHit] = {}
    if os.path.isdir(canon_dir):
        for name in sorted(os.listdir(canon_dir)):
            if not name.endswith(".json"):
                continue
            code = normalize_code(name[: -len(".json")])
            if not code:
                continue
            path_map[code] = ProfileSourceHit(
                company_code=code,
                path=os.path.abspath(os.path.join(canon_dir, name)),
                origin="canon",
            )
    for latent_dir in latent_dirs:
        if not os.path.isdir(latent_dir):
            continue
        for name in sorted(os.listdir(latent_dir)):
            if not name.endswith(".json"):
                continue
            code = normalize_code(name[: -len(".json")])
            if not code or code in path_map:
                continue
            path_map[code] = ProfileSourceHit(
                company_code=code,
                path=os.path.abspath(os.path.join(latent_dir, name)),
                origin="latent",
            )
    return path_map


def build_profile_overlay(
    *,
    overlay_dir: str = DEFAULT_OVERLAY_DIR,
    canon_dir: str = DEFAULT_CANON_PROFILE_DIR,
    latent_dirs: Sequence[str] = DEFAULT_LATENT_PROFILE_DIRS,
    refresh: bool = True,
) -> CoverageBuildResult:
    """
    在 A 轨 overlay 目录重建 symlink 并集。

    refresh=True 时清空 overlay 内既有 .json 链接/文件后重建。
    """
    path_map = discover_profile_path_map(canon_dir=canon_dir, latent_dirs=latent_dirs)
    os.makedirs(overlay_dir, exist_ok=True)
    if refresh:
        for name in os.listdir(overlay_dir):
            if not name.endswith(".json"):
                continue
            target = os.path.join(overlay_dir, name)
            if os.path.islink(target) or os.path.isfile(target):
                os.unlink(target)

    symlink_count = 0
    for code, hit in sorted(path_map.items()):
        link_path = os.path.join(overlay_dir, f"{code}.json")
        if os.path.lexists(link_path):
            os.unlink(link_path)
        os.symlink(hit.path, link_path)
        symlink_count += 1

    canon_count = sum(1 for h in path_map.values() if h.origin == "canon")
    latent_only = sum(1 for h in path_map.values() if h.origin == "latent")
    return CoverageBuildResult(
        overlay_dir=os.path.abspath(overlay_dir),
        canon_count=canon_count,
        latent_only_count=latent_only,
        union_count=len(path_map),
        symlink_count=symlink_count,
        matrix_rows=0,
        cninfo_calls=0,
    )


def write_coverage_matrix(
    path_map: Dict[str, ProfileSourceHit],
    *,
    matrix_csv: str = DEFAULT_COVERAGE_MATRIX_CSV,
) -> str:
    """写入覆盖矩阵 CSV。"""
    os.makedirs(os.path.dirname(matrix_csv) or ".", exist_ok=True)
    with open(matrix_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MATRIX_COLUMNS)
        writer.writeheader()
        for code, hit in sorted(path_map.items()):
            writer.writerow(
                {
                    "company_code": code,
                    "in_canon": "yes" if hit.origin == "canon" else "no",
                    "in_latent": "yes" if hit.origin == "latent" else "no",
                    "overlay_source": hit.origin,
                    "source_path": hit.path,
                    "has_listing_date": "yes" if _profile_has_listing_date(hit.path) else "no",
                    "prefix3": code_prefix3(code),
                }
            )
    return matrix_csv


def write_coverage_summary(
    result: CoverageBuildResult,
    path_map: Dict[str, ProfileSourceHit],
    *,
    summary_md: str = DEFAULT_COVERAGE_SUMMARY_MD,
    matrix_csv: str = DEFAULT_COVERAGE_MATRIX_CSV,
) -> str:
    """写入覆盖摘要 Markdown。"""
    prefix_all = Counter(code_prefix3(c) for c in path_map)
    prefix_latent = Counter(
        code_prefix3(c) for c, h in path_map.items() if h.origin == "latent"
    )
    with_ld = sum(1 for h in path_map.values() if _profile_has_listing_date(h.path))
    lines = [
        "# A-FM-06 — basic_profile 覆盖扩展（offline）",
        "",
        "_track A · CNINFO = 0 · 不 mutate C harvest / S1–S6 live_",
        "",
        "## Metrics",
        "",
        f"| 项 | 值 |",
        f"|----|-----|",
        f"| canon profiles | **{result.canon_count}** |",
        f"| latent-only added | **{result.latent_only_count}** |",
        f"| union (overlay) | **{result.union_count}** |",
        f"| overlay symlinks | **{result.symlink_count}** |",
        f"| union with listing_date | **{with_ld}** |",
        f"| CNINFO calls | **{result.cninfo_calls}** |",
        f"| overlay_dir | `{result.overlay_dir}` |",
        f"| matrix_csv | `{matrix_csv}` |",
        "",
        "## Prefix (union top 12)",
        "",
        "```text",
    ]
    for pref, n in prefix_all.most_common(12):
        lines.append(f"{pref}\t{n}")
    lines.extend(
        [
            "```",
            "",
            "## Prefix (latent-only top 12)",
            "",
            "```text",
        ]
    )
    for pref, n in prefix_latent.most_common(12):
        lines.append(f"{pref}\t{n}")
    lines.extend(
        [
            "```",
            "",
            "## Notes",
            "",
            "- overlay 仅为 A 轨 symlink 视图；C-class harvest 根未改写。",
            "- 扩大分母后，listing-aware 下一片应配合 prefix_concentration 门禁，",
            "  避免再现 S6 首轮 mono-301 批处理 network_timeout 窗。",
            "- S6 首轮 18×timeout 经独立 retry 可恢复，**不**作为永久点名黑名单。",
            "",
        ]
    )
    os.makedirs(os.path.dirname(summary_md) or ".", exist_ok=True)
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_md


def build_coverage_artifacts(
    *,
    overlay_dir: str = DEFAULT_OVERLAY_DIR,
    matrix_csv: str = DEFAULT_COVERAGE_MATRIX_CSV,
    summary_md: str = DEFAULT_COVERAGE_SUMMARY_MD,
    canon_dir: str = DEFAULT_CANON_PROFILE_DIR,
    latent_dirs: Sequence[str] = DEFAULT_LATENT_PROFILE_DIRS,
) -> CoverageBuildResult:
    """构建 overlay + 矩阵 + 摘要。"""
    path_map = discover_profile_path_map(canon_dir=canon_dir, latent_dirs=latent_dirs)
    result = build_profile_overlay(
        overlay_dir=overlay_dir,
        canon_dir=canon_dir,
        latent_dirs=latent_dirs,
        refresh=True,
    )
    write_coverage_matrix(path_map, matrix_csv=matrix_csv)
    result = CoverageBuildResult(
        overlay_dir=result.overlay_dir,
        canon_count=result.canon_count,
        latent_only_count=result.latent_only_count,
        union_count=result.union_count,
        symlink_count=result.symlink_count,
        matrix_rows=len(path_map),
        cninfo_calls=0,
    )
    write_coverage_summary(
        result, path_map, summary_md=summary_md, matrix_csv=matrix_csv
    )
    return result


def main(argv: Optional[Iterable[str]] = None) -> int:
    """CLI：构建 A 轨 profile coverage overlay（CNINFO=0）。"""
    import argparse

    parser = argparse.ArgumentParser(
        description="A-class basic_profile coverage overlay（CNINFO=0）"
    )
    parser.add_argument("--overlay-dir", default=DEFAULT_OVERLAY_DIR)
    parser.add_argument("--matrix-csv", default=DEFAULT_COVERAGE_MATRIX_CSV)
    parser.add_argument("--summary-md", default=DEFAULT_COVERAGE_SUMMARY_MD)
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = build_coverage_artifacts(
        overlay_dir=args.overlay_dir,
        matrix_csv=args.matrix_csv,
        summary_md=args.summary_md,
    )
    print(
        f"a_class_profile_coverage_built union={result.union_count} "
        f"canon={result.canon_count} latent_only={result.latent_only_count} "
        f"overlay={result.overlay_dir} cninfo_calls={result.cninfo_calls}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

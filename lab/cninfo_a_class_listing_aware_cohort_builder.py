"""
A-class listing-aware next cohort 构建器（纯离线 · CNINFO = 0）。

用途：在 S1（AD2E501–600）封闭后，从具备 C-class basic_profile 的全市场码中
按 listing_period_gate 硬拒规则生成下一片 AD2E601+ universe。

选取规则（本构建器冻结）：
1. 源：company_basic_profile ∩ full_market_2024 名称/交易所
2. 排除 A cumulative：scale-200 ∪ slice1 ∪ slice2 S1
   （S3 另含 listing-aware S2；S4 另含 S2+S3；S5 另含 S2+S3+S4；
    S6 另含 S2+S3+S4+S5）
3. ST-EXCLUDE（名称命中 *ST / S*ST）
4. 非 BSE（4/8/92 前缀）
5. 按 company_code 升序；为候选分配 case_id 与 report_type/expected_period 后
   再跑 listing_period_gate；不通过则跳过该码（不得静默改 period）
6. B 轨 overlap：**允许**（全市场 A 周期报告元数据 vs B 披露事件，跨轨不同维度）

切片：
- S2：AD2E601–650（`--slice s2`）
- S3：AD2E651–700（`--slice s3`）
- S4：AD2E701–750（`--slice s4`）
- S5：AD2E751–800（`--slice s5`）
- S6：AD2E801–850（默认 · `--slice s6`）

禁止：CNINFO live、伪造上市日、mutate 封闭 S1/S2/S3/S4/S5 live 根、静默改写 expected_period。
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import yaml

import cninfo_a_class_listing_period_gate as listing_period_gate

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)

DEFAULT_FULL_MARKET_YAML = os.path.join(_LAB_DIR, "eval_companies_full_market_2024.yaml")
DEFAULT_PROFILE_DIR = listing_period_gate.DEFAULT_PROFILE_DIR

DEFAULT_A_EXCLUDE_UNIVERSE_CSVS: Tuple[str, ...] = (
    os.path.join(
        _BASE_DIR,
        "outputs",
        "validation",
        "cninfo_a_class_erad_scale_200_universe_draft.csv",
    ),
    os.path.join(
        _BASE_DIR,
        "outputs",
        "validation",
        "cninfo_a_class_erad_next_scale_candidate_universe_draft.csv",
    ),
    os.path.join(
        _BASE_DIR,
        "outputs",
        "validation",
        "cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv",
    ),
)

DEFAULT_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s2_plus50_universe_20260715.csv",
)
DEFAULT_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s2_reject_ledger_20260715.csv",
)

# A-FM-02：listing-aware S3（AD2E651–700）；A exclude 含 S2 +50
DEFAULT_A_EXCLUDE_S3_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_UNIVERSE_CSVS + (
    DEFAULT_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S3_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s3_plus50_universe_20260715.csv",
)
DEFAULT_S3_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s3_reject_ledger_20260715.csv",
)

# A-FM-03：listing-aware S4（AD2E701–750）；A exclude 含 S2 + S3
DEFAULT_A_EXCLUDE_S4_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S3_UNIVERSE_CSVS + (
    DEFAULT_S3_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S4_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s4_plus50_universe_20260715.csv",
)
DEFAULT_S4_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s4_reject_ledger_20260715.csv",
)

# A-FM-04：listing-aware S5（AD2E751–800）；A exclude 含 S2 + S3 + S4
DEFAULT_A_EXCLUDE_S5_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S4_UNIVERSE_CSVS + (
    DEFAULT_S4_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S5_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s5_plus50_universe_20260715.csv",
)
DEFAULT_S5_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s5_reject_ledger_20260715.csv",
)

# A-FM-05：listing-aware S6（AD2E801–850）；A exclude 含 S2 + S3 + S4 + S5
DEFAULT_A_EXCLUDE_S6_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S5_UNIVERSE_CSVS + (
    DEFAULT_S5_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S6_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s6_plus50_universe_20260715.csv",
)
DEFAULT_S6_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s6_reject_ledger_20260715.csv",
)

COHORT_LABEL = "next_scale_listing_aware"
CASE_ID_START = 601
CASE_ID_START_S3 = 651
CASE_ID_START_S4 = 701
CASE_ID_START_S5 = 751
CASE_ID_START_S6 = 801
DEFAULT_TARGET_SIZE = 50
ST_NAME_PATTERN = re.compile(r"(?:\*?ST|S\*ST)")
UNIVERSE_COLUMNS = ["company_code", "company_name", "case_id", "cohort"]
REJECT_COLUMNS = [
    "company_code",
    "company_name",
    "reject_stage",
    "failure_class",
    "listing_date",
    "expected_period_attempted",
    "notes",
]


@dataclass(frozen=True)
class CohortRow:
    """单条选中 universe 行。"""

    company_code: str
    company_name: str
    case_id: str
    cohort: str
    report_type: str
    expected_period: str
    listing_date: str


@dataclass(frozen=True)
class RejectRow:
    """单条拒绝台账行。"""

    company_code: str
    company_name: str
    reject_stage: str
    failure_class: str
    listing_date: str
    expected_period_attempted: str
    notes: str


@dataclass(frozen=True)
class BuildResult:
    """构建结果。"""

    selected: List[CohortRow]
    rejected: List[RejectRow]
    a_exclude_count: int
    profile_candidate_count: int
    cninfo_calls: int = 0


def normalize_code(code: str) -> str:
    """规范化证券代码。"""
    return listing_period_gate.normalize_code(code)


def is_bse_code(company_code: str) -> bool:
    """北交所码段判定（4/8/92 前缀）。"""
    code = normalize_code(company_code)
    return code.startswith(("4", "8")) or code.startswith("92")


def is_st_name(company_name: str) -> bool:
    """ST 名称命中。"""
    return bool(ST_NAME_PATTERN.search(company_name or ""))


def derive_report_fields_for_case_num(case_num: int) -> Tuple[str, str, str, str]:
    """
    与 slice2 S1 相同的 mod-10 报告期混合（以 case_num 相对 501 的偏移）。

    AD2E601 → idx=100 → slot=0 → annual_report / 2024-12-31。
    """
    idx = case_num - 501
    slot = idx % 10
    if slot < 7:
        return (
            "annual_report",
            "2024-12-31",
            "年度报告",
            "半年度报告|一季度报告|三季度报告|英文|English",
        )
    if slot == 7:
        return (
            "semi_annual_report",
            "2024-06-30",
            "半年度报告",
            "年度报告|一季度报告|三季度报告|英文|English",
        )
    if slot == 8:
        return (
            "quarterly_report_q1",
            "2024-03-31",
            "一季度报告",
            "年度报告|半年度报告|三季度报告|英文|English",
        )
    return (
        "quarterly_report_q3",
        "2024-09-30",
        "三季度报告",
        "年度报告|半年度报告|一季度报告|英文|English",
    )


def load_company_codes_from_csv(path: str, column: str = "company_code") -> Set[str]:
    """从 CSV 读取公司代码集合。"""
    codes: Set[str] = set()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = normalize_code(row.get(column, ""))
            if code:
                codes.add(code)
    return codes


def load_a_exclude_codes(
    universe_csvs: Sequence[str] = DEFAULT_A_EXCLUDE_UNIVERSE_CSVS,
) -> Set[str]:
    """加载 A cumulative 已占用码（同轨禁止重跑）。"""
    excluded: Set[str] = set()
    for path in universe_csvs:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"a_exclude_universe_missing:{path}")
        excluded |= load_company_codes_from_csv(path)
    return excluded


def load_full_market_name_map(
    yaml_path: str = DEFAULT_FULL_MARKET_YAML,
) -> Dict[str, str]:
    """从 full_market_2024 YAML 加载 code→short_name。"""
    with open(yaml_path, "r", encoding="utf-8") as f:
        payload = yaml.safe_load(f)
    companies = payload.get("companies") if isinstance(payload, dict) else None
    if not isinstance(companies, list):
        raise ValueError("full_market_yaml_companies_missing")
    names: Dict[str, str] = {}
    for item in companies:
        if not isinstance(item, dict):
            continue
        code = normalize_code(str(item.get("stock_code", "")))
        if not code:
            continue
        names[code] = str(item.get("short_name") or "").strip()
    return names


def list_profile_codes(profile_dir: str = DEFAULT_PROFILE_DIR) -> List[str]:
    """列出 basic_profile 目录下全部证券代码（有序）。"""
    if not os.path.isdir(profile_dir):
        raise FileNotFoundError(f"profile_dir_missing:{profile_dir}")
    codes = [
        normalize_code(name[: -len(".json")])
        for name in os.listdir(profile_dir)
        if name.endswith(".json")
    ]
    return sorted({c for c in codes if c})


def build_listing_aware_cohort(
    *,
    target_size: int = DEFAULT_TARGET_SIZE,
    case_id_start: int = CASE_ID_START,
    a_exclude_csvs: Sequence[str] = DEFAULT_A_EXCLUDE_UNIVERSE_CSVS,
    profile_dir: str = DEFAULT_PROFILE_DIR,
    full_market_yaml: str = DEFAULT_FULL_MARKET_YAML,
    cohort: str = COHORT_LABEL,
) -> BuildResult:
    """
    构建 listing-aware 下一片 cohort。

    对每个候选：先按排序取码，再按即将占用的 case_num 派生 expected_period，
    再调用 listing_period_gate；拒绝则记台账并尝试下一码。
    """
    if target_size <= 0:
        raise ValueError("target_size_must_be_positive")
    if case_id_start < CASE_ID_START:
        raise ValueError(f"case_id_start_must_be_ge_{CASE_ID_START}")

    a_exclude = load_a_exclude_codes(a_exclude_csvs)
    names = load_full_market_name_map(full_market_yaml)
    profile_codes = list_profile_codes(profile_dir)

    selected: List[CohortRow] = []
    rejected: List[RejectRow] = []
    profile_candidates = 0

    for code in profile_codes:
        if len(selected) >= target_size:
            break
        name = names.get(code, "")
        if code in a_exclude:
            rejected.append(
                RejectRow(
                    company_code=code,
                    company_name=name,
                    reject_stage="a_cumulative_exclude",
                    failure_class="already_in_a_universe",
                    listing_date="",
                    expected_period_attempted="",
                    notes="同轨 A cumulative 已占用；禁止重跑",
                )
            )
            continue
        if not name:
            rejected.append(
                RejectRow(
                    company_code=code,
                    company_name="",
                    reject_stage="full_market_name_missing",
                    failure_class="name_missing",
                    listing_date="",
                    expected_period_attempted="",
                    notes="profile 存在但 full_market_2024 无 short_name；不编造名称",
                )
            )
            continue
        if is_st_name(name):
            rejected.append(
                RejectRow(
                    company_code=code,
                    company_name=name,
                    reject_stage="st_exclude",
                    failure_class="st_name_hit",
                    listing_date="",
                    expected_period_attempted="",
                    notes="S1 ST-EXCLUDE 策略延续",
                )
            )
            continue
        if is_bse_code(code):
            rejected.append(
                RejectRow(
                    company_code=code,
                    company_name=name,
                    reject_stage="bse_exclude",
                    failure_class="bse_code",
                    listing_date="",
                    expected_period_attempted="",
                    notes="非 BSE 策略",
                )
            )
            continue

        profile_candidates += 1
        case_num = case_id_start + len(selected)
        report_type, expected_period, _title_kw, _excl_kw = derive_report_fields_for_case_num(
            case_num
        )
        gate = listing_period_gate.assess_listing_vs_expected_period(
            code, expected_period, profile_dir=profile_dir
        )
        if listing_period_gate.is_listing_period_reject(gate):
            rejected.append(
                RejectRow(
                    company_code=code,
                    company_name=name,
                    reject_stage="listing_period_gate",
                    failure_class=gate.failure_class,
                    listing_date=gate.listing_date,
                    expected_period_attempted=expected_period,
                    notes=gate.notes or gate.root_cause,
                )
            )
            continue

        selected.append(
            CohortRow(
                company_code=code,
                company_name=name,
                case_id=f"AD2E{case_num:03d}",
                cohort=cohort,
                report_type=report_type,
                expected_period=expected_period,
                listing_date=gate.listing_date,
            )
        )

    if len(selected) < target_size:
        raise RuntimeError(
            f"listing_aware_cohort_undersized:got={len(selected)} expected={target_size} "
            f"profile_candidates={profile_candidates} a_exclude={len(a_exclude)}"
        )

    return BuildResult(
        selected=selected,
        rejected=rejected,
        a_exclude_count=len(a_exclude),
        profile_candidate_count=profile_candidates,
        cninfo_calls=0,
    )


def write_universe_csv(rows: Sequence[CohortRow], path: str) -> str:
    """写入 4 列 universe CSV（与 S1 冻结格式兼容）。"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=UNIVERSE_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "company_code": row.company_code,
                    "company_name": row.company_name,
                    "case_id": row.case_id,
                    "cohort": row.cohort,
                }
            )
    return path


def write_reject_ledger(rows: Sequence[RejectRow], path: str) -> str:
    """写入拒绝台账 CSV。"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REJECT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "company_code": row.company_code,
                    "company_name": row.company_name,
                    "reject_stage": row.reject_stage,
                    "failure_class": row.failure_class,
                    "listing_date": row.listing_date,
                    "expected_period_attempted": row.expected_period_attempted,
                    "notes": row.notes,
                }
            )
    return path


def build_and_write_default_plus50(
    *,
    universe_csv: str = DEFAULT_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
) -> BuildResult:
    """构建默认 +50 listing-aware S2 universe（AD2E601–650）并落盘。"""
    result = build_listing_aware_cohort(target_size=target_size)
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s3_plus50(
    *,
    universe_csv: str = DEFAULT_S3_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S3_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
) -> BuildResult:
    """构建 listing-aware S3 +50 universe（AD2E651–700 · 排除 S2）并落盘。"""
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S3,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S3_UNIVERSE_CSVS,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s4_plus50(
    *,
    universe_csv: str = DEFAULT_S4_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S4_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
) -> BuildResult:
    """构建 listing-aware S4 +50 universe（AD2E701–750 · 排除 S2+S3）并落盘。"""
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S4,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S4_UNIVERSE_CSVS,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s5_plus50(
    *,
    universe_csv: str = DEFAULT_S5_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S5_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
) -> BuildResult:
    """构建 listing-aware S5 +50 universe（AD2E751–800 · 排除 S2+S3+S4）并落盘。"""
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S5,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S5_UNIVERSE_CSVS,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s6_plus50(
    *,
    universe_csv: str = DEFAULT_S6_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S6_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
) -> BuildResult:
    """构建 listing-aware S6 +50 universe（AD2E801–850 · 排除 S2+S3+S4+S5）并落盘。"""
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S6,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S6_UNIVERSE_CSVS,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def main(argv: Optional[Iterable[str]] = None) -> int:
    """CLI：生成 listing-aware universe（offline · 默认 S6）。"""
    import argparse

    parser = argparse.ArgumentParser(description="listing-aware A cohort builder（CNINFO=0）")
    parser.add_argument(
        "--slice",
        choices=("s2", "s3", "s4", "s5", "s6"),
        default="s6",
        help="s2=AD2E601-650；s3=AD2E651-700；s4=AD2E701-750；s5=AD2E751-800；s6=AD2E801-850（默认）",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.slice == "s2":
        result = build_and_write_default_plus50()
        universe_path = DEFAULT_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s3":
        result = build_and_write_s3_plus50()
        universe_path = DEFAULT_S3_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s4":
        result = build_and_write_s4_plus50()
        universe_path = DEFAULT_S4_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s5":
        result = build_and_write_s5_plus50()
        universe_path = DEFAULT_S5_OUTPUT_UNIVERSE_CSV
    else:
        result = build_and_write_s6_plus50()
        universe_path = DEFAULT_S6_OUTPUT_UNIVERSE_CSV
    print(
        f"listing_aware_cohort_built slice={args.slice} size={len(result.selected)} "
        f"rejected={len(result.rejected)} a_exclude={result.a_exclude_count} "
        f"profile_candidates={result.profile_candidate_count} "
        f"cninfo_calls={result.cninfo_calls} "
        f"universe={universe_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

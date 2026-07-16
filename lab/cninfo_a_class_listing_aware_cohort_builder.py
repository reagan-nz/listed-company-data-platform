"""
A-class listing-aware next cohort 构建器（纯离线 · CNINFO = 0）。

用途：在 S1（AD2E501–600）封闭后，从具备 C-class basic_profile 的全市场码中
按 listing_period_gate 硬拒规则生成下一片 AD2E601+ universe。

选取规则（本构建器冻结）：
1. 源：company_basic_profile ∩ full_market_2024 名称/交易所
   （S7/S8/S9/S10/S11/S12/S13/S14/S15/S16/S17/S18/S19/S20/S21/S22 默认使用 A 轨 coverage overlay，合并 latent harvest profiles）
2. 排除 A cumulative：scale-200 ∪ slice1 ∪ slice2 S1
   （S3 另含 listing-aware S2；S4 另含 S2+S3；S5 另含 S2+S3+S4；
    S6 另含 S2+S3+S4+S5；S7 另含 S2–S6；S8 另含 S2–S7；S9 另含 S2–S8；S10 另含 S2–S9；
    S11 另含 S2–S10；S12 另含 S2–S11；S13 另含 S2–S12；S14 另含 S2–S13；S15 另含 S2–S14；
    S16 另含 S2–S15；S17 另含 S2–S16；S18 另含 S2–S17；S19 另含 S2–S18；S20 另含 S2–S19；
    S21 另含 S2–S20；S22 另含 S2–S21）
3. ST-EXCLUDE（名称命中 *ST / S*ST）
4. 非 BSE（4/8/92 前缀）
5. 可选 prefix_concentration：同一 3 位码前缀在本片最多 N 个
   （S7/S8/S9/S10/S11/S12/S13/S14/S15/S16/S17/S18/S19/S20/S21/S22 默认 N=25；避免 mono-prefix 批处理再现 S6 首轮 timeout 窗）
6. 按 company_code 升序；为候选分配 case_id 与 report_type/expected_period 后
   再跑 listing_period_gate；不通过则跳过该码（不得静默改 period）
7. B 轨 overlap：**允许**（全市场 A 周期报告元数据 vs B 披露事件，跨轨不同维度）

切片：
- S2：AD2E601–650（`--slice s2`）
- S3：AD2E651–700（`--slice s3`）
- S4：AD2E701–750（`--slice s4`）
- S5：AD2E751–800（`--slice s5`）
- S6：AD2E801–850（`--slice s6`）
- S7：AD2E851–900（`--slice s7` · overlay + prefix cap）
- S8：AD2E901–950（`--slice s8` · overlay + prefix cap）
- S9：AD2E951–1000（`--slice s9` · overlay + prefix cap）
- S10：AD2E1001–1050（`--slice s10` · overlay + prefix cap）
- S11：AD2E1051–1100（`--slice s11` · overlay + prefix cap）
- S12：AD2E1101–1150（`--slice s12` · overlay + prefix cap）
- S13：AD2E1151–1200（`--slice s13` · overlay + prefix cap）
- S14：AD2E1201–1250（`--slice s14` · overlay + prefix cap）
- S15：AD2E1251–1300（`--slice s15` · overlay + prefix cap）
- S16：AD2E1301–1350（`--slice s16` · overlay + prefix cap）
- S17：AD2E1351–1400（`--slice s17` · overlay + prefix cap）
- S18：AD2E1401–1450（`--slice s18` · overlay + prefix cap）
- S19：AD2E1451–1500（`--slice s19` · overlay + prefix cap）
- S20：AD2E1501–1550（`--slice s20` · overlay + prefix cap）
- S21：AD2E1551–1600（`--slice s21` · overlay + prefix cap）
- S22：AD2E1601–1650（默认 · `--slice s22` · overlay + prefix cap）
- S23：AD2E1651–1850（`--slice s23` · ~200 · overlay + prefix cap；R19 ladder）
- S24：AD2E1851–2221（`--slice s24` · residual≈371 · overlay + prefix cap；
  R19 excellence 诚实残差；分母不足 1000 时不得声称 1000）

禁止：CNINFO live、伪造上市日、mutate 封闭 S1–S23 live 根、静默改写 expected_period。
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import yaml

import cninfo_a_class_listing_period_gate as listing_period_gate
import cninfo_a_class_profile_coverage as profile_coverage

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

# A-FM-06：listing-aware S7（AD2E851–900）；A exclude 含 S2–S6；overlay + prefix cap
DEFAULT_A_EXCLUDE_S7_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S6_UNIVERSE_CSVS + (
    DEFAULT_S6_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S7_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s7_plus50_universe_20260715.csv",
)
DEFAULT_S7_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s7_reject_ledger_20260715.csv",
)
DEFAULT_S7_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
# 单片内同一 3 位前缀上限（S6 首轮 50×301 触发 timeout 窗的防护）
DEFAULT_MAX_SAME_PREFIX_S7 = 25

# A-FM-08：listing-aware S8（AD2E901–950）；A exclude 含 S2–S7；overlay + prefix cap
DEFAULT_A_EXCLUDE_S8_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S7_UNIVERSE_CSVS + (
    DEFAULT_S7_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S8_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s8_plus50_universe_20260715.csv",
)
DEFAULT_S8_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s8_reject_ledger_20260715.csv",
)
DEFAULT_S8_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S8 = 25

# A-FM-09：listing-aware S9（AD2E951–1000）；A exclude 含 S2–S8；overlay + prefix cap
DEFAULT_A_EXCLUDE_S9_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S8_UNIVERSE_CSVS + (
    DEFAULT_S8_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S9_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s9_plus50_universe_20260715.csv",
)
DEFAULT_S9_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s9_reject_ledger_20260715.csv",
)
DEFAULT_S9_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S9 = 25

# A-FM-10：listing-aware S10（AD2E1001–1050）；A exclude 含 S2–S9；overlay + prefix cap
DEFAULT_A_EXCLUDE_S10_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S9_UNIVERSE_CSVS + (
    DEFAULT_S9_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S10_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s10_plus50_universe_20260715.csv",
)
DEFAULT_S10_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s10_reject_ledger_20260715.csv",
)
DEFAULT_S10_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S10 = 25

# A-FM-11：listing-aware S11（AD2E1051–1100）；A exclude 含 S2–S10；overlay + prefix cap
DEFAULT_A_EXCLUDE_S11_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S10_UNIVERSE_CSVS + (
    DEFAULT_S10_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S11_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s11_plus50_universe_20260715.csv",
)
DEFAULT_S11_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s11_reject_ledger_20260715.csv",
)
DEFAULT_S11_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S11 = 25

# A-FM-12：listing-aware S12（AD2E1101–1150）；A exclude 含 S2–S11；overlay + prefix cap
DEFAULT_A_EXCLUDE_S12_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S11_UNIVERSE_CSVS + (
    DEFAULT_S11_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S12_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s12_plus50_universe_20260715.csv",
)
DEFAULT_S12_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s12_reject_ledger_20260715.csv",
)
DEFAULT_S12_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S12 = 25

# A-FM-13：listing-aware S13（AD2E1151–1200）；A exclude 含 S2–S12；overlay + prefix cap
DEFAULT_A_EXCLUDE_S13_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S12_UNIVERSE_CSVS + (
    DEFAULT_S12_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S13_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s13_plus50_universe_20260715.csv",
)
DEFAULT_S13_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s13_reject_ledger_20260715.csv",
)
DEFAULT_S13_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S13 = 25

# A-FM-14：listing-aware S14（AD2E1201–1250）；A exclude 含 S2–S13；overlay + prefix cap
DEFAULT_A_EXCLUDE_S14_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S13_UNIVERSE_CSVS + (
    DEFAULT_S13_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S14_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s14_plus50_universe_20260715.csv",
)
DEFAULT_S14_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s14_reject_ledger_20260715.csv",
)
DEFAULT_S14_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S14 = 25

# A-FM-15：listing-aware S15（AD2E1251–1300）；A exclude 含 S2–S14；overlay + prefix cap
DEFAULT_A_EXCLUDE_S15_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S14_UNIVERSE_CSVS + (
    DEFAULT_S14_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S15_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s15_plus50_universe_20260715.csv",
)
DEFAULT_S15_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s15_reject_ledger_20260715.csv",
)
DEFAULT_S15_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S15 = 25

# A-FM-16：listing-aware S16（AD2E1301–1350）；A exclude 含 S2–S15；overlay + prefix cap
DEFAULT_A_EXCLUDE_S16_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S15_UNIVERSE_CSVS + (
    DEFAULT_S15_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S16_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s16_plus50_universe_20260715.csv",
)
DEFAULT_S16_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s16_reject_ledger_20260715.csv",
)
DEFAULT_S16_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S16 = 25

# A-FM-17：listing-aware S17（AD2E1351–1400）；A exclude 含 S2–S16；overlay + prefix cap
DEFAULT_A_EXCLUDE_S17_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S16_UNIVERSE_CSVS + (
    DEFAULT_S16_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S17_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s17_plus50_universe_20260715.csv",
)
DEFAULT_S17_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s17_reject_ledger_20260715.csv",
)
DEFAULT_S17_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S17 = 25

# A-FM-18：listing-aware S18（AD2E1401–1450）；A exclude 含 S2–S17；overlay + prefix cap
DEFAULT_A_EXCLUDE_S18_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S17_UNIVERSE_CSVS + (
    DEFAULT_S17_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S18_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s18_plus50_universe_20260715.csv",
)
DEFAULT_S18_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s18_reject_ledger_20260715.csv",
)
DEFAULT_S18_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S18 = 25

# A-FM-19：listing-aware S19（AD2E1451–1500）；A exclude 含 S2–S18；overlay + prefix cap
DEFAULT_A_EXCLUDE_S19_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S18_UNIVERSE_CSVS + (
    DEFAULT_S18_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S19_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s19_plus50_universe_20260715.csv",
)
DEFAULT_S19_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s19_reject_ledger_20260715.csv",
)
DEFAULT_S19_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S19 = 25

# A-FM-20：listing-aware S20（AD2E1501–1550）；A exclude 含 S2–S19；overlay + prefix cap
DEFAULT_A_EXCLUDE_S20_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S19_UNIVERSE_CSVS + (
    DEFAULT_S19_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S20_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s20_plus50_universe_20260716.csv",
)
DEFAULT_S20_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s20_reject_ledger_20260716.csv",
)
DEFAULT_S20_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S20 = 25

# A-FM-01：listing-aware S21（AD2E1551–1600）；A exclude 含 S2–S20；overlay + prefix cap
DEFAULT_A_EXCLUDE_S21_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S20_UNIVERSE_CSVS + (
    DEFAULT_S20_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S21_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s21_plus50_universe_20260716.csv",
)
DEFAULT_S21_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s21_reject_ledger_20260716.csv",
)
DEFAULT_S21_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S21 = 25

# A-FM-02：listing-aware S22（AD2E1601–1650）；A exclude 含 S2–S21；overlay + prefix cap
DEFAULT_A_EXCLUDE_S22_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S21_UNIVERSE_CSVS + (
    DEFAULT_S21_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S22_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s22_plus50_universe_20260716.csv",
)
DEFAULT_S22_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s22_reject_ledger_20260716.csv",
)
DEFAULT_S22_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S22 = 25

# A-FM-03：listing-aware S23（AD2E1651–1850 · ~200）；A exclude 含 S2–S22；overlay + prefix cap
DEFAULT_A_EXCLUDE_S23_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S22_UNIVERSE_CSVS + (
    DEFAULT_S22_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S23_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s23_plus200_universe_20260716.csv",
)
DEFAULT_S23_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s23_reject_ledger_20260716.csv",
)
DEFAULT_S23_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S23 = 100
DEFAULT_TARGET_SIZE_S23 = 200

# A-FM-05：listing-aware S24 residual（AD2E1851–2221 · ≈371）；A exclude 含 S2–S23
DEFAULT_A_EXCLUDE_S24_UNIVERSE_CSVS: Tuple[str, ...] = DEFAULT_A_EXCLUDE_S23_UNIVERSE_CSVS + (
    DEFAULT_S23_OUTPUT_UNIVERSE_CSV,
)
DEFAULT_S24_OUTPUT_UNIVERSE_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s24_residual371_universe_20260716.csv",
)
DEFAULT_S24_REJECT_LEDGER_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s24_reject_ledger_20260716.csv",
)
DEFAULT_S24_PROFILE_DIR = profile_coverage.DEFAULT_OVERLAY_DIR
DEFAULT_MAX_SAME_PREFIX_S24 = 371
DEFAULT_TARGET_SIZE_S24 = 371

COHORT_LABEL = "next_scale_listing_aware"
CASE_ID_START = 601
CASE_ID_START_S3 = 651
CASE_ID_START_S4 = 701
CASE_ID_START_S5 = 751
CASE_ID_START_S6 = 801
CASE_ID_START_S7 = 851
CASE_ID_START_S8 = 901
CASE_ID_START_S9 = 951
CASE_ID_START_S10 = 1001
CASE_ID_START_S11 = 1051
CASE_ID_START_S12 = 1101
CASE_ID_START_S13 = 1151
CASE_ID_START_S14 = 1201
CASE_ID_START_S15 = 1251
CASE_ID_START_S16 = 1301
CASE_ID_START_S17 = 1351
CASE_ID_START_S18 = 1401
CASE_ID_START_S19 = 1451
CASE_ID_START_S20 = 1501
CASE_ID_START_S21 = 1551
CASE_ID_START_S22 = 1601
CASE_ID_START_S23 = 1651
CASE_ID_START_S24 = 1851
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


def code_prefix3(company_code: str) -> str:
    """三位码前缀（浓度门禁用）。"""
    return profile_coverage.code_prefix3(company_code)


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
    max_same_prefix: Optional[int] = None,
) -> BuildResult:
    """
    构建 listing-aware 下一片 cohort。

    对每个候选：先按排序取码，再按即将占用的 case_num 派生 expected_period，
    再调用 listing_period_gate；拒绝则记台账并尝试下一码。

    max_same_prefix:
      None = 不启用（S2–S6 回放兼容）；
      正整数 = 本片内同一 3 位前缀最多入选该数量（S7 默认 25）。
    """
    if target_size <= 0:
        raise ValueError("target_size_must_be_positive")
    if case_id_start < CASE_ID_START:
        raise ValueError(f"case_id_start_must_be_ge_{CASE_ID_START}")
    if max_same_prefix is not None and max_same_prefix <= 0:
        raise ValueError("max_same_prefix_must_be_positive_or_none")

    a_exclude = load_a_exclude_codes(a_exclude_csvs)
    names = load_full_market_name_map(full_market_yaml)
    profile_codes = list_profile_codes(profile_dir)

    selected: List[CohortRow] = []
    rejected: List[RejectRow] = []
    profile_candidates = 0
    selected_prefix_counts: Counter = Counter()

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

        prefix = code_prefix3(code)
        if max_same_prefix is not None and selected_prefix_counts[prefix] >= max_same_prefix:
            rejected.append(
                RejectRow(
                    company_code=code,
                    company_name=name,
                    reject_stage="prefix_concentration_exclude",
                    failure_class="prefix_concentration_cap",
                    listing_date="",
                    expected_period_attempted="",
                    notes=(
                        f"本片前缀 {prefix} 已达上限 {max_same_prefix}；"
                        "跳过以降低 mono-prefix 批处理 timeout 风险"
                    ),
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
        selected_prefix_counts[prefix] += 1

    if len(selected) < target_size:
        raise RuntimeError(
            f"listing_aware_cohort_undersized:got={len(selected)} expected={target_size} "
            f"profile_candidates={profile_candidates} a_exclude={len(a_exclude)} "
            f"max_same_prefix={max_same_prefix}"
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


def build_and_write_s7_plus50(
    *,
    universe_csv: str = DEFAULT_S7_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S7_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S7_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S7,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S7 +50 universe（AD2E851–900）。

    - A exclude：S2–S6
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S7,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S7_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s8_plus50(
    *,
    universe_csv: str = DEFAULT_S8_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S8_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S8_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S8,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S8 +50 universe（AD2E901–950）。

    - A exclude：S2–S7
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S8,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S8_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s9_plus50(
    *,
    universe_csv: str = DEFAULT_S9_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S9_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S9_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S9,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S9 +50 universe（AD2E951–1000）。

    - A exclude：S2–S8
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S9,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S9_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result



def build_and_write_s10_plus50(
    *,
    universe_csv: str = DEFAULT_S10_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S10_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S10_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S10,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S10 +50 universe（AD2E1001–1050）。

    - A exclude：S2–S9
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S10,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S10_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result




def build_and_write_s11_plus50(
    *,
    universe_csv: str = DEFAULT_S11_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S11_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S11_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S11,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S11 +50 universe（AD2E1051–1100）。

    - A exclude：S2–S10
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S11,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S11_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s12_plus50(
    *,
    universe_csv: str = DEFAULT_S12_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S12_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S12_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S12,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S12 +50 universe（AD2E1101–1150）。

    - A exclude：S2–S11
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S12,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S12_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s13_plus50(
    *,
    universe_csv: str = DEFAULT_S13_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S13_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S13_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S13,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S13 +50 universe（AD2E1151–1200）。

    - A exclude：S2–S12
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S13,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S13_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s14_plus50(
    *,
    universe_csv: str = DEFAULT_S14_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S14_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S14_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S14,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S14 +50 universe（AD2E1201–1250）。

    - A exclude：S2–S13
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S14,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S14_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s15_plus50(
    *,
    universe_csv: str = DEFAULT_S15_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S15_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S15_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S15,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S15 +50 universe（AD2E1251–1300）。

    - A exclude：S2–S14
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S15,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S15_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s16_plus50(
    *,
    universe_csv: str = DEFAULT_S16_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S16_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S16_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S16,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S16 +50 universe（AD2E1301–1350）。

    - A exclude：S2–S15
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S16,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S16_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s17_plus50(
    *,
    universe_csv: str = DEFAULT_S17_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S17_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S17_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S17,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S17 +50 universe（AD2E1351–1400）。

    - A exclude：S2–S16
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S17,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S17_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s18_plus50(
    *,
    universe_csv: str = DEFAULT_S18_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S18_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S18_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S18,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S18 +50 universe（AD2E1401–1450）。

    - A exclude：S2–S17
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S18,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S18_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result



def build_and_write_s19_plus50(
    *,
    universe_csv: str = DEFAULT_S19_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S19_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S19_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S19,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S19 +50 universe（AD2E1451–1500）。

    - A exclude：S2–S18
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S19,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S19_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result



def build_and_write_s20_plus50(
    *,
    universe_csv: str = DEFAULT_S20_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S20_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S20_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S20,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S20 +50 universe（AD2E1501–1550）。

    - A exclude：S2–S19
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S20,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S20_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s21_plus50(
    *,
    universe_csv: str = DEFAULT_S21_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S21_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S21_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S21,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S21 +50 universe（AD2E1551–1600）。

    - A exclude：S2–S20
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S21,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S21_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s22_plus50(
    *,
    universe_csv: str = DEFAULT_S22_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S22_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE,
    profile_dir: str = DEFAULT_S22_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S22,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S22 +50 universe（AD2E1601–1650）。

    - A exclude：S2–S21
    - profile_dir：默认 A 轨 coverage overlay（扩大分母）
    - max_same_prefix：默认 25（前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S22,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S22_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result



def build_and_write_s23_plus200(
    *,
    universe_csv: str = DEFAULT_S23_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S23_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE_S23,
    profile_dir: str = DEFAULT_S23_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S23,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S23 ~200 universe（AD2E1651–1850）。

    - A exclude：S2–S22
    - profile_dir：默认 A 轨 coverage overlay
    - max_same_prefix：默认 100（~200 尺度前缀浓度门禁）
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S23,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S23_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def build_and_write_s24_residual371(
    *,
    universe_csv: str = DEFAULT_S24_OUTPUT_UNIVERSE_CSV,
    reject_ledger_csv: str = DEFAULT_S24_REJECT_LEDGER_CSV,
    target_size: int = DEFAULT_TARGET_SIZE_S24,
    profile_dir: str = DEFAULT_S24_PROFILE_DIR,
    max_same_prefix: int = DEFAULT_MAX_SAME_PREFIX_S24,
    ensure_overlay: bool = True,
) -> BuildResult:
    """
    构建 listing-aware S24 诚实残差 universe（AD2E1851–2221 · ≈371）。

    - A exclude：S2–S23（含 a_exclude≈1850）
    - profile_dir：默认 A 轨 coverage overlay（离线并集；不伪造 listing_date）
    - max_same_prefix：默认 371（残差全量；不因前缀门挡下可选码）
    - 不得把 size 抬到 1000：当前分母不足时诚实跑残差
    """
    if ensure_overlay:
        profile_coverage.build_profile_overlay(overlay_dir=profile_dir, refresh=True)
    result = build_listing_aware_cohort(
        target_size=target_size,
        case_id_start=CASE_ID_START_S24,
        a_exclude_csvs=DEFAULT_A_EXCLUDE_S24_UNIVERSE_CSVS,
        profile_dir=profile_dir,
        max_same_prefix=max_same_prefix,
    )
    write_universe_csv(result.selected, universe_csv)
    write_reject_ledger(result.rejected, reject_ledger_csv)
    return result


def main(argv: Optional[Iterable[str]] = None) -> int:
    """CLI：生成 listing-aware universe（offline · 默认 S24 residual）。"""
    import argparse

    parser = argparse.ArgumentParser(description="listing-aware A cohort builder（CNINFO=0）")
    parser.add_argument(
        "--slice",
        choices=(
            "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10",
            "s11", "s12", "s13", "s14", "s15", "s16", "s17", "s18", "s19", "s20",
            "s21", "s22", "s23", "s24",
        ),
        default="s24",
        help=(
            "s2=AD2E601-650；s3=AD2E651-700；s4=AD2E701-750；"
            "s5=AD2E751-800；s6=AD2E801-850；s7=AD2E851-900；"
            "s8=AD2E901-950；s9=AD2E951-1000；s10=AD2E1001-1050；"
            "s11=AD2E1051-1100；s12=AD2E1101-1150；s13=AD2E1151-1200；"
            "s14=AD2E1201-1250；s15=AD2E1251-1300；s16=AD2E1301-1350；"
            "s17=AD2E1351-1400；s18=AD2E1401-1450；s19=AD2E1451-1500；"
            "s20=AD2E1501-1550；s21=AD2E1551-1600；s22=AD2E1601-1650；"
            "s23=AD2E1651-1850~200；s24=AD2E1851-2221 residual≈371（默认）"
        ),
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
    elif args.slice == "s6":
        result = build_and_write_s6_plus50()
        universe_path = DEFAULT_S6_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s7":
        result = build_and_write_s7_plus50()
        universe_path = DEFAULT_S7_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s8":
        result = build_and_write_s8_plus50()
        universe_path = DEFAULT_S8_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s9":
        result = build_and_write_s9_plus50()
        universe_path = DEFAULT_S9_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s10":
        result = build_and_write_s10_plus50()
        universe_path = DEFAULT_S10_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s11":
        result = build_and_write_s11_plus50()
        universe_path = DEFAULT_S11_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s12":
        result = build_and_write_s12_plus50()
        universe_path = DEFAULT_S12_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s13":
        result = build_and_write_s13_plus50()
        universe_path = DEFAULT_S13_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s14":
        result = build_and_write_s14_plus50()
        universe_path = DEFAULT_S14_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s15":
        result = build_and_write_s15_plus50()
        universe_path = DEFAULT_S15_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s16":
        result = build_and_write_s16_plus50()
        universe_path = DEFAULT_S16_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s17":
        result = build_and_write_s17_plus50()
        universe_path = DEFAULT_S17_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s18":
        result = build_and_write_s18_plus50()
        universe_path = DEFAULT_S18_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s19":
        result = build_and_write_s19_plus50()
        universe_path = DEFAULT_S19_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s20":
        result = build_and_write_s20_plus50()
        universe_path = DEFAULT_S20_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s21":
        result = build_and_write_s21_plus50()
        universe_path = DEFAULT_S21_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s22":
        result = build_and_write_s22_plus50()
        universe_path = DEFAULT_S22_OUTPUT_UNIVERSE_CSV
    elif args.slice == "s23":
        result = build_and_write_s23_plus200()
        universe_path = DEFAULT_S23_OUTPUT_UNIVERSE_CSV
    else:
        result = build_and_write_s24_residual371()
        universe_path = DEFAULT_S24_OUTPUT_UNIVERSE_CSV
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

"""
A-class 离线上市日 vs expected_period 门禁（纯离线 · CNINFO = 0）。

用途：在全市场扩展 / universe 筛选时，识别「期望报告期早于上市日」
或「未上市（listing_date 空）」导致的 true_not_found，避免把 query/keyword
问题与 listing_gap 混淆。

权威只读源：
  outputs/harvest/cninfo_c_class/normalized/company_basic_profile/{code}.json
  （字段 listing_date；缺失时回退 raw_record_json.basicInformation[0].F006D）

禁止：CNINFO live、静默伪造上市日、改写封闭 slice2 S1 live 根。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)

DEFAULT_PROFILE_DIR = os.path.join(
    _BASE_DIR,
    "outputs",
    "harvest",
    "cninfo_c_class",
    "normalized",
    "company_basic_profile",
)

# A-R16-01 三案锚点（orgId 已解析但仍 records=0）
SLICE2_S1_EMPTY_ANNOUNCEMENT_CODES: Tuple[str, ...] = ("688605", "688688", "688758")

FAILURE_LISTING_GAP = "listing_gap_true_not_found"
FAILURE_UNLISTED = "true_not_found_likely_unlisted"
FAILURE_OK = "listing_ok_period_plausible"
FAILURE_PROFILE_MISSING = "listing_profile_missing"

ROOT_PERIOD_BEFORE_LISTING = "expected_period_before_listing"
ROOT_UNLISTED = "unlisted_or_listing_date_null"
ROOT_OK = "listing_on_or_before_period_end"
ROOT_PROFILE_MISSING = "basic_profile_missing"


@dataclass(frozen=True)
class ListingPeriodGateResult:
    """单次门禁结果。"""

    company_code: str
    expected_period: str
    listing_date: str
    found_profile: bool
    root_cause: str
    failure_class: str
    retry_recommended: bool
    source: str
    cninfo_calls: int = 0  # 恒为 0
    notes: str = ""

    @property
    def blocks_periodic_retrieval(self) -> bool:
        """是否应视为周期报告检索不可达（勿再烧 CNINFO retry）。"""
        return self.failure_class in (FAILURE_LISTING_GAP, FAILURE_UNLISTED)


def normalize_code(code: str) -> str:
    """规范化证券代码：去空白；纯数字左侧补零至 6 位。"""
    s = str(code or "").strip()
    if not s:
        return ""
    return s.zfill(6) if s.isdigit() else s


def parse_iso_date(value: Any) -> Optional[date]:
    """解析 YYYY-MM-DD；空/None 返回 None，不抛异常冒充成功。"""
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.lower() in ("none", "null"):
        return None
    s = s[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _extract_listing_date_from_profile(data: Dict[str, Any]) -> Tuple[Optional[date], str]:
    """从 normalized basic_profile 提取上市日。"""
    ld = parse_iso_date(data.get("listing_date"))
    if ld is not None:
        return ld, "listing_date"
    raw = data.get("raw_record_json") or {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = {}
    bi_list = (raw or {}).get("basicInformation") or []
    bi = bi_list[0] if bi_list else {}
    ld2 = parse_iso_date((bi or {}).get("F006D"))
    if ld2 is not None:
        return ld2, "raw_record_json.basicInformation.F006D"
    return None, "listing_date_null"


def load_listing_date(
    company_code: str, profile_dir: str = DEFAULT_PROFILE_DIR
) -> Tuple[Optional[date], bool, str]:
    """
    读取上市日。

    返回 (listing_date|None, found_profile, source_or_error)。
    文件缺失时 found_profile=False，不得伪造日期。
    """
    code = normalize_code(company_code)
    if not code:
        return None, False, "empty_company_code"
    path = os.path.join(profile_dir, f"{code}.json")
    if not os.path.isfile(path):
        return None, False, f"profile_missing:{path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return None, False, "profile_invalid_json_object"
    ld, field_src = _extract_listing_date_from_profile(data)
    return ld, True, f"c_class_basic_profile:{field_src}"


def assess_listing_vs_expected_period(
    company_code: str,
    expected_period: str,
    *,
    profile_dir: str = DEFAULT_PROFILE_DIR,
) -> ListingPeriodGateResult:
    """
    判定 expected_period 相对上市日是否可达。

    - listing_date > expected_period → listing_gap_true_not_found（不建议 retry）
    - listing_date 空且 profile 存在 → true_not_found_likely_unlisted（不建议 retry）
    - profile 缺失 → listing_profile_missing（需补证据，不假装通过）
    - 否则 listing_ok_period_plausible
    """
    code = normalize_code(company_code)
    period = parse_iso_date(expected_period)
    ld, found, src = load_listing_date(code, profile_dir=profile_dir)

    if not found:
        return ListingPeriodGateResult(
            company_code=code,
            expected_period=(expected_period or "").strip(),
            listing_date="",
            found_profile=False,
            root_cause=ROOT_PROFILE_MISSING,
            failure_class=FAILURE_PROFILE_MISSING,
            retry_recommended=False,
            source=src,
            notes="缺少 C-class basic_profile；不得推断上市日",
        )

    if ld is None:
        return ListingPeriodGateResult(
            company_code=code,
            expected_period=(expected_period or "").strip(),
            listing_date="",
            found_profile=True,
            root_cause=ROOT_UNLISTED,
            failure_class=FAILURE_UNLISTED,
            retry_recommended=False,
            source=src,
            notes="listing_date/F006D 为空；疑似未完成上市或无正式上市日",
        )

    if period is None:
        return ListingPeriodGateResult(
            company_code=code,
            expected_period=(expected_period or "").strip(),
            listing_date=ld.isoformat(),
            found_profile=True,
            root_cause="expected_period_unparseable",
            failure_class=FAILURE_PROFILE_MISSING,
            retry_recommended=False,
            source=src,
            notes="expected_period 无法解析为日期",
        )

    if ld > period:
        return ListingPeriodGateResult(
            company_code=code,
            expected_period=period.isoformat(),
            listing_date=ld.isoformat(),
            found_profile=True,
            root_cause=ROOT_PERIOD_BEFORE_LISTING,
            failure_class=FAILURE_LISTING_GAP,
            retry_recommended=False,
            source=src,
            notes="期望报告期早于上市日；hisAnnouncement 空结果属预期",
        )

    return ListingPeriodGateResult(
        company_code=code,
        expected_period=period.isoformat(),
        listing_date=ld.isoformat(),
        found_profile=True,
        root_cause=ROOT_OK,
        failure_class=FAILURE_OK,
        retry_recommended=False,
        source=src,
        notes="上市日不晚于报告期；空公告需另查 query/keyword/matching",
    )

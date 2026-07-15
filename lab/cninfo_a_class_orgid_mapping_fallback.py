"""
A-class 离线 orgId 映射回退（纯离线 · CNINFO = 0）。

当 topSearch 返回 null orgId 时，从仓库内已提交的映射证据解析已知 orgId，
不发起任何 CNINFO / live 请求。

权威只读源（按优先级）：
1. slice2 S1 offline recovery CSV（Run 14 三案恢复表）
2. outputs/validation/cninfo_report_p1_identity_mapping.csv
3. lab/eval_companies_full_market_2024.yaml

缺失码显式返回未命中（found=False / 空 org_id），禁止静默伪造。
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML required: pip install pyyaml") from exc

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)

DEFAULT_RECOVERY_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice2_s1_orgid_offline_recovery_20260715.csv",
)
DEFAULT_IDENTITY_MAPPING_CSV = os.path.join(
    _BASE_DIR,
    "outputs",
    "validation",
    "cninfo_report_p1_identity_mapping.csv",
)
DEFAULT_FULL_MARKET_YAML = os.path.join(
    _LAB_DIR,
    "eval_companies_full_market_2024.yaml",
)

# Run 14 诊断中已恢复的三案（测试与证据锚点）
SLICE2_S1_UNRESOLVED_CODES: Tuple[str, ...] = ("688605", "688688", "688758")
SLICE2_S1_EXPECTED_ORGIDS: Dict[str, str] = {
    "688605": "9900059045",  # 先锋精科
    "688688": "9900046315",  # 蚂蚁集团
    "688758": "9900057459",  # 赛分科技
}


class OrgIdMappingMissError(LookupError):
    """离线映射未命中：调用方必须显式处理，不得静默当作成功。"""


@dataclass(frozen=True)
class OrgIdLookupResult:
    """单次离线查找结果。"""

    company_code: str
    org_id: str
    found: bool
    source: str
    company_name: str = ""
    error: str = ""

    def require_org_id(self) -> str:
        """命中则返回 org_id；未命中抛出 OrgIdMappingMissError。"""
        if not self.found or not (self.org_id or "").strip():
            raise OrgIdMappingMissError(
                self.error
                or f"offline orgId mapping miss for code={self.company_code!r}"
            )
        return self.org_id.strip()


def normalize_code(code: str) -> str:
    """规范化证券代码：去空白；纯数字左侧补零至 6 位。"""
    s = str(code or "").strip()
    if not s:
        return ""
    return s.zfill(6) if s.isdigit() else s


def is_valid_orgid(org_id: str) -> bool:
    """判定 orgId 是否可用（非空且非 unknown）。"""
    o = (org_id or "").strip()
    return bool(o) and o.lower() != "unknown"


@dataclass
class OfflineOrgIdIndex:
    """
    离线 orgId 索引。

    entries: code -> (org_id, source, company_name)
    同码多源时保留首次写入（高优先级源优先）。
    """

    entries: Dict[str, Tuple[str, str, str]]
    source_paths: List[str]
    cninfo_calls: int = 0  # 恒为 0；便于证据断言

    def lookup(self, company_code: str) -> OrgIdLookupResult:
        code = normalize_code(company_code)
        if not code:
            return OrgIdLookupResult(
                company_code="",
                org_id="",
                found=False,
                source="",
                error="empty_company_code",
            )
        hit = self.entries.get(code)
        if hit is None:
            return OrgIdLookupResult(
                company_code=code,
                org_id="",
                found=False,
                source="",
                error=f"offline_orgid_not_found:{code}",
            )
        org_id, source, name = hit
        if not is_valid_orgid(org_id):
            return OrgIdLookupResult(
                company_code=code,
                org_id="",
                found=False,
                source=source,
                company_name=name,
                error=f"offline_orgid_invalid:{code}",
            )
        return OrgIdLookupResult(
            company_code=code,
            org_id=org_id.strip(),
            found=True,
            source=source,
            company_name=name,
        )

    def resolve(self, company_code: str) -> str:
        """查找并要求命中；未命中抛 OrgIdMappingMissError。"""
        return self.lookup(company_code).require_org_id()


def _put_if_absent(
    entries: Dict[str, Tuple[str, str, str]],
    code: str,
    org_id: str,
    source: str,
    name: str = "",
) -> None:
    code_n = normalize_code(code)
    if not code_n or not is_valid_orgid(org_id):
        return
    if code_n in entries:
        return
    entries[code_n] = (org_id.strip(), source, (name or "").strip())


def load_recovery_csv(
    path: str = DEFAULT_RECOVERY_CSV,
) -> Dict[str, Tuple[str, str, str]]:
    """加载 Run 14 offline recovery CSV：code -> (org_id, source, name)。"""
    out: Dict[str, Tuple[str, str, str]] = {}
    if not os.path.isfile(path):
        return out
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = row.get("company_code", "")
            org_id = row.get("offline_recovered_org_id", "")
            name = row.get("company_name", "")
            src_label = row.get("offline_source", "") or "recovery_csv"
            source = f"recovery_csv:{os.path.basename(path)}|{src_label}"
            _put_if_absent(out, code, org_id, source, name)
    return out


def load_identity_mapping_csv(
    path: str = DEFAULT_IDENTITY_MAPPING_CSV,
) -> Dict[str, Tuple[str, str, str]]:
    """加载 P1 identity mapping CSV。"""
    out: Dict[str, Tuple[str, str, str]] = {}
    if not os.path.isfile(path):
        return out
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = row.get("company_code", "") or row.get("cninfo_stock_code", "")
            org_id = row.get("cninfo_org_id", "")
            name = row.get("company_name", "")
            status = (row.get("mapping_status") or "").strip().lower()
            if status and status != "mapped":
                continue
            source = f"identity_mapping:{os.path.basename(path)}"
            _put_if_absent(out, code, org_id, source, name)
    return out


def load_full_market_yaml(
    path: str = DEFAULT_FULL_MARKET_YAML,
) -> Dict[str, Tuple[str, str, str]]:
    """加载全市场 YAML 中的 stock_code/orgid。"""
    out: Dict[str, Tuple[str, str, str]] = {}
    if not os.path.isfile(path):
        return out
    with open(path, encoding="utf-8") as fh:
        payload = yaml.safe_load(fh) or {}
    companies = payload.get("companies") or []
    source = f"full_market_yaml:{os.path.basename(path)}"
    for rec in companies:
        if not isinstance(rec, dict):
            continue
        code = rec.get("stock_code", "")
        org_id = rec.get("orgid", "")
        name = rec.get("short_name", "")
        _put_if_absent(out, str(code), str(org_id) if org_id is not None else "", source, str(name or ""))
    return out


def build_offline_orgid_index(
    recovery_csv: str = DEFAULT_RECOVERY_CSV,
    identity_mapping_csv: str = DEFAULT_IDENTITY_MAPPING_CSV,
    full_market_yaml: str = DEFAULT_FULL_MARKET_YAML,
    *,
    include_recovery: bool = True,
    include_identity_mapping: bool = True,
    include_full_market_yaml: bool = True,
) -> OfflineOrgIdIndex:
    """
    构建离线索引。优先级：recovery > identity_mapping > full_market_yaml。
    全程无网络 / 无 CNINFO。
    """
    entries: Dict[str, Tuple[str, str, str]] = {}
    source_paths: List[str] = []

    layers: List[Tuple[bool, str, Callable[[str], Dict[str, Tuple[str, str, str]]]]] = [
        (include_recovery, recovery_csv, load_recovery_csv),
        (include_identity_mapping, identity_mapping_csv, load_identity_mapping_csv),
        (include_full_market_yaml, full_market_yaml, load_full_market_yaml),
    ]
    for enabled, path, loader in layers:
        if not enabled:
            continue
        if not os.path.isfile(path):
            continue
        layer = loader(path)
        for code, triple in layer.items():
            _put_if_absent(entries, code, triple[0], triple[1], triple[2])
        source_paths.append(path)

    return OfflineOrgIdIndex(entries=entries, source_paths=source_paths, cninfo_calls=0)


_DEFAULT_INDEX: Optional[OfflineOrgIdIndex] = None


def get_default_index() -> OfflineOrgIdIndex:
    """懒加载默认离线索引（进程内缓存）。"""
    global _DEFAULT_INDEX
    if _DEFAULT_INDEX is None:
        _DEFAULT_INDEX = build_offline_orgid_index()
    return _DEFAULT_INDEX


def reset_default_index() -> None:
    """清空默认索引缓存（测试用）。"""
    global _DEFAULT_INDEX
    _DEFAULT_INDEX = None


def lookup_orgid(
    company_code: str,
    index: Optional[OfflineOrgIdIndex] = None,
) -> OrgIdLookupResult:
    """离线查找 orgId；未命中返回 found=False（不抛异常）。"""
    idx = index if index is not None else get_default_index()
    return idx.lookup(company_code)


def resolve_orgid(
    company_code: str,
    index: Optional[OfflineOrgIdIndex] = None,
) -> str:
    """
    离线解析 orgId；未命中抛 OrgIdMappingMissError。

    供 A-class 在 topSearch 失败后可选调用；本模块本身不触网。
    """
    idx = index if index is not None else get_default_index()
    return idx.resolve(company_code)


def lookup_many(
    company_codes: Iterable[str],
    index: Optional[OfflineOrgIdIndex] = None,
) -> List[OrgIdLookupResult]:
    """批量离线查找。"""
    idx = index if index is not None else get_default_index()
    return [idx.lookup(c) for c in company_codes]


def verify_slice2_s1_recovered_orgids(
    index: Optional[OfflineOrgIdIndex] = None,
) -> List[OrgIdLookupResult]:
    """
    校验 Run 14 三案恢复锚点：688605 / 688688 / 688758。
    返回三次查找结果；调用方断言 found 与 org_id。
    """
    idx = index if index is not None else get_default_index()
    results: List[OrgIdLookupResult] = []
    for code in SLICE2_S1_UNRESOLVED_CODES:
        results.append(idx.lookup(code))
    return results


if __name__ == "__main__":
    # 本地烟测：仅离线，打印三案与索引规模
    reset_default_index()
    index = get_default_index()
    print(f"cninfo_calls={index.cninfo_calls}")
    print(f"index_size={len(index.entries)}")
    print(f"sources={len(index.source_paths)}")
    for code in SLICE2_S1_UNRESOLVED_CODES:
        r = index.lookup(code)
        expected = SLICE2_S1_EXPECTED_ORGIDS[code]
        status = "OK" if r.found and r.org_id == expected else "MISS"
        print(
            f"{status} code={r.company_code} org_id={r.org_id!r} "
            f"expected={expected!r} source={r.source}"
        )

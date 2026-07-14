"""
CNINFO C-class Era D cleanup 保护工具（仅测试 teardown / 临时目录清理）。

禁止清理生产 harvest / snapshot / validation 根；仅允许 `_mock_*` / `_mock_live_test` 下路径。
"""

from __future__ import annotations

import csv
import os
import shutil
import tempfile
from functools import lru_cache
from typing import Iterable, List, Sequence, Tuple

# lab/ 上一级为仓库根
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

PROTECTED_ROOTS_CSV_REL = (
    "outputs/validation/cninfo_c_class_erad_protected_output_roots.csv"
)

# 磁盘上存在、CSV 可能未列出的生产根（与 Era C 产物对齐）
_EXTRA_PRODUCTION_ROOT_RELS: Tuple[str, ...] = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001",
)

CLEANUP_REFUSED_MSG = "C_CLASS_ERAD_CLEANUP_REFUSED"

# Era D harvest resume audit 默认只写此 validation 子树（或 _mock_*）
DEFAULT_ERAD_AUDIT_OUTPUT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_erad_harvest_resume_audit"
)


def normalize_cleanup_path(path: str, *, base_dir: str = BASE_DIR) -> str:
    """解析为绝对路径并规范化（抵御 ../ 与尾斜杠）。"""
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    return os.path.normpath(os.path.abspath(path))


def _path_segments(path: str) -> List[str]:
    return [p for p in path.split(os.sep) if p]


def is_allowed_mock_test_cleanup_path(path: str, *, base_dir: str = BASE_DIR) -> bool:
    """仅 `_mock_*` 或 `_mock_live_test` 段下允许测试清理。"""
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    segments = _path_segments(norm)
    for seg in segments:
        if seg == "_mock_live_test":
            return True
        if seg.startswith("_mock_"):
            return True
    return False


@lru_cache(maxsize=1)
def load_protected_production_root_prefixes(
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[str, ...]:
    """从 CSV 加载 production 根前缀（绝对路径、已排序：长前缀优先）。"""
    prefixes: List[str] = []
    csv_path = os.path.join(base_dir, csv_rel)
    if os.path.isfile(csv_path):
        with open(csv_path, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row.get("protection_level") != "production":
                    continue
                pattern = (row.get("path_pattern") or "").strip().rstrip("/")
                if not pattern or "**" in pattern or "*" in pattern:
                    continue
                prefixes.append(normalize_cleanup_path(pattern, base_dir=base_dir))

    for rel in _EXTRA_PRODUCTION_ROOT_RELS:
        prefixes.append(normalize_cleanup_path(rel, base_dir=base_dir))

    # 去重并按路径长度降序，避免短前缀误匹配
    unique = sorted(set(prefixes), key=len, reverse=True)
    return tuple(unique)


def _is_under_prefix(path: str, prefix: str) -> bool:
    if path == prefix:
        return True
    return path.startswith(prefix + os.sep)


def is_protected_c_class_production_root(path: str, *, base_dir: str = BASE_DIR) -> bool:
    """路径落在生产 C 类根下且非 mock 测试区。"""
    if is_allowed_mock_test_cleanup_path(path, base_dir=base_dir):
        return False
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    for prefix in load_protected_production_root_prefixes(base_dir=base_dir):
        if _is_under_prefix(norm, prefix):
            return True
    # validation：cninfo_c_class_phase35_* 等文档根
    validation_root = normalize_cleanup_path("outputs/validation", base_dir=base_dir)
    if _is_under_prefix(norm, validation_root):
        rel = os.path.relpath(norm, validation_root)
        if rel.startswith("cninfo_c_class"):
            return True
    return False


def assert_safe_test_cleanup_path(path: str, *, base_dir: str = BASE_DIR) -> None:
    """非 mock 且落在生产根时拒绝清理。"""
    if is_allowed_mock_test_cleanup_path(path, base_dir=base_dir):
        return
    if is_protected_c_class_production_root(path, base_dir=base_dir):
        norm = normalize_cleanup_path(path, base_dir=base_dir)
        raise RuntimeError(f"{CLEANUP_REFUSED_MSG}: {norm}")


def safe_cleanup_temp_output_root(path: str, *, base_dir: str = BASE_DIR) -> None:
    """安全删除临时测试目录；生产根硬拒绝。"""
    assert_safe_test_cleanup_path(path, base_dir=base_dir)
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    if os.path.isdir(norm):
        shutil.rmtree(norm, ignore_errors=True)


def assert_safe_erad_audit_write_path(
    path: str,
    *,
    base_dir: str = BASE_DIR,
    allowed_audit_root_rel: str = DEFAULT_ERAD_AUDIT_OUTPUT_ROOT_REL,
) -> None:
    """审计 runner 写入路径：仅允许 Era D audit 根或 mock 测试区；禁止生产 harvest/snapshot。"""
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    if is_allowed_mock_test_cleanup_path(norm, base_dir=base_dir):
        return
    allowed = normalize_cleanup_path(allowed_audit_root_rel, base_dir=base_dir)
    if norm == allowed or norm.startswith(allowed + os.sep):
        return
    if is_protected_c_class_production_root(norm, base_dir=base_dir):
        raise RuntimeError(f"{CLEANUP_REFUSED_MSG}: audit write refused: {norm}")
    raise RuntimeError(f"{CLEANUP_REFUSED_MSG}: audit write outside allowed root: {norm}")


def create_c_class_mock_test_output_root(
    parent_rel: str = "outputs/harvest/cninfo_c_class/_mock_live_test",
    *,
    prefix: str = "run_",
    base_dir: str = BASE_DIR,
) -> str:
    """在 mock 父目录下创建临时子目录。"""
    parent = normalize_cleanup_path(parent_rel, base_dir=base_dir)
    if not is_allowed_mock_test_cleanup_path(parent, base_dir=base_dir):
        raise RuntimeError(f"{CLEANUP_REFUSED_MSG}: mock parent not allowed: {parent}")
    os.makedirs(parent, exist_ok=True)
    return tempfile.mkdtemp(prefix=prefix, dir=parent)

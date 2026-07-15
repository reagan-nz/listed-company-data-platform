"""
CNINFO C-class Era D cleanup 保护工具（仅测试 teardown / 临时目录清理）。

禁止清理生产 harvest / snapshot / validation 根；仅允许 `_mock_*` / `_mock_live_test` 下路径。
同时提供 snapshot dry-run 写根守卫与隔离 dry-run 可复现指纹（无 CNINFO）。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

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
PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN = (
    "PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN"
)

# Era D harvest resume audit 默认只写此 validation 子树（或 _mock_*）
DEFAULT_ERAD_AUDIT_OUTPUT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_erad_harvest_resume_audit"
)

# 标准 snapshot batch dry-run 默认隔离根（禁止默认写入生产 snapshot quality）
DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL = (
    "outputs/validation/_mock_snapshot_batch_standard_dryrun_isolated"
)

# QA closure 累积双层证据索引权威根（只读；禁止 runner 覆盖）
AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL = (
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index"
)

DUAL_LAYER_INDEX_WRITE_FORBIDDEN = "DUAL_LAYER_INDEX_WRITE_FORBIDDEN"


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


def is_authoritative_dual_layer_index_path(
    path: str,
    *,
    base_dir: str = BASE_DIR,
    authoritative_root_rel: str = AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
) -> bool:
    """路径是否落在权威 dual-layer QA closure 索引根下（非 mock）。"""
    if is_allowed_mock_test_cleanup_path(path, base_dir=base_dir):
        return False
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    root = normalize_cleanup_path(authoritative_root_rel, base_dir=base_dir)
    return norm == root or norm.startswith(root + os.sep)


def assert_authoritative_dual_layer_index_write_forbidden(
    path: str,
    *,
    base_dir: str = BASE_DIR,
    authoritative_root_rel: str = AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
) -> str:
    """
    权威 dual-layer 索引写拒绝：任何落在 QA closure dual_layer_index 根下的写路径硬拒绝。
    mock 路径不受此守卫约束（由调用方另做 mock 隔离断言）。
    返回规范化绝对路径（当未拒绝时）。
    """
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    if is_authoritative_dual_layer_index_path(
        norm,
        base_dir=base_dir,
        authoritative_root_rel=authoritative_root_rel,
    ):
        rel = os.path.relpath(norm, base_dir).replace("\\", "/")
        raise RuntimeError(
            f"{DUAL_LAYER_INDEX_WRITE_FORBIDDEN}: {rel} "
            f"(authoritative dual-layer index is read-only; write only under validation/_mock_*)"
        )
    return norm


def assert_safe_erad_audit_write_path(
    path: str,
    *,
    base_dir: str = BASE_DIR,
    allowed_audit_root_rel: str = DEFAULT_ERAD_AUDIT_OUTPUT_ROOT_REL,
) -> None:
    """审计 runner 写入路径：仅允许 Era D audit 根或 mock 测试区；禁止生产 harvest/snapshot。"""
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    # 权威 dual-layer 索引：即使误配 allowed_audit_root 也硬拒绝覆盖
    assert_authoritative_dual_layer_index_write_forbidden(norm, base_dir=base_dir)
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


@lru_cache(maxsize=1)
def load_protected_snapshot_root_prefixes(
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[str, ...]:
    """从 CSV 加载 production snapshot 根前缀（绝对路径、长前缀优先）。"""
    prefixes: List[str] = []
    csv_path = os.path.join(base_dir, csv_rel)
    if os.path.isfile(csv_path):
        with open(csv_path, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row.get("protection_level") != "production":
                    continue
                if (row.get("root_class") or "").strip() != "snapshot":
                    continue
                pattern = (row.get("path_pattern") or "").strip().rstrip("/")
                if not pattern or "**" in pattern or "*" in pattern:
                    continue
                prefixes.append(normalize_cleanup_path(pattern, base_dir=base_dir))
    unique = sorted(set(prefixes), key=len, reverse=True)
    return tuple(unique)


def is_protected_c_class_production_snapshot_root(
    path: str, *, base_dir: str = BASE_DIR
) -> bool:
    """路径落在生产 C 类 snapshot 根下且非 mock 测试区。"""
    if is_allowed_mock_test_cleanup_path(path, base_dir=base_dir):
        return False
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    for prefix in load_protected_snapshot_root_prefixes(base_dir=base_dir):
        if _is_under_prefix(norm, prefix):
            return True
    return False


def assert_safe_c_class_snapshot_dryrun_write_root(
    path: str,
    *,
    base_dir: str = BASE_DIR,
    allow_production_scaffold: bool = False,
) -> str:
    """
    Snapshot dry-run 写根守卫：
      - mock / 临时隔离根：允许
      - 生产 snapshot 根：默认拒绝（需显式 allow_production_scaffold）
    返回规范化绝对路径。
    """
    norm = normalize_cleanup_path(path, base_dir=base_dir)
    if allow_production_scaffold:
        return norm
    if is_allowed_mock_test_cleanup_path(norm, base_dir=base_dir):
        return norm
    if is_protected_c_class_production_snapshot_root(norm, base_dir=base_dir):
        rel = os.path.relpath(norm, base_dir).replace("\\", "/")
        raise RuntimeError(
            f"{PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN}: {rel} "
            f"(use isolated validation/_mock_* root or "
            f"--allow-production-dryrun-scaffold)"
        )
    return norm


def resolve_standard_snapshot_dryrun_output_root(
    requested: Optional[str],
    *,
    base_dir: str = BASE_DIR,
    allow_production_scaffold: bool = False,
    default_isolated_rel: str = DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
) -> str:
    """
    解析标准 dry-run 输出根：未指定时落到隔离 mock 根；
    指定生产 snapshot 根时除非显式允许否则拒绝。
    """
    if not requested:
        target = normalize_cleanup_path(default_isolated_rel, base_dir=base_dir)
    else:
        target = normalize_cleanup_path(requested, base_dir=base_dir)
    return assert_safe_c_class_snapshot_dryrun_write_root(
        target,
        base_dir=base_dir,
        allow_production_scaffold=allow_production_scaffold,
    )


def fingerprint_isolated_snapshot_dryrun(
    output_root: str,
    *,
    base_dir: str = BASE_DIR,
    gate: str = "",
    company_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    对隔离 dry-run 产物做可复现指纹（status/error/report 存在性 + 内容哈希）。
    不读取生产 snapshot JSON。
    """
    root = normalize_cleanup_path(output_root, base_dir=base_dir)
    quality = os.path.join(root, "quality")
    candidates = [
        os.path.join(quality, "company_snapshot_status.csv"),
        os.path.join(quality, "company_snapshot_error.csv"),
        os.path.join(root, "dryrun_report.csv"),
        os.path.join(root, "dryrun_summary.md"),
    ]
    parts: List[str] = []
    present: Dict[str, bool] = {}
    status_rows = 0
    for path in candidates:
        rel = os.path.relpath(path, root).replace("\\", "/")
        exists = os.path.isfile(path)
        present[rel] = exists
        if not exists:
            parts.append(f"{rel}:missing")
            continue
        with open(path, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        parts.append(f"{rel}:{digest}")
        if rel.endswith("company_snapshot_status.csv"):
            with open(path, encoding="utf-8", newline="") as fh:
                status_rows = max(0, sum(1 for _ in fh) - 1)

    payload = {
        "output_root": os.path.relpath(root, base_dir).replace("\\", "/"),
        "gate": gate,
        "company_count": company_count if company_count is not None else status_rows,
        "status_row_count": status_rows,
        "files_present": present,
        "content_sha256": hashlib.sha256(
            "\n".join(parts).encode("utf-8")
        ).hexdigest(),
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
    }
    payload["fingerprint_sha256"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return payload

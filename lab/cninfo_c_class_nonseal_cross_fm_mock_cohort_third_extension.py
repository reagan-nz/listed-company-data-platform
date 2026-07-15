"""
CNINFO C-class — 非 seal Cross-FM mock cohort 三次完整性扩展（离线 · C-FM-20）。

在 C-FM-19（non-seal second-extension post-commit drift recheck）已 commit 且 EXECUTE 仍
human-held 之上，补齐非 seal 能力（不新增 seal / decision-await / commit-boundary 文档层）：
  1) 扩大非 seal mock cohort 注册表：FM-01..05 + FM-12 + FM-13..19（MOCK15–21）
  2) 指纹链只读核验：含二次扩展 / 二次漂移矩阵零漂移重算
  3) 冻结 mock 写隔离：MOCK3–21 拒绝；本任务 MOCK22 / ephemeral 放行
  4) harvest/exclusion dual-layer 一致性交叉指纹（FM-03）
  5) 生产保护根写守卫 battery（harvest / snapshot / 权威索引拒绝）
  6) FM-01..05 + FM-12..19 gate battery（显式跳过 seal FM06–11）
  7) protected_output_roots.csv 注册一致性（含 MOCK22）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–21 / 权威 dual-layer 索引 ·
verified 声称 · 翻转 approved_for_snapshot_rebuild · 扩展 seal-chain ·
因 AWAITING 而 IDLE · commit/push。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cninfo_c_class_cross_fm_mock_cohort_integrity import (  # noqa: E402
    MockCohortSpec,
    build_mock_cohort_registry_rows,
    build_protected_write_guard_battery_rows,
    fingerprint_integrity_matrix,
)
from cninfo_c_class_dryrun_fingerprint_lineage_isolation import (  # noqa: E402
    fingerprint_isolation_matrix,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_frozen_mock_cohort_write_forbidden,
    assert_safe_erad_audit_write_path,
    fingerprint_isolated_snapshot_dryrun,
    is_allowed_mock_test_cleanup_path,
    load_frozen_mock_cohort_roots,
    resolve_frozen_mock_cohort_root_id,
)
from cninfo_c_class_dual_layer_ledger_resume_lineage import (  # noqa: E402
    fingerprint_lineage_matrix,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    fingerprint_status_csv,
    load_csv_rows,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)
from cninfo_c_class_nonseal_cross_fm_mock_cohort_extension import (  # noqa: E402
    ExtensionPaths as Fm13Paths,
    build_harvest_exclusion_consistency_rows as _fm13_harvest_rows,
    fingerprint_extension_matrix,
    load_json,
    load_protected_root_rows,
)
from cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM18_MOCK_ROOT_REL,
    default_nonseal_second_extension_cohort_specs,
)
from cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM19_MOCK_ROOT_REL,
    FROZEN_SECOND_EXTENSION_FP_SHA256,
)
from cninfo_c_class_nonseal_extension_controller_commit_boundary import (  # noqa: E402
    fingerprint_boundary_matrix,
)
from cninfo_c_class_nonseal_extension_human_decision_readiness_ledger import (  # noqa: E402
    fingerprint_ledger_matrix,
)
from cninfo_c_class_nonseal_extension_post_commit_drift_recheck import (  # noqa: E402
    fingerprint_drift_matrix,
)
from cninfo_c_class_nonseal_extension_post_commit_seal_attestation import (  # noqa: E402
    fingerprint_attestation_matrix,
)

TASK_ID = "C-FM-20"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm20_nonseal_cross_fm_mock_cohort_third_extension"
)

FM01_GATE_JSON_REL = (
    "outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json"
)
FM02_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json"
)
FM03_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json"
)
FM04_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json"
)
FM05_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.json"
)
FM12_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_dryrun_fingerprint_lineage_isolation_20260715.json"
)
FM13_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_cross_fm_mock_cohort_extension_20260715.json"
)
FM14_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_drift_recheck_20260715.json"
)
FM15_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_controller_commit_boundary_20260715.json"
)
FM16_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_seal_attestation_20260715.json"
)
FM17_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_human_decision_readiness_ledger_20260715.json"
)
FM18_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension_20260715.json"
)
FM19_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck_20260715.json"
)

HARVEST_863_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
)
FM03_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
)

# C-FM-18/19 冻结二次扩展链指纹（三次扩展零漂移锚点）
FROZEN_SECOND_EXTENSION_DRIFT_FP_SHA256 = (
    "fdcbffafc22a180d5d9d42dcb36e104bb650566b6fab3119885a6fd9c878284a"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK22"
FROZEN_ROOT_IDS_MUST_BLOCK = (
    "C-ROOT-MOCK3",
    "C-ROOT-MOCK4",
    "C-ROOT-MOCK5",
    "C-ROOT-MOCK6",
    "C-ROOT-MOCK7",
    "C-ROOT-MOCK8",
    "C-ROOT-MOCK9",
    "C-ROOT-MOCK10",
    "C-ROOT-MOCK11",
    "C-ROOT-MOCK12",
    "C-ROOT-MOCK13",
    "C-ROOT-MOCK14",
    "C-ROOT-MOCK15",
    "C-ROOT-MOCK16",
    "C-ROOT-MOCK17",
    "C-ROOT-MOCK18",
    "C-ROOT-MOCK19",
    "C-ROOT-MOCK20",
    "C-ROOT-MOCK21",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    "C-ROOT-AUTH1",
)

MATRIX_FIELDS = [
    "check_id",
    "layer",
    "cohort_id",
    "root_id",
    "path",
    "expected",
    "observed",
    "ok",
    "notes",
]

# 矩阵文件名与指纹 kind 映射
_MATRIX_FILE_BY_KIND = {
    "extension_matrix": "extension_matrix.csv",
    "drift_matrix": "drift_matrix.csv",
    "boundary_matrix": "boundary_matrix.csv",
    "attestation_matrix": "attestation_matrix.csv",
    "readiness_matrix": "readiness_matrix.csv",
    "integrity_matrix": "integrity_matrix.csv",
    "isolation_matrix": "isolation_matrix.csv",
    "lineage_matrix": "lineage_matrix.csv",
}


@dataclass(frozen=True)
class ThirdExtensionPaths:
    """只读输入与隔离写根路径规格（三次扩展）。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    fm12_gate_json_rel: str = FM12_GATE_JSON_REL
    fm13_gate_json_rel: str = FM13_GATE_JSON_REL
    fm14_gate_json_rel: str = FM14_GATE_JSON_REL
    fm15_gate_json_rel: str = FM15_GATE_JSON_REL
    fm16_gate_json_rel: str = FM16_GATE_JSON_REL
    fm17_gate_json_rel: str = FM17_GATE_JSON_REL
    fm18_gate_json_rel: str = FM18_GATE_JSON_REL
    fm19_gate_json_rel: str = FM19_GATE_JSON_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    fm03_mock_root_rel: str = FM03_MOCK_ROOT_REL
    output_root_rel: str = DEFAULT_MOCK_OUTPUT_ROOT_REL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str, *, base_dir: str = BASE_DIR) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, base_dir).replace("\\", "/")


def _abs(path: str, *, base_dir: str = BASE_DIR) -> str:
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(base_dir, path))


def _row(
    *,
    check_id: str,
    layer: str,
    cohort_id: str = "*",
    root_id: str = "",
    path: str = "",
    expected: str = "",
    observed: str = "",
    ok: bool = False,
    notes: str = "",
) -> Dict[str, str]:
    return {
        "check_id": check_id,
        "layer": layer,
        "cohort_id": cohort_id,
        "root_id": root_id,
        "path": path,
        "expected": expected,
        "observed": observed,
        "ok": "yes" if ok else "no",
        "notes": notes or ("ok" if ok else "fail"),
    }


def assert_fm20_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-20 写根：须 validation/_mock_*，不得覆盖 MOCK3–21，
    不得写权威 dual-layer 索引；允许本任务 MOCK22 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-20 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def default_nonseal_third_extension_cohort_specs() -> Tuple[MockCohortSpec, ...]:
    """三次扩展：二次扩展（FM-01..05+FM-12+FM-13..17）之上追加 FM-18..19。"""
    base = list(default_nonseal_second_extension_cohort_specs())
    base.extend(
        [
            MockCohortSpec(
                cohort_id="fm18_nonseal_cross_fm_mock_cohort_second_extension",
                root_rel=FM18_MOCK_ROOT_REL,
                root_id="C-ROOT-MOCK20",
                required_files=(
                    "extension_matrix.csv",
                    "extension_fingerprint.json",
                    "nonseal_mock_cohort_registry.json",
                    "fm_gate_battery.json",
                    "extension_packet.json",
                    "README.md",
                ),
                fingerprint_kind="extension_matrix",
                gate_json_rel=FM18_GATE_JSON_REL,
            ),
            MockCohortSpec(
                cohort_id="fm19_nonseal_second_extension_post_commit_drift_recheck",
                root_rel=FM19_MOCK_ROOT_REL,
                root_id="C-ROOT-MOCK21",
                required_files=(
                    "drift_matrix.csv",
                    "drift_fingerprint.json",
                    "drift_seal_packet.json",
                    "fm_gate_battery.json",
                    "README.md",
                ),
                fingerprint_kind="drift_matrix",
                gate_json_rel=FM19_GATE_JSON_REL,
            ),
        ]
    )
    return tuple(base)



def _expected_fingerprint_from_gate(
    spec: MockCohortSpec, gate: Dict[str, Any]
) -> Optional[str]:
    """从既有 gate JSON 提取期望指纹。"""
    if spec.fingerprint_kind == "dryrun":
        if spec.cohort_id.startswith("fm01"):
            runs = gate.get("runs") or []
            if runs:
                return str(runs[0].get("fingerprint_sha256") or "")
            return ""
        slice1 = gate.get("slice1_190") or {}
        fp = slice1.get("fingerprint") or {}
        return str(fp.get("fingerprint_sha256") or "")
    if spec.fingerprint_kind == "harvest_863":
        fp = gate.get("fingerprint_863") or {}
        return str(fp.get("fingerprint_sha256") or "")
    if spec.fingerprint_kind in (
        "lineage_matrix",
        "integrity_matrix",
        "isolation_matrix",
        "extension_matrix",
        "drift_matrix",
        "boundary_matrix",
        "attestation_matrix",
        "readiness_matrix",
    ):
        fp = gate.get("fingerprint") or {}
        return str(fp.get("fingerprint_sha256") or "")
    return None


def _recompute_fingerprint(
    spec: MockCohortSpec,
    *,
    harvest_863_status_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[str, str]:
    """只读重算指纹；不重跑 dry-run / 不写生产根。"""
    if spec.fingerprint_kind == "dryrun":
        fp = fingerprint_isolated_snapshot_dryrun(
            spec.root_rel,
            base_dir=base_dir,
            gate=spec.dryrun_gate_label,
            company_count=spec.expected_company_count,
        )
        return str(fp.get("fingerprint_sha256") or ""), "dryrun_recompute"
    if spec.fingerprint_kind == "harvest_863":
        path = _abs(harvest_863_status_rel, base_dir=base_dir)
        fp = fingerprint_status_csv(path)
        return str(fp.get("fingerprint_sha256") or ""), "harvest_863_recompute"
    matrix_name = _MATRIX_FILE_BY_KIND.get(spec.fingerprint_kind)
    if not matrix_name:
        return "", "none"
    matrix_path = _abs(os.path.join(spec.root_rel, matrix_name), base_dir=base_dir)
    rows = load_csv_rows(matrix_path)
    if spec.fingerprint_kind == "lineage_matrix":
        fp = fingerprint_lineage_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "lineage_matrix_recompute"
    if spec.fingerprint_kind == "integrity_matrix":
        fp = fingerprint_integrity_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "integrity_matrix_recompute"
    if spec.fingerprint_kind == "isolation_matrix":
        fp = fingerprint_isolation_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "isolation_matrix_recompute"
    if spec.fingerprint_kind == "extension_matrix":
        fp = fingerprint_extension_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "extension_matrix_recompute"
    if spec.fingerprint_kind == "drift_matrix":
        fp = fingerprint_drift_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "drift_matrix_recompute"
    if spec.fingerprint_kind == "boundary_matrix":
        fp = fingerprint_boundary_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "boundary_matrix_recompute"
    if spec.fingerprint_kind == "attestation_matrix":
        fp = fingerprint_attestation_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "attestation_matrix_recompute"
    if spec.fingerprint_kind == "readiness_matrix":
        fp = fingerprint_ledger_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "readiness_matrix_recompute"
    return "", "none"


def build_third_extension_fingerprint_chain_rows(
    specs: Sequence[MockCohortSpec],
    *,
    paths: ThirdExtensionPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """三次扩展指纹链：FM01–05 + FM12–19 与 gate JSON 对齐。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    for spec in specs:
        gate_path = _abs(spec.gate_json_rel, base_dir=base_dir)
        gate_exists = os.path.isfile(gate_path)
        gate: Dict[str, Any] = {}
        if gate_exists:
            gate = load_json(gate_path)
        expected = _expected_fingerprint_from_gate(spec, gate) if gate_exists else ""
        observed, detail = ("", "gate_missing")
        if gate_exists:
            observed, detail = _recompute_fingerprint(
                spec,
                harvest_863_status_rel=paths.harvest_863_status_rel,
                base_dir=base_dir,
            )
        ok = bool(expected) and bool(observed) and expected == observed
        check_id = f"fingerprint_chain_{spec.cohort_id}"
        rows.append(
            _row(
                check_id=check_id,
                layer="fingerprint_chain",
                cohort_id=spec.cohort_id,
                root_id=spec.root_id,
                path=spec.root_rel,
                expected=f"sha256={expected[:16] + '...' if expected else 'missing'}",
                observed=(
                    f"sha256={observed[:16] + '...' if observed else 'missing'};"
                    f"detail={detail};gate_exists={gate_exists}"
                ),
                ok=ok,
                notes="ok" if ok else "fingerprint_mismatch",
            )
        )
        checks[check_id] = ok

    all_ok = all(checks.values()) if checks else False
    rows.append(
        _row(
            check_id="fingerprint_chain_all_pass",
            layer="fingerprint_chain",
            expected="all_nonseal_fm_fingerprints_match_gate_json",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fingerprint_chain_incomplete",
        )
    )
    checks["fingerprint_chain_all_pass"] = all_ok
    return rows, checks


def build_nonseal_chain_anchor_rows(
    *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """nonseal-chain 连续性锚点：MOCK20 二次扩展 + MOCK21 二次漂移冻结指纹对齐。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    anchors = [
        (
            "anchor_second_extension_fp",
            f"{FM18_MOCK_ROOT_REL}/extension_fingerprint.json",
            FROZEN_SECOND_EXTENSION_FP_SHA256,
            "C-ROOT-MOCK20",
        ),
        (
            "anchor_second_extension_drift_fp",
            f"{FM19_MOCK_ROOT_REL}/drift_fingerprint.json",
            FROZEN_SECOND_EXTENSION_DRIFT_FP_SHA256,
            "C-ROOT-MOCK21",
        ),
    ]
    for check_id, rel, frozen, root_id in anchors:
        path = _abs(rel, base_dir=base_dir)
        present = os.path.isfile(path)
        observed = ""
        ok = False
        if present:
            payload = load_json(path)
            observed = str(
                (payload.get("fingerprint") or {}).get("fingerprint_sha256") or ""
            )
            ok = bool(observed) and observed == frozen
        checks[check_id] = ok
        rows.append(
            _row(
                check_id=check_id,
                layer="nonseal_chain_continuity",
                root_id=root_id,
                path=rel,
                expected=frozen,
                observed=observed or ("missing" if not present else "empty"),
                ok=ok,
                notes="ok" if ok else "anchor_drift",
            )
        )

    all_ok = all(checks.values()) if checks else False
    checks["nonseal_chain_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="nonseal_chain_continuity_all_pass",
            layer="nonseal_chain_continuity",
            expected="MOCK20-21_frozen_anchors_match",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "continuity_fail",
        )
    )
    return rows, checks


def build_frozen_mock_isolation_rows(
    paths: ThirdExtensionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–21 拒绝 · MOCK22 放行。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    load_frozen_mock_cohort_roots.cache_clear()
    frozen = dict(load_frozen_mock_cohort_roots(base_dir=base_dir))

    for root_id in FROZEN_ROOT_IDS_MUST_BLOCK:
        prefix = frozen.get(root_id)
        exists = prefix is not None
        refused = False
        if prefix:
            try:
                assert_frozen_mock_cohort_write_forbidden(
                    prefix, allow_root_ids=(), base_dir=base_dir
                )
            except RuntimeError as exc:
                refused = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
        ok = exists and refused
        checks[f"frozen_block_{root_id}"] = ok
        rows.append(
            _row(
                check_id=f"frozen_block_{root_id}",
                layer="frozen_mock_isolation",
                root_id=root_id,
                path=_rel(prefix, base_dir=base_dir) if prefix else "",
                expected="write_refused",
                observed=f"listed={exists};refused={refused}",
                ok=ok,
                notes="ok" if ok else "freeze_guard_gap",
            )
        )

    mock22_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock22_listed = mock22_prefix is not None
    mock22_allowed = False
    if mock22_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock22_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock22_allowed = True
        except RuntimeError:
            mock22_allowed = False
    checks["frozen_allow_mock22"] = mock22_listed and mock22_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock22",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=_rel(mock22_prefix, base_dir=base_dir) if mock22_prefix else "",
            expected="listed_and_allowed_when_in_allowlist",
            observed=f"listed={mock22_listed};allowed={mock22_allowed}",
            ok=mock22_listed and mock22_allowed,
            notes="ok" if mock22_listed and mock22_allowed else "mock22_allow_fail",
        )
    )

    out_ok = False
    out_detail = ""
    try:
        assert_fm20_output_root(paths.output_root_rel, base_dir=base_dir)
        out_ok = True
        out_detail = "allowed"
    except RuntimeError as exc:
        out_detail = str(exc)[:120]
    checks["frozen_output_root_allowed"] = out_ok
    rows.append(
        _row(
            check_id="frozen_output_root_allowed",
            layer="frozen_mock_isolation",
            path=paths.output_root_rel,
            expected="MOCK22_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
        )
    )

    # seal 根仍冻结（抽样 MOCK8）；不得因本任务而可写
    mock8 = frozen.get("C-ROOT-MOCK8")
    seal_still_frozen = False
    if mock8:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock8, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
            )
        except RuntimeError as exc:
            seal_still_frozen = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["seal_mock8_still_frozen"] = seal_still_frozen
    rows.append(
        _row(
            check_id="seal_mock8_still_frozen",
            layer="frozen_mock_isolation",
            root_id="C-ROOT-MOCK8",
            expected="seal_chain_not_writable_by_fm20",
            observed=f"refused={seal_still_frozen}",
            ok=seal_still_frozen,
            notes="ok" if seal_still_frozen else "seal_freeze_regressed",
        )
    )

    # 前序 nonseal 根 MOCK21 必须拒绝
    mock21 = frozen.get("C-ROOT-MOCK21")
    mock21_frozen = False
    if mock21:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock21, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
            )
        except RuntimeError as exc:
            mock21_frozen = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock21_still_frozen"] = mock21_frozen
    rows.append(
        _row(
            check_id="mock21_still_frozen",
            layer="frozen_mock_isolation",
            root_id="C-ROOT-MOCK21",
            expected="prior_nonseal_not_writable_by_fm20",
            observed=f"refused={mock21_frozen}",
            ok=mock21_frozen,
            notes="ok" if mock21_frozen else "mock21_freeze_regressed",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-21_blocked_MOCK22_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "frozen_isolation_fail",
        )
    )
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected CSV：MOCK3–22 + AUTH1 注册一致性。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    csv_rows = load_protected_root_rows(csv_rel, base_dir=base_dir)
    by_id = {str(r.get("root_id") or ""): r for r in csv_rows}

    for root_id in REQUIRED_PROTECTED_ROOT_IDS:
        present = root_id in by_id
        checks[f"protected_csv_has_{root_id}"] = present
        rows.append(
            _row(
                check_id=f"protected_csv_has_{root_id}",
                layer="protected_csv_registry",
                root_id=root_id,
                path=csv_rel,
                expected="listed_in_protected_csv",
                observed="present" if present else "missing",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )

    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_ok = (auth.get("write_policy") or "") == "read_only_no_overwrite"
    checks["protected_csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="protected_csv_auth1_readonly",
            layer="protected_csv_registry",
            root_id="C-ROOT-AUTH1",
            expected="write_policy=read_only_no_overwrite",
            observed=str(auth.get("write_policy") or ""),
            ok=auth_ok,
            notes="ok" if auth_ok else "auth_policy_drift",
        )
    )

    mock22 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock22_path = (mock22.get("path_pattern") or "").strip().rstrip("/")
    expected_path = DEFAULT_MOCK_OUTPUT_ROOT_REL
    mock22_ok = mock22_path.endswith(
        "_mock_c_fm20_nonseal_cross_fm_mock_cohort_third_extension"
    ) or mock22_path == expected_path
    checks["protected_csv_mock22_path"] = mock22_ok
    rows.append(
        _row(
            check_id="protected_csv_mock22_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            path=mock22_path,
            expected=expected_path,
            observed=mock22_path or "missing",
            ok=mock22_ok,
            notes="ok" if mock22_ok else "mock22_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-22+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *,
    gates: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..19 既有 gate 只读聚合（跳过 seal FM06–11）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    specs = [
        ("fm01_isolated_dryrun_repro", "fm01"),
        ("fm02_isolated_validation_cohorts", "fm02"),
        ("fm03_harvest_exclusion_dual_layer", "fm03"),
        ("fm04_ledger_resume_lineage", "fm04"),
        ("fm05_cross_fm_mock_cohort_integrity", "fm05"),
        ("fm12_dryrun_fingerprint_lineage_isolation", "fm12"),
        ("fm13_nonseal_cross_fm_mock_cohort_extension", "fm13"),
        ("fm14_nonseal_extension_post_commit_drift_recheck", "fm14"),
        ("fm15_nonseal_extension_controller_commit_boundary", "fm15"),
        ("fm16_nonseal_extension_post_commit_seal_attestation", "fm16"),
        ("fm17_nonseal_extension_human_decision_readiness_ledger", "fm17"),
        ("fm18_nonseal_cross_fm_mock_cohort_second_extension", "fm18"),
        ("fm19_nonseal_second_extension_post_commit_drift_recheck", "fm19"),
    ]
    for check_id, key in specs:
        payload = gates[key]
        gate = str(payload.get("gate") or "").strip()
        cninfo = payload.get("cninfo_calls", None)
        execute = payload.get("execute_production_snapshot_rebuild", None)
        ok = gate == "PASS_OFFLINE" and cninfo == 0 and execute is False
        if key in ("fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19"):
            if "seal_chain_extended" in payload:
                ok = ok and payload.get("seal_chain_extended") is False
        rows.append(
            _row(
                check_id=check_id,
                layer="fm_gate_battery",
                cohort_id=key,
                expected="gate=PASS_OFFLINE;cninfo=0;execute=false",
                observed=f"gate={gate};cninfo={cninfo};execute={execute}",
                ok=ok,
                notes="ok" if ok else "prior_fm_gate_not_pass",
            )
        )
        checks[check_id] = ok

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="fm01_05_12_19_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_19_battery_all_pass"] = all_ok
    return rows, checks


def write_extension_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in MATRIX_FIELDS})


def fingerprint_third_extension_matrix(
    rows: Sequence[Dict[str, str]],
) -> Dict[str, Any]:
    """三次扩展完整性矩阵结构指纹。"""
    ok_count = sum(1 for r in rows if r.get("ok") == "yes")
    fail_count = sum(1 for r in rows if r.get("ok") != "yes")
    layers: Dict[str, int] = {}
    for r in rows:
        layer = str(r.get("layer") or "")
        layers[layer] = layers.get(layer, 0) + 1
    canon = json.dumps(
        {
            "row_count": len(rows),
            "ok_count": ok_count,
            "fail_count": fail_count,
            "layers": dict(sorted(layers.items())),
            "check_ids": [str(r.get("check_id") or "") for r in rows],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return {
        "row_count": len(rows),
        "ok_count": ok_count,
        "fail_count": fail_count,
        "layers": layers,
        "fingerprint_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
    }


def run_nonseal_cross_fm_mock_cohort_third_extension(
    *,
    paths: ThirdExtensionPaths = ThirdExtensionPaths(),
    cohort_specs: Optional[Sequence[MockCohortSpec]] = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-20 非 seal Cross-FM mock cohort 三次扩展 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_fm20_output_root(paths.output_root_rel, base_dir=base_dir)
    specs = (
        tuple(cohort_specs)
        if cohort_specs is not None
        else default_nonseal_third_extension_cohort_specs()
    )

    gates = {
        "fm01": load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir)),
        "fm02": load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir)),
        "fm03": load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir)),
        "fm04": load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir)),
        "fm05": load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir)),
        "fm12": load_json(_abs(paths.fm12_gate_json_rel, base_dir=base_dir)),
        "fm13": load_json(_abs(paths.fm13_gate_json_rel, base_dir=base_dir)),
        "fm14": load_json(_abs(paths.fm14_gate_json_rel, base_dir=base_dir)),
        "fm15": load_json(_abs(paths.fm15_gate_json_rel, base_dir=base_dir)),
        "fm16": load_json(_abs(paths.fm16_gate_json_rel, base_dir=base_dir)),
        "fm17": load_json(_abs(paths.fm17_gate_json_rel, base_dir=base_dir)),
        "fm18": load_json(_abs(paths.fm18_gate_json_rel, base_dir=base_dir)),
        "fm19": load_json(_abs(paths.fm19_gate_json_rel, base_dir=base_dir)),
    }

    # 复用 FM13 harvest 路径规格（仅用其 harvest 层；不写其根）
    fm13_paths = Fm13Paths(
        fm03_gate_json_rel=paths.fm03_gate_json_rel,
        harvest_863_status_rel=paths.harvest_863_status_rel,
        fm03_mock_root_rel=paths.fm03_mock_root_rel,
        output_root_rel=paths.output_root_rel,
    )

    reg_rows, reg_checks = build_mock_cohort_registry_rows(specs, base_dir=base_dir)
    # 将 registry 层名统一为 nonseal_cohort_registry（二次扩展语义）
    for r in reg_rows:
        if r.get("layer") == "mock_cohort_registry":
            r["layer"] = "nonseal_cohort_registry"
    fp_rows, fp_checks = build_third_extension_fingerprint_chain_rows(
        specs, paths=paths, base_dir=base_dir
    )
    anc_rows, anc_checks = build_nonseal_chain_anchor_rows(base_dir=base_dir)
    fr_rows, fr_checks = build_frozen_mock_isolation_rows(paths, base_dir=base_dir)
    he_rows, he_checks = _fm13_harvest_rows(fm13_paths, base_dir=base_dir)
    wg_rows, wg_checks = build_protected_write_guard_battery_rows(
        mock_probe_rel=paths.output_root_rel, base_dir=base_dir
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)

    matrix = (
        reg_rows
        + fp_rows
        + anc_rows
        + fr_rows
        + he_rows
        + wg_rows
        + csv_rows
        + bat_rows
    )
    layer_gates = {
        "nonseal_cohort_registry": (
            "PASS_OFFLINE"
            if all(reg_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "fingerprint_chain": (
            "PASS_OFFLINE" if all(fp_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "nonseal_chain_continuity": (
            "PASS_OFFLINE" if all(anc_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "frozen_mock_isolation": (
            "PASS_OFFLINE" if all(fr_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "harvest_exclusion_consistency": (
            "PASS_OFFLINE" if all(he_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "protected_write_guard": (
            "PASS_OFFLINE" if all(wg_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "protected_csv_registry": (
            "PASS_OFFLINE" if all(csv_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
    }
    overall = (
        "PASS_OFFLINE"
        if all(g == "PASS_OFFLINE" for g in layer_gates.values())
        else "FAIL_REVIEW_REQUIRED"
    )

    os.makedirs(out_root, exist_ok=True)
    matrix_path = os.path.join(out_root, "extension_matrix.csv")
    write_extension_matrix_csv(matrix, matrix_path)
    fp = fingerprint_third_extension_matrix(matrix)
    fp_path = os.path.join(out_root, "extension_fingerprint.json")
    assert_safe_erad_audit_write_path(
        fp_path,
        base_dir=base_dir,
        allowed_audit_root_rel=paths.output_root_rel,
    )
    with open(fp_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
                "seal_chain_extended": False,
                "frozen_second_extension_fp_sha256": FROZEN_SECOND_EXTENSION_FP_SHA256,
                "frozen_second_extension_drift_fp_sha256": FROZEN_SECOND_EXTENSION_DRIFT_FP_SHA256,
                "fingerprint": fp,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    registry_path = os.path.join(out_root, "nonseal_mock_cohort_registry.json")
    with open(registry_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "seal_chain_extended": False,
                "cohort_count": len(specs),
                "cohorts": [
                    {
                        "cohort_id": s.cohort_id,
                        "root_rel": s.root_rel,
                        "root_id": s.root_id,
                        "required_files": list(s.required_files),
                        "fingerprint_kind": s.fingerprint_kind,
                        "gate_json_rel": s.gate_json_rel,
                    }
                    for s in specs
                ],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    battery_path = os.path.join(out_root, "fm_gate_battery.json")
    with open(battery_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "gate": overall,
                "layer_gates": layer_gates,
                "fm01_gate": gates["fm01"].get("gate"),
                "fm02_gate": gates["fm02"].get("gate"),
                "fm03_gate": gates["fm03"].get("gate"),
                "fm04_gate": gates["fm04"].get("gate"),
                "fm05_gate": gates["fm05"].get("gate"),
                "fm12_gate": gates["fm12"].get("gate"),
                "fm13_gate": gates["fm13"].get("gate"),
                "fm14_gate": gates["fm14"].get("gate"),
                "fm15_gate": gates["fm15"].get("gate"),
                "fm16_gate": gates["fm16"].get("gate"),
                "fm17_gate": gates["fm17"].get("gate"),
                "fm18_gate": gates["fm18"].get("gate"),
                "fm19_gate": gates["fm19"].get("gate"),
                "cninfo_calls": 0,
                "seal_chain_extended": False,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    packet_path = os.path.join(out_root, "extension_packet.json")
    with open(packet_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "gate": overall,
                "capability": [
                    "nonseal_cross_fm_mock_cohort_third_extension",
                    "fingerprint_chain_fm01_05_12_19",
                    "nonseal_chain_continuity_mock20_21",
                    "frozen_mock_cohort_write_isolation_mock3_21",
                    "harvest_exclusion_dual_layer_consistency",
                    "protected_output_root_mock22",
                ],
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
                "approved_for_snapshot_rebuild": False,
                "ready_for_execute": False,
                "hold_recommendation": "KEEP_EXECUTE_FALSE",
                "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
                "idle_not_required_while_awaiting": True,
                "seal_chain_extended": False,
                "notes": (
                    "本包在 C-FM-19 commit 后做 non-seal 三次 cohort 完整性扩展："
                    "FM01-05+FM12-19 注册表 · MOCK20-21 锚点零漂移 · MOCK3-21 写隔离 · "
                    "MOCK22 保护根；不新增 seal/decision-await/commit-boundary 层；"
                    "不覆盖 MOCK3-21；不翻转 approved_for_snapshot_rebuild；"
                    "生产 snapshot EXECUTE 仍须独立人批；本 executor 不 commit/push。"
                ),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    out_rel = _rel(out_root, base_dir=base_dir)
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "layer_gates": layer_gates,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "seal_chain_extended": False,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "cohort_count": len(specs),
        "output_root": out_rel,
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "registry_path": _rel(registry_path, base_dir=base_dir),
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "packet_path": _rel(packet_path, base_dir=base_dir),
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
        "frozen_second_extension_drift_fp_sha256": FROZEN_SECOND_EXTENSION_DRIFT_FP_SHA256,
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "fm05_gate_json": paths.fm05_gate_json_rel,
            "fm12_gate_json": paths.fm12_gate_json_rel,
            "fm13_gate_json": paths.fm13_gate_json_rel,
            "fm14_gate_json": paths.fm14_gate_json_rel,
            "fm15_gate_json": paths.fm15_gate_json_rel,
            "fm16_gate_json": paths.fm16_gate_json_rel,
            "fm17_gate_json": paths.fm17_gate_json_rel,
            "fm18_gate_json": paths.fm18_gate_json_rel,
            "fm19_gate_json": paths.fm19_gate_json_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
            "harvest_863_status": paths.harvest_863_status_rel,
        },
    }

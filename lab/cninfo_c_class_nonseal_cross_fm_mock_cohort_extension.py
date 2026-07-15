"""
CNINFO C-class — 非 seal-chain Cross-FM mock cohort 完整性扩展（离线 · C-FM-13）。

在 C-FM-12（dry-run fingerprint lineage isolation）已 commit 且 EXECUTE 仍 human-held 之上，
补齐非 seal 能力（不新增 MOCK seal 层）：
  1) 非 seal mock cohort 注册表：FM-01..05 + FM-12（存在 · 隔离 · 必要产物）
  2) 指纹链只读核验：含 FM-05 integrity / FM-12 isolation 矩阵指纹（不重跑 dry-run）
  3) 冻结 mock 写隔离：MOCK3–14 拒绝；本任务 MOCK15 / ephemeral 放行
  4) harvest/exclusion dual-layer 一致性交叉指纹（FM-03）
  5) FM-01..05 + FM-12 gate battery 只读聚合
  6) protected_output_roots.csv 注册一致性（含 MOCK15）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–14 / 权威 dual-layer 索引 ·
verified 声称 · 翻转 approved_for_snapshot_rebuild · 扩展 seal-chain。
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
    default_mock_cohort_specs,
    fingerprint_integrity_matrix,
)
from cninfo_c_class_dryrun_fingerprint_lineage_isolation import (  # noqa: E402
    fingerprint_isolation_matrix,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
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

TASK_ID = "C-FM-13"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm13_nonseal_cross_fm_mock_cohort_extension"
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

FM02_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
)
FM03_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
)
FM04_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage"
)
FM05_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm05_cross_fm_mock_cohort_integrity"
)
FM12_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm12_dryrun_fingerprint_lineage_isolation"
)

HARVEST_863_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK15"
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


@dataclass(frozen=True)
class ExtensionPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    fm12_gate_json_rel: str = FM12_GATE_JSON_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    fm03_mock_root_rel: str = FM03_MOCK_ROOT_REL
    fm04_mock_root_rel: str = FM04_MOCK_ROOT_REL
    fm05_mock_root_rel: str = FM05_MOCK_ROOT_REL
    fm12_mock_root_rel: str = FM12_MOCK_ROOT_REL
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


def assert_fm13_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-13 写根：须 validation/_mock_*，不得覆盖 MOCK3–14，
    不得写权威 dual-layer 索引；允许本任务 MOCK15 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-13 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is None:
        # ephemeral：仍须拒绝权威索引以外的非 mock（已由 isolation assert 覆盖）
        pass
    else:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_protected_root_rows(
    csv_rel: str = PROTECTED_ROOTS_CSV_REL, *, base_dir: str = BASE_DIR
) -> List[Dict[str, str]]:
    path = _abs(csv_rel, base_dir=base_dir)
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def default_nonseal_cohort_specs() -> Tuple[MockCohortSpec, ...]:
    """非 seal mock cohort：FM-01..04（FM05 既有）+ FM-05 + FM-12。"""
    base = list(default_mock_cohort_specs())
    base.extend(
        [
            MockCohortSpec(
                cohort_id="fm05_cross_fm_mock_cohort_integrity",
                root_rel=FM05_MOCK_ROOT_REL,
                root_id="C-ROOT-MOCK7",
                required_files=(
                    "integrity_matrix.csv",
                    "integrity_fingerprint.json",
                    "mock_cohort_registry.json",
                    "fm_gate_battery.json",
                    "README.md",
                ),
                fingerprint_kind="integrity_matrix",
                gate_json_rel=FM05_GATE_JSON_REL,
            ),
            MockCohortSpec(
                cohort_id="fm12_dryrun_fingerprint_lineage_isolation",
                root_rel=FM12_MOCK_ROOT_REL,
                root_id="C-ROOT-MOCK14",
                required_files=(
                    "isolation_matrix.csv",
                    "isolation_fingerprint.json",
                    "fm_gate_battery.json",
                    "lineage_isolation_packet.json",
                    "README.md",
                ),
                fingerprint_kind="isolation_matrix",
                gate_json_rel=FM12_GATE_JSON_REL,
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
    if spec.fingerprint_kind == "lineage_matrix":
        fp = gate.get("fingerprint") or {}
        return str(fp.get("fingerprint_sha256") or "")
    if spec.fingerprint_kind in ("integrity_matrix", "isolation_matrix"):
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
    if spec.fingerprint_kind == "lineage_matrix":
        matrix_path = _abs(
            os.path.join(spec.root_rel, "lineage_matrix.csv"), base_dir=base_dir
        )
        rows = load_csv_rows(matrix_path)
        fp = fingerprint_lineage_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "lineage_matrix_recompute"
    if spec.fingerprint_kind == "integrity_matrix":
        matrix_path = _abs(
            os.path.join(spec.root_rel, "integrity_matrix.csv"), base_dir=base_dir
        )
        rows = load_csv_rows(matrix_path)
        fp = fingerprint_integrity_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "integrity_matrix_recompute"
    if spec.fingerprint_kind == "isolation_matrix":
        matrix_path = _abs(
            os.path.join(spec.root_rel, "isolation_matrix.csv"), base_dir=base_dir
        )
        rows = load_csv_rows(matrix_path)
        fp = fingerprint_isolation_matrix(rows)
        return str(fp.get("fingerprint_sha256") or ""), "isolation_matrix_recompute"
    return "", "none"


def build_extended_fingerprint_chain_rows(
    specs: Sequence[MockCohortSpec],
    *,
    paths: ExtensionPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """扩展指纹链：FM01–05 + FM12 与 gate JSON 对齐。"""
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


def build_frozen_mock_isolation_rows(
    paths: ExtensionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离 battery：MOCK3–14 拒绝 · MOCK15 放行。"""
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

    mock15_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock15_listed = mock15_prefix is not None
    mock15_allowed = False
    if mock15_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock15_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock15_allowed = True
        except RuntimeError:
            mock15_allowed = False
    checks["frozen_allow_mock15"] = mock15_listed and mock15_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock15",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=_rel(mock15_prefix, base_dir=base_dir) if mock15_prefix else "",
            expected="listed_and_allowed_when_in_allowlist",
            observed=f"listed={mock15_listed};allowed={mock15_allowed}",
            ok=mock15_listed and mock15_allowed,
            notes="ok" if mock15_listed and mock15_allowed else "mock15_allow_fail",
        )
    )

    # 本任务写根：若已登记为 MOCK15 则放行；ephemeral 亦放行
    out_abs = _abs(paths.output_root_rel, base_dir=base_dir)
    out_ok = False
    out_detail = ""
    try:
        assert_fm13_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK15_or_ephemeral_allowed",
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
            expected="seal_chain_not_writable_by_fm13",
            observed=f"refused={seal_still_frozen}",
            ok=seal_still_frozen,
            notes="ok" if seal_still_frozen else "seal_freeze_regressed",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-14_blocked_MOCK15_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "frozen_isolation_fail",
        )
    )
    return rows, checks


def build_harvest_exclusion_consistency_rows(
    paths: ExtensionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """harvest/exclusion dual-layer 一致性：FM-03 指纹 + gate + mock 产物。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm03_expected = str(
        (fm03.get("fingerprint_863") or {}).get("fingerprint_sha256") or ""
    )
    harvest_fp = fingerprint_status_csv(
        _abs(paths.harvest_863_status_rel, base_dir=base_dir)
    )
    fm03_obs = str(harvest_fp.get("fingerprint_sha256") or "")
    fm03_ok = bool(fm03_expected) and fm03_expected == fm03_obs
    checks["harvest_excl_fm03_fingerprint"] = fm03_ok
    rows.append(
        _row(
            check_id="harvest_excl_fm03_fingerprint",
            layer="harvest_exclusion_consistency",
            cohort_id="fm03_harvest_exclusion",
            root_id="C-ROOT-MOCK5",
            path=paths.harvest_863_status_rel,
            expected=fm03_expected[:16] + "…" if fm03_expected else "missing",
            observed=fm03_obs[:16] + "…" if fm03_obs else "missing",
            ok=fm03_ok,
            notes="ok" if fm03_ok else "harvest_863_drift",
        )
    )

    gate_ok = (
        fm03.get("gate") == "PASS_OFFLINE"
        and int(fm03.get("cninfo_calls") or 0) == 0
        and not fm03.get("execute_production_snapshot_rebuild")
    )
    checks["harvest_excl_fm03_gate"] = gate_ok
    rows.append(
        _row(
            check_id="harvest_excl_fm03_gate",
            layer="harvest_exclusion_consistency",
            cohort_id="fm03",
            expected="PASS_OFFLINE cninfo=0 no_execute",
            observed=(
                f"gate={fm03.get('gate')};cninfo={fm03.get('cninfo_calls')};"
                f"exec={fm03.get('execute_production_snapshot_rebuild')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "gate_regressed",
        )
    )

    matrix_abs = _abs(
        os.path.join(paths.fm03_mock_root_rel, "consistency_matrix.csv"),
        base_dir=base_dir,
    )
    matrix_ok = os.path.isfile(matrix_abs)
    checks["harvest_excl_fm03_matrix_present"] = matrix_ok
    rows.append(
        _row(
            check_id="harvest_excl_fm03_matrix_present",
            layer="harvest_exclusion_consistency",
            cohort_id="fm03_harvest_exclusion",
            root_id="C-ROOT-MOCK5",
            path=os.path.join(paths.fm03_mock_root_rel, "consistency_matrix.csv"),
            expected="consistency_matrix.csv present",
            observed="present" if matrix_ok else "missing",
            ok=matrix_ok,
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["harvest_exclusion_consistency_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="harvest_exclusion_consistency_all_pass",
            layer="harvest_exclusion_consistency",
            expected="fm03_harvest_exclusion_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "harvest_exclusion_fail",
        )
    )
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected CSV：MOCK3–15 + AUTH1 注册一致性。"""
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

    mock15 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock15_path = (mock15.get("path_pattern") or "").strip().rstrip("/")
    expected_path = DEFAULT_MOCK_OUTPUT_ROOT_REL
    mock15_ok = mock15_path.endswith(
        "_mock_c_fm13_nonseal_cross_fm_mock_cohort_extension"
    ) or mock15_path == expected_path
    checks["protected_csv_mock15_path"] = mock15_ok
    rows.append(
        _row(
            check_id="protected_csv_mock15_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            path=mock15_path,
            expected=expected_path,
            observed=mock15_path or "missing",
            ok=mock15_ok,
            notes="ok" if mock15_ok else "mock15_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-15+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
    fm05: Dict[str, Any],
    fm12: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12 既有 gate 只读聚合（跳过 seal FM06–11）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    specs = [
        ("fm01_isolated_dryrun_repro", fm01),
        ("fm02_isolated_validation_cohorts", fm02),
        ("fm03_harvest_exclusion_dual_layer", fm03),
        ("fm04_ledger_resume_lineage", fm04),
        ("fm05_cross_fm_mock_cohort_integrity", fm05),
        ("fm12_dryrun_fingerprint_lineage_isolation", fm12),
    ]
    for check_id, payload in specs:
        gate = str(payload.get("gate") or "").strip()
        cninfo = payload.get("cninfo_calls", None)
        execute = payload.get("execute_production_snapshot_rebuild", None)
        ok = gate == "PASS_OFFLINE" and cninfo == 0 and execute is False
        # FM-12 额外要求 seal_chain_extended=false（若字段存在）
        if check_id.startswith("fm12") and "seal_chain_extended" in payload:
            ok = ok and payload.get("seal_chain_extended") is False
        rows.append(
            _row(
                check_id=check_id,
                layer="fm_gate_battery",
                cohort_id=check_id.split("_", 1)[0],
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
            check_id="fm01_05_12_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_battery_all_pass"] = all_ok
    return rows, checks


def write_extension_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in MATRIX_FIELDS})


def fingerprint_extension_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """扩展完整性矩阵结构指纹。"""
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


def run_nonseal_cross_fm_mock_cohort_extension(
    *,
    paths: ExtensionPaths = ExtensionPaths(),
    cohort_specs: Optional[Sequence[MockCohortSpec]] = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-13 非 seal Cross-FM mock cohort 扩展 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_fm13_output_root(paths.output_root_rel, base_dir=base_dir)
    specs = (
        tuple(cohort_specs)
        if cohort_specs is not None
        else default_nonseal_cohort_specs()
    )

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))
    fm12 = load_json(_abs(paths.fm12_gate_json_rel, base_dir=base_dir))

    reg_rows, reg_checks = build_mock_cohort_registry_rows(specs, base_dir=base_dir)
    fp_rows, fp_checks = build_extended_fingerprint_chain_rows(
        specs, paths=paths, base_dir=base_dir
    )
    fr_rows, fr_checks = build_frozen_mock_isolation_rows(paths, base_dir=base_dir)
    he_rows, he_checks = build_harvest_exclusion_consistency_rows(
        paths, base_dir=base_dir
    )
    # 复用 FM05 生产写守卫 battery（mock 探针指向本任务根）
    wg_rows, wg_checks = build_protected_write_guard_battery_rows(
        mock_probe_rel=paths.output_root_rel, base_dir=base_dir
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    bat_rows, bat_checks = build_fm_gate_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04, fm05=fm05, fm12=fm12
    )

    matrix = (
        reg_rows + fp_rows + fr_rows + he_rows + wg_rows + csv_rows + bat_rows
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
    fp = fingerprint_extension_matrix(matrix)
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
                "fm01_gate": fm01.get("gate"),
                "fm02_gate": fm02.get("gate"),
                "fm03_gate": fm03.get("gate"),
                "fm04_gate": fm04.get("gate"),
                "fm05_gate": fm05.get("gate"),
                "fm12_gate": fm12.get("gate"),
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
                    "nonseal_cross_fm_mock_cohort_registry_extension",
                    "fingerprint_chain_fm01_05_12",
                    "frozen_mock_cohort_write_isolation_mock3_14",
                    "harvest_exclusion_dual_layer_consistency",
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
                    "non-seal-chain offline QA extension; "
                    "EXECUTE remains human-held; does not overwrite MOCK3-14"
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
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "fm05_gate_json": paths.fm05_gate_json_rel,
            "fm12_gate_json": paths.fm12_gate_json_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
            "harvest_863_status": paths.harvest_863_status_rel,
            "fm03_mock_root": paths.fm03_mock_root_rel,
            "fm05_mock_root": paths.fm05_mock_root_rel,
            "fm12_mock_root": paths.fm12_mock_root_rel,
        },
    }

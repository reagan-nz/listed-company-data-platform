"""
CNINFO C-class — Cross-FM mock cohort 完整性 + 保护根写守卫 battery（离线 · C-FM-05）。

在 C-FM-04（ledger↔resume lineage + 权威索引写隔离）之上，补齐：
  1) mock cohort 注册表：FM-01..04 隔离根存在性 · 隔离前缀 · 必要产物
  2) 指纹链只读核验：dry-run / 863 ledger / lineage 矩阵与既有 gate JSON 对齐（不重跑 dry-run）
  3) 保护根写守卫 battery：harvest / snapshot / 权威 dual-layer 拒绝；mock 放行
  4) FM-01..04 gate battery 只读聚合（含 FM-04）
  5) protected_output_roots.csv 注册一致性（MOCK3–6 · AUTH1 · MOCK7）

禁止：CNINFO live · production EXECUTE · 覆盖权威 dual-layer 索引 · verified 声称。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cninfo_c_class_dual_layer_ledger_resume_lineage import (  # noqa: E402
    fingerprint_lineage_matrix,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    CLEANUP_REFUSED_MSG,
    DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
    DUAL_LAYER_INDEX_WRITE_FORBIDDEN,
    PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_safe_c_class_snapshot_dryrun_write_root,
    assert_safe_erad_audit_write_path,
    fingerprint_isolated_snapshot_dryrun,
    is_allowed_mock_test_cleanup_path,
    is_protected_c_class_production_root,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    fingerprint_status_csv,
    load_csv_rows,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)

TASK_ID = "C-FM-05"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm05_cross_fm_mock_cohort_integrity"
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

FM02_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
)
FM03_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
)
FM04_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage"
)

HARVEST_863_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
)
HARVEST_SLICE1_REL = "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
SNAPSHOT_FULL_REL = "outputs/snapshot/cninfo_c_class/full"

# protected CSV 必须登记的 mock / 权威根
REQUIRED_PROTECTED_ROOT_IDS = (
    "C-ROOT-MOCK3",
    "C-ROOT-MOCK4",
    "C-ROOT-MOCK5",
    "C-ROOT-MOCK6",
    "C-ROOT-MOCK7",
    "C-ROOT-AUTH1",
)

INTEGRITY_MATRIX_FIELDS = [
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
class MockCohortSpec:
    """单个 FM mock cohort 注册规格。"""

    cohort_id: str
    root_rel: str
    root_id: str
    required_files: Tuple[str, ...]
    fingerprint_kind: str  # dryrun | lineage_matrix | harvest_863 | none
    gate_json_rel: str
    expected_company_count: Optional[int] = None
    dryrun_gate_label: str = "PASS_WITH_CAVEAT"


@dataclass(frozen=True)
class IntegrityPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    output_root_rel: str = DEFAULT_MOCK_OUTPUT_ROOT_REL


def default_mock_cohort_specs() -> Tuple[MockCohortSpec, ...]:
    """FM-01..04 mock cohort 注册表。"""
    return (
        MockCohortSpec(
            cohort_id="fm01_standard_isolated_dryrun",
            root_rel=DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
            root_id="C-ROOT-MOCK3",
            required_files=(
                "quality/company_snapshot_status.csv",
                "quality/company_snapshot_error.csv",
                "dryrun_report.csv",
                "dryrun_summary.md",
            ),
            fingerprint_kind="dryrun",
            gate_json_rel=FM01_GATE_JSON_REL,
            expected_company_count=863,
        ),
        MockCohortSpec(
            cohort_id="fm02_slice1_190_validation",
            root_rel=FM02_MOCK_ROOT_REL,
            root_id="C-ROOT-MOCK4",
            required_files=(
                "quality/company_snapshot_status.csv",
                "dryrun_report.csv",
                "dryrun_summary.md",
                "filtered_universe_included.yaml",
                "cohort_lineage_matrix.csv",
            ),
            fingerprint_kind="dryrun",
            gate_json_rel=FM02_GATE_JSON_REL,
            expected_company_count=190,
        ),
        MockCohortSpec(
            cohort_id="fm03_harvest_exclusion_consistency",
            root_rel=FM03_MOCK_ROOT_REL,
            root_id="C-ROOT-MOCK5",
            required_files=(
                "consistency_matrix.csv",
                "harvest_863_structural_fingerprint.json",
                "README.md",
            ),
            fingerprint_kind="harvest_863",
            gate_json_rel=FM03_GATE_JSON_REL,
        ),
        MockCohortSpec(
            cohort_id="fm04_ledger_resume_lineage",
            root_rel=FM04_MOCK_ROOT_REL,
            root_id="C-ROOT-MOCK6",
            required_files=(
                "lineage_matrix.csv",
                "lineage_fingerprint.json",
                "fm_gate_battery.json",
                "README.md",
            ),
            fingerprint_kind="lineage_matrix",
            gate_json_rel=FM04_GATE_JSON_REL,
        ),
    )


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


def assert_integrity_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """完整性产物写根：必须 validation/_mock_*，并拒绝权威 dual-layer 索引根。"""
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
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


def build_mock_cohort_registry_rows(
    specs: Sequence[MockCohortSpec],
    *,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """mock cohort 注册表：存在 · 隔离 · 必要产物。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    for spec in specs:
        root_abs = _abs(spec.root_rel, base_dir=base_dir)
        exists = os.path.isdir(root_abs)
        isolated = is_allowed_mock_test_cleanup_path(root_abs, base_dir=base_dir)
        missing = [
            rel
            for rel in spec.required_files
            if not os.path.isfile(os.path.join(root_abs, rel))
        ]
        ok = exists and isolated and not missing
        check_id = f"cohort_registry_{spec.cohort_id}"
        rows.append(
            _row(
                check_id=check_id,
                layer="mock_cohort_registry",
                cohort_id=spec.cohort_id,
                root_id=spec.root_id,
                path=spec.root_rel,
                expected="exists;isolated_mock;required_files",
                observed=(
                    f"exists={exists};isolated={isolated};"
                    f"missing={','.join(missing) or 'none'}"
                ),
                ok=ok,
                notes="ok" if ok else "cohort_registry_incomplete",
            )
        )
        checks[check_id] = ok

        # 不得把 mock 根误判为生产保护根
        prod_leak = is_protected_c_class_production_root(root_abs, base_dir=base_dir)
        leak_id = f"cohort_not_production_{spec.cohort_id}"
        rows.append(
            _row(
                check_id=leak_id,
                layer="mock_cohort_registry",
                cohort_id=spec.cohort_id,
                root_id=spec.root_id,
                path=spec.root_rel,
                expected="not_classified_as_production",
                observed=f"is_production={prod_leak}",
                ok=not prod_leak,
                notes="ok" if not prod_leak else "mock_classified_as_production",
            )
        )
        checks[leak_id] = not prod_leak

    all_ok = all(checks.values()) if checks else False
    rows.append(
        _row(
            check_id="mock_cohort_registry_all_pass",
            layer="mock_cohort_registry",
            expected="all_registered_cohorts_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "registry_incomplete",
        )
    )
    checks["mock_cohort_registry_all_pass"] = all_ok
    return rows, checks


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
        # fm02：嵌套在 slice1_190.fingerprint
        slice1 = gate.get("slice1_190") or {}
        fp = slice1.get("fingerprint") or {}
        return str(fp.get("fingerprint_sha256") or "")
    if spec.fingerprint_kind == "harvest_863":
        fp = gate.get("fingerprint_863") or {}
        return str(fp.get("fingerprint_sha256") or "")
    if spec.fingerprint_kind == "lineage_matrix":
        fp = gate.get("fingerprint") or {}
        return str(fp.get("fingerprint_sha256") or "")
    return None


def _recompute_fingerprint(
    spec: MockCohortSpec,
    *,
    harvest_863_status_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[str, str]:
    """
    只读重算指纹；返回 (sha256, detail)。
    不重跑 dry-run / 不写生产根。
    """
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
    return "", "none"


def build_fingerprint_chain_rows(
    specs: Sequence[MockCohortSpec],
    *,
    paths: IntegrityPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """指纹链：重算与 gate JSON 对齐。"""
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
            expected="all_fm_fingerprints_match_gate_json",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fingerprint_chain_incomplete",
        )
    )
    checks["fingerprint_chain_all_pass"] = all_ok
    return rows, checks


def build_protected_write_guard_battery_rows(
    *,
    mock_probe_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """保护根写守卫 battery：生产拒绝 · mock 放行。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    # 1) harvest slice1 审计写拒绝
    harvest_probe = os.path.join(HARVEST_SLICE1_REL, "quality", "probe_write_forbidden.csv")
    harvest_refused = False
    harvest_msg = ""
    try:
        assert_safe_erad_audit_write_path(
            _abs(harvest_probe, base_dir=base_dir),
            base_dir=base_dir,
            allowed_audit_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        )
    except RuntimeError as exc:
        harvest_refused = CLEANUP_REFUSED_MSG in str(exc)
        harvest_msg = str(exc)[:120]
    checks["write_guard_harvest_slice1_refused"] = harvest_refused
    rows.append(
        _row(
            check_id="write_guard_harvest_slice1_refused",
            layer="protected_write_guard",
            path=harvest_probe,
            expected="CLEANUP_REFUSED",
            observed=f"refused={harvest_refused};msg={harvest_msg}",
            ok=harvest_refused,
        )
    )

    # 2) snapshot full dry-run 写拒绝
    snap_refused = False
    snap_msg = ""
    try:
        assert_safe_c_class_snapshot_dryrun_write_root(
            _abs(SNAPSHOT_FULL_REL, base_dir=base_dir),
            base_dir=base_dir,
            allow_production_scaffold=False,
        )
    except RuntimeError as exc:
        snap_refused = PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN in str(exc)
        snap_msg = str(exc)[:120]
    checks["write_guard_snapshot_full_refused"] = snap_refused
    rows.append(
        _row(
            check_id="write_guard_snapshot_full_refused",
            layer="protected_write_guard",
            path=SNAPSHOT_FULL_REL,
            expected="PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN",
            observed=f"refused={snap_refused};msg={snap_msg}",
            ok=snap_refused,
        )
    )

    # 3) 权威 dual-layer 索引写拒绝
    auth_probe = os.path.join(
        AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
        "qa_closure_dual_layer_evidence_index.csv",
    )
    auth_refused = False
    auth_msg = ""
    try:
        assert_authoritative_dual_layer_index_write_forbidden(
            _abs(auth_probe, base_dir=base_dir), base_dir=base_dir
        )
    except RuntimeError as exc:
        auth_refused = DUAL_LAYER_INDEX_WRITE_FORBIDDEN in str(exc)
        auth_msg = str(exc)[:120]
    checks["write_guard_auth_dual_layer_refused"] = auth_refused
    rows.append(
        _row(
            check_id="write_guard_auth_dual_layer_refused",
            layer="protected_write_guard",
            path=auth_probe,
            expected="DUAL_LAYER_INDEX_WRITE_FORBIDDEN",
            observed=f"refused={auth_refused};msg={auth_msg}",
            ok=auth_refused,
        )
    )

    # 4) mock 探针允许（写守卫本身不拒绝；不实际写文件）
    mock_abs = _abs(mock_probe_rel, base_dir=base_dir)
    mock_ok = True
    mock_detail = "allowed"
    try:
        assert_authoritative_dual_layer_index_write_forbidden(
            mock_abs, base_dir=base_dir
        )
        assert_safe_erad_audit_write_path(
            os.path.join(mock_abs, "integrity_probe.json"),
            base_dir=base_dir,
            allowed_audit_root_rel=mock_probe_rel,
        )
        assert_safe_c_class_snapshot_dryrun_write_root(
            mock_abs, base_dir=base_dir, allow_production_scaffold=False
        )
    except RuntimeError as exc:
        mock_ok = False
        mock_detail = str(exc)[:120]
    checks["write_guard_mock_allowed"] = mock_ok
    rows.append(
        _row(
            check_id="write_guard_mock_allowed",
            layer="protected_write_guard",
            path=mock_probe_rel,
            expected="mock_writable_by_guards",
            observed=mock_detail,
            ok=mock_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="protected_write_guard_battery_all_pass",
            layer="protected_write_guard",
            expected="harvest+snapshot+auth_refused;mock_allowed",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "write_guard_battery_incomplete",
        )
    )
    checks["protected_write_guard_battery_all_pass"] = all_ok
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected_output_roots.csv 注册一致性。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    csv_rows = load_protected_root_rows(csv_rel, base_dir=base_dir)
    by_id = {
        str(r.get("root_id") or "").strip(): r
        for r in csv_rows
        if str(r.get("root_id") or "").strip()
    }

    for root_id in REQUIRED_PROTECTED_ROOT_IDS:
        present = root_id in by_id
        check_id = f"protected_csv_has_{root_id}"
        path = ""
        if present:
            path = str(by_id[root_id].get("path_pattern") or "").strip()
        rows.append(
            _row(
                check_id=check_id,
                layer="protected_csv_registry",
                root_id=root_id,
                path=path,
                expected="listed_in_protected_csv",
                observed=f"present={present}",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )
        checks[check_id] = present

    # AUTH1 必须 read_only_no_overwrite
    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_policy = str(auth.get("write_policy") or "").strip()
    auth_ok = auth_policy == "read_only_no_overwrite"
    checks["protected_csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="protected_csv_auth1_readonly",
            layer="protected_csv_registry",
            root_id="C-ROOT-AUTH1",
            path=str(auth.get("path_pattern") or ""),
            expected="write_policy=read_only_no_overwrite",
            observed=f"write_policy={auth_policy or 'missing'}",
            ok=auth_ok,
        )
    )

    # MOCK7 路径应对齐本任务默认 mock 根
    mock7 = by_id.get("C-ROOT-MOCK7") or {}
    mock7_path = str(mock7.get("path_pattern") or "").strip().rstrip("/")
    mock7_ok = mock7_path == DEFAULT_MOCK_OUTPUT_ROOT_REL
    checks["protected_csv_mock7_path"] = mock7_ok
    rows.append(
        _row(
            check_id="protected_csv_mock7_path",
            layer="protected_csv_registry",
            root_id="C-ROOT-MOCK7",
            path=mock7_path,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=mock7_path or "missing",
            ok=mock7_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-7+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["protected_csv_registry_all_pass"] = all_ok
    return rows, checks


def build_fm_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..04 既有 gate 只读聚合（不重跑）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    specs = [
        ("fm01_isolated_dryrun_repro", fm01),
        ("fm02_isolated_validation_cohorts", fm02),
        ("fm03_harvest_exclusion_dual_layer", fm03),
        ("fm04_ledger_resume_lineage", fm04),
    ]
    for check_id, payload in specs:
        gate = str(payload.get("gate") or "").strip()
        cninfo = payload.get("cninfo_calls", None)
        execute = payload.get("execute_production_snapshot_rebuild", None)
        ok = gate == "PASS_OFFLINE" and cninfo == 0 and execute is False
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
            check_id="fm01_02_03_04_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_prior_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_02_03_04_battery_all_pass"] = all_ok
    return rows, checks


def write_integrity_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=INTEGRITY_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in INTEGRITY_MATRIX_FIELDS})


def fingerprint_integrity_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """mock cohort 工具：完整性矩阵结构指纹。"""
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


def run_cross_fm_mock_cohort_integrity(
    *,
    paths: IntegrityPaths = IntegrityPaths(),
    cohort_specs: Optional[Sequence[MockCohortSpec]] = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-05 cross-FM mock cohort 完整性 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_integrity_output_root(paths.output_root_rel, base_dir=base_dir)
    specs = tuple(cohort_specs) if cohort_specs is not None else default_mock_cohort_specs()

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))

    reg_rows, reg_checks = build_mock_cohort_registry_rows(specs, base_dir=base_dir)
    fp_rows, fp_checks = build_fingerprint_chain_rows(
        specs, paths=paths, base_dir=base_dir
    )
    wg_rows, wg_checks = build_protected_write_guard_battery_rows(
        mock_probe_rel=paths.output_root_rel, base_dir=base_dir
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    bat_rows, bat_checks = build_fm_gate_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04
    )

    matrix = reg_rows + fp_rows + wg_rows + csv_rows + bat_rows
    all_checks = {
        **reg_checks,
        **fp_checks,
        **wg_checks,
        **csv_checks,
        **bat_checks,
    }
    layer_gates = {
        "mock_cohort_registry": (
            "PASS_OFFLINE"
            if all(reg_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "fingerprint_chain": (
            "PASS_OFFLINE" if all(fp_checks.values()) else "FAIL_REVIEW_REQUIRED"
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

    matrix_path = os.path.join(out_root, "integrity_matrix.csv")
    write_integrity_matrix_csv(matrix, matrix_path)
    fp = fingerprint_integrity_matrix(matrix)
    fp_path = os.path.join(out_root, "integrity_fingerprint.json")
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
                "fingerprint": fp,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    registry_path = os.path.join(out_root, "mock_cohort_registry.json")
    with open(registry_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
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
                "fm01_gate": fm01.get("gate"),
                "fm02_gate": fm02.get("gate"),
                "fm03_gate": fm03.get("gate"),
                "fm04_gate": fm04.get("gate"),
                "fm05_gate": overall,
                "cninfo_calls": 0,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "gate": overall,
        "layer_gates": layer_gates,
        "checks": all_checks,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "registry_path": _rel(registry_path, base_dir=base_dir),
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
            "harvest_863_status": paths.harvest_863_status_rel,
        },
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
    }

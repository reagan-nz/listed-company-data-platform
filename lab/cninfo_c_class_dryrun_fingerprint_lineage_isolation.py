"""
CNINFO C-class — dry-run 指纹 lineage 扩展 + 冻结 mock 写隔离 +
harvest/exclusion dual-layer 交叉指纹 QA（离线 · C-FM-12）。

在 C-FM-11（decision-await hold continuity）已 commit 且 EXECUTE 仍 human-held 之上，
补齐非 seal-chain 能力（不新增 MOCK seal 层）：
  1) dry-run base 指纹零漂移：FM-01 / FM-02 与既有 gate JSON 对齐（不重跑 dry-run）
  2) dry-run lineage 扩展指纹：纳入 filtered_universe / cohort_lineage；
     FM-02 扩展 ≠ base；FM-01 无 lineage 产物时扩展仍可复算
  3) 冻结 mock cohort 写隔离 battery：MOCK3–13 拒绝；本任务 MOCK14 / ephemeral 放行
  4) harvest/exclusion dual-layer 交叉指纹：FM-03 harvest_863 + FM-04 lineage 与 gate 对齐
  5) protected_output_roots.csv 注册一致性（含 MOCK14）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–13 / 权威 dual-layer 索引 ·
verified 声称 · 翻转 approved_for_snapshot_rebuild。
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
    DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_frozen_mock_cohort_write_forbidden,
    fingerprint_isolated_snapshot_dryrun,
    is_allowed_mock_test_cleanup_path,
    load_frozen_mock_cohort_roots,
    resolve_frozen_mock_cohort_root_id,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    fingerprint_status_csv,
    load_csv_rows,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)

TASK_ID = "C-FM-12"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm12_dryrun_fingerprint_lineage_isolation"
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

# 冻结根：本任务仅允许写 MOCK14；其余 MOCK3–13 必须拒绝
THIS_TASK_ROOT_ID = "C-ROOT-MOCK14"
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
class IsolationPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm01_mock_root_rel: str = DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL
    fm02_mock_root_rel: str = FM02_MOCK_ROOT_REL
    fm03_mock_root_rel: str = FM03_MOCK_ROOT_REL
    fm04_mock_root_rel: str = FM04_MOCK_ROOT_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    output_root_rel: str = DEFAULT_MOCK_OUTPUT_ROOT_REL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _abs(path: str, *, base_dir: str = BASE_DIR) -> str:
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(base_dir, path))


def _rel(path: str, *, base_dir: str = BASE_DIR) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, base_dir).replace("\\", "/")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _row(
    *,
    check_id: str,
    layer: str,
    expected: str,
    observed: str,
    ok: bool,
    notes: str = "",
    cohort_id: str = "*",
    root_id: str = "",
    path: str = "",
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
        "notes": notes,
    }


def assert_fm12_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-12 写根：须 validation/_mock_*，不得覆盖 MOCK3–13，
    不得写权威 dual-layer 索引；允许本任务 MOCK14 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    # 刷新冻结根缓存（CSV 可能刚登记 MOCK14）
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"{_rel(out, base_dir=base_dir)} (root_id={root_id}; "
            f"C-FM-12 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    # 显式守卫：即使未来误配 allow，也不写 MOCK3–13
    assert_frozen_mock_cohort_write_forbidden(
        out,
        allow_root_ids=(THIS_TASK_ROOT_ID,),
        base_dir=base_dir,
    )
    return out


def build_dryrun_base_fingerprint_rows(
    paths: IsolationPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01 / FM-02 base dry-run 指纹与 gate 对齐。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    # FM-01
    fm01_gate = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm01_runs = fm01_gate.get("runs") or []
    fm01_expected = (
        str(fm01_runs[0].get("fingerprint_sha256") or "") if fm01_runs else ""
    )
    fm01_fp = fingerprint_isolated_snapshot_dryrun(
        paths.fm01_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=863,
        lineage_artifacts=False,
    )
    fm01_obs = str(fm01_fp.get("fingerprint_sha256") or "")
    fm01_ok = bool(fm01_expected) and fm01_expected == fm01_obs
    checks["dryrun_base_fm01"] = fm01_ok
    rows.append(
        _row(
            check_id="dryrun_base_fm01",
            layer="dryrun_base_fingerprint",
            cohort_id="fm01_standard_isolated",
            root_id="C-ROOT-MOCK3",
            path=paths.fm01_mock_root_rel,
            expected=fm01_expected[:16] + "…" if fm01_expected else "missing",
            observed=fm01_obs[:16] + "…" if fm01_obs else "missing",
            ok=fm01_ok,
            notes="base_matches_gate" if fm01_ok else "base_drift",
        )
    )

    # FM-02
    fm02_gate = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    slice1 = fm02_gate.get("slice1_190") or {}
    fm02_expected = str((slice1.get("fingerprint") or {}).get("fingerprint_sha256") or "")
    fm02_fp = fingerprint_isolated_snapshot_dryrun(
        paths.fm02_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=190,
        lineage_artifacts=False,
    )
    fm02_obs = str(fm02_fp.get("fingerprint_sha256") or "")
    fm02_ok = bool(fm02_expected) and fm02_expected == fm02_obs
    checks["dryrun_base_fm02"] = fm02_ok
    rows.append(
        _row(
            check_id="dryrun_base_fm02",
            layer="dryrun_base_fingerprint",
            cohort_id="fm02_slice1_190",
            root_id="C-ROOT-MOCK4",
            path=paths.fm02_mock_root_rel,
            expected=fm02_expected[:16] + "…" if fm02_expected else "missing",
            observed=fm02_obs[:16] + "…" if fm02_obs else "missing",
            ok=fm02_ok,
            notes="base_matches_gate" if fm02_ok else "base_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["dryrun_base_fingerprint_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="dryrun_base_fingerprint_all_pass",
            layer="dryrun_base_fingerprint",
            expected="fm01_fm02_base_zero_drift",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "base_fingerprint_drift",
        )
    )
    return rows, checks


def build_dryrun_lineage_extension_rows(
    paths: IsolationPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, str]]:
    """dry-run lineage 扩展指纹：与 base 区分；可复算。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    # FM-02：有 lineage 产物 → 扩展 ≠ base，且两次扩展一致
    base = fingerprint_isolated_snapshot_dryrun(
        paths.fm02_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=190,
        lineage_artifacts=False,
    )
    ext1 = fingerprint_isolated_snapshot_dryrun(
        paths.fm02_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=190,
        lineage_artifacts=True,
    )
    ext2 = fingerprint_isolated_snapshot_dryrun(
        paths.fm02_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=190,
        lineage_artifacts=True,
    )
    base_sha = str(base.get("fingerprint_sha256") or "")
    ext_sha = str(ext1.get("fingerprint_sha256") or "")
    differs = bool(base_sha) and bool(ext_sha) and base_sha != ext_sha
    checks["lineage_ext_fm02_differs_base"] = differs
    rows.append(
        _row(
            check_id="lineage_ext_fm02_differs_base",
            layer="dryrun_lineage_extension",
            cohort_id="fm02_slice1_190",
            root_id="C-ROOT-MOCK4",
            path=paths.fm02_mock_root_rel,
            expected="ext_sha != base_sha",
            observed=f"differs={differs}",
            ok=differs,
            notes="lineage_artifacts_change_hash",
        )
    )
    repro = ext_sha == str(ext2.get("fingerprint_sha256") or "")
    checks["lineage_ext_fm02_reproducible"] = repro
    rows.append(
        _row(
            check_id="lineage_ext_fm02_reproducible",
            layer="dryrun_lineage_extension",
            cohort_id="fm02_slice1_190",
            path=paths.fm02_mock_root_rel,
            expected="ext_sha stable across recomputes",
            observed=ext_sha[:16] + "…" if ext_sha else "missing",
            ok=repro,
            notes="ok" if repro else "ext_unstable",
        )
    )
    present = ext1.get("files_present") or {}
    has_universe = bool(present.get("filtered_universe_included.yaml"))
    has_matrix = bool(present.get("cohort_lineage_matrix.csv"))
    artifacts_ok = has_universe and has_matrix and bool(ext1.get("lineage_artifacts"))
    checks["lineage_ext_fm02_artifacts_present"] = artifacts_ok
    rows.append(
        _row(
            check_id="lineage_ext_fm02_artifacts_present",
            layer="dryrun_lineage_extension",
            cohort_id="fm02_slice1_190",
            path=paths.fm02_mock_root_rel,
            expected="filtered_universe+cohort_lineage+flag",
            observed=(
                f"universe={has_universe};matrix={has_matrix};"
                f"flag={bool(ext1.get('lineage_artifacts'))}"
            ),
            ok=artifacts_ok,
            notes="ok" if artifacts_ok else "lineage_artifacts_missing",
        )
    )

    # FM-01：无 lineage 产物 → 扩展指纹仍可复算，且标记 lineage_artifacts
    fm01_ext1 = fingerprint_isolated_snapshot_dryrun(
        paths.fm01_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=863,
        lineage_artifacts=True,
    )
    fm01_ext2 = fingerprint_isolated_snapshot_dryrun(
        paths.fm01_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=863,
        lineage_artifacts=True,
    )
    fm01_base = fingerprint_isolated_snapshot_dryrun(
        paths.fm01_mock_root_rel,
        base_dir=base_dir,
        gate="PASS_WITH_CAVEAT",
        company_count=863,
        lineage_artifacts=False,
    )
    fm01_ext_sha = str(fm01_ext1.get("fingerprint_sha256") or "")
    fm01_repro = fm01_ext_sha == str(fm01_ext2.get("fingerprint_sha256") or "")
    fm01_differs = fm01_ext_sha != str(fm01_base.get("fingerprint_sha256") or "")
    # 即使文件缺失，扩展模式因 flag+missing 条目也应与 base 不同
    checks["lineage_ext_fm01_reproducible"] = fm01_repro and fm01_differs
    rows.append(
        _row(
            check_id="lineage_ext_fm01_reproducible",
            layer="dryrun_lineage_extension",
            cohort_id="fm01_standard_isolated",
            root_id="C-ROOT-MOCK3",
            path=paths.fm01_mock_root_rel,
            expected="ext stable and differs base (missing lineage noted)",
            observed=f"repro={fm01_repro};differs={fm01_differs}",
            ok=fm01_repro and fm01_differs,
            notes="missing_lineage_still_extends_hash",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["dryrun_lineage_extension_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="dryrun_lineage_extension_all_pass",
            layer="dryrun_lineage_extension",
            expected="lineage_extension_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "lineage_extension_fail",
        )
    )
    return rows, checks, {"fm02_lineage_ext_sha256": ext_sha, "fm01_lineage_ext_sha256": fm01_ext_sha}


def build_frozen_mock_isolation_rows(
    paths: IsolationPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离 battery。"""
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

    # MOCK14 本任务根放行
    mock14_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock14_listed = mock14_prefix is not None
    mock14_allowed = False
    if mock14_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock14_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock14_allowed = True
        except RuntimeError:
            mock14_allowed = False
    checks["frozen_allow_mock14"] = mock14_listed and mock14_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock14",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="listed_and_allowable",
            observed=f"listed={mock14_listed};allowed={mock14_allowed}",
            ok=mock14_listed and mock14_allowed,
            notes="ok" if mock14_listed and mock14_allowed else "mock14_not_ready",
        )
    )

    # ephemeral 未登记根放行
    ephemeral = "outputs/validation/_mock_c_fm12_ephemeral_isolation_probe"
    eph_id = resolve_frozen_mock_cohort_root_id(ephemeral, base_dir=base_dir)
    eph_ok = eph_id is None
    if eph_ok:
        try:
            assert_frozen_mock_cohort_write_forbidden(ephemeral, base_dir=base_dir)
        except RuntimeError:
            eph_ok = False
    checks["frozen_ephemeral_allowed"] = eph_ok
    rows.append(
        _row(
            check_id="frozen_ephemeral_allowed",
            layer="frozen_mock_isolation",
            path=ephemeral,
            expected="unregistered_mock_allowed",
            observed=f"root_id={eph_id!s}",
            ok=eph_ok,
            notes="ok" if eph_ok else "ephemeral_blocked",
        )
    )

    # 权威 dual-layer 仍拒绝
    auth_probe = os.path.join(
        AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
        "qa_closure_dual_layer_evidence_index.csv",
    )
    auth_refused = False
    try:
        assert_authoritative_dual_layer_index_write_forbidden(
            auth_probe, base_dir=base_dir
        )
    except RuntimeError:
        auth_refused = True
    checks["auth_dual_layer_still_forbidden"] = auth_refused
    rows.append(
        _row(
            check_id="auth_dual_layer_still_forbidden",
            layer="frozen_mock_isolation",
            path=auth_probe,
            expected="DUAL_LAYER_INDEX_WRITE_FORBIDDEN",
            observed=f"refused={auth_refused}",
            ok=auth_refused,
            notes="ok" if auth_refused else "auth_guard_regressed",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-13_blocked_MOCK14_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "isolation_fail",
        )
    )
    return rows, checks


def build_harvest_exclusion_dual_layer_cross_fp_rows(
    paths: IsolationPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-03 harvest_863 + FM-04 lineage 交叉指纹与 gate 对齐。"""
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
    checks["cross_fp_fm03_harvest_863"] = fm03_ok
    rows.append(
        _row(
            check_id="cross_fp_fm03_harvest_863",
            layer="harvest_exclusion_dual_layer_cross_fp",
            cohort_id="fm03_harvest_exclusion",
            root_id="C-ROOT-MOCK5",
            path=paths.harvest_863_status_rel,
            expected=fm03_expected[:16] + "…" if fm03_expected else "missing",
            observed=fm03_obs[:16] + "…" if fm03_obs else "missing",
            ok=fm03_ok,
            notes="ok" if fm03_ok else "harvest_863_drift",
        )
    )

    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm04_expected = str((fm04.get("fingerprint") or {}).get("fingerprint_sha256") or "")
    matrix_path = _abs(
        os.path.join(paths.fm04_mock_root_rel, "lineage_matrix.csv"),
        base_dir=base_dir,
    )
    lineage_rows = load_csv_rows(matrix_path)
    lineage_fp = fingerprint_lineage_matrix(lineage_rows)
    fm04_obs = str(lineage_fp.get("fingerprint_sha256") or "")
    fm04_ok = bool(fm04_expected) and fm04_expected == fm04_obs
    checks["cross_fp_fm04_lineage"] = fm04_ok
    rows.append(
        _row(
            check_id="cross_fp_fm04_lineage",
            layer="harvest_exclusion_dual_layer_cross_fp",
            cohort_id="fm04_ledger_resume_lineage",
            root_id="C-ROOT-MOCK6",
            path=os.path.join(paths.fm04_mock_root_rel, "lineage_matrix.csv"),
            expected=fm04_expected[:16] + "…" if fm04_expected else "missing",
            observed=fm04_obs[:16] + "…" if fm04_obs else "missing",
            ok=fm04_ok,
            notes="ok" if fm04_ok else "lineage_fp_drift",
        )
    )

    # FM-03 / FM-04 gate 仍为 PASS_OFFLINE 且 cninfo=0
    for label, doc, cid in (
        ("fm03", fm03, "cross_fp_fm03_gate"),
        ("fm04", fm04, "cross_fp_fm04_gate"),
    ):
        gate_ok = (
            doc.get("gate") == "PASS_OFFLINE"
            and int(doc.get("cninfo_calls") or 0) == 0
            and not doc.get("execute_production_snapshot_rebuild")
        )
        checks[cid] = gate_ok
        rows.append(
            _row(
                check_id=cid,
                layer="harvest_exclusion_dual_layer_cross_fp",
                cohort_id=label,
                expected="PASS_OFFLINE cninfo=0 no_execute",
                observed=(
                    f"gate={doc.get('gate')};cninfo={doc.get('cninfo_calls')};"
                    f"exec={doc.get('execute_production_snapshot_rebuild')}"
                ),
                ok=gate_ok,
                notes="ok" if gate_ok else "gate_regressed",
            )
        )

    all_ok = all(checks.values()) if checks else False
    checks["harvest_exclusion_dual_layer_cross_fp_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="harvest_exclusion_dual_layer_cross_fp_all_pass",
            layer="harvest_exclusion_dual_layer_cross_fp",
            expected="fm03_fm04_cross_fp_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "cross_fp_fail",
        )
    )
    return rows, checks


def load_protected_root_rows(
    csv_rel: str, *, base_dir: str = BASE_DIR
) -> List[Dict[str, str]]:
    path = _abs(csv_rel, base_dir=base_dir)
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected CSV：MOCK3–14 + AUTH1 注册一致性。"""
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

    mock14 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock14_path = (mock14.get("path_pattern") or "").strip().rstrip("/")
    expected_path = DEFAULT_MOCK_OUTPUT_ROOT_REL
    mock14_ok = mock14_path.endswith(
        "_mock_c_fm12_dryrun_fingerprint_lineage_isolation"
    ) or mock14_path == expected_path
    checks["protected_csv_mock14_path"] = mock14_ok
    rows.append(
        _row(
            check_id="protected_csv_mock14_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            path=mock14_path,
            expected=expected_path,
            observed=mock14_path or "missing",
            ok=mock14_ok,
            notes="ok" if mock14_ok else "mock14_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-14+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def fingerprint_isolation_matrix(
    rows: Sequence[Dict[str, str]],
) -> Dict[str, Any]:
    """对隔离 QA matrix 做稳定指纹。"""
    canon_lines = []
    for r in rows:
        canon_lines.append(
            "|".join(
                [
                    r.get("check_id", ""),
                    r.get("layer", ""),
                    r.get("ok", ""),
                    r.get("expected", ""),
                    r.get("observed", ""),
                ]
            )
        )
    canon = "\n".join(canon_lines)
    return {
        "row_count": len(rows),
        "ok_count": sum(1 for r in rows if r.get("ok") == "yes"),
        "fail_count": sum(1 for r in rows if r.get("ok") != "yes"),
        "layers": sorted({r.get("layer", "") for r in rows}),
        "fingerprint_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
    }


def run_dryrun_fingerprint_lineage_isolation(
    paths: Optional[IsolationPaths] = None,
    *,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-12 dry-run 指纹 lineage 扩展 + 冻结隔离 QA（CNINFO=0）。"""
    paths = paths or IsolationPaths()
    out_root = assert_fm12_output_root(paths.output_root_rel, base_dir=base_dir)
    os.makedirs(out_root, exist_ok=True)

    base_rows, base_checks = build_dryrun_base_fingerprint_rows(
        paths, base_dir=base_dir
    )
    ext_rows, ext_checks, ext_meta = build_dryrun_lineage_extension_rows(
        paths, base_dir=base_dir
    )
    iso_rows, iso_checks = build_frozen_mock_isolation_rows(
        paths, base_dir=base_dir
    )
    cross_rows, cross_checks = build_harvest_exclusion_dual_layer_cross_fp_rows(
        paths, base_dir=base_dir
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )

    matrix = base_rows + ext_rows + iso_rows + cross_rows + csv_rows
    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "dryrun_base_fingerprint": (
            "PASS_OFFLINE"
            if base_checks.get("dryrun_base_fingerprint_all_pass")
            else "FAIL"
        ),
        "dryrun_lineage_extension": (
            "PASS_OFFLINE"
            if ext_checks.get("dryrun_lineage_extension_all_pass")
            else "FAIL"
        ),
        "frozen_mock_isolation": (
            "PASS_OFFLINE"
            if iso_checks.get("frozen_mock_isolation_all_pass")
            else "FAIL"
        ),
        "harvest_exclusion_dual_layer_cross_fp": (
            "PASS_OFFLINE"
            if cross_checks.get("harvest_exclusion_dual_layer_cross_fp_all_pass")
            else "FAIL"
        ),
        "protected_csv_registry": (
            "PASS_OFFLINE"
            if csv_checks.get("protected_csv_registry_all_pass")
            else "FAIL"
        ),
    }
    gate = (
        "PASS_OFFLINE"
        if fail_count == 0 and all(v == "PASS_OFFLINE" for v in layer_gates.values())
        else "FAIL"
    )

    matrix_path = os.path.join(out_root, "isolation_matrix.csv")
    with open(matrix_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        writer.writerows(matrix)

    fp = fingerprint_isolation_matrix(matrix)
    fp_path = os.path.join(out_root, "isolation_fingerprint.json")
    with open(fp_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": _utc_now_iso(),
                "task_id": TASK_ID,
                "fingerprint": fp,
                "lineage_extension": ext_meta,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    battery = {
        "generated_at": _utc_now_iso(),
        "task_id": TASK_ID,
        "gate": gate,
        "layer_gates": layer_gates,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "lineage_extension": ext_meta,
    }
    battery_path = os.path.join(out_root, "fm_gate_battery.json")
    with open(battery_path, "w", encoding="utf-8") as fh:
        json.dump(battery, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    packet = {
        "generated_at": _utc_now_iso(),
        "task_id": TASK_ID,
        "gate": gate,
        "capability": [
            "dryrun_base_fingerprint_zero_drift",
            "dryrun_lineage_fingerprint_extension",
            "frozen_mock_cohort_write_isolation",
            "harvest_exclusion_dual_layer_cross_fingerprint",
        ],
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "seal_chain_extended": False,
        "notes": "non-seal-chain offline QA; EXECUTE remains human-held",
    }
    packet_path = os.path.join(out_root, "lineage_isolation_packet.json")
    with open(packet_path, "w", encoding="utf-8") as fh:
        json.dump(packet, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    return {
        "generated_at": _utc_now_iso(),
        "task_id": TASK_ID,
        "gate": gate,
        "layer_gates": layer_gates,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "packet_path": _rel(packet_path, base_dir=base_dir),
        "lineage_extension": ext_meta,
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "fm01_mock_root": paths.fm01_mock_root_rel,
            "fm02_mock_root": paths.fm02_mock_root_rel,
            "fm03_mock_root": paths.fm03_mock_root_rel,
            "fm04_mock_root": paths.fm04_mock_root_rel,
            "harvest_863_status": paths.harvest_863_status_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
    }

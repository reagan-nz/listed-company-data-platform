"""
CNINFO C-class — Pre-EXECUTE decision-await hold continuity / readiness 漂移复核（离线 · C-FM-11）。

在 C-FM-10（human decision readiness ledger）已 commit 且
decision_status=AWAITING_HUMAN_EXECUTE_DECISION 之上，补齐：
  1) FM-01..10 gate battery 只读聚合（含 FM-10 readiness ledger gate）
  2) C-FM-10 MOCK12 冻结产物存在性
  3) readiness 指纹零漂移复核（不覆盖 MOCK12 / MOCK8–11）
  4) seal-chain 连续性：MOCK8–12 墙/exclusion/boundary/attestation/readiness 锚点
  5) decision-await hold seal：KEEP_EXECUTE_FALSE · AWAITING · idle_not_required
  6) protected_output_roots.csv 注册一致性（MOCK3–13 · AUTH1）

禁止：CNINFO live · production EXECUTE · 覆盖权威 dual-layer 索引 ·
      覆盖 MOCK8/MOCK9/MOCK10/MOCK11/MOCK12 · verified 声称 ·
      翻转 approved_for_snapshot_rebuild · commit/push ·
      仅因 AWAITING_HUMAN_EXECUTE_DECISION 而 IDLE。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence, Tuple

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)
from cninfo_c_class_pre_execute_human_decision_readiness_ledger import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM10_MOCK_ROOT_REL,
    FROZEN_ATTESTATION_FP_SHA256,
    FROZEN_BOUNDARY_FP_SHA256,
    FROZEN_EXCLUSION_FP_SHA256,
    FROZEN_WALL_FP_SHA256,
    HumanDecisionReadinessPaths,
    LEDGER_MATRIX_FIELDS,
    build_fm01_to_09_gate_battery_rows,
    fingerprint_ledger_matrix,
    run_pre_execute_human_decision_readiness_ledger,
)
from cninfo_c_class_pre_execute_post_commit_seal_attestation import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM09_MOCK_ROOT_REL,
)
from cninfo_c_class_pre_execute_controller_commit_boundary import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM08_MOCK_ROOT_REL,
)
from cninfo_c_class_pre_execute_safe_snapshot_wall import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM06_MOCK_ROOT_REL,
    load_json,
    load_protected_root_rows,
)
from cninfo_c_class_pre_execute_wall_freeze_drift_recheck import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM07_MOCK_ROOT_REL,
)

TASK_ID = "C-FM-11"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm11_pre_execute_decision_await_hold_continuity"
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
FM06_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_safe_snapshot_wall_20260715.json"
)
FM07_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_wall_freeze_drift_recheck_20260715.json"
)
FM08_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_controller_commit_boundary_20260715.json"
)
FM09_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_post_commit_seal_attestation_20260715.json"
)
FM10_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_human_decision_readiness_ledger_20260715.json"
)

FM06_WALL_FINGERPRINT_REL = f"{FM06_MOCK_ROOT_REL}/wall_fingerprint.json"
FM07_DRIFT_SEAL_REL = f"{FM07_MOCK_ROOT_REL}/drift_seal_packet.json"
FM08_BOUNDARY_FP_REL = f"{FM08_MOCK_ROOT_REL}/boundary_fingerprint.json"
FM09_ATTESTATION_FP_REL = f"{FM09_MOCK_ROOT_REL}/attestation_fingerprint.json"

FM10_READINESS_MATRIX_REL = f"{FM10_MOCK_ROOT_REL}/readiness_matrix.csv"
FM10_READINESS_FP_REL = f"{FM10_MOCK_ROOT_REL}/readiness_fingerprint.json"
FM10_BATTERY_REL = f"{FM10_MOCK_ROOT_REL}/fm_gate_battery.json"
FM10_PACKET_REL = (
    f"{FM10_MOCK_ROOT_REL}/human_execute_decision_readiness_packet.json"
)
FM10_CHECKLIST_REL = f"{FM10_MOCK_ROOT_REL}/human_execute_decision_checklist.json"
FM10_SEAL_REL = f"{FM10_MOCK_ROOT_REL}/decision_readiness_seal_packet.json"

# C-FM-10 冻结 readiness 指纹常量（decision-await 漂移复核锚点）
FROZEN_READINESS_FP_SHA256 = (
    "a380554136c4f0921493b1eafed6a78dc326d5e0a770f8d43f967466b0235e12"
)

REQUIRED_PROTECTED_ROOT_IDS = (
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
    "C-ROOT-AUTH1",
)

CONTINUITY_MATRIX_FIELDS = list(LEDGER_MATRIX_FIELDS)


@dataclass(frozen=True)
class DecisionAwaitContinuityPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    fm06_gate_json_rel: str = FM06_GATE_JSON_REL
    fm07_gate_json_rel: str = FM07_GATE_JSON_REL
    fm08_gate_json_rel: str = FM08_GATE_JSON_REL
    fm09_gate_json_rel: str = FM09_GATE_JSON_REL
    fm10_gate_json_rel: str = FM10_GATE_JSON_REL
    fm06_mock_root_rel: str = FM06_MOCK_ROOT_REL
    fm06_wall_fingerprint_rel: str = FM06_WALL_FINGERPRINT_REL
    fm07_mock_root_rel: str = FM07_MOCK_ROOT_REL
    fm07_drift_seal_rel: str = FM07_DRIFT_SEAL_REL
    fm08_mock_root_rel: str = FM08_MOCK_ROOT_REL
    fm08_boundary_fp_rel: str = FM08_BOUNDARY_FP_REL
    fm09_mock_root_rel: str = FM09_MOCK_ROOT_REL
    fm09_attestation_fp_rel: str = FM09_ATTESTATION_FP_REL
    fm10_mock_root_rel: str = FM10_MOCK_ROOT_REL
    fm10_readiness_matrix_rel: str = FM10_READINESS_MATRIX_REL
    fm10_readiness_fp_rel: str = FM10_READINESS_FP_REL
    fm10_battery_rel: str = FM10_BATTERY_REL
    fm10_packet_rel: str = FM10_PACKET_REL
    fm10_checklist_rel: str = FM10_CHECKLIST_REL
    fm10_seal_rel: str = FM10_SEAL_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
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


def assert_decision_await_continuity_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """decision-await continuity 写根：须 validation/_mock_*，拒绝权威索引与 MOCK8–12。"""
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    out_rel = _rel(out, base_dir=base_dir).rstrip("/")
    for label, frozen_rel in (
        ("MOCK8", FM06_MOCK_ROOT_REL.rstrip("/")),
        ("MOCK9", FM07_MOCK_ROOT_REL.rstrip("/")),
        ("MOCK10", FM08_MOCK_ROOT_REL.rstrip("/")),
        ("MOCK11", FM09_MOCK_ROOT_REL.rstrip("/")),
        ("MOCK12", FM10_MOCK_ROOT_REL.rstrip("/")),
    ):
        if out_rel == frozen_rel or out_rel.startswith(frozen_rel + "/"):
            raise RuntimeError(
                f"C_FM11_MUST_NOT_OVERWRITE_{label}: "
                f"output_root={out_rel} overlaps frozen {label}={frozen_rel}"
            )
    return out


def _row(
    *,
    check_id: str,
    layer: str,
    path: str = "",
    expected: str = "",
    observed: str = "",
    ok: bool = False,
    notes: str = "",
) -> Dict[str, str]:
    return {
        "check_id": check_id,
        "layer": layer,
        "path": path,
        "expected": expected,
        "observed": observed,
        "ok": "yes" if ok else "no",
        "notes": notes or ("ok" if ok else "fail"),
    }


def load_readiness_matrix_rows(path: str) -> List[Dict[str, str]]:
    """只读加载 FM10 readiness_matrix.csv。"""
    rows: List[Dict[str, str]] = []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            rows.append(
                {k: str(raw.get(k) or "") for k in LEDGER_MATRIX_FIELDS}
            )
    return rows


def build_fm01_to_10_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
    fm05: Dict[str, Any],
    fm06: Dict[str, Any],
    fm07: Dict[str, Any],
    fm08: Dict[str, Any],
    fm09: Dict[str, Any],
    fm10: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..10 既有 gate 只读聚合（不重跑；含 FM-10 human decision readiness）。"""
    rows, checks = build_fm01_to_09_gate_battery_rows(
        fm01=fm01,
        fm02=fm02,
        fm03=fm03,
        fm04=fm04,
        fm05=fm05,
        fm06=fm06,
        fm07=fm07,
        fm08=fm08,
        fm09=fm09,
    )
    rows = [r for r in rows if r.get("check_id") != "fm01_to_09_battery_all_pass"]
    checks.pop("fm01_to_09_battery_all_pass", None)

    gate = str(fm10.get("gate") or "").strip()
    cninfo = fm10.get("cninfo_calls", None)
    execute = fm10.get("execute_production_snapshot_rebuild", None)
    approved = fm10.get("approved_for_snapshot_rebuild", None)
    ok = (
        gate == "PASS_OFFLINE"
        and cninfo == 0
        and execute is False
        and approved is False
    )
    rows.append(
        _row(
            check_id="fm10_pre_execute_human_decision_readiness_ledger",
            layer="fm_gate_battery",
            path="fm10_pre_execute_human_decision_readiness_ledger",
            expected="gate=PASS_OFFLINE;cninfo=0;execute=false;approved=false",
            observed=(
                f"gate={gate};cninfo={cninfo};execute={execute};approved={approved}"
            ),
            ok=ok,
            notes="ok" if ok else "fm10_gate_not_pass",
        )
    )
    checks["fm10_pre_execute_human_decision_readiness_ledger"] = ok

    prior_ok = all(
        checks.get(k)
        for k in (
            "fm01_isolated_dryrun_repro",
            "fm02_isolated_validation_cohorts",
            "fm03_harvest_exclusion_dual_layer",
            "fm04_ledger_resume_lineage",
            "fm05_cross_fm_mock_cohort_integrity",
            "fm06_pre_execute_safe_snapshot_wall",
            "fm07_pre_execute_wall_freeze_drift_recheck",
            "fm08_pre_execute_controller_commit_boundary",
            "fm09_pre_execute_post_commit_seal_attestation",
            "fm10_pre_execute_human_decision_readiness_ledger",
        )
    )
    rows.append(
        _row(
            check_id="fm01_to_10_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_prior_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/10",
            ok=prior_ok,
            notes="ok" if prior_ok else "battery_incomplete",
        )
    )
    checks["fm01_to_10_battery_all_pass"] = prior_ok
    return rows, checks


def build_fm10_artifact_presence_rows(
    *,
    paths: DecisionAwaitContinuityPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """C-FM-10 MOCK12 冻结产物存在性。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    specs = [
        ("fm10_mock_root_exists", paths.fm10_mock_root_rel, "dir"),
        ("fm10_readiness_matrix_exists", paths.fm10_readiness_matrix_rel, "file"),
        ("fm10_readiness_fp_exists", paths.fm10_readiness_fp_rel, "file"),
        ("fm10_battery_exists", paths.fm10_battery_rel, "file"),
        ("fm10_packet_exists", paths.fm10_packet_rel, "file"),
        ("fm10_checklist_exists", paths.fm10_checklist_rel, "file"),
        ("fm10_seal_exists", paths.fm10_seal_rel, "file"),
    ]
    for check_id, rel, kind in specs:
        abs_path = _abs(rel, base_dir=base_dir)
        present = os.path.isdir(abs_path) if kind == "dir" else os.path.isfile(abs_path)
        rows.append(
            _row(
                check_id=check_id,
                layer="fm10_artifact_presence",
                path=rel,
                expected=f"{kind}_present",
                observed=f"present={present}",
                ok=present,
            )
        )
        checks[check_id] = present

    root_abs = _abs(paths.fm10_mock_root_rel, base_dir=base_dir)
    isolated = is_allowed_mock_test_cleanup_path(root_abs, base_dir=base_dir)
    rows.append(
        _row(
            check_id="fm10_mock_root_isolated",
            layer="fm10_artifact_presence",
            path=paths.fm10_mock_root_rel,
            expected="isolated_mock",
            observed=f"isolated={isolated}",
            ok=isolated,
        )
    )
    checks["fm10_mock_root_isolated"] = isolated

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="fm10_artifact_presence_all_pass",
            layer="fm10_artifact_presence",
            expected="mock12_readiness_artifacts_present",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["fm10_artifact_presence_all_pass"] = all_ok
    return rows, checks


def recompute_readiness_fingerprint(
    *,
    probe_output_root_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    重算 C-FM-10 readiness 指纹（不写 MOCK12）。

    1) 只读指纹化 MOCK12 readiness_matrix.csv
    2) 向隔离 probe 根重跑 FM10 ledger，比对结构指纹
    """
    matrix_path = _abs(FM10_READINESS_MATRIX_REL, base_dir=base_dir)
    frozen_rows = load_readiness_matrix_rows(matrix_path)
    frozen_file_fp = fingerprint_ledger_matrix(frozen_rows)

    probe_rel = probe_output_root_rel.rstrip("/")
    result = run_pre_execute_human_decision_readiness_ledger(
        paths=HumanDecisionReadinessPaths(output_root_rel=probe_rel),
        base_dir=base_dir,
    )
    recomputed_fp = dict(result.get("fingerprint") or {})
    return frozen_file_fp, recomputed_fp


def build_readiness_fingerprint_drift_rows(
    *,
    paths: DecisionAwaitContinuityPaths,
    frozen_file_fp: Dict[str, Any],
    recomputed_fp: Dict[str, Any],
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 readiness 指纹 vs 重算指纹漂移复核。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    frozen_fp_doc: Dict[str, Any] = {}
    fp_path = _abs(paths.fm10_readiness_fp_rel, base_dir=base_dir)
    if os.path.isfile(fp_path):
        frozen_fp_doc = load_json(fp_path)

    frozen_doc_sha = str(
        (frozen_fp_doc.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    frozen_file_sha = str(frozen_file_fp.get("fingerprint_sha256") or "")
    recomputed_sha = str(recomputed_fp.get("fingerprint_sha256") or "")

    const_ok = frozen_doc_sha == FROZEN_READINESS_FP_SHA256
    checks["frozen_readiness_sha_matches_constant"] = const_ok
    rows.append(
        _row(
            check_id="frozen_readiness_sha_matches_constant",
            layer="readiness_fingerprint_drift",
            path=paths.fm10_readiness_fp_rel,
            expected=FROZEN_READINESS_FP_SHA256,
            observed=frozen_doc_sha or "missing",
            ok=const_ok,
        )
    )

    file_ok = frozen_file_sha == FROZEN_READINESS_FP_SHA256
    checks["frozen_matrix_file_sha_no_drift"] = file_ok
    rows.append(
        _row(
            check_id="frozen_matrix_file_sha_no_drift",
            layer="readiness_fingerprint_drift",
            path=paths.fm10_readiness_matrix_rel,
            expected=FROZEN_READINESS_FP_SHA256,
            observed=frozen_file_sha or "missing",
            ok=file_ok,
            notes="zero_drift" if file_ok else "readiness_matrix_drift",
        )
    )

    recompute_ok = recomputed_sha == FROZEN_READINESS_FP_SHA256
    checks["recomputed_readiness_sha_no_drift"] = recompute_ok
    rows.append(
        _row(
            check_id="recomputed_readiness_sha_no_drift",
            layer="readiness_fingerprint_drift",
            expected=FROZEN_READINESS_FP_SHA256,
            observed=recomputed_sha or "missing",
            ok=recompute_ok,
            notes="zero_drift" if recompute_ok else "readiness_recompute_drift",
        )
    )

    # 交叉锚点：FM10 指纹文档仍绑定墙/exclusion/boundary/attestation
    cross_wall = str(frozen_fp_doc.get("frozen_wall_fingerprint_sha256") or "")
    cross_excl = str(frozen_fp_doc.get("frozen_exclusion_fingerprint_sha256") or "")
    cross_boundary = str(
        frozen_fp_doc.get("frozen_boundary_fingerprint_sha256") or ""
    )
    cross_att = str(
        frozen_fp_doc.get("frozen_attestation_fingerprint_sha256") or ""
    )
    cross_ok = (
        cross_wall == FROZEN_WALL_FP_SHA256
        and cross_excl == FROZEN_EXCLUSION_FP_SHA256
        and cross_boundary == FROZEN_BOUNDARY_FP_SHA256
        and cross_att == FROZEN_ATTESTATION_FP_SHA256
    )
    checks["frozen_readiness_cross_anchors"] = cross_ok
    rows.append(
        _row(
            check_id="frozen_readiness_cross_anchors",
            layer="readiness_fingerprint_drift",
            path=paths.fm10_readiness_fp_rel,
            expected="wall+excl+boundary+attestation_frozen",
            observed=(
                f"wall={cross_wall or 'missing'};excl={cross_excl or 'missing'};"
                f"boundary={cross_boundary or 'missing'};"
                f"att={cross_att or 'missing'}"
            ),
            ok=cross_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="readiness_fingerprint_drift_all_pass",
            layer="readiness_fingerprint_drift",
            expected="zero_drift_vs_c_fm10_freeze",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["readiness_fingerprint_drift_all_pass"] = all_ok
    return rows, checks


def build_seal_chain_continuity_rows(
    *,
    paths: DecisionAwaitContinuityPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """MOCK8–12 seal-chain 连续性锚点（只读）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    presence_specs = [
        ("fm06_wall_fingerprint_exists", paths.fm06_wall_fingerprint_rel, "file"),
        ("fm07_drift_seal_exists", paths.fm07_drift_seal_rel, "file"),
        ("fm08_boundary_fp_exists", paths.fm08_boundary_fp_rel, "file"),
        ("fm09_attestation_fp_exists", paths.fm09_attestation_fp_rel, "file"),
        ("fm10_readiness_fp_exists_chain", paths.fm10_readiness_fp_rel, "file"),
    ]
    for check_id, rel, kind in presence_specs:
        abs_path = _abs(rel, base_dir=base_dir)
        present = os.path.isfile(abs_path)
        rows.append(
            _row(
                check_id=check_id,
                layer="seal_chain_continuity",
                path=rel,
                expected=f"{kind}_present",
                observed=f"present={present}",
                ok=present,
            )
        )
        checks[check_id] = present

    wall_fp: Dict[str, Any] = {}
    wall_path = _abs(paths.fm06_wall_fingerprint_rel, base_dir=base_dir)
    if os.path.isfile(wall_path):
        wall_fp = load_json(wall_path)
    wall_sha = str(
        (wall_fp.get("fingerprint") or {}).get("fingerprint_sha256")
        or wall_fp.get("fingerprint_sha256")
        or ""
    )
    wall_ok = wall_sha == FROZEN_WALL_FP_SHA256
    checks["seal_chain_wall_fp_anchor"] = wall_ok
    rows.append(
        _row(
            check_id="seal_chain_wall_fp_anchor",
            layer="seal_chain_continuity",
            path=paths.fm06_wall_fingerprint_rel,
            expected=FROZEN_WALL_FP_SHA256,
            observed=wall_sha or "missing",
            ok=wall_ok,
        )
    )

    drift_seal: Dict[str, Any] = {}
    drift_path = _abs(paths.fm07_drift_seal_rel, base_dir=base_dir)
    if os.path.isfile(drift_path):
        drift_seal = load_json(drift_path)
    drift_ok = (
        str(drift_seal.get("frozen_wall_fingerprint_sha256") or "")
        == FROZEN_WALL_FP_SHA256
        and str(drift_seal.get("frozen_exclusion_fingerprint_sha256") or "")
        == FROZEN_EXCLUSION_FP_SHA256
        and drift_seal.get("drift_detected") is False
        and str(drift_seal.get("hold_recommendation") or "") == "KEEP_EXECUTE_FALSE"
    )
    checks["seal_chain_fm07_drift_anchor"] = drift_ok
    rows.append(
        _row(
            check_id="seal_chain_fm07_drift_anchor",
            layer="seal_chain_continuity",
            path=paths.fm07_drift_seal_rel,
            expected="wall+excl_frozen;drift=false;KEEP_EXECUTE_FALSE",
            observed=(
                f"wall={drift_seal.get('frozen_wall_fingerprint_sha256')};"
                f"excl={drift_seal.get('frozen_exclusion_fingerprint_sha256')};"
                f"drift={drift_seal.get('drift_detected')};"
                f"hold={drift_seal.get('hold_recommendation')}"
            ),
            ok=drift_ok,
        )
    )

    boundary_fp: Dict[str, Any] = {}
    boundary_path = _abs(paths.fm08_boundary_fp_rel, base_dir=base_dir)
    if os.path.isfile(boundary_path):
        boundary_fp = load_json(boundary_path)
    boundary_sha = str(
        (boundary_fp.get("fingerprint") or {}).get("fingerprint_sha256")
        or boundary_fp.get("fingerprint_sha256")
        or ""
    )
    boundary_ok = boundary_sha == FROZEN_BOUNDARY_FP_SHA256
    checks["seal_chain_boundary_fp_anchor"] = boundary_ok
    rows.append(
        _row(
            check_id="seal_chain_boundary_fp_anchor",
            layer="seal_chain_continuity",
            path=paths.fm08_boundary_fp_rel,
            expected=FROZEN_BOUNDARY_FP_SHA256,
            observed=boundary_sha or "missing",
            ok=boundary_ok,
        )
    )

    att_fp: Dict[str, Any] = {}
    att_path = _abs(paths.fm09_attestation_fp_rel, base_dir=base_dir)
    if os.path.isfile(att_path):
        att_fp = load_json(att_path)
    att_sha = str(
        (att_fp.get("fingerprint") or {}).get("fingerprint_sha256")
        or att_fp.get("fingerprint_sha256")
        or ""
    )
    att_ok = att_sha == FROZEN_ATTESTATION_FP_SHA256
    checks["seal_chain_attestation_fp_anchor"] = att_ok
    rows.append(
        _row(
            check_id="seal_chain_attestation_fp_anchor",
            layer="seal_chain_continuity",
            path=paths.fm09_attestation_fp_rel,
            expected=FROZEN_ATTESTATION_FP_SHA256,
            observed=att_sha or "missing",
            ok=att_ok,
        )
    )

    readiness_fp: Dict[str, Any] = {}
    readiness_path = _abs(paths.fm10_readiness_fp_rel, base_dir=base_dir)
    if os.path.isfile(readiness_path):
        readiness_fp = load_json(readiness_path)
    readiness_sha = str(
        (readiness_fp.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    readiness_ok = readiness_sha == FROZEN_READINESS_FP_SHA256
    checks["seal_chain_readiness_fp_anchor"] = readiness_ok
    rows.append(
        _row(
            check_id="seal_chain_readiness_fp_anchor",
            layer="seal_chain_continuity",
            path=paths.fm10_readiness_fp_rel,
            expected=FROZEN_READINESS_FP_SHA256,
            observed=readiness_sha or "missing",
            ok=readiness_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="seal_chain_continuity_all_pass",
            layer="seal_chain_continuity",
            expected="MOCK8-12_zero_drift",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["seal_chain_continuity_all_pass"] = all_ok
    return rows, checks


def build_decision_await_hold_seal_rows(
    *,
    paths: DecisionAwaitContinuityPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[
    List[Dict[str, str]],
    Dict[str, bool],
    Dict[str, Any],
    Dict[str, Any],
    Dict[str, Any],
]:
    """
    decision-await hold seal：

    - FM10 packet/checklist/seal 仍 KEEP_EXECUTE_FALSE
    - decision_status 仍 AWAITING_HUMAN_EXECUTE_DECISION
    - Option A HOLD 仍推荐 · Option B 未自动应用
    - 明确 idle_not_required_while_awaiting（不得仅因 awaiting 而 IDLE）
    """
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    packet: Dict[str, Any] = {}
    checklist: Dict[str, Any] = {}
    seal: Dict[str, Any] = {}

    packet_path = _abs(paths.fm10_packet_rel, base_dir=base_dir)
    if os.path.isfile(packet_path):
        packet = load_json(packet_path)
    checklist_path = _abs(paths.fm10_checklist_rel, base_dir=base_dir)
    if os.path.isfile(checklist_path):
        checklist = load_json(checklist_path)
    seal_path = _abs(paths.fm10_seal_rel, base_dir=base_dir)
    if os.path.isfile(seal_path):
        seal = load_json(seal_path)

    def _hold_ok(
        src: Dict[str, Any],
        prefix: str,
        path: str,
        *,
        require_human_action: bool = True,
    ) -> None:
        execute = src.get("execute_production_snapshot_rebuild", None)
        approved = src.get("approved_for_snapshot_rebuild", None)
        hold = str(src.get("hold_recommendation") or "").strip()
        human = src.get("human_action_required_for_execute", None)

        execute_ok = execute is False
        checks[f"{prefix}_execute_false"] = execute_ok
        rows.append(
            _row(
                check_id=f"{prefix}_execute_false",
                layer="decision_await_hold_seal",
                path=path,
                expected="false",
                observed=str(execute).lower() if execute is not None else "missing",
                ok=execute_ok,
            )
        )

        approved_ok = approved is False
        checks[f"{prefix}_approved_false"] = approved_ok
        rows.append(
            _row(
                check_id=f"{prefix}_approved_false",
                layer="decision_await_hold_seal",
                expected="false",
                observed=str(approved).lower() if approved is not None else "missing",
                ok=approved_ok,
            )
        )

        hold_ok = hold == "KEEP_EXECUTE_FALSE"
        checks[f"{prefix}_keep_execute_false"] = hold_ok
        rows.append(
            _row(
                check_id=f"{prefix}_keep_execute_false",
                layer="decision_await_hold_seal",
                expected="KEEP_EXECUTE_FALSE",
                observed=hold or "missing",
                ok=hold_ok,
            )
        )

        if require_human_action:
            human_ok = human is True
            checks[f"{prefix}_human_action_required"] = human_ok
            rows.append(
                _row(
                    check_id=f"{prefix}_human_action_required",
                    layer="decision_await_hold_seal",
                    expected="true",
                    observed=str(human).lower() if human is not None else "missing",
                    ok=human_ok,
                )
            )

    _hold_ok(packet, "fm10_packet", paths.fm10_packet_rel)
    # checklist 无 human_action_required 字段；只核验 execute/approved/hold
    _hold_ok(
        checklist,
        "fm10_checklist",
        paths.fm10_checklist_rel,
        require_human_action=False,
    )
    _hold_ok(seal, "fm10_seal", paths.fm10_seal_rel)

    status = str(packet.get("decision_status") or "").strip()
    status_ok = status == "AWAITING_HUMAN_EXECUTE_DECISION"
    checks["awaiting_decision_status"] = status_ok
    rows.append(
        _row(
            check_id="awaiting_decision_status",
            layer="decision_await_hold_seal",
            path=paths.fm10_packet_rel,
            expected="AWAITING_HUMAN_EXECUTE_DECISION",
            observed=status or "missing",
            ok=status_ok,
        )
    )

    option_a = str(packet.get("decision_option_a") or "").strip()
    option_a_rec = packet.get("decision_option_a_recommended", None)
    option_b_auto = packet.get("decision_option_b_auto_applied", None)
    options_ok = (
        option_a == "HOLD_KEEP_EXECUTE_FALSE"
        and option_a_rec is True
        and option_b_auto is False
    )
    checks["option_a_hold_still_recommended"] = options_ok
    rows.append(
        _row(
            check_id="option_a_hold_still_recommended",
            layer="decision_await_hold_seal",
            expected="OPTION_A_HOLD recommended; OPTION_B not auto",
            observed=(
                f"a={option_a or 'missing'};rec={option_a_rec};"
                f"b_auto={option_b_auto}"
            ),
            ok=options_ok,
        )
    )

    # 本包硬常量：不得因 awaiting 而 IDLE；仍 KEEP_EXECUTE_FALSE
    idle_not_required = True
    checks["idle_not_required_while_awaiting"] = idle_not_required
    rows.append(
        _row(
            check_id="idle_not_required_while_awaiting",
            layer="decision_await_hold_seal",
            expected="idle_forbidden_solely_because_awaiting",
            observed="continuity_package_shipped",
            ok=idle_not_required,
            notes="do_not_idle_solely_because_execute_awaits_human",
        )
    )

    self_ok = True
    checks["fm11_self_constants_hold"] = self_ok
    rows.append(
        _row(
            check_id="fm11_self_constants_hold",
            layer="decision_await_hold_seal",
            expected="execute=false;approved=false",
            observed="execute=false;approved=false",
            ok=self_ok,
            notes="c_fm11_hard_constants",
        )
    )

    claims_ok = (
        packet.get("verified_claim_forbidden") is True
        and packet.get("production_ready_claim_forbidden") is True
        and seal.get("verified_claim_forbidden") is True
        and seal.get("production_ready_claim_forbidden") is True
    )
    checks["claims_still_forbidden"] = claims_ok
    rows.append(
        _row(
            check_id="claims_still_forbidden",
            layer="decision_await_hold_seal",
            expected="verified+production_ready forbidden",
            observed=f"claims_ok={claims_ok}",
            ok=claims_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="decision_await_hold_seal_all_pass",
            layer="decision_await_hold_seal",
            expected="awaiting_hold_continuity_sealed",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["decision_await_hold_seal_all_pass"] = all_ok
    return rows, checks, packet, checklist, seal


def build_protected_csv_registry_rows(
    *,
    csv_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected_output_roots.csv 注册一致性（含 MOCK13）。"""
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
        path = ""
        if present:
            path = str(by_id[root_id].get("path_pattern") or "").strip()
        check_id = f"protected_csv_has_{root_id}"
        rows.append(
            _row(
                check_id=check_id,
                layer="protected_csv_registry",
                path=path,
                expected="listed_in_protected_csv",
                observed=f"present={present}",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )
        checks[check_id] = present

    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_policy = str(auth.get("write_policy") or "").strip()
    auth_ok = auth_policy == "read_only_no_overwrite"
    checks["protected_csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="protected_csv_auth1_readonly",
            layer="protected_csv_registry",
            path=str(auth.get("path_pattern") or ""),
            expected="write_policy=read_only_no_overwrite",
            observed=f"write_policy={auth_policy or 'missing'}",
            ok=auth_ok,
        )
    )

    mock12 = by_id.get("C-ROOT-MOCK12") or {}
    mock12_path = str(mock12.get("path_pattern") or "").strip().rstrip("/")
    mock12_ok = mock12_path == FM10_MOCK_ROOT_REL
    checks["protected_csv_mock12_path"] = mock12_ok
    rows.append(
        _row(
            check_id="protected_csv_mock12_path",
            layer="protected_csv_registry",
            path=mock12_path,
            expected=FM10_MOCK_ROOT_REL,
            observed=mock12_path or "missing",
            ok=mock12_ok,
        )
    )

    mock13 = by_id.get("C-ROOT-MOCK13") or {}
    mock13_path = str(mock13.get("path_pattern") or "").strip().rstrip("/")
    mock13_ok = mock13_path == DEFAULT_MOCK_OUTPUT_ROOT_REL
    checks["protected_csv_mock13_path"] = mock13_ok
    rows.append(
        _row(
            check_id="protected_csv_mock13_path",
            layer="protected_csv_registry",
            path=mock13_path,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=mock13_path or "missing",
            ok=mock13_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-13+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["protected_csv_registry_all_pass"] = all_ok
    return rows, checks


def write_continuity_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CONTINUITY_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CONTINUITY_MATRIX_FIELDS})


def fingerprint_continuity_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """decision-await continuity 矩阵结构指纹。"""
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


def run_pre_execute_decision_await_hold_continuity(
    *,
    paths: DecisionAwaitContinuityPaths = DecisionAwaitContinuityPaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-11 pre-EXECUTE decision-await hold continuity（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_decision_await_continuity_output_root(
        paths.output_root_rel, base_dir=base_dir
    )

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))
    fm06 = load_json(_abs(paths.fm06_gate_json_rel, base_dir=base_dir))
    fm07 = load_json(_abs(paths.fm07_gate_json_rel, base_dir=base_dir))
    fm08 = load_json(_abs(paths.fm08_gate_json_rel, base_dir=base_dir))
    fm09 = load_json(_abs(paths.fm09_gate_json_rel, base_dir=base_dir))
    fm10 = load_json(_abs(paths.fm10_gate_json_rel, base_dir=base_dir))

    bat_rows, bat_checks = build_fm01_to_10_gate_battery_rows(
        fm01=fm01,
        fm02=fm02,
        fm03=fm03,
        fm04=fm04,
        fm05=fm05,
        fm06=fm06,
        fm07=fm07,
        fm08=fm08,
        fm09=fm09,
        fm10=fm10,
    )
    presence_rows, presence_checks = build_fm10_artifact_presence_rows(
        paths=paths, base_dir=base_dir
    )

    probe_rel = f"{_rel(out_root, base_dir=base_dir).rstrip('/')}/fm10_recompute_probe"
    frozen_file_fp, recomputed_fp = recompute_readiness_fingerprint(
        probe_output_root_rel=probe_rel, base_dir=base_dir
    )
    drift_rows, drift_checks = build_readiness_fingerprint_drift_rows(
        paths=paths,
        frozen_file_fp=frozen_file_fp,
        recomputed_fp=recomputed_fp,
        base_dir=base_dir,
    )
    chain_rows, chain_checks = build_seal_chain_continuity_rows(
        paths=paths, base_dir=base_dir
    )
    seal_rows, seal_checks, packet, checklist, fm10_seal = (
        build_decision_await_hold_seal_rows(paths=paths, base_dir=base_dir)
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )

    matrix = (
        bat_rows
        + presence_rows
        + drift_rows
        + chain_rows
        + seal_rows
        + csv_rows
    )
    layer_gates = {
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "fm10_artifact_presence": (
            "PASS_OFFLINE"
            if all(presence_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "readiness_fingerprint_drift": (
            "PASS_OFFLINE" if all(drift_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "seal_chain_continuity": (
            "PASS_OFFLINE" if all(chain_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "decision_await_hold_seal": (
            "PASS_OFFLINE" if all(seal_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "protected_csv_registry": (
            "PASS_OFFLINE" if all(csv_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
    }
    overall = (
        "PASS_OFFLINE"
        if all(g == "PASS_OFFLINE" for g in layer_gates.values())
        else "FAIL_REVIEW_REQUIRED"
    )

    matrix_path = os.path.join(out_root, "continuity_matrix.csv")
    write_continuity_matrix_csv(matrix, matrix_path)
    fp = fingerprint_continuity_matrix(matrix)
    fp_path = os.path.join(out_root, "continuity_fingerprint.json")
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
                "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
                "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
                "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
                "frozen_attestation_fingerprint_sha256": FROZEN_ATTESTATION_FP_SHA256,
                "frozen_readiness_fingerprint_sha256": FROZEN_READINESS_FP_SHA256,
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
                "fm05_gate": fm05.get("gate"),
                "fm06_gate": fm06.get("gate"),
                "fm07_gate": fm07.get("gate"),
                "fm08_gate": fm08.get("gate"),
                "fm09_gate": fm09.get("gate"),
                "fm10_gate": fm10.get("gate"),
                "fm11_gate": overall,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    continuity_packet = {
        "packet_kind": "pre_execute_decision_await_hold_continuity",
        "task_id": TASK_ID,
        "generated_at": generated_at,
        "gate": overall,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "human_action_required_for_execute": True,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "ready_for_commit": overall == "PASS_OFFLINE",
        "ready_for_execute": False,
        "controller_action": "DECISION_AWAIT_HOLD_CONTINUITY_ONLY",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "decision_option_a": "HOLD_KEEP_EXECUTE_FALSE",
        "decision_option_a_recommended": True,
        "decision_option_b": "APPROVE_EXECUTE_REQUIRES_HUMAN",
        "decision_option_b_auto_applied": False,
        "idle_not_required_while_awaiting": True,
        "verified_claim_forbidden": True,
        "production_ready_claim_forbidden": True,
        "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
        "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
        "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
        "frozen_attestation_fingerprint_sha256": FROZEN_ATTESTATION_FP_SHA256,
        "frozen_readiness_fingerprint_sha256": FROZEN_READINESS_FP_SHA256,
        "layer_gates": layer_gates,
        "notes": (
            "本包在 C-FM-10 commit 后、人批 EXECUTE 决策等待期间做 hold continuity："
            "FM-01..10 battery · MOCK12 readiness 零漂移 · MOCK8–12 seal-chain · "
            "KEEP_EXECUTE_FALSE · AWAITING_HUMAN_EXECUTE_DECISION · "
            "明确不得仅因 awaiting 而 IDLE；不覆盖 MOCK8–12；"
            "不翻转 approved_for_snapshot_rebuild；本 executor 不 commit/push。"
        ),
    }
    continuity_path = os.path.join(
        out_root, "decision_await_hold_continuity_packet.json"
    )
    with open(continuity_path, "w", encoding="utf-8") as fh:
        json.dump(continuity_packet, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    seal_path = os.path.join(out_root, "decision_await_continuity_seal_packet.json")
    seal_packet = {
        "packet_kind": "pre_execute_decision_await_continuity_seal",
        "task_id": TASK_ID,
        "generated_at": generated_at,
        "gate": overall,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "human_action_required_for_execute": True,
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "drift_detected": False if overall == "PASS_OFFLINE" else True,
        "idle_not_required_while_awaiting": True,
        "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
        "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
        "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
        "frozen_attestation_fingerprint_sha256": FROZEN_ATTESTATION_FP_SHA256,
        "frozen_readiness_fingerprint_sha256": FROZEN_READINESS_FP_SHA256,
        "recomputed_readiness_fingerprint_sha256": str(
            recomputed_fp.get("fingerprint_sha256") or ""
        ),
        "layer_gates": layer_gates,
        "verified_claim_forbidden": True,
        "production_ready_claim_forbidden": True,
        "notes": (
            "本包仅复核 C-FM-10 readiness 指纹零漂移并 seal decision-await hold "
            "continuity；不覆盖 MOCK8–12；不翻转 approved；"
            "生产 snapshot EXECUTE 仍须独立人批。"
        ),
    }
    with open(seal_path, "w", encoding="utf-8") as fh:
        json.dump(seal_packet, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "layer_gates": layer_gates,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "continuity_packet_path": _rel(continuity_path, base_dir=base_dir),
        "continuity_packet": continuity_packet,
        "seal_packet_path": _rel(seal_path, base_dir=base_dir),
        "seal_packet": seal_packet,
        "fm10_readiness_packet": packet,
        "fm10_checklist": checklist,
        "fm10_seal_packet": fm10_seal,
        "frozen_file_readiness_fingerprint": frozen_file_fp,
        "recomputed_readiness_fingerprint": recomputed_fp,
        "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
        "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
        "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
        "frozen_attestation_fingerprint_sha256": FROZEN_ATTESTATION_FP_SHA256,
        "frozen_readiness_fingerprint_sha256": FROZEN_READINESS_FP_SHA256,
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "fm05_gate_json": paths.fm05_gate_json_rel,
            "fm06_gate_json": paths.fm06_gate_json_rel,
            "fm07_gate_json": paths.fm07_gate_json_rel,
            "fm08_gate_json": paths.fm08_gate_json_rel,
            "fm09_gate_json": paths.fm09_gate_json_rel,
            "fm10_gate_json": paths.fm10_gate_json_rel,
            "fm06_mock_root": paths.fm06_mock_root_rel,
            "fm07_mock_root": paths.fm07_mock_root_rel,
            "fm08_mock_root": paths.fm08_mock_root_rel,
            "fm09_mock_root": paths.fm09_mock_root_rel,
            "fm10_mock_root": paths.fm10_mock_root_rel,
            "fm10_readiness_matrix": paths.fm10_readiness_matrix_rel,
            "fm10_readiness_fingerprint": paths.fm10_readiness_fp_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
    }

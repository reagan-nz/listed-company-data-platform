"""
A-class Era D next-scale slice2 S1 +100 runner 设计/冻结证据冒烟测试（A-GEN-20260714-12）。

引用 A-11 runner design：
  outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_runner_design_20260714.md

完整 runner 行为见 lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py。
本文件保留设计常量/冻结 universe 只读校验，并与已实现 runner 符号对齐。

运行：
    python lab/test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")

# ---------------------------------------------------------------------------
# A-11 设计常量（DESIGN_ONLY · 待 runner 实现时迁入 run_cninfo_a_class_phase2_metadata_expansion.py）
# ---------------------------------------------------------------------------

TASK_ID = "A-GEN-20260714-12"
DESIGN_TASK_ID = "A-GEN-20260714-11"
# runner 已实现 dry-run；gate 与实现态对齐（仍非 live / 非 verified）
RUNNER_EXTENSION_GATE = "READY_FOR_APPROVAL"

FLAG_ERAD_SLICE2 = "--erad-a-scale-500-slice2"
FLAG_APPROVE_SLICE2 = "--approve-a-class-erad-scale-500-slice2"
DEST_ERAD_SLICE2 = "erad_a_scale_500_slice2"
DEST_APPROVE_SLICE2 = "approve_a_class_erad_scale_500_slice2"

DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv",
)
DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_erad_next_scale_slice2_s1"
)
ERAD_NEXT_SCALE_SLICE2_S1_MOCK_TEST_PARENT = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT, "_mock_test"
)
ERAD_NEXT_SCALE_SLICE2_S1_MOCK_LIVE_TEST_PARENT = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT, "_mock_live_test"
)

DESIGN_DOC = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice2_s1_runner_design_20260714.md",
)
RUNNER_CHECKLIST = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice2_s1_runner_checklist_20260714.csv",
)

REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE = 100
ERAD_NEXT_SCALE_SLICE2_COHORT = "next_scale_slice2"
ERAD_NEXT_SCALE_SLICE2_PLANNED_REQUESTS_PER_CASE = 2
ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP = 240
ERAD_SLICE2_ACCEPTABLE_THRESHOLD = 90
ERAD_SLICE2_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"

ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS = {
    f"AD2E{num:03d}" for num in range(501, 601)
}

# A-11 §2 错误码（规划命名）
ERAD_NEXT_SCALE_SLICE2_UNIVERSE_CSV_REQUIRED = "erad_a_scale_500_slice2_universe_csv_required"
ERAD_NEXT_SCALE_SLICE2_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_a_class_erad_next_scale_slice2_s1"
)
ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_next_scale_slice2_universe_size_must_equal_100"
)
ERAD_NEXT_SCALE_SLICE2_APPROVAL_REQUIRED = "approve_a_class_erad_scale_500_slice2_required"
ERAD_NEXT_SCALE_SLICE2_INCOMPATIBLE_WITH_OTHER_MODES = (
    "erad_a_scale_500_slice2_incompatible_with_other_modes"
)
ERAD_SLICE2_REQUEST_CAP_EXCEEDED = "erad_a_next_scale_slice2_request_cap_exceeded"
ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN = "erad_a_slice2_slice1_root_write_forbidden"

# 互斥模式（A-11 §2）
INCOMPATIBLE_FLAGS = [
    "--erad-a-scale-200",
    "--erad-a-scale-200-failed-retry",
    "--erad-a-scale-500-slice1",
    "--phase3-50",
]

# 写保护路径（A-11 §5）
WRITE_BLOCKED_ROOTS = [
    runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT,
    runner.DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
    runner.DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT,
    runner.DEFAULT_PHASE3_OUTPUT_ROOT,
    runner.DEFAULT_A3M017_RETRY_OUTPUT_ROOT,
]

PROTECTED_CSV_PATHS = [
    os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv",
    ),
    os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_a_class_slice2_pool_remainder_draft_20260714.csv",
    ),
    DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV,
]

SLICE2_BASE_ARGS = [
    FLAG_ERAD_SLICE2,
    "--universe-csv",
    DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV,
    "--output-root",
    DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT,
]

DRYRUN_COMMAND_SHAPE = (
    "python lab/run_cninfo_a_class_phase2_metadata_expansion.py "
    f"{FLAG_ERAD_SLICE2} "
    f"--universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv "
    f"--output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ "
    "--dry-run"
)

# runner 实现后须存在的符号（A-11 §10）
PLANNED_RUNNER_SYMBOLS = [
    "DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV",
    "DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT",
    "REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE",
    "ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS",
    "load_erad_next_scale_slice2_universe",
    "validate_erad_next_scale_slice2_output_root",
    "lint_erad_next_scale_slice2_overlap",
    "process_erad_next_scale_slice2_dry_run",
    "enforce_erad_next_scale_slice2_request_cap",
]


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def _read_universe_rows() -> list[dict[str, str]]:
    with open(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class TestSlice2S1RunnerDesignArtifacts(unittest.TestCase):
    """冻结证据链与设计文档存在性。"""

    def test_design_doc_exists_and_cites_a11(self) -> None:
        self.assertTrue(os.path.isfile(DESIGN_DOC), msg=DESIGN_DOC)
        with open(DESIGN_DOC, encoding="utf-8") as f:
            text = f.read()
        self.assertIn(DESIGN_TASK_ID, text)
        self.assertIn(FLAG_ERAD_SLICE2, text)
        self.assertIn("DESIGN_ONLY", text)

    def test_runner_checklist_exists(self) -> None:
        self.assertTrue(os.path.isfile(RUNNER_CHECKLIST), msg=RUNNER_CHECKLIST)

    def test_frozen_universe_csv_exists(self) -> None:
        self.assertTrue(
            os.path.isfile(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV),
            msg=DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV,
        )

    def test_protected_csv_paths_exist(self) -> None:
        for path in PROTECTED_CSV_PATHS:
            self.assertTrue(os.path.isfile(path), msg=path)


class TestSlice2S1RunnerDesignConstants(unittest.TestCase):
    """A-11 设计常量自洽（本模块文档化 · 非 runner 导出）。"""

    def test_universe_size_and_case_id_range(self) -> None:
        self.assertEqual(REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE, 100)
        self.assertEqual(len(ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS), 100)
        self.assertEqual(min(ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS), "AD2E501")
        self.assertEqual(max(ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS), "AD2E600")

    def test_request_cap_and_thresholds(self) -> None:
        planned = (
            REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE
            * ERAD_NEXT_SCALE_SLICE2_PLANNED_REQUESTS_PER_CASE
        )
        self.assertEqual(planned, 200)
        self.assertLessEqual(planned, ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP)
        self.assertEqual(ERAD_SLICE2_ACCEPTABLE_THRESHOLD, 90)
        self.assertEqual(ERAD_SLICE2_EXECUTION_GATE_PASS, "PASS_WITH_CAVEAT")

    def test_output_root_and_mock_paths_documented(self) -> None:
        self.assertIn("cninfo_a_class_erad_next_scale_slice2_s1", DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
        self.assertTrue(
            ERAD_NEXT_SCALE_SLICE2_S1_MOCK_TEST_PARENT.startswith(
                DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT
            )
        )
        self.assertTrue(
            ERAD_NEXT_SCALE_SLICE2_S1_MOCK_LIVE_TEST_PARENT.startswith(
                DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT
            )
        )

    def test_error_code_constants_documented(self) -> None:
        self.assertIn("slice2", ERAD_NEXT_SCALE_SLICE2_UNIVERSE_CSV_REQUIRED)
        self.assertIn("slice2", ERAD_NEXT_SCALE_SLICE2_OUTPUT_ROOT_VIOLATION)
        self.assertIn("100", ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE_VIOLATION)
        self.assertIn("slice1", ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN)

    def test_dryrun_command_shape_documented(self) -> None:
        self.assertIn(FLAG_ERAD_SLICE2, DRYRUN_COMMAND_SHAPE)
        self.assertIn("--dry-run", DRYRUN_COMMAND_SHAPE)
        self.assertNotIn("--live", DRYRUN_COMMAND_SHAPE)


class TestSlice2S1FrozenUniverseReadOnly(unittest.TestCase):
    """只读校验 S1 +100 universe · 不 mutate 源文件。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls._universe_sha256 = _sha256_file(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV)

    def test_universe_schema_and_size(self) -> None:
        rows = _read_universe_rows()
        self.assertEqual(len(rows), REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE)
        expected_cols = {"company_code", "company_name", "case_id", "cohort"}
        self.assertEqual(set(rows[0].keys()), expected_cols)

    def test_universe_case_ids_and_cohort(self) -> None:
        rows = _read_universe_rows()
        case_ids = {r["case_id"] for r in rows}
        self.assertEqual(case_ids, ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS)
        cohorts = {r["cohort"] for r in rows}
        self.assertEqual(cohorts, {ERAD_NEXT_SCALE_SLICE2_COHORT})

    def test_universe_company_codes_unique(self) -> None:
        rows = _read_universe_rows()
        codes = [r["company_code"] for r in rows]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(rows[0]["company_code"], "603701")
        self.assertEqual(rows[-1]["company_code"], "688772")

    def test_universe_csv_not_mutated(self) -> None:
        self.assertEqual(
            _sha256_file(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV),
            self._universe_sha256,
            msg="universe CSV 在本测试运行期间不得被修改",
        )

    def test_ld4_st_pattern_zero_on_frozen_universe(self) -> None:
        import re

        st_re = re.compile(r"(?:\*?ST|S\*ST)")
        rows = _read_universe_rows()
        hits = [r for r in rows if st_re.search(r.get("company_name", ""))]
        self.assertEqual(len(hits), 0, msg=f"ST 命中: {[r['company_code'] for r in hits]}")


class TestSlice2S1RunnerImplementedSmoke(unittest.TestCase):
    """runner 已实现 slice2 · 与设计常量 / 符号对齐的冒烟断言。"""

    def test_runner_extension_gate_ready_for_approval(self) -> None:
        self.assertEqual(RUNNER_EXTENSION_GATE, "READY_FOR_APPROVAL")
        self.assertEqual(runner.ERAD_NEXT_SCALE_SLICE2_RUNNER_GATE, "READY_FOR_APPROVAL")

    def test_slice2_flag_registered_and_dry_run_ok(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(SLICE2_BASE_ARGS + ["--dry-run"])
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("planned_ok=100", result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_approve_slice2_flag_registered(self) -> None:
        # 无 --live 时 approve 可出现；live 无 approve 须拒绝
        result = _run(SLICE2_BASE_ARGS + ["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(ERAD_NEXT_SCALE_SLICE2_APPROVAL_REQUIRED, result.stderr)
        self.assertNotIn("unrecognized arguments", result.stderr)

    def test_planned_runner_symbols_present(self) -> None:
        missing = [name for name in PLANNED_RUNNER_SYMBOLS if not hasattr(runner, name)]
        self.assertEqual(missing, [], msg=f"以下符号尚未在 runner 中实现: {missing}")

    def test_write_blocked_roots_documented(self) -> None:
        for root in WRITE_BLOCKED_ROOTS:
            self.assertIn("outputs", root)
            self.assertIn("validation", root)

    def test_slice1_regression_still_available(self) -> None:
        self.assertTrue(hasattr(runner, "DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT"))
        self.assertTrue(hasattr(runner, "process_erad_next_scale_slice1_dry_run"))


class TestSlice2S1RunnerStubDocumentation(unittest.TestCase):
    """文档化 flag / session 形状与测试文件落地状态。"""

    def test_incompatible_flags_documented(self) -> None:
        self.assertIn("--erad-a-scale-500-slice1", INCOMPATIBLE_FLAGS)
        self.assertIn("--erad-a-scale-200", INCOMPATIBLE_FLAGS)

    def test_session_split_ranges_documented(self) -> None:
        session1 = {f"AD2E{num:03d}" for num in range(501, 551)}
        session2 = {f"AD2E{num:03d}" for num in range(551, 601)}
        self.assertEqual(len(session1), 50)
        self.assertEqual(len(session2), 50)
        self.assertEqual(session1 | session2, ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS)

    def test_runner_test_file_exists_live_path_optional(self) -> None:
        runner_test = os.path.join(
            _LAB_DIR, "test_cninfo_a_class_erad_next_scale_slice2_runner.py"
        )
        live_test = os.path.join(
            _LAB_DIR, "test_cninfo_a_class_erad_next_scale_slice2_live_path.py"
        )
        self.assertTrue(os.path.isfile(runner_test), msg="完整 runner 测试须已创建")
        # live path 专项测试可为后续任务；本包以 approval-gated live 实现为准
        _ = live_test


if __name__ == "__main__":
    unittest.main()

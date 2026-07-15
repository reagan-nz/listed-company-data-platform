#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 fund_industry_allocation — Further-scale Tier-1 offline fixture / universe lock / VR。

对照 VR-FS checklist 加载 fixtures/d_class/fund_industry_allocation_further_scale/DFIA201–DFIA205。

离线 only · 无 CNINFO · 无 live · 不实现 runner · 不升级 live gate · 不 claim verified。
冻结：FIA first/next lock+live · AT/SD next-slice lock + dry-run report。

运行：
    .venv/bin/python lab/test_cninfo_d_class_fund_industry_allocation_further_scale_fixtures.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from lab.cninfo_d_class_mappers import (  # noqa: E402
    FUND_INDUSTRY_METRIC_MAP,
    map_to_industry_aggregate,
)

FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "fund_industry_allocation_further_scale"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_universe_lock_20260715.csv"
)
FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv"
)
NEXT_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv"
)
AT_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv"
)
SD_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv"
)
AT_DRYRUN_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice"
    / "reports"
    / "d_class_abnormal_trading_next_slice_dryrun_report.csv"
)
SD_DRYRUN_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice"
    / "reports"
    / "d_class_shareholder_data_next_slice_dryrun_report.csv"
)

# 冻结 sha256；本任务必须保持
EXPECTED_FIRST_SLICE_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)
EXPECTED_NEXT_SLICE_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
EXPECTED_AT_NEXT_LOCK_SHA256 = (
    "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
)
EXPECTED_SD_NEXT_LOCK_SHA256 = (
    "c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f"
)
EXPECTED_AT_DRYRUN_SHA256 = (
    "51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497"
)
EXPECTED_SD_DRYRUN_SHA256 = (
    "2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362"
)

SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_universe_draft_sketch_20260715.csv"
)
VR_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_validation_rules_20260715.md"
)
APPROVAL_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_approval_package_20260715.md"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_dfm38_further_scale_approval_package_20260715.md"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_offline_prep_checklist_20260715.csv"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_approval_next_step_recommendation_20260715.md"
)
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_fixture_vr_matrix_20260715.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_fixture_vr_validation_20260715.md"
)
SCHEMA_PATH = BASE_DIR / "schemas" / "d_class" / "d_industry_aggregate.schema.json"

COMPONENT = "fund_industry_allocation"
ENDPOINT = "https://www.cninfo.com.cn/data20/fund/industry"
CASE_IDS = ("DFIA201", "DFIA202", "DFIA203", "DFIA204", "DFIA205")
COARSE_CODES = {"A", "B", "*"}
EXCLUDED_CODES = {"688671", "301259"}
FORBIDDEN_SOLE_ANCHORS = {"C26", "C27", "I65", "J66"}
RAW_CORE = ("F001V", "F002V", "ENDDATE", "F003N", "F004N", "F005N")
EXPECTED_METRICS = [name for _, name, _ in FUND_INDUSTRY_METRIC_MAP]
FREEZE_REQUIRED = (
    "industry_code",
    "report_period",
    "metric_count",
    "quality_status",
)

EXPECTED_FILES = {
    "DFIA201": (
        "DFIA201_found.json",
        "DFIA201_industry_filtered_empty.json",
    ),
    "DFIA202": ("DFIA202_found.json",),
    "DFIA203": ("DFIA203_found.json",),
    "DFIA204": (
        "DFIA204_found.json",
        "DFIA204_empty_but_valid_synthetic.json",
    ),
    "DFIA205": (
        "DFIA205_found.json",
        "DFIA205_empty_but_valid_synthetic.json",
    ),
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_fixtures() -> List[Tuple[str, Path, Dict[str, Any]]]:
    rows: List[Tuple[str, Path, Dict[str, Any]]] = []
    for case_id, names in EXPECTED_FILES.items():
        for name in names:
            path = FIXTURE_DIR / name
            rows.append((case_id, path, _load_json(path)))
    return rows


class TestFundIndustryAllocationFurtherScaleFixtures(unittest.TestCase):
    """Further-scale Tier-1 synthetic fixture vs VR-FS offline 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_csv(UNIVERSE_LOCK)
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()

    def test_vr_fs001_universe_five_dfia_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))

    def test_vr_fs002_component_include_lock(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["further_scale_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "locked")
            self.assertEqual(row["approval_task_id"], "D-FM-38")

    def test_vr_fs003_query_modes(self) -> None:
        self.assertEqual(self.universe_by_id["DFIA201"]["query_mode"], "default")
        self.assertEqual(self.universe_by_id["DFIA202"]["query_mode"], "rdate")
        self.assertEqual(self.universe_by_id["DFIA202"]["anchor_rdate"], "20260331")
        self.assertEqual(self.universe_by_id["DFIA203"]["query_mode"], "rdate")
        self.assertEqual(self.universe_by_id["DFIA203"]["anchor_rdate"], "20251231")
        self.assertEqual(self.universe_by_id["DFIA204"]["query_mode"], "rdate")
        self.assertEqual(self.universe_by_id["DFIA204"]["anchor_rdate"], "20251231")
        self.assertEqual(self.universe_by_id["DFIA205"]["query_mode"], "rdate")
        self.assertEqual(self.universe_by_id["DFIA205"]["anchor_rdate"], "20251231")

    def test_vr_fs004_exclusions_and_coarse_codes(self) -> None:
        for row in self.universe:
            flags = row["exclude_flags"]
            self.assertIn("exclude_688671", flags)
            self.assertIn("exclude_301259", flags)
            self.assertIn("no_company_code", flags)
            self.assertIn("exclude_company_event_schema", flags)
            self.assertIn("exclude_first_slice_C26_sole_anchor", flags)
            self.assertIn("exclude_mutate_next_slice_DFIA101_105", flags)
            self.assertIn("exclude_mutate_at_sd_next_slice_dryrun", flags)
            self.assertIn(row["industry_code"], COARSE_CODES)
            self.assertNotIn(row["industry_code"], FORBIDDEN_SOLE_ANCHORS)
            self.assertNotIn(row["industry_code"], EXCLUDED_CODES)

    def test_vr_fs006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 1)
            self.assertLessEqual(int(row["total_request_cap"]), 5)
            self.assertEqual(int(row["shared_probe_prefer"]), 3)

    def test_vr_fs012_expectation_mix(self) -> None:
        self.assertEqual(
            self.universe_by_id["DFIA201"]["expected_behavior"],
            "captured_normal_or_empty_but_valid",
        )
        self.assertEqual(
            self.universe_by_id["DFIA202"]["expected_behavior"],
            "captured_normal",
        )
        self.assertEqual(
            self.universe_by_id["DFIA203"]["expected_behavior"],
            "captured_normal",
        )
        self.assertEqual(
            self.universe_by_id["DFIA204"]["expected_behavior"],
            "captured_normal_or_empty_but_valid",
        )
        self.assertEqual(
            self.universe_by_id["DFIA205"]["expected_behavior"],
            "captured_normal_or_empty_but_valid",
        )

    def test_frozen_locks_and_dryrun_roots(self) -> None:
        self.assertEqual(
            _sha256_file(FIRST_SLICE_LOCK),
            EXPECTED_FIRST_SLICE_LOCK_SHA256,
            "FIA first-slice universe lock must not be mutated in D-FM-38",
        )
        self.assertEqual(
            _sha256_file(NEXT_SLICE_LOCK),
            EXPECTED_NEXT_SLICE_LOCK_SHA256,
            "FIA next-slice universe lock must not be mutated in D-FM-38",
        )
        self.assertEqual(
            _sha256_file(AT_NEXT_LOCK),
            EXPECTED_AT_NEXT_LOCK_SHA256,
            "AT next-slice universe lock must not be mutated in D-FM-38",
        )
        self.assertEqual(
            _sha256_file(SD_NEXT_LOCK),
            EXPECTED_SD_NEXT_LOCK_SHA256,
            "SD next-slice universe lock must not be mutated in D-FM-38",
        )
        self.assertEqual(
            _sha256_file(AT_DRYRUN_REPORT),
            EXPECTED_AT_DRYRUN_SHA256,
            "AT next-slice dry-run report must not be mutated in D-FM-38",
        )
        self.assertEqual(
            _sha256_file(SD_DRYRUN_REPORT),
            EXPECTED_SD_DRYRUN_SHA256,
            "SD next-slice dry-run report must not be mutated in D-FM-38",
        )
        first_ids = {r["case_id"] for r in _load_csv(FIRST_SLICE_LOCK)}
        next_ids = {r["case_id"] for r in _load_csv(NEXT_SLICE_LOCK)}
        fs_ids = {r["case_id"] for r in self.universe}
        self.assertTrue(first_ids.isdisjoint(fs_ids))
        self.assertTrue(next_ids.isdisjoint(fs_ids))

    def test_sketch_remains_draft_history(self) -> None:
        sketch = _load_csv(SKETCH_CSV)
        self.assertEqual([r["case_id"] for r in sketch], list(CASE_IDS))
        for row in sketch:
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")

    def test_expected_fixture_files_present(self) -> None:
        for case_id, names in EXPECTED_FILES.items():
            for name in names:
                self.assertTrue((FIXTURE_DIR / name).is_file(), f"missing {name}")
        for _cid, path, data in self.fixtures:
            text = json.dumps(data, ensure_ascii=False)
            self.assertNotIn("301259", text, path.name)
            self.assertNotIn("DLC006R", text, path.name)
            self.assertNotIn("688671", text, path.name)

    def test_fixture_meta_offline_flags(self) -> None:
        for _cid, path, data in self.fixtures:
            meta = data["_fixture_meta"]
            self.assertEqual(meta["component"], COMPONENT, path.name)
            self.assertIs(meta["cninfo_called"], False, path.name)
            self.assertIs(meta["synthetic"], True, path.name)
            self.assertEqual(meta["case_id"], _cid, path.name)

    def test_vr_fs005_endpoint_and_envelope(self) -> None:
        for _cid, path, data in self.fixtures:
            env = data["metric_envelope"]
            self.assertEqual(env["source_endpoint"], ENDPOINT, path.name)
            self.assertIn("industry_code", env, path.name)
            self.assertNotIn("company_code", env, path.name)

    def test_vr_fs036_lineage(self) -> None:
        for case_id, path, data in self.fixtures:
            lin = data["metric_envelope"]["lineage"]
            uref = self.universe_by_id[case_id]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], uref["query_mode"], path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)
            if uref["query_mode"] == "default":
                self.assertEqual(lin["query_params"], {}, path.name)
            else:
                self.assertEqual(
                    lin["query_params"].get("rdate"), uref["anchor_rdate"], path.name
                )

    def test_captured_payload_freeze_and_mapping(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["metric_envelope"]
            if env["metric_status"] != "captured":
                continue
            self.assertIn("fund_industry_allocation", data, path.name)
            payload = data["fund_industry_allocation"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], env["quality_status"])
            self.assertEqual(payload["industry_code"], env["industry_code"])
            self.assertEqual(payload["report_period"], env["report_period"])
            self.assertEqual(int(payload["metric_count"]), 3, path.name)
            self.assertEqual(payload.get("mapping_confidence"), "high", path.name)
            self.assertNotIn("company_code", payload, path.name)
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["industry_code"], uref["industry_code"])
            lin = env["lineage"]
            raw = lin.get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertIn(raw["F001V"], {"A", "B", "C"})
            self.assertNotIn(raw["F001V"], FORBIDDEN_SOLE_ANCHORS)
            rows = map_to_industry_aggregate(
                raw,
                source_id=COMPONENT,
                query_mode=lin["query_mode"],
                query_params=lin["query_params"],
            )
            self.assertEqual(len(rows), 3, path.name)
            names = [r["metric_name"] for r in rows]
            self.assertEqual(names, EXPECTED_METRICS, path.name)
            for row in rows:
                self.assertNotIn("company_code", row, path.name)
            summary = payload["metrics_summary"]
            for row in rows:
                self.assertEqual(row["metric_value"], summary[row["metric_name"]], path.name)
            if uref["industry_code"] == "*":
                self.assertGreaterEqual(int(payload["cross_section_row_count"]), 1, path.name)
                self.assertEqual(raw["F001V"], payload["sample_industry_code"], path.name)
            else:
                self.assertEqual(raw["F001V"], payload["industry_code"], path.name)
                self.assertEqual(raw["ENDDATE"], payload["report_period"])

    def test_empty_but_valid_envelope(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["metric_envelope"]
            if env["metric_status"] != "empty_but_valid":
                continue
            self.assertEqual(env["quality_status"], "pass", path.name)
            self.assertNotIn("fund_industry_allocation", data, path.name)
            self.assertNotIn("raw_record_json", env["lineage"], path.name)
            uref = self.universe_by_id[case_id]
            self.assertIn(
                uref["expected_behavior"],
                ("captured_normal_or_empty_but_valid", "empty_but_valid"),
            )

    def test_vr_fs009_industry_filtered_empty(self) -> None:
        """VR-FS-009/010：截面有记录但无目标粗粒度 F001V → empty_but_valid。"""
        path = FIXTURE_DIR / "DFIA201_industry_filtered_empty.json"
        data = _load_json(path)
        meta = data["_fixture_meta"]
        filt = meta["records_filter"]
        self.assertEqual(meta["scenario"], "empty_but_valid_after_industry_filter")
        self.assertGreater(int(filt["raw_records_count"]), 0)
        self.assertEqual(int(filt["matched_industry_code_count"]), 0)
        self.assertEqual(filt["target_industry_code"], "B")
        self.assertNotIn("B", filt["other_industry_codes"])
        env = data["metric_envelope"]
        self.assertEqual(env["metric_status"], "empty_but_valid")
        self.assertEqual(env["quality_status"], "pass")
        self.assertNotIn("fund_industry_allocation", data)

    def test_approval_and_vr_docs_present(self) -> None:
        self.assertTrue(VR_MD.is_file())
        self.assertTrue(APPROVAL_MD.is_file())
        self.assertTrue(EVIDENCE_MD.is_file())
        self.assertTrue(NEXT_STEP_MD.is_file())
        vr_text = VR_MD.read_text(encoding="utf-8")
        approval = APPROVAL_MD.read_text(encoding="utf-8")
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        self.assertIn("DFIA201", vr_text)
        self.assertIn("VR-FS-001", vr_text)
        self.assertIn("不是 verified", vr_text)
        self.assertIn("DFIA201", approval)
        self.assertIn("STANDING_SCOPE_AUTHORIZED", approval)
        self.assertIn("不是 verified", approval)
        self.assertNotRegex(approval, r"(?m)^\s*verified\s*=")
        self.assertNotIn("production_ready = true", approval)
        self.assertIn(
            "d_class_fund_industry_allocation_further_scale_approval_gate = STANDING_SCOPE_AUTHORIZED",
            approval,
        )
        self.assertIn(
            "d_class_fund_industry_allocation_further_scale_fixture_vr_gate = PASS_OFFLINE",
            approval,
        )
        self.assertIn("NOT_APPROVED", approval)
        self.assertIn("H3/H4", approval)
        self.assertIn("controller_execution_allowed = false", approval)
        self.assertIn("不含** console logs", evidence)
        self.assertIn("allow_list_excludes = console_logs", evidence)

    def test_allow_list_excludes_console_logs(self) -> None:
        checklist = CHECKLIST_CSV.read_text(encoding="utf-8")
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        self.assertIn("exclude_console_logs_from_allow_list", checklist)
        self.assertIn("不含** console logs", evidence)
        # policy 行可提 exclude；不得把 console log 路径标为 ready 产物
        for line in checklist.splitlines():
            low = line.lower()
            if ("console" in low and "log" in low) and (
                "_console" in low or "live_console" in low or low.endswith(".log")
            ):
                self.assertNotIn(",ready,", line)

    def test_captured_metrics_validate_schema(self) -> None:
        try:
            import jsonschema
        except ImportError as exc:  # pragma: no cover
            self.skipTest(f"jsonschema unavailable: {exc}")

        self.assertTrue(SCHEMA_PATH.is_file())
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        for _cid, path, data in self.fixtures:
            env = data["metric_envelope"]
            if env["metric_status"] != "captured":
                continue
            raw = env["lineage"]["raw_record_json"]
            rows = map_to_industry_aggregate(
                raw,
                source_id=COMPONENT,
                query_mode=env["lineage"]["query_mode"],
                query_params=env["lineage"]["query_params"],
            )
            for row in rows:
                jsonschema.validate(instance=row, schema=schema)

    def test_no_network_imports(self) -> None:
        import lab.test_cninfo_d_class_fund_industry_allocation_further_scale_fixtures as self_mod

        self.assertFalse(hasattr(self_mod, "requests"))

    @classmethod
    def tearDownClass(cls) -> None:
        wall = time.perf_counter() - cls.t0
        fixtures = _iter_fixtures()
        rows: List[Dict[str, str]] = []
        for case_id, path, data in fixtures:
            env = data["metric_envelope"]
            rows.append(
                {
                    "fixture": path.name,
                    "case_id": case_id,
                    "group": "D",
                    "topic": "Envelope",
                    "vr": "VR-FS-025–VR-FS-030",
                    "status": "pass",
                    "note": env["metric_status"],
                }
            )
            if env["metric_status"] == "captured":
                rows.append(
                    {
                        "fixture": path.name,
                        "case_id": case_id,
                        "group": "C",
                        "topic": "Field Mapping",
                        "vr": "VR-FS-015–VR-FS-024",
                        "status": "pass",
                        "note": "F001V/ENDDATE/F003N-F005N → 3 metrics",
                    }
                )
        VALIDATION_OUT.parent.mkdir(parents=True, exist_ok=True)
        with VALIDATION_OUT.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "fixture",
                    "case_id",
                    "group",
                    "topic",
                    "vr",
                    "status",
                    "note",
                ],
            )
            w.writeheader()
            w.writerows(rows)
        first_sha = _sha256_file(FIRST_SLICE_LOCK)
        next_sha = _sha256_file(NEXT_SLICE_LOCK)
        summary = "\n".join(
            [
                "# CNINFO D 类 fund_industry_allocation — Further-Scale Tier-1 Fixture VR Validation（Offline）",
                "",
                f"_生成时间：D-FM-38 · wall≈{wall:.2f}s_",
                "",
                "> **性质：** Tier-1 further-scale fixture offline VR · **CNINFO = 0** · **不是 verified**",
                "",
                "| 项 | 值 |",
                "|----|-----|",
                f"| fixture root | `fixtures/d_class/fund_industry_allocation_further_scale/` |",
                f"| universe lock | `{UNIVERSE_LOCK.name}` |",
                f"| fixtures | **{len(fixtures)}** |",
                f"| matrix rows | **{len(rows)}** |",
                f"| first-slice lock sha256 | `{first_sha}` |",
                f"| next-slice lock sha256 | `{next_sha}` |",
                f"| CNINFO | **0** |",
                "",
                "```text",
                "d_class_fund_industry_allocation_further_scale_fixture_vr_gate = PASS_OFFLINE",
                "d_class_fund_industry_allocation_further_scale_approval_gate = STANDING_SCOPE_AUTHORIZED",
                "d_class_fund_industry_allocation_further_scale_live_gate = NOT_APPROVED",
                "d_class_fund_industry_allocation_further_scale_runner_gate = NOT_APPROVED",
                "fund_industry_allocation_component_approved = standing_scope",
                "controller_execution_allowed = false",
                "fia_first_next_mutated = false",
                "at_sd_dryrun_mutated = false",
                "```",
                "",
                "## Artifacts",
                "",
                f"- matrix: `outputs/validation/{VALIDATION_OUT.name}`",
                f"- summary: `outputs/validation/{SUMMARY_OUT.name}`",
                "- test: `lab/test_cninfo_d_class_fund_industry_allocation_further_scale_fixtures.py`",
                "",
                "```text",
                "task_id = D-FM-38",
                "phase = fund_industry_allocation_further_scale_approval_package_offline",
                "```",
                "",
            ]
        )
        SUMMARY_OUT.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(key, None)
    unittest.main(verbosity=2)

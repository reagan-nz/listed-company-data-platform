#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 shareholder_data — Tier-1 offline fixture / universe lock / VR 校验。

对照 VR checklist 加载 fixtures/d_class/shareholder_data_first_slice/DSD001–DSD005。

离线 only · 无 CNINFO · 无 live · 不升级 live gate · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_shareholder_data_fixtures.py
"""

from __future__ import annotations

import csv
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
    SHAREHOLDER_DATA_METRIC_MAP,
    map_to_company_metric_periodic,
)

FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "shareholder_data_first_slice"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv"
)
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_fixture_vr_matrix_20260715.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_fixture_vr_validation_20260715.md"
)
SCHEMA_PATH = BASE_DIR / "schemas" / "d_class" / "d_company_metric_periodic.schema.json"

COMPONENT = "shareholder_data"
ENDPOINT = "https://www.cninfo.com.cn/data20/shareholeder/data"
ANCHOR_RDATE = "20260331"
REPORT_PERIOD = "2026-03-31"
CASE_IDS = ("DSD001", "DSD002", "DSD003", "DSD004", "DSD005")
EXCLUDED_CODES = {"688671", "301259"}
RAW_CORE = ("SECCODE", "SECNAME", "ENDDATE", "F001N", "F002N", "F003N", "F004N", "F005N", "F006N")
EXPECTED_METRICS = [name for _, name, _ in SHAREHOLDER_DATA_METRIC_MAP]
FREEZE_REQUIRED = (
    "company_code",
    "report_period",
    "metric_count",
    "quality_status",
)

EXPECTED_FILES = {
    "DSD001": ("DSD001_found.json",),
    "DSD002": ("DSD002_found.json", "DSD002_empty.json"),
    "DSD003": (
        "DSD003_found.json",
        "DSD003_empty.json",
        "DSD003_records_filtered_empty.json",
    ),
    "DSD004": ("DSD004_found.json", "DSD004_empty.json"),
    "DSD005": ("DSD005_empty_but_valid_synthetic.json",),
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_universe() -> List[Dict[str, str]]:
    with UNIVERSE_LOCK.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _iter_fixtures() -> List[Tuple[str, Path, Dict[str, Any]]]:
    rows: List[Tuple[str, Path, Dict[str, Any]]] = []
    for case_id, names in EXPECTED_FILES.items():
        for name in names:
            path = FIXTURE_DIR / name
            rows.append((case_id, path, _load_json(path)))
    return rows


class TestShareholderDataFixtures(unittest.TestCase):
    """Tier-1 synthetic fixture vs VR offline schema 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_universe()
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()

    def test_vr001_universe_five_dsd_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))

    def test_vr002_component_and_include(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["first_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "locked")
            self.assertEqual(row["approval_task_id"], "D-FM-07")

    def test_vr003_shared_rdate_contract(self) -> None:
        for row in self.universe:
            self.assertEqual(row["anchor_rdate"], ANCHOR_RDATE)
        for _cid, path, data in self.fixtures:
            qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(qp["rdate"], ANCHOR_RDATE, path.name)
            lin = data["metric_envelope"]["lineage"]
            self.assertEqual(lin["query_mode"], "rdate_report_period", path.name)
            self.assertEqual(lin["query_params"]["rdate"], ANCHOR_RDATE, path.name)

    def test_vr004_exclusions(self) -> None:
        codes = {r["company_code"] for r in self.universe}
        self.assertTrue(EXCLUDED_CODES.isdisjoint(codes))
        for row in self.universe:
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])

    def test_vr006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 1)
            self.assertLessEqual(int(row["total_request_cap"]), 5)
            self.assertEqual(int(row["shared_rdate_prefer"]), 1)

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

    def test_vr005_endpoint_and_envelope(self) -> None:
        for _cid, path, data in self.fixtures:
            env = data["metric_envelope"]
            self.assertEqual(env["source_endpoint"], ENDPOINT, path.name)
            self.assertEqual(env["report_period"], REPORT_PERIOD, path.name)

    def test_vr036_lineage(self) -> None:
        for _cid, path, data in self.fixtures:
            lin = data["metric_envelope"]["lineage"]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], "rdate_report_period", path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)

    def test_captured_payload_freeze_and_mapping(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["metric_envelope"]
            if env["metric_status"] != "captured":
                continue
            self.assertIn("shareholder_data", data, path.name)
            payload = data["shareholder_data"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], env["quality_status"])
            self.assertEqual(payload["company_code"], env["company_code"])
            self.assertEqual(payload["report_period"], env["report_period"])
            self.assertEqual(int(payload["metric_count"]), 6, path.name)
            self.assertEqual(payload.get("mapping_confidence"), "high", path.name)
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["company_code"], uref["company_code"])
            lin = env["lineage"]
            raw = lin.get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertEqual(raw["SECCODE"], payload["company_code"])
            self.assertEqual(raw["ENDDATE"], payload["report_period"])
            # mapper 产出 6 metrics 且与 summary 一致
            rows = map_to_company_metric_periodic(
                raw,
                source_id=COMPONENT,
                query_mode="rdate_report_period",
                query_params={"rdate": ANCHOR_RDATE},
            )
            self.assertEqual(len(rows), 6, path.name)
            names = [r["metric_name"] for r in rows]
            self.assertEqual(names, EXPECTED_METRICS, path.name)
            summary = payload["metrics_summary"]
            for row in rows:
                self.assertEqual(row["metric_value"], summary[row["metric_name"]], path.name)

    def test_empty_but_valid_envelope(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["metric_envelope"]
            if env["metric_status"] != "empty_but_valid":
                continue
            self.assertEqual(env["quality_status"], "pass", path.name)
            self.assertNotIn("shareholder_data", data, path.name)
            self.assertNotIn("raw_record_json", env["lineage"], path.name)

    def test_dsd001_captured_and_dsd005_empty(self) -> None:
        dsd001 = next(d for c, _p, d in self.fixtures if c == "DSD001")
        self.assertEqual(dsd001["metric_envelope"]["metric_status"], "captured")
        self.assertEqual(
            self.universe_by_id["DSD001"]["expected_behavior"], "captured_normal"
        )
        dsd005 = next(d for c, _p, d in self.fixtures if c == "DSD005")
        self.assertEqual(dsd005["metric_envelope"]["metric_status"], "empty_but_valid")
        self.assertEqual(
            self.universe_by_id["DSD005"]["expected_behavior"], "empty_but_valid"
        )

    def test_vr009_records_filtered_empty(self) -> None:
        """VR-009/010：截面有记录但无目标 SECCODE → empty_but_valid。"""
        path = FIXTURE_DIR / "DSD003_records_filtered_empty.json"
        data = _load_json(path)
        meta = data["_fixture_meta"]
        filt = meta["records_filter"]
        self.assertEqual(meta["scenario"], "empty_but_valid_after_SECCODE_filter")
        self.assertGreater(int(filt["raw_records_count"]), 0)
        self.assertEqual(int(filt["matched_SECCODE_count"]), 0)
        self.assertEqual(filt["target_SECCODE"], "600000")
        self.assertNotIn("600000", filt["other_SECCODEs"])
        env = data["metric_envelope"]
        self.assertEqual(env["metric_status"], "empty_but_valid")
        self.assertEqual(env["quality_status"], "pass")
        self.assertNotIn("shareholder_data", data)

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
            rows = map_to_company_metric_periodic(
                raw,
                source_id=COMPONENT,
                query_mode="rdate_report_period",
                query_params={"rdate": ANCHOR_RDATE},
            )
            for row in rows:
                jsonschema.validate(instance=row, schema=schema)

    def test_no_network_imports(self) -> None:
        import lab.test_cninfo_d_class_shareholder_data_fixtures as self_mod

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
                    "vr": "VR-025–VR-030",
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
                        "vr": "VR-015–VR-024",
                        "status": "pass",
                        "note": "SECCODE/ENDDATE/F001N-F006N → 6 metrics",
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
        summary = "\n".join(
            [
                "# CNINFO D 类 shareholder_data — Tier-1 Fixture VR Validation（Offline）",
                "",
                f"_生成时间：D-FM-07 · wall≈{wall:.2f}s_",
                "",
                "> **性质：** Tier-1 fixture offline VR · **CNINFO = 0** · **不是 verified**",
                "",
                "| 项 | 值 |",
                "|----|-----|",
                f"| fixture root | `fixtures/d_class/shareholder_data_first_slice/` |",
                f"| universe lock | `{UNIVERSE_LOCK.name}` |",
                f"| fixtures | **{len(fixtures)}** |",
                f"| matrix rows | **{len(rows)}** |",
                f"| CNINFO | **0** |",
                "",
                "```text",
                "d_class_shareholder_data_fixture_vr_gate = PASS_OFFLINE",
                "d_class_shareholder_data_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
                "d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED",
                "d_class_shareholder_data_first_slice_runner_gate = NOT_APPROVED",
                "shareholder_data_component_approved = standing_scope",
                "```",
                "",
                "## Artifacts",
                "",
                f"- matrix: `outputs/validation/{VALIDATION_OUT.name}`",
                f"- summary: `outputs/validation/{SUMMARY_OUT.name}`",
                "- test: `lab/test_cninfo_d_class_shareholder_data_fixtures.py`",
                "",
                "```text",
                "task_id = D-FM-07",
                "phase = shareholder_data_first_slice_approval_package_offline",
                "```",
                "",
            ]
        )
        SUMMARY_OUT.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    unittest.main(verbosity=2)

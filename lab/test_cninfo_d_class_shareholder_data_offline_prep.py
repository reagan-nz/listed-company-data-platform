#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 shareholder_data — D-FM-06 offline prep smoke（Tier-0 mapper + universe sketch）。

离线 only · 无 CNINFO · 无 live · 无 runner · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_shareholder_data_offline_prep.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from lab.cninfo_d_class_mappers import (  # noqa: E402
    SHAREHOLDER_DATA_METRIC_MAP,
    map_to_company_metric_periodic,
)

SAMPLE_RAW = BASE_DIR / "fixtures" / "d_class" / "shareholder_data" / "sample_raw.json"
SCHEMA_PATH = BASE_DIR / "schemas" / "d_class" / "d_company_metric_periodic.schema.json"
UNIVERSE_SKETCH = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_first_slice_universe_draft_sketch_20260715.csv"
)
REGISTRY = BASE_DIR / "config" / "cninfo_d_class_source_registry_draft.yaml"

COMPONENT = "shareholder_data"
ANCHOR_RDATE = "20260331"
CASE_IDS = ("DSD001", "DSD002", "DSD003", "DSD004", "DSD005")
EXCLUDED_CODES = {"688671", "301259"}
EXPECTED_METRICS = [name for _, name, _ in SHAREHOLDER_DATA_METRIC_MAP]
REQUIRED_METRIC_KEYS = (
    "metric_id",
    "company_code",
    "company_name",
    "report_period",
    "metric_name",
    "metric_value",
    "unit",
    "raw_field",
    "source_id",
    "raw_record_hash",
)


def _load_sample() -> Dict[str, Any]:
    return json.loads(SAMPLE_RAW.read_text(encoding="utf-8"))


def _load_universe_rows() -> List[Dict[str, str]]:
    with UNIVERSE_SKETCH.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class ShareholderDataOfflinePrepTests(unittest.TestCase):
    """D-FM-06：Tier-0 sample_raw 映射 + universe sketch 结构校验。"""

    def test_sample_raw_exists_and_component_match(self) -> None:
        self.assertTrue(SAMPLE_RAW.is_file(), f"missing {SAMPLE_RAW}")
        payload = _load_sample()
        self.assertEqual(payload.get("source_id"), COMPONENT)
        self.assertEqual(payload.get("query_mode"), "rdate_report_period")
        self.assertEqual(payload.get("expected_logical_table"), "d_company_metric_periodic")
        self.assertEqual(str(payload.get("query_params", {}).get("rdate")), ANCHOR_RDATE)
        raw = payload["raw_record"]
        self.assertEqual(str(raw.get("SECCODE")), "000001")

    def test_mapper_emits_six_metrics(self) -> None:
        payload = _load_sample()
        rows = map_to_company_metric_periodic(
            payload["raw_record"],
            source_id=COMPONENT,
            query_mode=payload["query_mode"],
            query_params=payload.get("query_params") or {},
        )
        self.assertEqual(len(rows), 6)
        names = [r["metric_name"] for r in rows]
        self.assertEqual(names, EXPECTED_METRICS)
        for row in rows:
            for key in REQUIRED_METRIC_KEYS:
                self.assertIn(key, row)
            self.assertEqual(row["source_id"], COMPONENT)
            self.assertEqual(row["company_code"], "000001")
            self.assertEqual(row["report_period"], "2026-03-31")
            self.assertIsInstance(row["metric_value"], float)

    def test_metric_rows_validate_against_schema(self) -> None:
        try:
            import jsonschema
        except ImportError as exc:  # pragma: no cover
            self.skipTest(f"jsonschema unavailable: {exc}")

        self.assertTrue(SCHEMA_PATH.is_file(), f"missing {SCHEMA_PATH}")
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        payload = _load_sample()
        rows = map_to_company_metric_periodic(
            payload["raw_record"],
            source_id=COMPONENT,
            query_mode=payload["query_mode"],
            query_params=payload.get("query_params") or {},
        )
        for row in rows:
            jsonschema.validate(instance=row, schema=schema)

    def test_universe_sketch_five_cases_and_excludes(self) -> None:
        self.assertTrue(UNIVERSE_SKETCH.is_file(), f"missing {UNIVERSE_SKETCH}")
        rows = _load_universe_rows()
        self.assertEqual(len(rows), 5)
        case_ids = [r["case_id"] for r in rows]
        self.assertEqual(tuple(case_ids), CASE_IDS)
        codes = {r["company_code"] for r in rows}
        self.assertTrue(codes.isdisjoint(EXCLUDED_CODES))
        for row in rows:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["anchor_rdate"], ANCHOR_RDATE)
            self.assertEqual(row["first_slice_include"], "yes")
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])
        self.assertEqual(rows[0]["company_code"], "000001")
        self.assertEqual(rows[0]["sample_raw_reference"], "yes")
        self.assertEqual(rows[0]["expected_behavior"], "captured_normal")
        self.assertEqual(rows[4]["expected_behavior"], "empty_but_valid")

    def test_registry_shareholder_data_block_present(self) -> None:
        self.assertTrue(REGISTRY.is_file())
        text = REGISTRY.read_text(encoding="utf-8")
        self.assertIn("source_id: shareholder_data", text)
        self.assertIn("shareholeder/data", text)
        self.assertIn("rdate_report_period", text)
        self.assertIn("d_company_metric_periodic", text)

    def test_no_network_imports_for_cninfo(self) -> None:
        # 本测试模块不得引入 requests；映射路径纯离线
        import lab.test_cninfo_d_class_shareholder_data_offline_prep as self_mod

        self.assertFalse(hasattr(self_mod, "requests"))


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    unittest.main(verbosity=2)

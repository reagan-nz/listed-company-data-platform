#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 shareholder_data — Next-slice Tier-1 offline fixture / universe lock / VR。

对照 VR-NS checklist 加载 fixtures/d_class/shareholder_data_next_slice/DSD101–DSD105。

离线 only · 无 CNINFO · 无 live · 不实现 runner · 不升级 live gate · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_shareholder_data_next_slice_fixtures.py
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

FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "shareholder_data_next_slice"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv"
)
AT_FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv"
)
AT_NEXT_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv"
)
SD_FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv"
)
FIA_NEXT_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv"
)
FIA_FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv"
)
# 关闭根冻结 sha256；本任务必须保持
EXPECTED_AT_FIRST_SLICE_LOCK_SHA256 = (
    "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
)
EXPECTED_AT_NEXT_SLICE_LOCK_SHA256 = (
    "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
)
EXPECTED_SD_FIRST_SLICE_LOCK_SHA256 = (
    "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
)
EXPECTED_FIA_NEXT_SLICE_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
EXPECTED_FIA_FIRST_SLICE_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)
SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_universe_draft_sketch_20260715.csv"
)
VR_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_validation_rules_20260715.md"
)
APPROVAL_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_approval_package_20260715.md"
)
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_fixture_vr_matrix_20260715.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_fixture_vr_validation_20260715.md"
)

COMPONENT = "shareholder_data"
ENDPOINT = "https://www.cninfo.com.cn/data20/shareholeder/data"
RDATES = {"20260331", "20251231"}
CASE_IDS = ("DSD101", "DSD102", "DSD103", "DSD104", "DSD105")
EXCLUDED_CODES = {"688671", "301259"}
RAW_CORE = (
    "SECCODE",
    "SECNAME",
    "ENDDATE",
    "F001N",
    "F002N",
    "F003N",
    "F004N",
    "F005N",
    "F006N",
)
FREEZE_REQUIRED = (
    "company_code",
    "report_period",
    "metric_count",
    "quality_status",
)

EXPECTED_FILES = {
    "DSD101": ("DSD101_found.json",),
    "DSD102": ("DSD102_found.json", "DSD102_empty.json"),
    "DSD103": ("DSD103_found.json", "DSD103_empty.json"),
    "DSD104": ("DSD104_found.json", "DSD104_empty.json"),
    "DSD105": ("DSD105_empty_but_valid_synthetic.json",),
}

EXPECTED_RDATE_BY_CASE = {
    "DSD101": "20260331",
    "DSD102": "20260331",
    "DSD103": "20260331",
    "DSD104": "20251231",
    "DSD105": "20251231",
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


def _rperiod(rdate: str) -> str:
    return f"{rdate[:4]}-{rdate[4:6]}-{rdate[6:8]}"


def _iter_fixtures() -> List[Tuple[str, Path, Dict[str, Any]]]:
    rows: List[Tuple[str, Path, Dict[str, Any]]] = []
    for case_id, names in EXPECTED_FILES.items():
        for name in names:
            path = FIXTURE_DIR / name
            rows.append((case_id, path, _load_json(path)))
    return rows


class TestShareholderDataNextSliceFixtures(unittest.TestCase):
    """Next-slice Tier-1 synthetic fixture vs VR-NS offline 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_csv(UNIVERSE_LOCK)
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()

    def test_vr_ns001_universe_five_dsd_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))

    def test_vr_ns002_component_include_lock(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "locked")
            self.assertEqual(row["approval_task_id"], "D-FM-32")

    def test_vr_ns003_multi_rdate_set(self) -> None:
        for row in self.universe:
            self.assertIn(row["anchor_rdate"], RDATES)
            self.assertEqual(row["query_mode"], "rdate_report_period")
            self.assertEqual(
                row["anchor_rdate"],
                EXPECTED_RDATE_BY_CASE[row["case_id"]],
            )
        for case_id, path, data in self.fixtures:
            qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(qp["rdate"], EXPECTED_RDATE_BY_CASE[case_id], path.name)
            self.assertIn(qp["rdate"], RDATES, path.name)

    def test_vr_ns004_exclusions(self) -> None:
        codes = {r["company_code"] for r in self.universe}
        self.assertTrue(EXCLUDED_CODES.isdisjoint(codes))
        for row in self.universe:
            flags = row["exclude_flags"]
            self.assertIn("exclude_688671", flags)
            self.assertIn("exclude_301259", flags)
            self.assertIn("exclude_first_slice_mutate", flags)
            self.assertIn("allow_multi_rdate_next_slice_only", flags)

    def test_vr_ns006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 1)
            self.assertLessEqual(int(row["total_request_cap"]), 5)
            self.assertEqual(int(row["shared_probe_prefer"]), 2)

    def test_vr_ns012_expectation_mix(self) -> None:
        self.assertEqual(
            self.universe_by_id["DSD101"]["expected_behavior"],
            "captured_normal",
        )
        for cid in ("DSD102", "DSD103", "DSD104"):
            self.assertEqual(
                self.universe_by_id[cid]["expected_behavior"],
                "captured_normal_or_empty_but_valid",
            )
        self.assertEqual(
            self.universe_by_id["DSD105"]["expected_behavior"],
            "empty_but_valid",
        )
        for row in self.universe:
            self.assertNotEqual(
                row["expected_behavior"],
                "captured_normal_or_needs_review",
            )

    def test_closed_roots_frozen(self) -> None:
        self.assertEqual(
            _sha256_file(AT_FIRST_SLICE_LOCK),
            EXPECTED_AT_FIRST_SLICE_LOCK_SHA256,
            "AT first-slice universe lock must not be mutated in D-FM-32",
        )
        self.assertEqual(
            _sha256_file(AT_NEXT_SLICE_LOCK),
            EXPECTED_AT_NEXT_SLICE_LOCK_SHA256,
            "AT next-slice universe lock must not be mutated in D-FM-32",
        )
        self.assertEqual(
            _sha256_file(SD_FIRST_SLICE_LOCK),
            EXPECTED_SD_FIRST_SLICE_LOCK_SHA256,
            "SD first-slice universe lock must not be mutated in D-FM-32",
        )
        self.assertEqual(
            _sha256_file(FIA_NEXT_SLICE_LOCK),
            EXPECTED_FIA_NEXT_SLICE_LOCK_SHA256,
            "FIA next-slice universe lock must not be mutated in D-FM-32",
        )
        self.assertEqual(
            _sha256_file(FIA_FIRST_SLICE_LOCK),
            EXPECTED_FIA_FIRST_SLICE_LOCK_SHA256,
            "FIA first-slice universe lock must not be mutated in D-FM-32",
        )
        first_ids = {r["case_id"] for r in _load_csv(SD_FIRST_SLICE_LOCK)}
        next_ids = {r["case_id"] for r in self.universe}
        self.assertTrue(first_ids.isdisjoint(next_ids))

    def test_sketch_remains_draft_history(self) -> None:
        sketch = _load_csv(SKETCH_CSV)
        self.assertEqual([r["case_id"] for r in sketch], list(CASE_IDS))
        for row in sketch:
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertIn(row["anchor_rdate"], RDATES)

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
            self.assertIs(meta["multi_rdate_slice"], True, path.name)
            self.assertEqual(meta["case_id"], _cid, path.name)

    def test_vr_ns005_endpoint_and_component(self) -> None:
        for _cid, path, data in self.fixtures:
            self.assertEqual(
                data["metric_envelope"]["source_endpoint"], ENDPOINT, path.name
            )

    def test_vr_ns036_lineage(self) -> None:
        for case_id, path, data in self.fixtures:
            lin = data["metric_envelope"]["lineage"]
            uref = self.universe_by_id[case_id]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], uref["query_mode"], path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)
            self.assertEqual(
                lin["query_params"]["rdate"],
                uref["anchor_rdate"],
                path.name,
            )

    def test_captured_payload_freeze(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["metric_envelope"]
            if env["metric_status"] != "captured":
                continue
            self.assertIn("shareholder_data", data, path.name)
            payload = data["shareholder_data"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], env["quality_status"])
            self.assertEqual(payload["metric_count"], 6, path.name)
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["company_code"], uref["company_code"])
            self.assertEqual(
                payload["report_period"],
                _rperiod(uref["anchor_rdate"]),
                path.name,
            )
            raw = env["lineage"].get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertEqual(raw["SECCODE"], uref["company_code"], path.name)
            self.assertEqual(
                raw["ENDDATE"],
                _rperiod(uref["anchor_rdate"]),
                path.name,
            )

    def test_empty_but_valid_envelope(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["metric_envelope"]
            if env["metric_status"] != "empty_but_valid":
                continue
            self.assertEqual(env["quality_status"], "pass", path.name)
            self.assertNotIn("shareholder_data", data, path.name)
            self.assertNotIn("raw_record_json", env["lineage"], path.name)
            uref = self.universe_by_id[case_id]
            self.assertIn(
                uref["expected_behavior"],
                (
                    "captured_normal",
                    "captured_normal_or_empty_but_valid",
                    "empty_but_valid",
                ),
            )

    def test_dsd101_found_only(self) -> None:
        names = EXPECTED_FILES["DSD101"]
        self.assertEqual(names, ("DSD101_found.json",))
        data = _load_json(FIXTURE_DIR / names[0])
        self.assertEqual(data["metric_envelope"]["metric_status"], "captured")
        self.assertEqual(data["metric_envelope"]["company_code"], "000001")
        self.assertEqual(data["_fixture_meta"]["query_params"]["rdate"], "20260331")

    def test_dsd105_empty_control_only(self) -> None:
        names = EXPECTED_FILES["DSD105"]
        self.assertEqual(names, ("DSD105_empty_but_valid_synthetic.json",))
        data = _load_json(FIXTURE_DIR / names[0])
        self.assertEqual(data["metric_envelope"]["metric_status"], "empty_but_valid")
        self.assertEqual(data["metric_envelope"]["company_code"], "000004")
        self.assertEqual(data["_fixture_meta"]["query_params"]["rdate"], "20251231")

    def test_dsd103_diversify_600519(self) -> None:
        self.assertEqual(self.universe_by_id["DSD103"]["company_code"], "600519")
        data = _load_json(FIXTURE_DIR / "DSD103_found.json")
        self.assertEqual(data["shareholder_data"]["company_code"], "600519")
        self.assertEqual(data["shareholder_data"]["company_name"], "贵州茅台")

    def test_approval_and_vr_docs_present(self) -> None:
        self.assertTrue(VR_MD.is_file())
        self.assertTrue(APPROVAL_MD.is_file())
        vr_text = VR_MD.read_text(encoding="utf-8")
        approval = APPROVAL_MD.read_text(encoding="utf-8")
        self.assertIn("DSD101", vr_text)
        self.assertIn("VR-NS-001", vr_text)
        self.assertIn("20251231", vr_text)
        self.assertIn("不是 verified", vr_text)
        self.assertIn("允许 multi-rdate", vr_text)
        self.assertIn("DSD101", approval)
        self.assertIn("STANDING_SCOPE_AUTHORIZED", approval)
        self.assertIn("不是 verified", approval)
        self.assertNotRegex(approval, r"(?m)^\s*verified\s*=")
        self.assertNotIn("production_ready = true", approval)
        self.assertIn(
            "d_class_shareholder_data_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
            approval,
        )
        self.assertIn(
            "d_class_shareholder_data_next_slice_fixture_vr_gate = PASS_OFFLINE",
            approval,
        )
        self.assertIn("NOT_APPROVED", approval)
        self.assertIn("H3/H4", approval)
        self.assertIn("controller_execution_allowed=false", approval)

    def test_no_network_imports(self) -> None:
        import lab.test_cninfo_d_class_shareholder_data_next_slice_fixtures as self_mod

        self.assertFalse(hasattr(self_mod, "requests"))

    def test_chinese_utf8_no_mojibake(self) -> None:
        vr_text = VR_MD.read_text(encoding="utf-8")
        approval = APPROVAL_MD.read_text(encoding="utf-8")
        found = (FIXTURE_DIR / "DSD103_found.json").read_text(encoding="utf-8")
        for text, label in (
            (vr_text, "vr"),
            (approval, "approval"),
            (found, "fixture"),
        ):
            self.assertNotIn("Ã", text, label)
            self.assertNotIn("ä¸", text, label)
        self.assertIn("不是 verified", vr_text)
        self.assertIn("禁止", vr_text)
        self.assertIn("不是 verified", approval)
        self.assertIn("贵州茅台", found)

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
                    "vr": "VR-NS-025–VR-NS-030",
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
                        "vr": "VR-NS-015–VR-NS-024",
                        "status": "pass",
                        "note": "SECCODE/ENDDATE/F001N-F006N freeze; 6 metrics",
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
        at_sha = _sha256_file(AT_FIRST_SLICE_LOCK)
        at_ns_sha = _sha256_file(AT_NEXT_SLICE_LOCK)
        sd_sha = _sha256_file(SD_FIRST_SLICE_LOCK)
        fia_ns_sha = _sha256_file(FIA_NEXT_SLICE_LOCK)
        fia_fs_sha = _sha256_file(FIA_FIRST_SLICE_LOCK)
        summary = "\n".join(
            [
                "# CNINFO D 类 shareholder_data — Next-Slice Tier-1 Fixture VR Validation（Offline）",
                "",
                f"_生成时间：D-FM-32 · wall≈{wall:.2f}s_",
                "",
                "> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**",
                "",
                "| 项 | 值 |",
                "|----|-----|",
                f"| fixture root | `fixtures/d_class/shareholder_data_next_slice/` |",
                f"| universe lock | `{UNIVERSE_LOCK.name}` |",
                f"| fixtures | **{len(fixtures)}** |",
                f"| matrix rows | **{len(rows)}** |",
                f"| rdate set | `20260331` + `20251231` |",
                f"| shared_probe_prefer | **2** |",
                f"| AT first-slice lock sha256 | `{at_sha}` |",
                f"| AT next-slice lock sha256 | `{at_ns_sha}` |",
                f"| SD first-slice lock sha256 | `{sd_sha}` |",
                f"| FIA next-slice lock sha256 | `{fia_ns_sha}` |",
                f"| FIA first-slice lock sha256 | `{fia_fs_sha}` |",
                f"| CNINFO | **0** |",
                "",
                "```text",
                "d_class_shareholder_data_next_slice_fixture_vr_gate = PASS_OFFLINE",
                "d_class_shareholder_data_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
                "d_class_shareholder_data_next_slice_live_gate = NOT_APPROVED",
                "d_class_shareholder_data_next_slice_runner_gate = NOT_APPROVED",
                "shareholder_data_component_approved = standing_scope",
                "closed_roots_mutated = false",
                "at_next_slice_live_flipped = false",
                "```",
                "",
                "## Artifacts",
                "",
                f"- matrix: `outputs/validation/{VALIDATION_OUT.name}`",
                f"- summary: `outputs/validation/{SUMMARY_OUT.name}`",
                "- test: `lab/test_cninfo_d_class_shareholder_data_next_slice_fixtures.py`",
                "",
                "```text",
                "task_id = D-FM-32",
                "phase = shareholder_data_next_slice_approval_package_offline",
                "```",
                "",
            ]
        )
        SUMMARY_OUT.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    unittest.main(verbosity=2)

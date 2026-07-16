"""
A-FM-07：A erad protected-root freeze + ladder CLOSED 断言（纯离线 · CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_fm07_erad_protected_root_freeze.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)
_VAL = os.path.join(_BASE_DIR, "outputs", "validation")

PROBE_JSON = os.path.join(_VAL, "cninfo_a_class_fm07_attestation_probe_20260716.json")
REGISTRY_CSV = os.path.join(
    _VAL, "cninfo_a_class_erad_protected_output_roots_fm07_20260716.csv"
)
ATTEST_CSV = os.path.join(
    _VAL, "cninfo_a_class_erad_protected_root_freeze_attestation_fm07_20260716.csv"
)
CLOSURE_MD = os.path.join(
    _VAL, "cninfo_a_class_listing_aware_scale_ladder_fm07_closed_20260716.md"
)
FM06_ATTEST = os.path.join(
    _VAL, "cninfo_a_class_listing_aware_s24_fm06_freeze_attestation_20260716.csv"
)
ISOLATED_DIR = os.path.join(_VAL, "_a_fm07_erad_protected_root_freeze")

SIZE_CLAIM = "residual_371_not_1000"


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class TestAClassFm07EradProtectedRootFreeze(unittest.TestCase):
    """冻结：ladder CLOSED、保护根存在、FM06 零漂移、禁止伪 1000。"""

    def test_artifacts_exist(self) -> None:
        for path in (PROBE_JSON, REGISTRY_CSV, ATTEST_CSV, CLOSURE_MD, ISOLATED_DIR):
            self.assertTrue(
                os.path.exists(path),
                msg=f"missing fm07 artifact: {path}",
            )

    def test_probe_offline_closed_gate(self) -> None:
        with open(PROBE_JSON, "r", encoding="utf-8") as f:
            probe = json.load(f)
        self.assertEqual(probe.get("cninfo_calls"), 0)
        self.assertEqual(probe.get("live_executed"), False)
        self.assertEqual(probe.get("listing_aware_scale_ladder_gate"), "CLOSED")
        self.assertEqual(probe.get("size_claim"), SIZE_CLAIM)
        self.assertEqual(probe.get("overlay_union"), 2213)
        self.assertEqual(probe.get("micro_residual_post_s24"), 2)
        self.assertEqual(
            probe.get("reopen_1000"), "BLOCKED_until_C_basic_profile"
        )
        self.assertEqual(probe.get("alternate_axis"), "a_erad_protected_root_freeze")
        self.assertFalse(probe.get("claimed_1000"))
        self.assertFalse(probe.get("s2_s24_live_main_roots_mutated"))
        self.assertEqual(probe.get("fm06_drift_count"), 0)
        self.assertEqual(probe.get("missing_anchor_paths"), [])
        self.assertEqual(probe.get("missing_protected_dirs"), [])
        self.assertEqual(
            probe.get("anchor_frozen_ok"), probe.get("anchor_count")
        )

    def test_closure_note_marks_closed(self) -> None:
        with open(CLOSURE_MD, "r", encoding="utf-8") as f:
            text = f.read()
        self.assertIn("listing_aware_scale_ladder_gate = CLOSED", text)
        self.assertIn(SIZE_CLAIM, text)
        self.assertIn("BLOCKED_until_C_basic_profile", text)
        self.assertNotIn("claimed_1000 = yes", text)

    def test_registry_covers_s2_s24_and_phase2(self) -> None:
        with open(REGISTRY_CSV, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        ids = {r["root_id"] for r in rows}
        for n in range(2, 25):
            self.assertIn(f"A-ROOT-S{n}", ids)
        self.assertIn("A-ROOT-PHASE2-EXP", ids)
        self.assertIn("A-ROOT-FM06-FREEZE", ids)
        # 不得伪造 listing_aware_s1
        self.assertNotIn("A-ROOT-S1", ids)
        for row in rows:
            if row["root_id"].startswith("A-ROOT-S") and row["root_id"] != "A-ROOT-SCALE200":
                self.assertEqual(row["write_policy"], "read_only_no_mutate")
                path = os.path.join(_BASE_DIR, row["path_pattern"].rstrip("/"))
                self.assertTrue(os.path.isdir(path), msg=row["path_pattern"])

    def test_attestation_sha256_matches_disk(self) -> None:
        with open(ATTEST_CSV, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 30)
        for row in rows:
            self.assertEqual(row["status"], "frozen_ok")
            abs_path = os.path.join(_BASE_DIR, row["path"])
            self.assertTrue(os.path.isfile(abs_path), msg=row["path"])
            self.assertEqual(_sha256(abs_path), row["sha256"], msg=row["path"])

    def test_fm06_crosscheck_zero_drift(self) -> None:
        self.assertTrue(os.path.isfile(FM06_ATTEST))
        with open(FM06_ATTEST, "r", encoding="utf-8") as f:
            fm06 = {r["path"]: r["sha256"] for r in csv.DictReader(f)}
        with open(ATTEST_CSV, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        checked = 0
        for row in rows:
            if row["path"] not in fm06:
                continue
            checked += 1
            self.assertEqual(row["fm06_match"], "MATCH", msg=row["path"])
            self.assertEqual(row["sha256"], fm06[row["path"]], msg=row["path"])
        self.assertGreaterEqual(checked, 20)

    def test_does_not_claim_thousand(self) -> None:
        with open(PROBE_JSON, "r", encoding="utf-8") as f:
            probe = json.load(f)
        self.assertNotEqual(probe.get("overlay_union"), 1000)
        self.assertLessEqual(int(probe.get("micro_residual_post_s24", 99)), 2)
        self.assertIn("BLOCKED", str(probe.get("reopen_1000")))


if __name__ == "__main__":
    unittest.main()

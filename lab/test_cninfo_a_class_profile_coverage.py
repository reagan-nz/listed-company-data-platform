"""
A-class profile coverage overlay 离线单测（CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_profile_coverage.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_LAB = Path(__file__).resolve().parent
if str(_LAB) not in sys.path:
    sys.path.insert(0, str(_LAB))

import cninfo_a_class_profile_coverage as coverage  # noqa: E402


def _write_profile(profile_dir: Path, code: str, listing_date: str) -> None:
    payload = {
        "company_code": code,
        "listing_date": listing_date,
        "raw_record_json": {"basicInformation": [{"F006D": listing_date}]},
    }
    (profile_dir / f"{code}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


class ProfileCoverageTests(unittest.TestCase):
    def test_discover_prefers_canon_over_latent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            canon = tmp_path / "canon"
            latent = tmp_path / "latent"
            canon.mkdir()
            latent.mkdir()
            _write_profile(canon, "000001", "1991-01-01")
            _write_profile(latent, "000001", "2099-01-01")  # 不应覆盖 canon
            _write_profile(latent, "000002", "2000-01-01")
            path_map = coverage.discover_profile_path_map(
                canon_dir=str(canon),
                latent_dirs=[str(latent)],
            )
            self.assertEqual(path_map["000001"].origin, "canon")
            self.assertEqual(path_map["000002"].origin, "latent")
            self.assertEqual(len(path_map), 2)

    def test_build_overlay_symlinks_union(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            canon = tmp_path / "canon"
            latent = tmp_path / "latent"
            overlay = tmp_path / "overlay"
            canon.mkdir()
            latent.mkdir()
            _write_profile(canon, "600000", "1999-01-01")
            _write_profile(latent, "688001", "2020-01-01")
            result = coverage.build_profile_overlay(
                overlay_dir=str(overlay),
                canon_dir=str(canon),
                latent_dirs=[str(latent)],
                refresh=True,
            )
            self.assertEqual(result.cninfo_calls, 0)
            self.assertEqual(result.union_count, 2)
            self.assertEqual(result.canon_count, 1)
            self.assertEqual(result.latent_only_count, 1)
            link = overlay / "688001.json"
            self.assertTrue(link.is_symlink())
            self.assertTrue(os.path.isfile(str(link)))

    def test_code_prefix3(self) -> None:
        self.assertEqual(coverage.code_prefix3("301131"), "301")
        self.assertEqual(coverage.code_prefix3("000001"), "000")


if __name__ == "__main__":
    unittest.main()

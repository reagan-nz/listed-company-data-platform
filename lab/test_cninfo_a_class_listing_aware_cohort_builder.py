"""
A-class listing-aware cohort builder 离线单测（CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_listing_aware_cohort_builder.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_LAB = Path(__file__).resolve().parent
if str(_LAB) not in sys.path:
    sys.path.insert(0, str(_LAB))

import cninfo_a_class_listing_aware_cohort_builder as builder  # noqa: E402


def _write_profile(profile_dir: Path, code: str, listing_date: str) -> None:
    payload = {
        "company_code": code,
        "listing_date": listing_date,
        "raw_record_json": {"basicInformation": [{"F006D": listing_date}]},
    }
    (profile_dir / f"{code}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _write_yaml(path: Path, companies: list) -> None:
    # 最小 YAML（避免测试依赖复杂结构）
    lines = ["companies:"]
    for c in companies:
        lines.append(f"  - stock_code: '{c['stock_code']}'")
        lines.append(f"    short_name: '{c['short_name']}'")
        lines.append(f"    exchange: '{c.get('exchange', 'SZSE')}'")
        lines.append(f"    orgid: '{c.get('orgid', 'x')}'")
        lines.append(f"    board: '{c.get('board', 'szse_main')}'")
        lines.append(f"    financial: {str(c.get('financial', False)).lower()}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_exclude_csv(path: Path, codes: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company_code", "company_name", "case_id", "cohort"])
        w.writeheader()
        for i, code in enumerate(codes):
            w.writerow(
                {
                    "company_code": code,
                    "company_name": f"已占用{i}",
                    "case_id": f"AD2E{i+1:03d}",
                    "cohort": "prior",
                }
            )


class ListingAwareCohortBuilderTests(unittest.TestCase):
    def test_derive_report_fields_mod10(self) -> None:
        rt, ep, _, _ = builder.derive_report_fields_for_case_num(601)
        self.assertEqual(rt, "annual_report")
        self.assertEqual(ep, "2024-12-31")
        rt7, ep7, _, _ = builder.derive_report_fields_for_case_num(608)
        self.assertEqual(rt7, "semi_annual_report")
        self.assertEqual(ep7, "2024-06-30")

    def test_build_skips_a_exclude_st_bse_and_listing_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"

            # 000001: A 已占用
            # 000002: ST
            # 430017: BSE
            # 000003: listing_gap（上市日晚于 Q1 期）
            # 000004–000008: 可选（足够填 target=3，中间会跳过 gap）
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000002", "short_name": "*ST乙"},
                {"stock_code": "430017", "short_name": "北交丙"},
                {"stock_code": "000003", "short_name": "晚上市丁"},
                {"stock_code": "000004", "short_name": "可选戊"},
                {"stock_code": "000005", "short_name": "可选己"},
                {"stock_code": "000006", "short_name": "可选庚"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            _write_profile(profile_dir, "000001", "1999-01-01")
            _write_profile(profile_dir, "000002", "1999-01-01")
            _write_profile(profile_dir, "430017", "1999-01-01")
            # 000003：若分配到 Q1(2024-03-31) 会 gap；若 annual 则 ok。
            # 为稳定触发 gap：用极晚上市日，对任何 2024 期窗都 gap。
            _write_profile(profile_dir, "000003", "2025-06-01")
            for code, ld in (
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
                ("000006", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)

            result = builder.build_listing_aware_cohort(
                target_size=3,
                case_id_start=601,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
            )
            self.assertEqual(result.cninfo_calls, 0)
            self.assertEqual(len(result.selected), 3)
            codes = [r.company_code for r in result.selected]
            self.assertEqual(codes, ["000004", "000005", "000006"])
            self.assertEqual(result.selected[0].case_id, "AD2E601")
            self.assertEqual(result.selected[0].cohort, builder.COHORT_LABEL)
            stages = {r.reject_stage for r in result.rejected}
            self.assertIn("a_cumulative_exclude", stages)
            self.assertIn("st_exclude", stages)
            self.assertIn("listing_period_gate", stages)
            self.assertTrue(builder.is_bse_code("430017"))
            self.assertFalse(builder.is_bse_code("000004"))

    def test_undersized_raises_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            _write_yaml(
                yaml_path,
                [{"stock_code": "000010", "short_name": "仅一码"}],
            )
            _write_exclude_csv(exclude_csv, [])
            _write_profile(profile_dir, "000010", "2010-01-01")
            with self.assertRaises(RuntimeError) as ctx:
                builder.build_listing_aware_cohort(
                    target_size=5,
                    a_exclude_csvs=[str(exclude_csv)],
                    profile_dir=str(profile_dir),
                    full_market_yaml=str(yaml_path),
                )
            self.assertIn("listing_aware_cohort_undersized", str(ctx.exception))

    def test_write_universe_csv_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "u.csv"
            rows = [
                builder.CohortRow(
                    company_code="000004",
                    company_name="可选戊",
                    case_id="AD2E601",
                    cohort=builder.COHORT_LABEL,
                    report_type="annual_report",
                    expected_period="2024-12-31",
                    listing_date="2010-01-01",
                )
            ]
            builder.write_universe_csv(rows, str(path))
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.assertEqual(reader.fieldnames, builder.UNIVERSE_COLUMNS)
                got = list(reader)
            self.assertEqual(len(got), 1)
            self.assertEqual(got[0]["case_id"], "AD2E601")
            self.assertEqual(got[0]["cohort"], builder.COHORT_LABEL)

    def test_s3_case_id_start_excludes_prior_codes(self) -> None:
        """S3 从 651 起编；已占用码不得入选。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选戊"},
                {"stock_code": "000005", "short_name": "可选己"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S3,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
            )
            self.assertEqual(result.selected[0].case_id, "AD2E651")
            self.assertEqual(result.selected[1].case_id, "AD2E652")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )

    def test_s4_case_id_start_excludes_prior_codes(self) -> None:
        """S4 从 701 起编；已占用码不得入选。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选戊"},
                {"stock_code": "000005", "short_name": "可选己"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S4,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
            )
            self.assertEqual(result.selected[0].case_id, "AD2E701")
            self.assertEqual(result.selected[1].case_id, "AD2E702")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )

    def test_s5_case_id_start_excludes_prior_codes(self) -> None:
        """S5 从 751 起编；已占用码不得入选。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选戊"},
                {"stock_code": "000005", "short_name": "可选己"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S5,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
            )
            self.assertEqual(result.selected[0].case_id, "AD2E751")
            self.assertEqual(result.selected[1].case_id, "AD2E752")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )

    def test_s6_case_id_start_excludes_prior_codes(self) -> None:
        """S6 从 801 起编；已占用码不得入选。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选庚"},
                {"stock_code": "000005", "short_name": "可选辛"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S6,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
            )
            self.assertEqual(result.selected[0].case_id, "AD2E801")
            self.assertEqual(result.selected[1].case_id, "AD2E802")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )

    def test_prefix_concentration_cap_skips_excess_same_prefix(self) -> None:
        """同前缀超过上限时记 prefix_concentration_exclude 并改选其他前缀。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "301001", "short_name": "创甲"},
                {"stock_code": "301002", "short_name": "创乙"},
                {"stock_code": "301003", "short_name": "创丙"},
                {"stock_code": "600001", "short_name": "沪丁"},
                {"stock_code": "600002", "short_name": "沪戊"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, [])
            for code in ("301001", "301002", "301003", "600001", "600002"):
                _write_profile(profile_dir, code, "2010-01-01")
            result = builder.build_listing_aware_cohort(
                target_size=3,
                case_id_start=builder.CASE_ID_START_S7,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=2,
            )
            self.assertEqual(result.cninfo_calls, 0)
            codes = [r.company_code for r in result.selected]
            self.assertEqual(codes, ["301001", "301002", "600001"])
            self.assertEqual(result.selected[0].case_id, "AD2E851")
            stages = {r.reject_stage for r in result.rejected}
            self.assertIn("prefix_concentration_exclude", stages)
            prefix_hits = [
                r for r in result.rejected if r.reject_stage == "prefix_concentration_exclude"
            ]
            self.assertEqual(prefix_hits[0].company_code, "301003")

    def test_s7_case_id_start_excludes_prior_codes(self) -> None:
        """S7 从 851 起编；已占用码不得入选。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选壬"},
                {"stock_code": "000005", "short_name": "可选癸"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S7,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=25,
            )
            self.assertEqual(result.selected[0].case_id, "AD2E851")
            self.assertEqual(result.selected[1].case_id, "AD2E852")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )

    def test_s8_case_id_start_excludes_prior_codes(self) -> None:
        """S8 从 901 起编；已占用码不得入选。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选壬"},
                {"stock_code": "000005", "short_name": "可选癸"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S8,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=25,
            )
            self.assertEqual(result.selected[0].case_id, "AD2E901")
            self.assertEqual(result.selected[1].case_id, "AD2E902")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )

    def test_s9_case_id_start_excludes_prior_codes(self) -> None:
        """S9 从 951 起编；已占用码不得入选；1000 号可格式化为 AD2E1000。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选子"},
                {"stock_code": "000005", "short_name": "可选丑"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S9,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=25,
            )
            self.assertEqual(result.selected[0].case_id, "AD2E951")
            self.assertEqual(result.selected[1].case_id, "AD2E952")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )
            self.assertEqual(f"AD2E{1000:03d}", "AD2E1000")

    def test_s10_case_id_start_excludes_prior_codes(self) -> None:
        """S10 从 1001 起编；已占用码不得入选；1050 号可格式化为 AD2E1050。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选子"},
                {"stock_code": "000005", "short_name": "可选丑"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S10,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=25,
            )
            self.assertEqual(result.selected[0].case_id, "AD2E1001")
            self.assertEqual(result.selected[1].case_id, "AD2E1002")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )
            self.assertEqual(f"AD2E{1050:03d}", "AD2E1050")

    def test_s11_case_id_start_excludes_prior_codes(self) -> None:
        """S11 从 1051 起编；已占用码不得入选；1100 号可格式化为 AD2E1100。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选子"},
                {"stock_code": "000005", "short_name": "可选丑"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S11,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=25,
            )
            self.assertEqual(result.selected[0].case_id, "AD2E1051")
            self.assertEqual(result.selected[1].case_id, "AD2E1052")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )
            self.assertEqual(f"AD2E{1100:03d}", "AD2E1100")

    def test_s12_case_id_start_excludes_prior_codes(self) -> None:
        """S12 从 1101 起编；已占用码不得入选；1150 号可格式化为 AD2E1150。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选子"},
                {"stock_code": "000005", "short_name": "可选丑"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S12,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=25,
            )
            self.assertEqual(result.selected[0].case_id, "AD2E1101")
            self.assertEqual(result.selected[1].case_id, "AD2E1102")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )
            self.assertEqual(f"AD2E{1150:03d}", "AD2E1150")

    def test_s13_case_id_start_excludes_prior_codes(self) -> None:
        """S13 从 1151 起编；已占用码不得入选；1200 号可格式化为 AD2E1200。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            profile_dir = tmp_path / "profiles"
            profile_dir.mkdir()
            yaml_path = tmp_path / "fm.yaml"
            exclude_csv = tmp_path / "a_exclude.csv"
            companies = [
                {"stock_code": "000001", "short_name": "已占用甲"},
                {"stock_code": "000004", "short_name": "可选子"},
                {"stock_code": "000005", "short_name": "可选丑"},
            ]
            _write_yaml(yaml_path, companies)
            _write_exclude_csv(exclude_csv, ["000001"])
            for code, ld in (
                ("000001", "2010-01-01"),
                ("000004", "2010-01-01"),
                ("000005", "2010-01-01"),
            ):
                _write_profile(profile_dir, code, ld)
            result = builder.build_listing_aware_cohort(
                target_size=2,
                case_id_start=builder.CASE_ID_START_S13,
                a_exclude_csvs=[str(exclude_csv)],
                profile_dir=str(profile_dir),
                full_market_yaml=str(yaml_path),
                max_same_prefix=25,
            )
            self.assertEqual(result.selected[0].case_id, "AD2E1151")
            self.assertEqual(result.selected[1].case_id, "AD2E1152")
            self.assertEqual(
                [r.company_code for r in result.selected],
                ["000004", "000005"],
            )
            self.assertEqual(f"AD2E{1200:03d}", "AD2E1200")


if __name__ == "__main__":
    unittest.main()

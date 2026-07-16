"""
B-FM-03（R19）：~50 known-doc residual scale live allow-list 锁测（离线 mock）。

覆盖：
- allow-list 恰 50 案；category 空
- 字段与 fixtures ready 对齐
- mock live 路径可对 50 案得到 pass
- 不包含已 LIVE_PASS 旧案包重开

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_residual_scale50_live.py
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from unittest import mock

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_corpus_retrieval as m  # noqa: E402

LIVE_DIR = os.path.join(
    _BASE, "outputs", "validation", "cninfo_b_class_residual_scale50_live_20260716"
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)
MANIFEST = os.path.join(_BASE, "outputs", "validation", "_bfm03_manifest.json")

with open(MANIFEST, encoding="utf-8") as f:
    _MANIFEST = json.load(f)

ALLOW_IDS = list(_MANIFEST["allow_ids"])

# (case_id, title, ann_id, ts_ms, code, date_str)
MOCK_FIXTURES = [('bond_trustee_report_known_008', '武汉精测电子集团股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（2024年度）', '1224015674', 1750982400000, '300567', '2025-06-27'), ('bond_trustee_report_known_009', '宁波润禾高新材料科技股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（2024年度）', '1224015196', 1750982400000, '300727', '2025-06-27'), ('bond_trustee_report_known_010', '华泰联合证券有限责任公司关于广东奥飞数据科技股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（2024年度）', '1224036503', 1751241600000, '300738', '2025-06-30'), ('bond_trustee_report_known_011', '东方证券股份有限公司关于宁波金田铜业（集团）股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（2024年度）', '1223972050', 1750723200000, '601609', '2025-06-24'), ('tracking_rating_report_known_011', '深圳中天精装股份有限公司关于精装转债跟踪评级结果的公告', '1223973961', 1750723200000, '002989', '2025-06-24'), ('tracking_rating_report_known_012', '关于“润达转债”与“23润达医疗MTN001”2025年跟踪评级结果的公告', '1223980905', 1750809600000, '603108', '2025-06-25'), ('bond_trustee_report_known_012', '四川省新能源动力股份有限公司公司债券受托管理事务报告（2024年度）', '1224041001', 1751241600000, '000155', '2025-06-30'), ('bond_trustee_report_known_013', '山东高速路桥集团股份有限公司公司债券受托管理事务报告（2024年度）', '1224037293', 1751241600000, '000498', '2025-06-30'), ('bond_trustee_report_known_014', '浙商证券股份有限公司关于荣盛石化股份有限公司公司债券受托管理事务报告（2024年度）', '1224014733', 1750982400000, '002493', '2025-06-27'), ('bond_trustee_report_known_015', '广州越秀资本控股集团股份有限公司公开发行公司债券受托管理事务报告（2024年度）', '1224038671', 1751241600000, '000987', '2025-06-30'), ('bond_trustee_report_known_016', '山西证券股份有限公司公司债券受托管理事务报告（2024年度）', '1224013440', 1750982400000, '002500', '2025-06-27'), ('bond_trustee_report_known_017', '天津红日药业股份有限公司2021年面向专业投资者公开发行公司债券（第一期）受托管理事务报告（2024年度）', '1224036930', 1751241600000, '300026', '2025-06-30'), ('legal_opinion_known_007', '北京市通商律师事务所关于华熙生物科技股份有限公司2024 年年度股东大会的法律意见书', '1223848710', 1749600000000, '688363', '2025-06-11'), ('legal_opinion_known_008', '北京市中伦（上海）律师事务所关于上海唯万密封科技股份有限公司2025年第三次临时股东大会的法律意见书', '1223997389', 1750896000000, '301161', '2025-06-26'), ('legal_opinion_known_009', '北京德和衡律师事务所关于海看网络科技（山东）股份有限公司2024年年度股东大会的法律意见书', '1223910602', 1750204800000, '301262', '2025-06-18'), ('legal_opinion_known_010', '北京市中伦（深圳）律师事务所关于公司2025年第二次临时股东大会的法律意见书', '1224016984', 1750982400000, '301308', '2025-06-27'), ('legal_opinion_known_011', '关于深圳市曼恩斯特科技股份有限公司2024年年度股东会的法律意见书', '1223804257', 1749168000000, '301325', '2025-06-06'), ('legal_opinion_known_012', '上海市锦天城律师事务所关于东峰集团2024年年度股东大会的法律意见书', '1224018742', 1750982400000, '601515', '2025-06-27'), ('legal_opinion_known_013', '湖南启元律师事务所关于长高电新科技股份公司2025年第二次临时股东大会的法律意见书', '1223749165', 1748908800000, '002452', '2025-06-03'), ('legal_opinion_known_014', '北京云嘉律师事务所关于杭州万隆光电设备股份有限公司2024年年度股东大会之法律意见书', '1223633257', 1747872000000, '300710', '2025-05-22'), ('legal_opinion_known_015', '上海市锦天城（深圳）律师事务所关于深圳市英可瑞科技股份有限公司2024年年度股东大会的法律意见书', '1223644992', 1747958400000, '300713', '2025-05-23'), ('legal_opinion_known_016', '北京市君致律师事务所关于北京科拓恒通生物技术股份有限公司2024年年度股东大会的法律意见书', '1223627232', 1747785600000, '300858', '2025-05-21'), ('legal_opinion_known_017', '上海市锦天城律师事务所关于公司2024年年度股东大会法律意见书', '1223527260', 1747008000000, '300141', '2025-05-12'), ('legal_opinion_known_018', '科力远2025年第一次临时股东大会法律意见书', '1223980750', 1750809600000, '600478', '2025-06-25'), ('shareholder_meeting_known_008', '2024年年度股东大会决议公告', '1223802837', 1749168000000, '300413', '2025-06-06'), ('shareholder_meeting_known_009', '关于召开2025年第二次临时股东会的通知', '1223953437', 1750377600000, '000595', '2025-06-20'), ('shareholder_meeting_known_010', '2025年第三次临时股东大会决议公告', '1223956193', 1750636800000, '301210', '2025-06-23'), ('shareholder_meeting_known_011', '2025年第一次临时股东大会决议公告', '1223956491', 1750636800000, '300688', '2025-06-23'), ('shareholder_meeting_known_012', '2025年第二次临时股东大会决议公告', '1223887834', 1750032000000, '300300', '2025-06-16'), ('shareholder_meeting_known_013', '哈尔滨空调股份有限公司2024年年度股东会决议公告', '1223732486', 1748563200000, '600202', '2025-05-30'), ('shareholder_meeting_known_014', '安彩高科2024年年度股东大会决议公告', '1223934489', 1750291200000, '600207', '2025-06-19'), ('continuous_supervision_annual_known_006', '民生证券股份有限公司关于杭州福斯达深冷装备股份有限公司2024年度持续督导年度报告书', '1223190051', 1745193600000, '603173', '2025-04-21'), ('board_resolution_known_006', '富士康工业互联网股份有限公司第三届董事会第二十三次会议决议公告', '1224015359', 1750982400000, '601138', '2025-06-27'), ('board_resolution_known_007', '关于第九届董事会第九次临时会议的决议公告', '1223826815', 1749427200000, '000981', '2025-06-09'), ('board_resolution_known_008', '第八届董事会第三十六次会议决议公告', '1223886943', 1750032000000, '002065', '2025-06-16'), ('raised_funds_cash_management_known_001', '关于终止部分募投项目并将剩余募集资金继续存放募集资金专户管理以及部分募投项目延期的公告', '1224016574', 1750982400000, '300316', '2025-06-27'), ('raised_funds_cash_management_known_002', '关于部分募集资金现金管理专用结算账户销户完成的公告', '1223886854', 1750032000000, '301107', '2025-06-16'), ('raised_funds_cash_management_known_003', '关于闲置募集资金（含超募资金）进行现金管理赎回并继续进行现金管理的公告', '1224013965', 1750982400000, '301303', '2025-06-27'), ('raised_funds_cash_management_known_004', '关于使用部分暂时闲置募集资金进行现金管理的进展公告', '1224014069', 1750982400000, '002549', '2025-06-27'), ('legal_opinion_known_019', '北京市安理律师事务所关于中粮糖业控股股份有限公司2024年年度股东大会的法律意见书', '1223934627', 1750291200000, '600737', '2025-06-19'), ('legal_opinion_known_020', '2024年年度股东大会法律意见书', '1224016242', 1750982400000, '600844', '2025-06-27'), ('legal_opinion_known_021', '北京金诚同达（深圳）律师事务所关于深圳市杰普特光电股份有限公司2024年度差异化分红事项的法律意见书', '1223888805', 1750032000000, '688025', '2025-06-16'), ('legal_opinion_known_022', '关于炬芯科技股份有限公司2024年年度股东大会的法律意见书', '1223974707', 1750723200000, '688049', '2025-06-24'), ('shareholder_meeting_known_015', '南京中央商场（集团）股份有限公司2024年年度股东大会决议公告', '1223608763', 1747699200000, '600280', '2025-05-20'), ('shareholder_meeting_known_016', '2024年年度股东会决议公告', '1224017350', 1750982400000, '600377', '2025-06-27'), ('shareholder_meeting_known_017', '绿地控股2024年年度股东大会决议公告', '1223627606', 1747785600000, '600606', '2025-05-21'), ('shareholder_meeting_known_018', '凤凰股份2024年年度股东大会决议公告', '1223633807', 1747872000000, '600716', '2025-05-22'), ('shareholder_meeting_known_019', '四川长虹2024年年度股东大会决议公告', '1223998811', 1750896000000, '600839', '2025-06-26'), ('board_resolution_known_009', '第七届董事会第一次会议决议公告', '1223626613', 1747785600000, '002247', '2025-05-21'), ('board_resolution_known_010', '恒源煤电第八届董事会第十六次会议决议公告', '1223979583', 1750809600000, '600971', '2025-06-25')]


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestResidualScale50LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_fifty(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual([c["case_id"] for c in known], ALLOW_IDS)
        self.assertEqual(len(known), 50)
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        ids = {c["case_id"] for c in known}
        for closed in (
            "tracking_rating_report_known_001",
            "tracking_rating_report_known_010",
            "bond_trustee_report_known_001",
            "bond_trustee_report_known_007",
            "audit_report_known_001",
            "listing_sponsor_known_001",
        ):
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        allow = _load_cases(KNOWN_ALLOW)
        fixture = _load_cases(FIXTURE_KNOWN)
        for case_id in ALLOW_IDS:
            ak = _by_id(allow, case_id)
            fk = _by_id(fixture, case_id)
            for key in (
                "company_code",
                "company_name",
                "title_pattern",
                "expected_document_type",
                "date_start",
                "date_end",
                "expected_route_to",
                "source_id",
            ):
                self.assertEqual(ak[key], fk[key], f"{case_id}.{key}")

    def test_mock_live_fifty_cases_pass(self) -> None:
        registry = os.path.join(_BASE, "config", "cninfo_b_class_source_registry_draft.yaml")
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        categories = os.path.join(_BASE, "config", "cninfo_announcement_categories.yaml")
        categories_config = m._load_yaml(categories)
        registry_ids = m._load_registry_source_ids(registry)
        document_types = m._load_document_types(schema)
        allow = _load_cases(KNOWN_ALLOW)

        for case_id, title, ann_id, ts_ms, code, date_str in MOCK_FIXTURES:
            known_case = _by_id(allow, case_id)
            fake = [
                {
                    "announcementId": ann_id,
                    "announcementTitle": title,
                    "announcementTime": ts_ms,
                    "adjunctUrl": f"/finalpage/{date_str}/{ann_id}.PDF",
                    "secCode": code,
                }
            ]
            with mock.patch.object(m, "resolve_orgid_via_topsearch", return_value="org-mock"):
                with mock.patch.object(
                    m, "fetch_announcements", return_value=(fake, "executed", "")
                ):
                    with mock.patch.object(m.time, "sleep", return_value=None):
                        row_k, qcount = m.process_live_known_case(
                            known_case, registry_ids, document_types, categories_config
                        )
            self.assertEqual(qcount, 1, case_id)
            self.assertEqual(row_k["case_result"], "pass", case_id)
            self.assertEqual(
                row_k["predicted_document_type"],
                known_case["expected_document_type"],
                case_id,
            )
            self.assertEqual(row_k["matched_title"], title, case_id)


if __name__ == "__main__":
    unittest.main()

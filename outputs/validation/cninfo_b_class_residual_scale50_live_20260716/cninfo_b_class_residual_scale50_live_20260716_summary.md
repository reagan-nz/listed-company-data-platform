# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary

_生成时间：2026-07-16（live metadata v1；仅公告 metadata；不下载 PDF）_

## 1. 目的

本次只做 **live metadata validation**：对 ready known-document case 调用
`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。
**不下载 PDF，不解析 PDF，不入库。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Ready known-document cases | `outputs/validation/cninfo_b_class_residual_scale50_live_20260716/known_document_retrieval_cases_live_allowlist.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| mode | **--live-metadata** |

Ready case IDs: `bond_trustee_report_known_008`, `bond_trustee_report_known_009`, `bond_trustee_report_known_010`, `bond_trustee_report_known_011`, `tracking_rating_report_known_011`, `tracking_rating_report_known_012`, `bond_trustee_report_known_012`, `bond_trustee_report_known_013`, `bond_trustee_report_known_014`, `bond_trustee_report_known_015`, `bond_trustee_report_known_016`, `bond_trustee_report_known_017`, `legal_opinion_known_007`, `legal_opinion_known_008`, `legal_opinion_known_009`, `legal_opinion_known_010`, `legal_opinion_known_011`, `legal_opinion_known_012`, `legal_opinion_known_013`, `legal_opinion_known_014`, `legal_opinion_known_015`, `legal_opinion_known_016`, `legal_opinion_known_017`, `legal_opinion_known_018`, `shareholder_meeting_known_008`, `shareholder_meeting_known_009`, `shareholder_meeting_known_010`, `shareholder_meeting_known_011`, `shareholder_meeting_known_012`, `shareholder_meeting_known_013`, `shareholder_meeting_known_014`, `continuous_supervision_annual_known_006`, `board_resolution_known_006`, `board_resolution_known_007`, `board_resolution_known_008`, `raised_funds_cash_management_known_001`, `raised_funds_cash_management_known_002`, `raised_funds_cash_management_known_003`, `raised_funds_cash_management_known_004`, `legal_opinion_known_019`, `legal_opinion_known_020`, `legal_opinion_known_021`, `legal_opinion_known_022`, `shareholder_meeting_known_015`, `shareholder_meeting_known_016`, `shareholder_meeting_known_017`, `shareholder_meeting_known_018`, `shareholder_meeting_known_019`, `board_resolution_known_009`, `board_resolution_known_010`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **50** |
| ready_cases | **50** |
| query_executed | **50** |
| pass | **48** |
| fail | **2** |
| ambiguous | **0** |
| not_found | **2** |
| request_error | **0** |
| result | **PARTIAL** |

## 4. 分 case 结果

| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |
|---------|------------------------|---------------|--------------|---------|-------|-------------|
| `bond_trustee_report_known_008` | 武汉精测电子集团股份有限公司向不特定对象发行可转换公司债券受 | 武汉精测电子集团股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（20… | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_009` | 宁波润禾高新材料科技股份有限公司向不特定对象发行可转换公司债 | 宁波润禾高新材料科技股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（… | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_010` | 广东奥飞数据科技股份有限公司向不特定对象发行可转换公司债券受 | 华泰联合证券有限责任公司关于广东奥飞数据科技股份有限公司向不特定对象发行可转换公… | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_011` | 宁波金田铜业（集团）股份有限公司向不特定对象发行可转换公司债 | 东方证券股份有限公司关于宁波金田铜业（集团）股份有限公司向不特定对象发行可转换公… | 2025-06-24 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_011` | 精装转债跟踪评级结果的公告 | 深圳中天精装股份有限公司关于精装转债跟踪评级结果的公告 | 2025-06-24 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_012` | “润达转债”与“23润达医疗MTN001”2025年跟踪评级 | 关于“润达转债”与“23润达医疗MTN001”2025年跟踪评级结果的公告 | 2025-06-25 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_012` | 四川省新能源动力股份有限公司公司债券受托管理事务报告（202 | 四川省新能源动力股份有限公司公司债券受托管理事务报告（2024年度） | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_013` | 山东高速路桥集团股份有限公司公司债券受托管理事务报告（202 | 山东高速路桥集团股份有限公司公司债券受托管理事务报告（2024年度） | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_014` | 浙商证券股份有限公司关于荣盛石化股份有限公司公司债券受托管理 | 浙商证券股份有限公司关于荣盛石化股份有限公司公司债券受托管理事务报告（2024年… | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_015` | 广州越秀资本控股集团股份有限公司公开发行公司债券受托管理事务 | 广州越秀资本控股集团股份有限公司公开发行公司债券受托管理事务报告（2024年度） | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_016` | 山西证券股份有限公司公司债券受托管理事务报告（2024年度） | 山西证券股份有限公司公司债券受托管理事务报告（2024年度） | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_017` | 天津红日药业股份有限公司2021年面向专业投资者公开发行公司 | 天津红日药业股份有限公司2021年面向专业投资者公开发行公司债券（第一期）受托管… | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_007` | 北京市通商律师事务所关于华熙生物科技股份有限公司2024 年 | 北京市通商律师事务所关于华熙生物科技股份有限公司2024 年年度股东大会的法律意… | 2025-06-11 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_008` | 北京市中伦（上海）律师事务所关于上海唯万密封科技股份有限公司 | 北京市中伦（上海）律师事务所关于上海唯万密封科技股份有限公司2025年第三次临时… | 2025-06-26 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_009` | 北京德和衡律师事务所关于海看网络科技（山东）股份有限公司20 | 北京德和衡律师事务所关于海看网络科技（山东）股份有限公司2024年年度股东大会的… | 2025-06-18 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_010` | 北京市中伦（深圳）律师事务所关于公司2025年第二次临时股东 | 北京市中伦（深圳）律师事务所关于公司2025年第二次临时股东大会的法律意见书 | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_011` | 关于深圳市曼恩斯特科技股份有限公司2024年年度股东会的法律 | 关于深圳市曼恩斯特科技股份有限公司2024年年度股东会的法律意见书 | 2025-06-06 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_012` | 上海市锦天城律师事务所关于东峰集团2024年年度股东大会的法 | 上海市锦天城律师事务所关于东峰集团2024年年度股东大会的法律意见书 | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_013` | 湖南启元律师事务所关于长高电新科技股份公司2025年第二次临 | 湖南启元律师事务所关于长高电新科技股份公司2025年第二次临时股东大会的法律意见… | 2025-06-03 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_014` | 北京云嘉律师事务所关于杭州万隆光电设备股份有限公司2024年 | 北京云嘉律师事务所关于杭州万隆光电设备股份有限公司2024年年度股东大会之法律意… | 2025-05-22 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_015` | 上海市锦天城（深圳）律师事务所关于深圳市英可瑞科技股份有限公 | 上海市锦天城（深圳）律师事务所关于深圳市英可瑞科技股份有限公司2024年年度股东… | 2025-05-23 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_016` | 北京市君致律师事务所关于北京科拓恒通生物技术股份有限公司20 | 北京市君致律师事务所关于北京科拓恒通生物技术股份有限公司2024年年度股东大会的… | 2025-05-21 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_017` | 上海市锦天城律师事务所关于公司2024年年度股东大会法律意见 | 上海市锦天城律师事务所关于公司2024年年度股东大会法律意见书 | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_018` | 科力远2025年第一次临时股东大会法律意见书 | 科力远2025年第一次临时股东大会法律意见书 | 2025-06-25 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_008` | 2024年年度股东大会决议公告 | 2024年年度股东大会决议公告 | 2025-06-06 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_009` | 关于召开2025年第二次临时股东会的通知 | 关于召开2025年第二次临时股东会的通知 | 2025-06-20 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_010` | 2025年第三次临时股东大会决议公告 | 2025年第三次临时股东大会决议公告 | 2025-06-23 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_011` | 2025年第一次临时股东大会决议公告 | 2025年第一次临时股东大会决议公告 | 2025-06-23 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_012` | 2025年第二次临时股东大会决议公告 | 2025年第二次临时股东大会决议公告 | 2025-06-16 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_013` | 哈尔滨空调股份有限公司2024年年度股东会决议公告 | 哈尔滨空调股份有限公司2024年年度股东会决议公告 | 2025-05-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_014` | 安彩高科2024年年度股东大会决议公告 | 安彩高科2024年年度股东大会决议公告 | 2025-06-19 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_006` | 民生证券股份有限公司关于杭州福斯达深冷装备股份有限公司202 | 民生证券股份有限公司关于杭州福斯达深冷装备股份有限公司2024年度持续督导年度报… | 2025-04-21 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_006` | 富士康工业互联网股份有限公司第三届董事会第二十三次会议决议公 | 富士康工业互联网股份有限公司第三届董事会第二十三次会议决议公告 | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_007` | 关于第九届董事会第九次临时会议的决议公告 | 关于第九届董事会第九次临时会议的决议公告 | 2025-06-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_008` | 第八届董事会第三十六次会议决议公告 | 第八届董事会第三十六次会议决议公告 | 2025-06-16 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_001` | 关于终止部分募投项目并将剩余募集资金继续存放募集资金专户管理 | 关于终止部分募投项目并将剩余募集资金继续存放募集资金专户管理以及部分募投项目延期… | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_002` | 关于部分募集资金现金管理专用结算账户销户完成的公告 | 关于部分募集资金现金管理专用结算账户销户完成的公告 | 2025-06-16 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_003` | 关于闲置募集资金（含超募资金）进行现金管理赎回并继续进行现金 | 关于闲置募集资金（含超募资金）进行现金管理赎回并继续进行现金管理的公告 | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_004` | 关于使用部分暂时闲置募集资金进行现金管理的进展公告 | 关于使用部分暂时闲置募集资金进行现金管理的进展公告 | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_019` | 北京市安理律师事务所关于中粮糖业控股股份有限公司2024年年 |  |  | false |  / not_found | **fail** |
| `legal_opinion_known_020` | 2024年年度股东大会法律意见书 | 2024年年度股东大会法律意见书 | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_021` | 北京金诚同达（深圳）律师事务所关于深圳市杰普特光电股份有限公 |  |  | false |  / not_found | **fail** |
| `legal_opinion_known_022` | 关于炬芯科技股份有限公司2024年年度股东大会的法律意见书 | 关于炬芯科技股份有限公司2024年年度股东大会的法律意见书 | 2025-06-24 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_015` | 南京中央商场（集团）股份有限公司2024年年度股东大会决议公 | 南京中央商场（集团）股份有限公司2024年年度股东大会决议公告 | 2025-05-20 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_016` | 2024年年度股东会决议公告 | 2024年年度股东会决议公告 | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_017` | 绿地控股2024年年度股东大会决议公告 | 绿地控股2024年年度股东大会决议公告 | 2025-05-21 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_018` | 凤凰股份2024年年度股东大会决议公告 | 凤凰股份2024年年度股东大会决议公告 | 2025-05-22 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_019` | 四川长虹2024年年度股东大会决议公告 | 四川长虹2024年年度股东大会决议公告 | 2025-06-26 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_009` | 第七届董事会第一次会议决议公告 | 第七届董事会第一次会议决议公告 | 2025-05-21 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_010` | 恒源煤电第八届董事会第十六次会议决议公告 | 恒源煤电第八届董事会第十六次会议决议公告 | 2025-06-25 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |

## 5. 质量边界

- 本次 **只验证 metadata retrieval**（标题 / 日期 / pdf_url 字段存在性）。
- **PDF 未下载**；**PDF 未解析**；未生成 chunk / embedding。
- **不代表** corpus parsing 成功；**不代表** RAG 可用。
- **不写 verified**；**不升级** source status。
- placeholder category-sample case **未请求** CNINFO。
- guard case（`periodic_guard_*`）仅做 route/type false-positive 审计。
- 正向 category-sample（`*_sample_*` ready）做全市场 metadata 抽样 + 类型审计。

## 6. 下一步

1. 若 category-sample live pass，可继续补 inquiry/meeting 类 placeholder。
2. 若 fail，先分析 query params / title matching / date window。
3. **暂不下载 PDF**；parse pipeline 仍保持 dry-run。

## 附录

详见 [cninfo_b_class_corpus_retrieval_live_report.csv](cninfo_b_class_corpus_retrieval_live_report.csv)。

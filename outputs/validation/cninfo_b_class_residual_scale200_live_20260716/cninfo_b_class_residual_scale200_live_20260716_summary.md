# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary

_生成时间：2026-07-16（live metadata v1；仅公告 metadata；不下载 PDF）_

## 1. 目的

本次只做 **live metadata validation**：对 ready known-document case 调用
`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。
**不下载 PDF，不解析 PDF，不入库。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Ready known-document cases | `outputs/validation/cninfo_b_class_residual_scale200_live_20260716/known_document_retrieval_cases_live_allowlist.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| mode | **--live-metadata** |

Ready case IDs: `legal_opinion_known_023`, `legal_opinion_known_024`, `legal_opinion_known_025`, `legal_opinion_known_026`, `legal_opinion_known_027`, `legal_opinion_known_028`, `legal_opinion_known_029`, `legal_opinion_known_030`, `legal_opinion_known_031`, `legal_opinion_known_032`, `legal_opinion_known_033`, `legal_opinion_known_034`, `legal_opinion_known_035`, `legal_opinion_known_036`, `legal_opinion_known_037`, `legal_opinion_known_038`, `legal_opinion_known_039`, `legal_opinion_known_040`, `legal_opinion_known_041`, `legal_opinion_known_042`, `legal_opinion_known_043`, `legal_opinion_known_044`, `legal_opinion_known_045`, `legal_opinion_known_046`, `legal_opinion_known_047`, `legal_opinion_known_048`, `legal_opinion_known_049`, `legal_opinion_known_050`, `legal_opinion_known_051`, `legal_opinion_known_052`, `legal_opinion_known_053`, `legal_opinion_known_054`, `legal_opinion_known_055`, `legal_opinion_known_056`, `legal_opinion_known_057`, `legal_opinion_known_058`, `legal_opinion_known_059`, `legal_opinion_known_060`, `legal_opinion_known_061`, `legal_opinion_known_062`, `bond_trustee_report_known_018`, `bond_trustee_report_known_019`, `bond_trustee_report_known_020`, `bond_trustee_report_known_021`, `bond_trustee_report_known_022`, `bond_trustee_report_known_023`, `bond_trustee_report_known_024`, `bond_trustee_report_known_025`, `bond_trustee_report_known_026`, `bond_trustee_report_known_027`, `bond_trustee_report_known_028`, `bond_trustee_report_known_029`, `bond_trustee_report_known_030`, `bond_trustee_report_known_031`, `bond_trustee_report_known_032`, `bond_trustee_report_known_033`, `bond_trustee_report_known_034`, `bond_trustee_report_known_035`, `bond_trustee_report_known_036`, `bond_trustee_report_known_037`, `bond_trustee_report_known_038`, `bond_trustee_report_known_039`, `bond_trustee_report_known_040`, `bond_trustee_report_known_041`, `bond_trustee_report_known_042`, `bond_trustee_report_known_043`, `bond_trustee_report_known_044`, `bond_trustee_report_known_045`, `bond_trustee_report_known_046`, `bond_trustee_report_known_047`, `tracking_rating_report_known_013`, `tracking_rating_report_known_014`, `tracking_rating_report_known_015`, `tracking_rating_report_known_016`, `tracking_rating_report_known_017`, `tracking_rating_report_known_018`, `tracking_rating_report_known_019`, `tracking_rating_report_known_020`, `tracking_rating_report_known_021`, `tracking_rating_report_known_022`, `tracking_rating_report_known_023`, `tracking_rating_report_known_024`, `tracking_rating_report_known_025`, `tracking_rating_report_known_026`, `tracking_rating_report_known_027`, `tracking_rating_report_known_028`, `tracking_rating_report_known_029`, `tracking_rating_report_known_030`, `tracking_rating_report_known_031`, `tracking_rating_report_known_032`, `shareholder_meeting_known_020`, `shareholder_meeting_known_021`, `shareholder_meeting_known_022`, `shareholder_meeting_known_023`, `shareholder_meeting_known_024`, `shareholder_meeting_known_025`, `shareholder_meeting_known_026`, `shareholder_meeting_known_027`, `shareholder_meeting_known_028`, `shareholder_meeting_known_029`, `shareholder_meeting_known_030`, `shareholder_meeting_known_031`, `shareholder_meeting_known_032`, `shareholder_meeting_known_033`, `shareholder_meeting_known_034`, `shareholder_meeting_known_035`, `shareholder_meeting_known_036`, `shareholder_meeting_known_037`, `shareholder_meeting_known_038`, `shareholder_meeting_known_039`, `shareholder_meeting_known_040`, `shareholder_meeting_known_041`, `shareholder_meeting_known_042`, `shareholder_meeting_known_043`, `shareholder_meeting_known_044`, `shareholder_meeting_known_045`, `shareholder_meeting_known_046`, `shareholder_meeting_known_047`, `shareholder_meeting_known_048`, `board_resolution_known_011`, `board_resolution_known_012`, `board_resolution_known_013`, `board_resolution_known_014`, `board_resolution_known_015`, `board_resolution_known_016`, `board_resolution_known_017`, `board_resolution_known_018`, `board_resolution_known_019`, `board_resolution_known_020`, `board_resolution_known_021`, `board_resolution_known_022`, `board_resolution_known_023`, `board_resolution_known_024`, `board_resolution_known_025`, `board_resolution_known_026`, `board_resolution_known_027`, `board_resolution_known_028`, `board_resolution_known_029`, `board_resolution_known_030`, `board_resolution_known_031`, `board_resolution_known_032`, `board_resolution_known_033`, `board_resolution_known_034`, `board_resolution_known_035`, `supervisory_board_known_006`, `supervisory_board_known_007`, `supervisory_board_known_008`, `supervisory_board_known_009`, `supervisory_board_known_010`, `supervisory_board_known_011`, `supervisory_board_known_012`, `supervisory_board_known_013`, `supervisory_board_known_014`, `supervisory_board_known_015`, `supervisory_board_known_016`, `supervisory_board_known_017`, `supervisory_board_known_018`, `supervisory_board_known_019`, `supervisory_board_known_020`, `raised_funds_cash_management_known_005`, `raised_funds_cash_management_known_006`, `raised_funds_cash_management_known_007`, `raised_funds_cash_management_known_008`, `raised_funds_cash_management_known_009`, `raised_funds_cash_management_known_010`, `raised_funds_cash_management_known_011`, `raised_funds_cash_management_known_012`, `raised_funds_cash_management_known_013`, `raised_funds_cash_management_known_014`, `raised_funds_cash_management_known_015`, `raised_funds_cash_management_known_016`, `raised_funds_cash_management_known_017`, `raised_funds_cash_management_known_018`, `raised_funds_cash_management_known_019`, `continuous_supervision_annual_known_007`, `continuous_supervision_annual_known_008`, `continuous_supervision_annual_known_009`, `continuous_supervision_annual_known_010`, `continuous_supervision_annual_known_011`, `continuous_supervision_annual_known_012`, `continuous_supervision_annual_known_013`, `continuous_supervision_annual_known_014`, `verification_opinion_known_005`, `verification_opinion_known_006`, `verification_opinion_known_007`, `verification_opinion_known_008`, `verification_opinion_known_009`, `verification_opinion_known_010`, `company_articles_known_006`, `company_articles_known_007`, `company_articles_known_008`, `company_articles_known_009`, `company_articles_known_010`, `employee_stock_ownership_plan_known_004`, `employee_stock_ownership_plan_known_005`, `employee_stock_ownership_plan_known_006`, `employee_stock_ownership_plan_known_007`, `legal_opinion_known_063`, `legal_opinion_known_064`, `legal_opinion_known_065`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **200** |
| ready_cases | **200** |
| query_executed | **202** |
| pass | **193** |
| fail | **5** |
| ambiguous | **2** |
| not_found | **5** |
| request_error | **0** |
| result | **PARTIAL** |

## 4. 分 case 结果

| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |
|---------|------------------------|---------------|--------------|---------|-------|-------------|
| `legal_opinion_known_023` | 贝泰妮生物科技集团股份有限公司2024年年度股东大会的法律意 | 北京市君合律师事务所关于云南贝泰妮生物科技集团股份有限公司2024年年度股东大会… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_024` | 美瑞新材料股份有限公司2024年股东大会之法律意见书 | 北京市长安律师事务所关于美瑞新材料股份有限公司2024年股东大会之法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_025` | 孩子王儿童用品股份有限公司2024年年度股东会的法律意见书 | 北京市汉坤律师事务所关于孩子王儿童用品股份有限公司2024年年度股东会的法律意见… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_026` | 海科新源材料科技股份有限公司2024年年度股东会的法律意见书 | 山东海科新源材料科技股份有限公司2024年年度股东会的法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_027` | 日科化学股份有限公司2024年年度股东会的法律意见书 | 山东德衡（济南）律师事务所关于山东日科化学股份有限公司2024年年度股东会的法律… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_028` | 阳普医疗科技股份有限公司2024年年度股东会的法律意见书 | 北京市中伦（广州）律师事务所关于阳普医疗科技股份有限公司2024年年度股东会的法… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_029` | 田中精机股份有限公司2024年年度股东大会之法律意见书 | 北京君合（杭州）律师事务所关于浙江田中精机股份有限公司2024年年度股东大会之法… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_030` | 民生健康药业股份有限公司2024 年年度股东大会法律意见书 | 国浩律师（杭州）事务所关于杭州民生健康药业股份有限公司2024 年年度股东大会法… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_031` | 唐源电气股份有限公司2024年年度股东大会的法律意见书 | 北京金杜（成都）律师事务所关于成都唐源电气股份有限公司2024年年度股东大会的法… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_032` | 新巨丰科技包装股份有限公司2024年度股东大会之法律意见书 | 北京市金杜律师事务所关于山东新巨丰科技包装股份有限公司2024年度股东大会之法律… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_033` | 汉嘉设计2024年年度股东大会法律意见书 |  |  | false |  / not_found | **fail** |
| `legal_opinion_known_034` | 乐普医疗可转换公司债券回售的法律意见书 | 北京市中伦律师事务所关于乐普医疗可转换公司债券回售的法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_035` | 利亚德光电股份有限公司2024年年度股东大会的法律意见书 | 关于利亚德光电股份有限公司2024年年度股东大会的法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_036` | 东宝生物技术股份有限公司2024年度股东大会的法律意见书 | 上海仁盈律师事务所关于包头东宝生物技术股份有限公司2024年度股东大会的法律意见… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_037` | 朗特智能控制股份有限公司2024年年度股东大会法律意见书 | 广东信达律师事务所关于深圳朗特智能控制股份有限公司2024年年度股东大会法律意见… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_038` | 矩子科技股份有限公司2024年年度股东大会的法律意见书 | 国浩律师（上海）事务所关于上海矩子科技股份有限公司2024年年度股东大会的法律意… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_039` | 节能铁汉生态环境股份有限公司2024年年度股东大会的法律意见 | 北京中银（深圳）律师事务所关于中节能铁汉生态环境股份有限公司2024年年度股东大… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_040` | 慧博云通2024年年度股东会之法律意见书 | 金杜上海分所关于慧博云通2024年年度股东会之法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_041` | 熵基科技股份有限公司2024年度股东大会之法律意见书 | 国浩律师（深圳）事务所关于熵基科技股份有限公司2024年度股东大会之法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_042` | 凯龙高科技股份有限公司2024年年度股东大会的法律意见书 | 江苏世纪同仁律师事务所关于凯龙高科技股份有限公司2024年年度股东大会的法律意见… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_043` | 贝达药业股份有限公司2023年限制性股票激励计划首次授予部分 | 浙江天册律师事务所关于贝达药业股份有限公司2023年限制性股票激励计划首次授予部… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_044` | 鼎泰高科技术股份有限公司2024年年度股东大会的法律意见书 | 北京市中伦（深圳）律师事务所关于广东鼎泰高科技术股份有限公司2024年年度股东大… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_045` | 万讯自控股份有限公司2024年年度股东大会的法律意见书 | 广东信达律师事务所关于深圳万讯自控股份有限公司2024年年度股东大会的法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_046` | 锦浪科技股份有限公司2025年度向不特定对象发行可转换公司债 | 国浩律师（北京）事务所关于锦浪科技股份有限公司2025年度向不特定对象发行可转换… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_047` | 富邦科技股份有限公司2024年年度股东会法律意见书 | 湖北富邦科技股份有限公司2024年年度股东会法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_048` | 逸豪新材料股份有限公司2024年年度股东大会法律意见书 | 广东信达律师事务所关于赣州逸豪新材料股份有限公司2024年年度股东大会法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_049` | 富特科技股份有限公司2024年年度股东大会的法律意见书 | 浙江天册律师事务所关于浙江富特科技股份有限公司2024年年度股东大会的法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_050` | 新莱福新材料股份有限公司2024年年度股东大会的见证法律意见 | 广东信达律师事务所关于广州新莱福新材料股份有限公司2024年年度股东大会的见证法… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_051` | 鸿特科技2024年年度股东会之法律意见书 | 鸿特科技2024年年度股东会之法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_052` | 容大感光科技股份有限公司2024年年度股东大会的法律意见书 | 广东信达律师事务所关于深圳市容大感光科技股份有限公司2024年年度股东大会的法律… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_053` | 佐力药业股份有限公司2024年度股东大会的法律意见书 | 上海东方华银律师事务所关于浙江佐力药业股份有限公司2024年度股东大会的法律意见… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_054` | 捷安高科股份有限公司2024年年度股东大会法律意见书 | 北京市通商律师事务所关于郑州捷安高科股份有限公司2024年年度股东大会法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_055` | 华塑科技股份有限公司2024年年度股东大会的法律意见书 | 国浩律师（杭州）事务所关于杭州华塑科技股份有限公司2024年年度股东大会的法律意… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_056` | 华策影视股份有限公司2024年年度股东大会的法律意见书 | 国浩律师（杭州）事务所关于浙江华策影视股份有限公司2024年年度股东大会的法律意… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_057` | 钢研高纳科技股份有限公司2024年年度股东大会的法律意见书 | 北京市中咨律师事务所关于北京钢研高纳科技股份有限公司2024年年度股东大会的法律… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_058` | 联盛化学股份有限公司2024年年度股东大会法律意见书 | 国浩律师（杭州）事务所关于浙江联盛化学股份有限公司2024年年度股东大会法律意见… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_059` | 六九一二通信技术股份有限公司2024年年度股东会之法律意见书 | 国浩律师（成都）事务所关于四川六九一二通信技术股份有限公司2024年年度股东会之… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_060` | 华星创业通信技术股份有限公司2024年年度股东大会的法律意见 | 国浩律师（杭州）事务所关于杭州华星创业通信技术股份有限公司2024年年度股东大会… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_061` | 浙江力诺流体控制科技股份有限公司2024年度股东会的法律意见 | 北京德恒（杭州）律师事务所关于浙江力诺流体控制科技股份有限公司2024年度股东会… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_062` | 新易盛通信技术股份有限公司2024年度股东大会的法律意见书 | 北京国枫律师事务所关于成都新易盛通信技术股份有限公司2024年度股东大会的法律意… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_018` | 西部证券股份有限公司公司债券2025年第二次临时受托管理事务 | 国元证券股份有限公司关于西部证券股份有限公司公司债券2025年第二次临时受托管理… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_019` | 松霖科技股份有限公司公开发行可转换公司债券受托管理事务报告（ | 厦门松霖科技股份有限公司公开发行可转换公司债券受托管理事务报告（2024年度） | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_020` | 通裕重工股份有限公司向不特定对象发行可转换公司债券公司控制权 | 中信证券股份有限公司关于通裕重工股份有限公司向不特定对象发行可转换公司债券公司控… | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_021` | 新洋丰可转换公司发生分配股利行为的债券临时受托管理事务报告 | 东北证券关于新洋丰可转换公司发生分配股利行为的债券临时受托管理事务报告 | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_022` | 富春染织股份有限公司公开发行可转换公司债券受托管理事务报告（ | 芜湖富春染织股份有限公司公开发行可转换公司债券受托管理事务报告（2024年度） | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_023` | 广发证券股份有限公司完成注册资本工商变更登记并修订公司章程的 | 平安证券股份有限公司关于广发证券股份有限公司完成注册资本工商变更登记并修订公司章… | 2025-05-12 | true | cninfo_general_announcement_pdf / ambiguous | **ambiguous** |
| `bond_trustee_report_known_024` | 中绿电投资股份有限公司董事长发生变动的临时受托管理事务报告 | 中信证券股份有限公司关于天津中绿电投资股份有限公司董事长发生变动的临时受托管理事… | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_025` | 武汉天源集团股份有限公司向不特定对象发行可转换公司债券受托管 | 中天国富证券有限公司关于武汉天源集团股份有限公司向不特定对象发行可转换公司债券受… | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_026` | 南京聚隆科技股份有限公司受托管理事务报告（2024年度） | 南京聚隆科技股份有限公司受托管理事务报告（2024年度） | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_027` | 京源环保股份有限公司向不特定对象发行可转换公司债券受托管理事 | 江苏京源环保股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（2024… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_028` | 正帆科技股份有限公司涉及利润分配的临时受托管理事务报告 | 国泰海通证券股份有限公司关于上海正帆科技股份有限公司涉及利润分配的临时受托管理事… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_029` | 长城汽车股份有限公司公开发行A股可转换公司债券受托管理事务报 | 长城汽车股份有限公司公开发行A股可转换公司债券受托管理事务报告（2024年度） | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_030` | 丝路视觉科技股份有限公司2022年向不特定对象发行可转换公司 | 丝路视觉科技股份有限公司2022年向不特定对象发行可转换公司债券受托管理事务报告… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_031` | 富淼科技股份有限公司向不特定对象发行可转换公司债券第一次临时 | 江苏富淼科技股份有限公司向不特定对象发行可转换公司债券第一次临时受托管理事务报告… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_032` | 渤海租赁股份有限公司面向合格投资者公开发行公司债券临时受托管 | 长城证券股份有限公司关于渤海租赁股份有限公司面向合格投资者公开发行公司债券临时受… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_033` | 越秀资本控股集团股份有限公司副董事长、总经理退休离任并由副总 | 华福证券有限责任公司关于广州越秀资本控股集团股份有限公司副董事长、总经理退休离任… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_034` | 永安行科技股份有限公司聘任高级管理人员的临时受托管理事务报告 | 中国国际金融股份有限公司关于永安行科技股份有限公司聘任高级管理人员的临时受托管理… | 2025-05-08 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_035` | 华宏科技股份有限公司公开发行可转换公司债券受托管理事务报告（ | 江苏华宏科技股份有限公司公开发行可转换公司债券受托管理事务报告（2024年度） | 2025-05-08 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_036` | 金埔园林股份有限公司向不特定对象发行可转换公司债券受托管理事 | 金埔园林股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（2024年度… | 2025-05-08 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_037` | 五矿新能源材料（湖南）股份有限公司向不特定对象发行可转换公司 | 五矿新能源材料（湖南）股份有限公司向不特定对象发行可转换公司债券受托管理事务报告… | 2025-05-07 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_038` | 航天宏图信息技术股份有限公司向不特定对象发行可转换公司债券受 | 航天宏图信息技术股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（20… | 2025-05-07 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_039` | 双良节能系统股份有限公司向不特定对象发行可转换公司债券第三次 | 双良节能系统股份有限公司向不特定对象发行可转换公司债券第三次临时受托管理事务报告… | 2025-05-06 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_040` | 泉峰汽车精密技术股份有限公司2021年公开发行可转换公司债券 | 南京泉峰汽车精密技术股份有限公司2021年公开发行可转换公司债券第二次临时受托管… | 2025-05-06 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_041` | 美锦能源股份有限公司公开发行可转换公司债券2025年度第一次 | 山西美锦能源股份有限公司公开发行可转换公司债券2025年度第一次临时受托管理事务… | 2025-05-05 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_042` | 天合光能股份有限公司向不特定对象发行可转换公司债券受托管理事 | 天合光能股份有限公司向不特定对象发行可转换公司债券受托管理事务报告（2024年度… | 2025-04-29 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_043` | 奇正藏药股份有限公司公开发行可转换公司债券受托管理事务报告（ | 申万宏源证券承销保荐有限责任公司关于西藏奇正藏药股份有限公司公开发行可转换公司债… | 2025-04-29 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_044` | 回盛生物科技股份有限公司创业板向不特定对象发行可转换公司债券 | 国泰海通证券股份有限公司关于武汉回盛生物科技股份有限公司创业板向不特定对象发行可… | 2025-04-29 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_045` | 华特气体股份有限公司向不特定对象发行可转换公司债券2025年 | 中信建投证券股份有限公司关于广东华特气体股份有限公司向不特定对象发行可转换公司债… | 2025-04-28 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_046` | 法本信息技术股份有限公司向不特定对象发行可转换公司债券受托管 | 方正证券承销保荐有限责任公司关于深圳市法本信息技术股份有限公司向不特定对象发行可… | 2025-04-28 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_047` | 开能健康科技集团股份有限公司向不特定对象发行可转换公司债券2 | 长江证券承销保荐有限公司关于开能健康科技集团股份有限公司向不特定对象发行可转换公… | 2025-04-28 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_013` | 环旭电子股份有限公司2025年度跟踪评级报告 | 环旭电子股份有限公司2025年度跟踪评级报告 | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_014` | 长城汽车股份有限公司2025年度跟踪评级报告 | 长城汽车股份有限公司2025年度跟踪评级报告 | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_015` | 富春染织关于“富春转债”2024年跟踪评级结果的公告 |  |  | false |  / not_found | **fail** |
| `tracking_rating_report_known_016` | 富淼科技股份有限公司主体与相关债项2025年度跟踪评级报告 | 江苏富淼科技股份有限公司主体与相关债项2025年度跟踪评级报告 | 2025-04-29 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_017` | 瑞华泰薄膜科技股份有限公司2022年度向不特定对象发行可转换 | 深圳瑞华泰薄膜科技股份有限公司2022年度向不特定对象发行可转换公司债券2025… | 2025-04-29 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_018` | 蓝天燃气股份有限公司向不特定对象发行可转换公司债券2025年 | 2023年河南蓝天燃气股份有限公司向不特定对象发行可转换公司债券2025年跟踪评… | 2025-04-29 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_019` | 新宙邦科技股份有限公司向不特定对象发行可转换公司债券2025 | 2022年深圳新宙邦科技股份有限公司向不特定对象发行可转换公司债券2025年跟踪… | 2025-04-28 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_020` | 柳药集团股份有限公司关于公开发行可转换公司债券2025年跟踪 | 广西柳药集团股份有限公司关于公开发行可转换公司债券2025年跟踪评级结果的公告 | 2025-04-28 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_021` | 广发证券股份有限公司2025年度公开发行公司债券跟踪评级报告 | 广发证券股份有限公司2025年度公开发行公司债券跟踪评级报告 | 2025-04-28 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_022` | 力合微电子股份有限公司主体及“力合转债”2025年度跟踪评级 | 深圳市力合微电子股份有限公司主体及“力合转债”2025年度跟踪评级报告 | 2025-04-22 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_023` | 荣晟环保纸业股份有限公司关于“荣23转债”2025年跟踪评级 |  |  | false |  / not_found | **fail** |
| `tracking_rating_report_known_024` | 精达股份关于可转换公司债券2025年跟踪评级结果的公告 | 精达股份关于可转换公司债券2025年跟踪评级结果的公告 | 2025-04-18 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_025` | 神马股份关于向不特定对象发行可转换公司债券2025年跟踪评级 | 神马股份关于向不特定对象发行可转换公司债券2025年跟踪评级结果的公告 | 2025-04-16 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_026` | 聚赛龙工程塑料股份有限公司相关债券2025年跟踪评级报告 | 广州市聚赛龙工程塑料股份有限公司相关债券2025年跟踪评级报告 | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_027` | 欣旺达电子股份有限公司相关债券2025年跟踪评级报告 | 欣旺达电子股份有限公司相关债券2025年跟踪评级报告 | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_028` | 奥飞数据科技股份有限公司相关债券2025年跟踪评级报告 | 广东奥飞数据科技股份有限公司相关债券2025年跟踪评级报告 | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_029` | 康泰生物制品股份有限公司相关债券2025年跟踪评级报告 | 深圳康泰生物制品股份有限公司相关债券2025年跟踪评级报告 | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_030` | 甘肃能化股份有限公司相关债券2025年跟踪评级报告 | 甘肃能化股份有限公司相关债券2025年跟踪评级报告 | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_031` | 大中矿业股份有限公司相关债券2025年跟踪评级报告 | 大中矿业股份有限公司相关债券2025年跟踪评级报告 | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_032` | 易瑞生物技术股份有限公司相关债券2025年跟踪评级报告 | 深圳市易瑞生物技术股份有限公司相关债券2025年跟踪评级报告 | 2025-06-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_020` | 国科天成科技股份有限公司2024年年度股东大会决议公告 | 国科天成科技股份有限公司2024年年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_021` | 联盛化学股份有限公司2024年年度股东大会决议公告 | 浙江联盛化学股份有限公司2024年年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_022` | 新易盛通信技术股份有限公司2024年度股东大会决议公告 | 成都新易盛通信技术股份有限公司2024年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_023` | 朗进科技股份有限公司2024年度股东大会决议公告 | 山东朗进科技股份有限公司2024年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_024` | 顺网科技股份有限公司2024年年度股东大会决议公告 | 杭州顺网科技股份有限公司2024年年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_025` | 亨迪药业股份有限公司2024年年度股东大会决议公告 | 湖北亨迪药业股份有限公司2024年年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_026` | 成大生物股份有限公司2024年年度股东大会决议公告 | 辽宁成大生物股份有限公司2024年年度股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_027` | 智光电气股份有限公司2024年年度股东大会决议公告 | 广州智光电气股份有限公司2024年年度股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_028` | 艾力斯医药科技股份有限公司2024年年度股东大会决议公告 | 上海艾力斯医药科技股份有限公司2024年年度股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_029` | 嘉泽新能源股份有限公司2025年第一次临时股东大会决议公告 | 嘉泽新能源股份有限公司2025年第一次临时股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_030` | 天士力2025年第三次临时股东大会决议公告 | 天士力2025年第三次临时股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_031` | 中盐化工2025年第二次临时股东大会决议公告 | 中盐化工2025年第二次临时股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_032` | 金能科技股份有限公司2025年第二次临时股东大会决议公告 | 金能科技股份有限公司2025年第二次临时股东大会决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_033` | ST宁科2025年第一次临时股东大会决议公告 | ST宁科2025年第一次临时股东大会决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_034` | 淮河能源（集团）股份有限公司2025年第一次临时股东大会决议 | 淮河能源（集团）股份有限公司2025年第一次临时股东大会决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_035` | 银邦股份2024年年度股东大会决议公告 | 银邦股份2024年年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_036` | 坤泰股份2024年年度股东大会决议公告 | 坤泰股份2024年年度股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_037` | 华勤技术2024年年度股东大会决议公告 | 华勤技术2024年年度股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_038` | 河南凯旺电子科技股份有限公司2024年年度股东大会决议公告 | 河南凯旺电子科技股份有限公司2024年年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_039` | 艾艾精密工业输送系统（上海）股份有限公司2025年第一次临时 | 艾艾精密工业输送系统（上海）股份有限公司2025年第一次临时股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_040` | 2025年第一次临时股东大会决议的公告 | 关于2025年第一次临时股东大会决议的公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_041` | 维维食品饮料股份有限公司2025年第一次临时股东大会决议公告 | 维维食品饮料股份有限公司2025年第一次临时股东大会决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_042` | 2024年年度股东大会决议的公告 | 2024年年度股东大会决议的公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_043` | 2024年度股东大会决议的公告 | 2024年度股东大会决议的公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_044` | 2025年第1次临时股东大会决议的公告 | 2025年第1次临时股东大会决议的公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_045` | 关于2024年年度股东大会决议公告 | 关于2024年年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_046` | 2025年第五次临时股东大会决议公告 | 2025年第五次临时股东大会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_047` | 2025年度第三次临时股东大会决议公告 | 2025年度第三次临时股东大会决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_048` | 2024年度股东大会决议公告 | 2024年度股东大会决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_011` | 国安达股份有限公司第四届董事会第二十八次会议决议公告 | 国安达股份有限公司第四届董事会第二十八次会议决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_012` | 银邦股份第五届董事会第十八次会议决议公告 | 银邦股份第五届董事会第十八次会议决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_013` | 浙江东日股份有限公司第九届董事会第四十次会议决议公告 | 浙江东日股份有限公司第九届董事会第四十次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_014` | 盛和资源控股股份有限公司第九届董事会第三次会议决议公告 | 盛和资源控股股份有限公司第九届董事会第三次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_015` | 旗滨集团第五届董事会第三十九次会议决议公告 | 旗滨集团第五届董事会第三十九次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_016` | 冠农股份有限公司第七届董事会第三十九次（临时）会议决议公告 | 新疆冠农股份有限公司第七届董事会第三十九次（临时）会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_017` | 景业智能第二届董事会第十五次会议决议公告 | 景业智能第二届董事会第十五次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_018` | 冠城新材第十二届董事会第十三次（临时）会议决议公告 | 冠城新材第十二届董事会第十三次（临时）会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_019` | 厦门钨业第十届董事会第十四次会议决议公告 | 厦门钨业第十届董事会第十四次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_020` | 创业环保第九届董事会第五十九次会议决议公告 | 创业环保第九届董事会第五十九次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_021` | 三元股份第八届董事会第四十一次会议决议公告 | 三元股份第八届董事会第四十一次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_022` | 精工钢构关于第九届董事会2025年度第十一次临时会议决议公告 | 精工钢构关于第九届董事会2025年度第十一次临时会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_023` | 开创国际第十届董事会第十六次（临时）会议决议公告 | 开创国际第十届董事会第十六次（临时）会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_024` | 上海贝岭第九届董事会第十九次会议决议公告 | 上海贝岭第九届董事会第十九次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_025` | 天成自控第五届董事会第十八次会议决议公告 | 天成自控第五届董事会第十八次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_026` | 国缆检测股份有限公司第二届董事会第十次会议决议公告-32 | 上海国缆检测股份有限公司第二届董事会第十次会议决议公告-32 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_027` | 百川能源第十二届董事会第一次会议决议公告 | 百川能源第十二届董事会第一次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_028` | 国睿科技股份有限公司第十届董事会第一次会议决议公告 | 国睿科技股份有限公司第十届董事会第一次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_029` | 华峰化学股份有限公司第九届董事会第十次会议决议公告 | 华峰化学股份有限公司第九届董事会第十次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_030` | 上海电力股份有限公司第九届董事会第三次会议决议公告 | 上海电力股份有限公司第九届董事会第三次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_031` | 珍宝岛药业股份有限公司第五届董事会第二十二次会议决议公告 | 黑龙江珍宝岛药业股份有限公司第五届董事会第二十二次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_032` | 平高电气股份有限公司第九届董事会第十三次临时会议决议公告 | 河南平高电气股份有限公司第九届董事会第十三次临时会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_033` | 钱江水利开发股份有限公司第八届董事会第十三次临时会议决议公告 | 钱江水利开发股份有限公司第八届董事会第十三次临时会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_034` | 均普智能制造股份有限公司第二届董事会第三十三次会议决议公告 | 宁波均普智能制造股份有限公司第二届董事会第三十三次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `board_resolution_known_035` | 华鑫股份第十一届董事会第十六次会议决议公告 | 华鑫股份第十一届董事会第十六次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_006` | 银邦股份第五届监事会第十六次会议决议公告 | 银邦股份第五届监事会第十六次会议决议公告 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_007` | 浙江东日股份有限公司第九届监事会第二十九次会议决议公告 | 浙江东日股份有限公司第九届监事会第二十九次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_008` | 旗滨集团第五届监事会第三十八次会议决议公告 | 旗滨集团第五届监事会第三十八次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_009` | 冠农股份有限公司第七届监事会第三十八次会议决议公告 | 新疆冠农股份有限公司第七届监事会第三十八次会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_010` | 精工钢构关于第九届监事会2025年度第二次临时会议决议公告 | 精工钢构关于第九届监事会2025年度第二次临时会议决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_011` | 川投能源股份有限公司十一届三十九次监事会决议公告 | 四川川投能源股份有限公司十一届三十九次监事会决议公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_012` | 国缆检测股份有限公司第二届监事会第九次会议决议公告-33 | 上海国缆检测股份有限公司第二届监事会第九次会议决议公告-33 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_013` | 动力源第八届监事会第三十三次会议决议公告 | 动力源第八届监事会第三十三次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_014` | 华峰化学股份有限公司第九届监事会第九次会议决议公告 | 华峰化学股份有限公司第九届监事会第九次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_015` | 珍宝岛药业股份有限公司第五届监事会第十八次会议决议公告 | 黑龙江珍宝岛药业股份有限公司第五届监事会第十八次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_016` | 均普智能制造股份有限公司第二届监事会第二十三次会议决议公告 | 宁波均普智能制造股份有限公司第二届监事会第二十三次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_017` | 华鑫股份第十一届监事会第十一次会议决议公告 | 华鑫股份第十一届监事会第十一次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_018` | 明泰铝业第六届监事会第十八次会议决议公告 | 明泰铝业第六届监事会第十八次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_019` | 顺网科技股份有限公司第五届监事会第二十次会议决议公告 | 杭州顺网科技股份有限公司第五届监事会第二十次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `supervisory_board_known_020` | 天铁科技股份有限公司第五届监事会第九次会议决议公告 | 浙江天铁科技股份有限公司第五届监事会第九次会议决议公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_005` | 佰维存储科技股份有限公司使用向特定对象发行股票部分暂时闲置募 | 华泰联合证券有限责任公司关于深圳佰维存储科技股份有限公司使用向特定对象发行股票部… | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_006` | 安徽合力股份有限公司关于使用部分暂时闲置募集资金进行现金管理 | 安徽合力股份有限公司关于使用部分暂时闲置募集资金进行现金管理到期赎回的公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_007` | 蓝天燃气关于使用部分闲置募集资金进行现金管理的进展公告 | 蓝天燃气关于使用部分闲置募集资金进行现金管理的进展公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_008` | 露笑科技股份有限公司使用部分闲置募集资金进行现金管理的核查意 | 国泰海通证券股份有限公司关于露笑科技股份有限公司使用部分闲置募集资金进行现金管理… | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_009` | 晨曦航空科技股份有限公司关于使用部分闲置募集资金进行现金管理 | 西安晨曦航空科技股份有限公司关于使用部分闲置募集资金进行现金管理的进展公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_010` | 国检集团关于使用闲置募集资金进行现金管理进展的公告 | 国检集团关于使用闲置募集资金进行现金管理进展的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_011` | 世运电路关于使用部分闲置募集资金进行现金管理到期赎回的公告 | 世运电路关于使用部分闲置募集资金进行现金管理到期赎回的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_012` | 首旅酒店（集团）股份有限公司关于使用闲置募集资金进行现金管理 | 北京首旅酒店（集团）股份有限公司关于使用闲置募集资金进行现金管理到期赎回并继续进… | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_013` | 中际联合关于使用闲置募集资金进行现金管理的进展公告 | 中际联合关于使用闲置募集资金进行现金管理的进展公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_014` | 大胜达包装股份有限公司关于使用部分闲置募集资金进行现金管理到 | 浙江大胜达包装股份有限公司关于使用部分闲置募集资金进行现金管理到期赎回的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_015` | 康辰药业关于使用部分闲置募集资金进行现金管理赎回的公告 | 康辰药业关于使用部分闲置募集资金进行现金管理赎回的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_016` | 中重科技关于使用部分闲置募集资金进行现金管理到期赎回的公告 | 中重科技关于使用部分闲置募集资金进行现金管理到期赎回的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_017` | 三江购物关于闲置募集资金进行现金管理部分到期赎回的公告 | 三江购物关于闲置募集资金进行现金管理部分到期赎回的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_018` | 恒尚节能：关于使用闲置募集资金进行现金管理部分到期赎回的公告 | 恒尚节能：关于使用闲置募集资金进行现金管理部分到期赎回的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `raised_funds_cash_management_known_019` | 信凯科技集团股份有限公司使用部分闲置募集资金进行现金管理的核 | 国投证券股份有限公司关于浙江信凯科技集团股份有限公司使用部分闲置募集资金进行现金… | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_007` | 康鹏科技股份有限公司2024年持续督导年度报告书 | 中信建投证券股份有限公司关于上海康鹏科技股份有限公司2024年持续督导年度报告书 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_008` | 盛景微电子股份有限公司2024年度持续督导年度报告书 |  光大证券股份有限公司关于无锡盛景微电子股份有限公司2024年度持续督导年度报告… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_009` | 鼎际得石化股份有限公司2024年度持续督导年度报告书 | 国泰海通证券股份有限公司关于辽宁鼎际得石化股份有限公司2024年度持续督导年度报… | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_010` | 曲美家居集团股份有限公司2024年持续督导年度报告书 | 华泰联合证券有限责任公司关于曲美家居集团股份有限公司2024年持续督导年度报告书 | 2025-05-09 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_011` | 航天长峰股份有限公司2024年持续督导年度报告书 | 中信建投证券股份有限公司关于北京航天长峰股份有限公司2024年持续督导年度报告书 | 2025-05-08 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_012` | 三房巷聚材股份有限公司2024年持续督导年度报告书 |  |  | false |  / not_found | **fail** |
| `continuous_supervision_annual_known_013` | 双良节能系统股份有限公司2024年度持续督导年度报告书 | 中国国际金融股份有限公司关于双良节能系统股份有限公司2024年度持续督导年度报告… | 2025-05-08 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `continuous_supervision_annual_known_014` | 安乃达驱动技术（上海）股份有限公司2024年度持续督导年度报 | 中泰证券股份有限公司关于安乃达驱动技术（上海）股份有限公司2024年度持续督导年… | 2025-05-08 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `verification_opinion_known_005` | 美瑞新材料股份有限公司使用募集资金置换预先已投入募投项目及已 | 关于美瑞新材料股份有限公司使用募集资金置换预先已投入募投项目及已支付发行费用的自… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `verification_opinion_known_006` | 孩子王儿童用品股份有限公司全资子公司参与汉桑（南京）科技股份 | 华泰联合证券有限责任公司关于孩子王儿童用品股份有限公司全资子公司参与汉桑（南京）… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `verification_opinion_known_007` | 乐普医疗可转换公司债券回售有关事项的核查意见 | 国泰海通证券股份有限公司关于乐普医疗可转换公司债券回售有关事项的核查意见 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `verification_opinion_known_008` | 艾比森光电股份有限公司2021年度向特定对象发行股票限售股解 | 国泰海通证券股份有限公司关于深圳市艾比森光电股份有限公司2021年度向特定对象发… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `verification_opinion_known_009` | 思林杰科技股份有限公司本次交易方案调整不构成重组方案重大调整 | 民生证券股份有限公司关于广州思林杰科技股份有限公司本次交易方案调整不构成重组方案… | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `verification_opinion_known_010` | 海通发展股份有限公司监事会关于2025年股票期权与限制性股票 | 福建海通发展股份有限公司监事会关于2025年股票期权与限制性股票激励计划首次授予… | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `company_articles_known_006` | 浙江东日股份有限公司关于取消监事会并修订《公司章程》的公告 | 浙江东日股份有限公司关于取消监事会并修订《公司章程》的公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `company_articles_known_007` | 盛和资源控股股份有限公司关于修改公司章程及议事规则的公告 | 盛和资源控股股份有限公司关于修改公司章程及议事规则的公告 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `company_articles_known_008` | 冠农股份有限公司章程（2025年5月修订） | 新疆冠农股份有限公司章程（2025年5月修订） | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `company_articles_known_009` | 美好医疗公司章程全文（2025年5月修订） | 美好医疗公司章程全文（2025年5月修订） | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `company_articles_known_010` | 华鑫股份关于取消监事会暨修改《公司章程》的公告 | 华鑫股份关于取消监事会暨修改《公司章程》的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / ambiguous | **ambiguous** |
| `employee_stock_ownership_plan_known_004` | 丰光精密机械股份有限公司2025年员工持股计划（草案）的法律 | 山东国曜琴岛（青岛）律师事务所关于青岛丰光精密机械股份有限公司2025年员工持股… | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `employee_stock_ownership_plan_known_005` | 海锅股份：张家港海锅新能源装备股份有限公司2025年员工持股 | 海锅股份：张家港海锅新能源装备股份有限公司2025年员工持股计划管理办法 | 2025-05-14 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `employee_stock_ownership_plan_known_006` | 中科微至关于第二期员工持股计划预留股份完成非交易过户的公告 | 中科微至关于第二期员工持股计划预留股份完成非交易过户的公告 | 2025-05-13 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `employee_stock_ownership_plan_known_007` | 创远信科（上海）技术股份有限公司2025年员工持股计划（草案 | 上海市金茂律师事务所关于创远信科（上海）技术股份有限公司2025年员工持股计划（… | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_063` | 田中精机股份有限公司2025年限制性股票激励计划首次授予相关 | 北京君合（杭州）律师事务所关于浙江田中精机股份有限公司2025年限制性股票激励计… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_064` | 乐普医疗2024年年度股东大会的法律意见书 | 北京市中伦律师事务所关于乐普医疗2024年年度股东大会的法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_065` | 乐普医疗“乐普转2”2025年第一次债券持有人会议的法律意见 |  |  | false |  / not_found | **fail** |

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

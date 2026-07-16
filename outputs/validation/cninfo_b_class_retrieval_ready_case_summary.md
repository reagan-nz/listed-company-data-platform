# CNINFO B 类 Retrieval Ready Case Summary

_生成时间：2026-07-16（ready-case selector；不请求 CNINFO）_

## 1. 目的

筛选 `case_status: ready` 且字段完备的 retrieval validation case。
**不是** live retrieval validation；不下载 PDF；不写 verified。

## 2. 输入

| 来源 | 路径 |
|------|------|
| Known-document cases | `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` |
| Category-sample cases | `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` |
| 规则 | `plans/cninfo_b_class_retrieval_ready_case_rules.md` |
| 脚本 | `lab/select_cninfo_b_class_retrieval_ready_cases.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **355** |
| placeholder | **2** |
| ready | **353** |
| retired | **0** |
| invalid_ready | **0** |
| result | **PASS** |

## 4. Ready case 明细

- `inquiry_known_001` (known_document) → `cninfo_inquiry_reply_pdf`
- `inquiry_known_002` (known_document) → `cninfo_inquiry_reply_pdf`
- `inquiry_known_003` (known_document) → `cninfo_inquiry_reply_pdf`
- `inquiry_known_004` (known_document) → `cninfo_inquiry_reply_pdf`
- `regulatory_known_001` (known_document) → `cninfo_inquiry_reply_pdf`
- `regulatory_known_002` (known_document) → `cninfo_inquiry_reply_pdf`
- `meeting_known_001` (known_document) → `cninfo_meeting_notice_pdf`
- `meeting_known_002` (known_document) → `cninfo_meeting_notice_pdf`
- `ir_activity_known_001` (known_document) → `cninfo_meeting_notice_pdf`
- `ir_activity_known_002` (known_document) → `cninfo_meeting_notice_pdf`
- `ir_activity_known_003` (known_document) → `cninfo_meeting_notice_pdf`
- `board_resolution_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `listing_sponsor_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `equity_change_report_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_training_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `nonstandard_audit_opinion_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_usage_report_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `independent_director_meeting_review_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `independent_director_nominee_declaration_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `independent_director_nominee_declaration_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `asset_valuation_explanation_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `audit_report_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `incentive_trading_self_inspection_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `employee_stock_ownership_plan_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `employee_stock_ownership_plan_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `employee_stock_ownership_plan_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_management_system_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `independent_ned_work_system_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `general_manager_work_rules_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `independent_director_annual_report_work_system_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `independent_director_annual_report_work_system_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `monetary_funds_management_system_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `external_guarantee_management_system_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `subsidiary_management_system_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `compensation_assessment_plan_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `external_guarantee_situation_brief_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `esg_report_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `incentive_object_list_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `sales_brief_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_015` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_016` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_017` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_015` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_016` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_017` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_018` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_001` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_002` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_003` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_019` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_020` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_021` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_022` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_015` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_016` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_017` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_018` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_019` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_023` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_024` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_025` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_026` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_027` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_028` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_029` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_030` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_031` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_032` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_033` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_034` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_035` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_036` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_037` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_038` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_039` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_040` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_041` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_042` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_043` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_044` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_045` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_046` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_047` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_048` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_049` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_050` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_051` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_052` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_053` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_054` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_055` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_056` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_057` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_058` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_059` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_060` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_061` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_062` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_018` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_019` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_020` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_021` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_022` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_023` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_024` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_025` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_026` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_027` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_028` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_029` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_030` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_031` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_032` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_033` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_034` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_035` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_036` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_037` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_038` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_039` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_040` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_041` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_042` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_043` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_044` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_045` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_046` (known_document) → `cninfo_general_announcement_pdf`
- `bond_trustee_report_known_047` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_015` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_016` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_017` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_018` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_019` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_020` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_021` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_022` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_023` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_024` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_025` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_026` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_027` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_028` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_029` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_030` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_031` (known_document) → `cninfo_general_announcement_pdf`
- `tracking_rating_report_known_032` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_020` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_021` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_022` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_023` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_024` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_025` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_026` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_027` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_028` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_029` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_030` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_031` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_032` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_033` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_034` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_035` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_036` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_037` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_038` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_039` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_040` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_041` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_042` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_043` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_044` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_045` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_046` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_047` (known_document) → `cninfo_general_announcement_pdf`
- `shareholder_meeting_known_048` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_015` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_016` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_017` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_018` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_019` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_020` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_021` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_022` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_023` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_024` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_025` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_026` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_027` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_028` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_029` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_030` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_031` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_032` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_033` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_034` (known_document) → `cninfo_general_announcement_pdf`
- `board_resolution_known_035` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_015` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_016` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_017` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_018` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_019` (known_document) → `cninfo_general_announcement_pdf`
- `supervisory_board_known_020` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_015` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_016` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_017` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_018` (known_document) → `cninfo_general_announcement_pdf`
- `raised_funds_cash_management_known_019` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_011` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_012` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_013` (known_document) → `cninfo_general_announcement_pdf`
- `continuous_supervision_annual_known_014` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `verification_opinion_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_008` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_009` (known_document) → `cninfo_general_announcement_pdf`
- `company_articles_known_010` (known_document) → `cninfo_general_announcement_pdf`
- `employee_stock_ownership_plan_known_004` (known_document) → `cninfo_general_announcement_pdf`
- `employee_stock_ownership_plan_known_005` (known_document) → `cninfo_general_announcement_pdf`
- `employee_stock_ownership_plan_known_006` (known_document) → `cninfo_general_announcement_pdf`
- `employee_stock_ownership_plan_known_007` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_063` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_064` (known_document) → `cninfo_general_announcement_pdf`
- `legal_opinion_known_065` (known_document) → `cninfo_general_announcement_pdf`
- `general_sample_001` (category_sample) → `cninfo_general_announcement_pdf`
- `general_sample_002` (category_sample) → `cninfo_general_announcement_pdf`
- `general_sample_003` (category_sample) → `cninfo_general_announcement_pdf`
- `inquiry_sample_001` (category_sample) → `cninfo_inquiry_reply_pdf`
- `inquiry_sample_002` (category_sample) → `cninfo_inquiry_reply_pdf`
- `inquiry_sample_003` (category_sample) → `cninfo_inquiry_reply_pdf`
- `meeting_sample_001` (category_sample) → `cninfo_meeting_notice_pdf`
- `meeting_sample_002` (category_sample) → `cninfo_general_announcement_pdf`
- `ir_activity_sample_001` (category_sample) → `cninfo_meeting_notice_pdf`
- `ir_activity_sample_002` (category_sample) → `cninfo_meeting_notice_pdf`
- `periodic_guard_002` (category_sample) → `cninfo_general_announcement_pdf`

## 5. Invalid ready 明细

_无 invalid_ready case。_

## 6. 质量边界

- Ready-case selector **不是** retrieval validation。
- **不代表** CNINFO coverage%。
- **不下载** PDF；**不写 verified**。
- 未来 live 脚本 **只** 应对 `ready_status=ready` 的 case 发起请求。

## 7. 下一步

1. 人工补 3–5 条真实 known-document case（company_code + date window + title）。
2. 将审核通过的 case 的 `case_status` 改为 `ready`。
3. 再跑 selector 确认 `invalid_ready=0`。
4. 实现 `validate_cninfo_b_class_corpus_retrieval.py` 仅消费 ready cases。

## 附录

详见 [cninfo_b_class_retrieval_ready_case_report.csv](cninfo_b_class_retrieval_ready_case_report.csv)。

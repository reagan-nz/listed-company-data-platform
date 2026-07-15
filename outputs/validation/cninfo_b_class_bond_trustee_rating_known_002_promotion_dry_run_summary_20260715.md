# CNINFO B 类 Corpus Retrieval Dry-run Summary

_生成时间：2026-07-15（corpus retrieval 脚本骨架 dry-run；不请求 CNINFO）_

## 1. 目的

验证 `lab/validate_cninfo_b_class_corpus_retrieval.py` 骨架：
加载 **ready** case、校验字段、输出 dry-run 报告。**不发起 CNINFO 请求。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Known-document cases | `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` |
| Category-sample cases | `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| dry_run | **True** |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **70** |
| ready_cases | **68** |
| invalid_ready | **0** |
| placeholder_cases | **2** |
| retired_cases | **0** |
| query_executed | **0** |
| result | **DRY_RUN_PASS** |

## 4. Ready case 明细

- `inquiry_known_001` would_query=true
- `inquiry_known_002` would_query=true
- `inquiry_known_003` would_query=true
- `inquiry_known_004` would_query=true
- `regulatory_known_001` would_query=true
- `regulatory_known_002` would_query=true
- `meeting_known_001` would_query=true
- `meeting_known_002` would_query=true
- `ir_activity_known_001` would_query=true
- `ir_activity_known_002` would_query=true
- `ir_activity_known_003` would_query=true
- `board_resolution_known_001` would_query=true
- `supervisory_board_known_001` would_query=true
- `supervisory_board_known_002` would_query=true
- `legal_opinion_known_001` would_query=true
- `legal_opinion_known_002` would_query=true
- `legal_opinion_known_003` would_query=true
- `legal_opinion_known_004` would_query=true
- `legal_opinion_known_005` would_query=true
- `legal_opinion_known_006` would_query=true
- `verification_opinion_known_001` would_query=true
- `verification_opinion_known_002` would_query=true
- `listing_sponsor_known_001` would_query=true
- `equity_change_report_known_001` would_query=true
- `bond_trustee_report_known_001` would_query=true
- `bond_trustee_report_known_002` would_query=true
- `tracking_rating_report_known_001` would_query=true
- `tracking_rating_report_known_002` would_query=true
- `continuous_supervision_annual_known_001` would_query=true
- `continuous_supervision_training_known_001` would_query=true
- `nonstandard_audit_opinion_known_001` would_query=true
- `raised_funds_usage_report_known_001` would_query=true
- `independent_director_meeting_review_known_001` would_query=true
- `independent_director_nominee_declaration_known_001` would_query=true
- `asset_valuation_explanation_known_001` would_query=true
- `audit_report_known_001` would_query=true
- `incentive_trading_self_inspection_known_001` would_query=true
- `employee_stock_ownership_plan_known_001` would_query=true
- `company_articles_known_001` would_query=true
- `raised_funds_management_system_known_001` would_query=true
- `independent_ned_work_system_known_001` would_query=true
- `general_manager_work_rules_known_001` would_query=true
- `monetary_funds_management_system_known_001` would_query=true
- `external_guarantee_management_system_known_001` would_query=true
- `subsidiary_management_system_known_001` would_query=true
- `compensation_assessment_plan_known_001` would_query=true
- `external_guarantee_situation_brief_known_001` would_query=true
- `esg_report_known_001` would_query=true
- `incentive_object_list_known_001` would_query=true
- `sales_brief_known_001` would_query=true
- `shareholder_meeting_known_001` would_query=true
- `shareholder_meeting_known_002` would_query=true
- `shareholder_meeting_known_003` would_query=true
- `shareholder_meeting_known_004` would_query=true
- `shareholder_meeting_known_005` would_query=true
- `shareholder_meeting_known_006` would_query=true
- `shareholder_meeting_known_007` would_query=true
- `general_sample_001` would_query=true
- `general_sample_002` would_query=true
- `general_sample_003` would_query=true
- `inquiry_sample_001` would_query=true
- `inquiry_sample_002` would_query=true
- `inquiry_sample_003` would_query=true
- `meeting_sample_001` would_query=true
- `meeting_sample_002` would_query=true
- `ir_activity_sample_001` would_query=true
- `ir_activity_sample_002` would_query=true
- `periodic_guard_002` would_query=true

## 5. Dry-run 行为

- `would_query=true` 仅表示 **未来** 将对该 case 发起 `hisAnnouncement/query`。
- 本阶段所有行 `query_status=not_executed_dry_run`。
- Live metadata：使用 `--live-metadata`（见 live summary 输出）。

## 6. 质量边界

- **不代表** CNINFO retrieval coverage%。
- **不代表** PDF URL 已补齐或 PDF 已下载/解析。
- **不写 verified**；**不升级** candidate source。

## 7. 下一步

1. 人工补 3–5 条真实 ready case（见 intake template + review checklist）。
2. 运行 `select_cninfo_b_class_retrieval_ready_cases.py` 确认 `invalid_ready=0`。
3. 再运行本 dry-run 脚本确认 ready case 被正确选中。
4. 最后才实现 live metadata request（单独评审）。

## 附录

详见 [cninfo_b_class_corpus_retrieval_dry_run_report.csv](cninfo_b_class_corpus_retrieval_dry_run_report.csv)。

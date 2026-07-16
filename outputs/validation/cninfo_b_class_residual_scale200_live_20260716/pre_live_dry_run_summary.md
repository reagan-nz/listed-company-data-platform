# CNINFO B 类 Corpus Retrieval Dry-run Summary

_生成时间：2026-07-16（corpus retrieval 脚本骨架 dry-run；不请求 CNINFO）_

## 1. 目的

验证 `lab/validate_cninfo_b_class_corpus_retrieval.py` 骨架：
加载 **ready** case、校验字段、输出 dry-run 报告。**不发起 CNINFO 请求。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Known-document cases | `outputs/validation/cninfo_b_class_residual_scale200_live_20260716/known_document_retrieval_cases_live_allowlist.yaml` |
| Category-sample cases | `outputs/validation/cninfo_b_class_residual_scale200_live_20260716/category_sample_cases_live_empty.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| dry_run | **True** |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **200** |
| ready_cases | **200** |
| invalid_ready | **0** |
| placeholder_cases | **0** |
| retired_cases | **0** |
| query_executed | **0** |
| result | **DRY_RUN_PASS** |

## 4. Ready case 明细

- `legal_opinion_known_023` would_query=true
- `legal_opinion_known_024` would_query=true
- `legal_opinion_known_025` would_query=true
- `legal_opinion_known_026` would_query=true
- `legal_opinion_known_027` would_query=true
- `legal_opinion_known_028` would_query=true
- `legal_opinion_known_029` would_query=true
- `legal_opinion_known_030` would_query=true
- `legal_opinion_known_031` would_query=true
- `legal_opinion_known_032` would_query=true
- `legal_opinion_known_033` would_query=true
- `legal_opinion_known_034` would_query=true
- `legal_opinion_known_035` would_query=true
- `legal_opinion_known_036` would_query=true
- `legal_opinion_known_037` would_query=true
- `legal_opinion_known_038` would_query=true
- `legal_opinion_known_039` would_query=true
- `legal_opinion_known_040` would_query=true
- `legal_opinion_known_041` would_query=true
- `legal_opinion_known_042` would_query=true
- `legal_opinion_known_043` would_query=true
- `legal_opinion_known_044` would_query=true
- `legal_opinion_known_045` would_query=true
- `legal_opinion_known_046` would_query=true
- `legal_opinion_known_047` would_query=true
- `legal_opinion_known_048` would_query=true
- `legal_opinion_known_049` would_query=true
- `legal_opinion_known_050` would_query=true
- `legal_opinion_known_051` would_query=true
- `legal_opinion_known_052` would_query=true
- `legal_opinion_known_053` would_query=true
- `legal_opinion_known_054` would_query=true
- `legal_opinion_known_055` would_query=true
- `legal_opinion_known_056` would_query=true
- `legal_opinion_known_057` would_query=true
- `legal_opinion_known_058` would_query=true
- `legal_opinion_known_059` would_query=true
- `legal_opinion_known_060` would_query=true
- `legal_opinion_known_061` would_query=true
- `legal_opinion_known_062` would_query=true
- `bond_trustee_report_known_018` would_query=true
- `bond_trustee_report_known_019` would_query=true
- `bond_trustee_report_known_020` would_query=true
- `bond_trustee_report_known_021` would_query=true
- `bond_trustee_report_known_022` would_query=true
- `bond_trustee_report_known_023` would_query=true
- `bond_trustee_report_known_024` would_query=true
- `bond_trustee_report_known_025` would_query=true
- `bond_trustee_report_known_026` would_query=true
- `bond_trustee_report_known_027` would_query=true
- `bond_trustee_report_known_028` would_query=true
- `bond_trustee_report_known_029` would_query=true
- `bond_trustee_report_known_030` would_query=true
- `bond_trustee_report_known_031` would_query=true
- `bond_trustee_report_known_032` would_query=true
- `bond_trustee_report_known_033` would_query=true
- `bond_trustee_report_known_034` would_query=true
- `bond_trustee_report_known_035` would_query=true
- `bond_trustee_report_known_036` would_query=true
- `bond_trustee_report_known_037` would_query=true
- `bond_trustee_report_known_038` would_query=true
- `bond_trustee_report_known_039` would_query=true
- `bond_trustee_report_known_040` would_query=true
- `bond_trustee_report_known_041` would_query=true
- `bond_trustee_report_known_042` would_query=true
- `bond_trustee_report_known_043` would_query=true
- `bond_trustee_report_known_044` would_query=true
- `bond_trustee_report_known_045` would_query=true
- `bond_trustee_report_known_046` would_query=true
- `bond_trustee_report_known_047` would_query=true
- `tracking_rating_report_known_013` would_query=true
- `tracking_rating_report_known_014` would_query=true
- `tracking_rating_report_known_015` would_query=true
- `tracking_rating_report_known_016` would_query=true
- `tracking_rating_report_known_017` would_query=true
- `tracking_rating_report_known_018` would_query=true
- `tracking_rating_report_known_019` would_query=true
- `tracking_rating_report_known_020` would_query=true
- `tracking_rating_report_known_021` would_query=true
- `tracking_rating_report_known_022` would_query=true
- `tracking_rating_report_known_023` would_query=true
- `tracking_rating_report_known_024` would_query=true
- `tracking_rating_report_known_025` would_query=true
- `tracking_rating_report_known_026` would_query=true
- `tracking_rating_report_known_027` would_query=true
- `tracking_rating_report_known_028` would_query=true
- `tracking_rating_report_known_029` would_query=true
- `tracking_rating_report_known_030` would_query=true
- `tracking_rating_report_known_031` would_query=true
- `tracking_rating_report_known_032` would_query=true
- `shareholder_meeting_known_020` would_query=true
- `shareholder_meeting_known_021` would_query=true
- `shareholder_meeting_known_022` would_query=true
- `shareholder_meeting_known_023` would_query=true
- `shareholder_meeting_known_024` would_query=true
- `shareholder_meeting_known_025` would_query=true
- `shareholder_meeting_known_026` would_query=true
- `shareholder_meeting_known_027` would_query=true
- `shareholder_meeting_known_028` would_query=true
- `shareholder_meeting_known_029` would_query=true
- `shareholder_meeting_known_030` would_query=true
- `shareholder_meeting_known_031` would_query=true
- `shareholder_meeting_known_032` would_query=true
- `shareholder_meeting_known_033` would_query=true
- `shareholder_meeting_known_034` would_query=true
- `shareholder_meeting_known_035` would_query=true
- `shareholder_meeting_known_036` would_query=true
- `shareholder_meeting_known_037` would_query=true
- `shareholder_meeting_known_038` would_query=true
- `shareholder_meeting_known_039` would_query=true
- `shareholder_meeting_known_040` would_query=true
- `shareholder_meeting_known_041` would_query=true
- `shareholder_meeting_known_042` would_query=true
- `shareholder_meeting_known_043` would_query=true
- `shareholder_meeting_known_044` would_query=true
- `shareholder_meeting_known_045` would_query=true
- `shareholder_meeting_known_046` would_query=true
- `shareholder_meeting_known_047` would_query=true
- `shareholder_meeting_known_048` would_query=true
- `board_resolution_known_011` would_query=true
- `board_resolution_known_012` would_query=true
- `board_resolution_known_013` would_query=true
- `board_resolution_known_014` would_query=true
- `board_resolution_known_015` would_query=true
- `board_resolution_known_016` would_query=true
- `board_resolution_known_017` would_query=true
- `board_resolution_known_018` would_query=true
- `board_resolution_known_019` would_query=true
- `board_resolution_known_020` would_query=true
- `board_resolution_known_021` would_query=true
- `board_resolution_known_022` would_query=true
- `board_resolution_known_023` would_query=true
- `board_resolution_known_024` would_query=true
- `board_resolution_known_025` would_query=true
- `board_resolution_known_026` would_query=true
- `board_resolution_known_027` would_query=true
- `board_resolution_known_028` would_query=true
- `board_resolution_known_029` would_query=true
- `board_resolution_known_030` would_query=true
- `board_resolution_known_031` would_query=true
- `board_resolution_known_032` would_query=true
- `board_resolution_known_033` would_query=true
- `board_resolution_known_034` would_query=true
- `board_resolution_known_035` would_query=true
- `supervisory_board_known_006` would_query=true
- `supervisory_board_known_007` would_query=true
- `supervisory_board_known_008` would_query=true
- `supervisory_board_known_009` would_query=true
- `supervisory_board_known_010` would_query=true
- `supervisory_board_known_011` would_query=true
- `supervisory_board_known_012` would_query=true
- `supervisory_board_known_013` would_query=true
- `supervisory_board_known_014` would_query=true
- `supervisory_board_known_015` would_query=true
- `supervisory_board_known_016` would_query=true
- `supervisory_board_known_017` would_query=true
- `supervisory_board_known_018` would_query=true
- `supervisory_board_known_019` would_query=true
- `supervisory_board_known_020` would_query=true
- `raised_funds_cash_management_known_005` would_query=true
- `raised_funds_cash_management_known_006` would_query=true
- `raised_funds_cash_management_known_007` would_query=true
- `raised_funds_cash_management_known_008` would_query=true
- `raised_funds_cash_management_known_009` would_query=true
- `raised_funds_cash_management_known_010` would_query=true
- `raised_funds_cash_management_known_011` would_query=true
- `raised_funds_cash_management_known_012` would_query=true
- `raised_funds_cash_management_known_013` would_query=true
- `raised_funds_cash_management_known_014` would_query=true
- `raised_funds_cash_management_known_015` would_query=true
- `raised_funds_cash_management_known_016` would_query=true
- `raised_funds_cash_management_known_017` would_query=true
- `raised_funds_cash_management_known_018` would_query=true
- `raised_funds_cash_management_known_019` would_query=true
- `continuous_supervision_annual_known_007` would_query=true
- `continuous_supervision_annual_known_008` would_query=true
- `continuous_supervision_annual_known_009` would_query=true
- `continuous_supervision_annual_known_010` would_query=true
- `continuous_supervision_annual_known_011` would_query=true
- `continuous_supervision_annual_known_012` would_query=true
- `continuous_supervision_annual_known_013` would_query=true
- `continuous_supervision_annual_known_014` would_query=true
- `verification_opinion_known_005` would_query=true
- `verification_opinion_known_006` would_query=true
- `verification_opinion_known_007` would_query=true
- `verification_opinion_known_008` would_query=true
- `verification_opinion_known_009` would_query=true
- `verification_opinion_known_010` would_query=true
- `company_articles_known_006` would_query=true
- `company_articles_known_007` would_query=true
- `company_articles_known_008` would_query=true
- `company_articles_known_009` would_query=true
- `company_articles_known_010` would_query=true
- `employee_stock_ownership_plan_known_004` would_query=true
- `employee_stock_ownership_plan_known_005` would_query=true
- `employee_stock_ownership_plan_known_006` would_query=true
- `employee_stock_ownership_plan_known_007` would_query=true
- `legal_opinion_known_063` would_query=true
- `legal_opinion_known_064` would_query=true
- `legal_opinion_known_065` would_query=true

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

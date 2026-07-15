# CNINFO B 类 Corpus Retrieval Dry-run Summary

_生成时间：2026-07-15（corpus retrieval 脚本骨架 dry-run；不请求 CNINFO）_

## 1. 目的

验证 `lab/validate_cninfo_b_class_corpus_retrieval.py` 骨架：
加载 **ready** case、校验字段、输出 dry-run 报告。**不发起 CNINFO 请求。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Known-document cases | `outputs/validation/cninfo_b_class_ir_activity_promotion_live_20260715/known_document_retrieval_cases_live_allowlist.yaml` |
| Category-sample cases | `outputs/validation/cninfo_b_class_ir_activity_promotion_live_20260715/category_sample_cases_live_allowlist.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| dry_run | **True** |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **4** |
| ready_cases | **4** |
| invalid_ready | **0** |
| placeholder_cases | **0** |
| retired_cases | **0** |
| query_executed | **0** |
| result | **DRY_RUN_PASS** |

## 4. Ready case 明细

- `ir_activity_known_002` would_query=true
- `ir_activity_known_003` would_query=true
- `ir_activity_sample_001` would_query=true
- `ir_activity_sample_002` would_query=true

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

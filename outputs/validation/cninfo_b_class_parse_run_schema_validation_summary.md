# CNINFO B 类 Parse Run Dry-run Fixture Summary

_生成时间：2026-07-05（parse_run dry-run metadata；parser 未执行）_

## 1. 目的

为已有 B 类 `b_document` fixture 生成 **`b_document_parse_run` dry-run** 记录，
打通 parse_run schema validation 链路。**不解析 PDF、不下载 PDF。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Periodic documents | `fixtures/b_class/document/periodic_report_document_fixtures.jsonl` |
| Non-periodic documents | `fixtures/b_class/document/non_periodic_document_fixtures.jsonl` |
| Periodic raw_file | `fixtures/b_class/raw_file/periodic_report_raw_file_fixtures.jsonl` |
| Schema | `schemas/b_class/b_document_parse_run.schema.json` |
| Seed 脚本 | `lab/seed_cninfo_b_class_parse_run_dry_run_fixtures.py` |
| Validation 脚本 | `lab/validate_cninfo_b_class_parse_run_schema.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_documents | **33** |
| parse_run_seeded | **33** |
| periodic_parse_run | **20** |
| non_periodic_parse_run | **13** |
| schema_pass | **33** |
| schema_fail | **0** |

## 4. Parse status 分布

- `not_started`: **20**（periodic；有 raw_file metadata）
- `skipped`: **13**（non-periodic；无 pdf_url）

Fixture 输出：`fixtures/b_class/parse_run/document_parse_run_dry_run_fixtures.jsonl`

## 5. 质量边界

- **PDF 未下载**；`parser_name=dry_run_no_parser`，parser **未运行**。
- `page_count` / `text_length` / `error_message` 为 **null** 是预期行为。
- **没有** section / chunk / citation 产出。
- **不代表** corpus 已解析；仅为 schema 链路 dry-run。
- **不写 verified**。

## 6. 下一步

1. 后续允许下载 PDF 后，更新 periodic `parse_status`（`not_started` → 真实解析状态）。
2. 有真实 parser 后再生成 section / chunk fixture。
3. 可做 B 类 registry lint 或 corpus retrieval validation 小样本。
4. **暂不解析 PDF。**

## 附录

- [cninfo_b_class_parse_run_dry_run_report.csv](cninfo_b_class_parse_run_dry_run_report.csv)
- [cninfo_b_class_parse_run_schema_validation_report.csv](cninfo_b_class_parse_run_schema_validation_report.csv)

# CNINFO B 类 Raw File Fixture Seed & Schema Validation Summary

_生成时间：2026-07-05（离线 document → raw_file metadata seed + schema validation）_

## 1. 目的

从 B 类 `b_document` metadata fixture 派生 `b_raw_file` metadata fixture，
并做离线 JSON Schema 校验。**不下载 PDF、不请求 CNINFO、不计算真实 sha256。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Document fixture | `fixtures/b_class/document/periodic_report_document_fixtures.jsonl` |
| Raw file fixture | `fixtures/b_class/raw_file/periodic_report_raw_file_fixtures.jsonl` |
| Schema | `schemas/b_class/b_raw_file.schema.json` |
| Seed 脚本 | `lab/seed_cninfo_b_class_raw_file_fixtures.py` |
| Validation 脚本 | `lab/validate_cninfo_b_class_raw_file_schema.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_documents | **20** |
| raw_file_seeded | **20** |
| skipped_missing_source_url | **0** |
| schema_pass | **20** |
| schema_fail | **0** |

## 4. 字段说明

| 字段 | 当前值 | 说明 |
|------|--------|------|
| `download_status` | `not_started` | PDF 尚未下载 |
| `sha256_candidate` | `null` | 未计算 hash |
| `file_size_candidate` | `null` | 未确认文件大小 |
| `storage_uri_candidate` | `null` | 未写入对象存储 |
| `fetch_time` | `null` | 无下载时间 |
| `mime_type` | `application/pdf` | 预期类型（未验证） |
| `created_from` | `b_document_fixture_seed` | 派生来源标记 |

## 5. 质量边界

- **PDF 未下载**；`source_url` 仅为 CNINFO 静态链接登记。
- **sha256 未计算**；`storage_uri` 未生成；`file_size` 未确认。
- **不写 verified**；这是 metadata-only fixture。
- 不接 MinIO / MongoDB / PostgreSQL。

## 6. 下一步

1. 起草 parser / chunker plan。
2. 若后续允许下载，再更新 `download_status` / `sha256_candidate` / `storage_uri_candidate`。
3. **暂不进入真实 storage。**

## 附录

详见 [cninfo_b_class_raw_file_schema_validation_report.csv](cninfo_b_class_raw_file_schema_validation_report.csv)。

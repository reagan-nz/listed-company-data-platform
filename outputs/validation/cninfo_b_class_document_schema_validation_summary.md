# CNINFO B 类 Document Schema Validation Summary

_生成时间：2026-07-05（离线 metadata fixture schema validation）_

## 1. 目的

对 B 类 `b_document` logical record 做 **离线 JSON Schema 校验**。
**不下载 PDF、不解析 PDF、不请求 CNINFO、不入库、不写 verified。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Schema | `schemas/b_class/b_document.schema.json` |
| Fixture JSONL | `fixtures/b_class/document/periodic_report_document_fixtures.jsonl` |
| 脚本 | `lab/validate_cninfo_b_class_document_schema.py` |

其余 7 个 B 类 schema（raw_file / version / section / chunk / citation / parse_run / event_link）已起草，待对应 fixture 后再校验。

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_documents | **20** |
| pass | **20** |
| fail | **0** |

### by document_type (pass)

- `annual_report`: **5**
- `quarterly_report_q1`: **5**
- `quarterly_report_q3`: **5**
- `semi_annual_report`: **5**

## 4. 错误案例

_无失败记录。_

## 5. 质量边界

- Fixture 是 **document metadata**，不是 corpus parsing 结果。
- **PDF 未下载**；`pdf_url` 仅为 CNINFO 静态链接登记。
- **PDF 未解析**；chunk / citation / embedding **未生成**。
- **不写 verified**；`source_confidence` 仅表示 registry 证据层级。

## 6. 下一步

1. 增加 `b_raw_file` fixture（URL 登记，download_status=not_started）。
2. 设计 parser / chunker plan。
3. Seed inquiry / meeting / general document fixtures。
4. 后续再考虑下载和解析。

## 附录

详见 [cninfo_b_class_document_schema_validation_report.csv](cninfo_b_class_document_schema_validation_report.csv)。

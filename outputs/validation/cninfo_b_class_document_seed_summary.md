# CNINFO B 类 Periodic Report Document Seed Summary

_生成时间：2026-07-05（离线 Phase 1 → B 类 document metadata seed）_

## 1. 目的

从 Phase 1 A 类 **effective found** 报告 retrieval 行离线生成 B 类 `document` metadata fixture。
**不下载 PDF、不解析 PDF、不请求 CNINFO、不入库、不写 verified。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Phase 1 coverage CSV | `outputs/validation/cninfo_report_p1_coverage_validation.csv` |
| P1 identity mapping | `outputs/validation/cninfo_report_p1_identity_mapping.csv` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/seed_cninfo_b_class_document_fixtures.py` |

抽样策略：每 `report_type` 最多 **5** 条（按 `company_code` 排序），总数 ≤ **20**。

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_candidates | **20** |
| seeded | **20** |
| skipped_title_excluded | **0** |
| skipped_missing_pdf_url | **0** |
| skipped_missing_required_field | **0** |

### by document_type (seeded)

- `annual_report`: **5**
- `semi_annual_report`: **5**
- `quarterly_report_q1`: **5**
- `quarterly_report_q3`: **5**

Fixture 输出：`fixtures/b_class/document/periodic_report_document_fixtures.jsonl`

## 4. Fixture 字段说明

| 字段 | 说明 |
|------|------|
| document_id | SHA256 派生逻辑主键 |
| source_id | `cninfo_periodic_report_pdf` |
| company_code / company_name / org_id | 公司标识（org_id 来自 P1 identity mapping） |
| title | Phase 1 `matched_title`（去 HTML 标签） |
| document_type | annual / semi / Q1 / Q3 |
| report_period | 由 `expected_period` 归一化为日期 |
| announcement_date | 来自 `publish_time` 日期部分 |
| pdf_url | Phase 1 检索 URL（未下载） |
| retrieval_status | `found` |
| classification_status | `classified_correctly` |
| source_confidence | `testing_stable_sample`（非 verified） |
| raw_metadata_json | 完整 Phase 1 行快照 |
| created_from | `phase1_report_retrieval` |

## 5. 质量边界

- 这是 **metadata fixture**，不是 corpus parsing 结果。
- **不代表** PDF 已下载、已解析或已生成 embedding。
- Phase 1 effective found 已做 title filter；本脚本 **二次 title guard** 防止误入 periodic seed。
- **不写 verified**；`source_confidence=testing_stable_sample` 仅表示 retrieval 机制证据层级。

## 6. 下一步

1. 起草 B 类 `document` JSON Schema（`schemas/b_class/`）。
2. 对 fixture 做 schema validation。
3. 后续才考虑 parser / chunker 设计。
4. **暂不下载 PDF。**

## 附录

详见 [cninfo_b_class_document_seed_report.csv](cninfo_b_class_document_seed_report.csv)。

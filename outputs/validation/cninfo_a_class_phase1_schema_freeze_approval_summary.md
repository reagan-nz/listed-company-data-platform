# CNINFO A 类 Phase 1 Schema Freeze v1 — 批准摘要

_生成时间：2026-07-09_

> **性质：** 批准包摘要；**无 CNINFO** · **无 live** · **NOT APPROVED**（待人工 signoff）  
> **清单：** [cninfo_a_class_phase1_schema_freeze_approval_checklist.md](cninfo_a_class_phase1_schema_freeze_approval_checklist.md)  
> **实施计划：** [cninfo_a_class_phase1_freeze_v1_implementation_plan.md](../../plans/cninfo_a_class_phase1_freeze_v1_implementation_plan.md)

---

## Approval Package Status

| 项 | 状态 |
|----|------|
| schema freeze review | 完成 · gate **`READY_FOR_APPROVAL`** |
| field decision matrix | 完成 · **40** 行 |
| fixture skeleton | 完成 · **3** 文件 |
| offline lint | **10/10 PASS** |
| approval checklist | 本回合新增 |
| approval summary | 本文件 |
| implementation plan | 本回合新增 · **未执行** |
| explicit human signoff | **待批准** |

---

## Final Proposed Contract

### report_document

定期报告主 metadata 记录。一条记录 = 一份 company × report_type × report_period 的期望定期报告。

| 级别 | 字段 |
|------|------|
| **required（13）** | `document_id` · `company_code` · `report_type` · `report_period` · `publish_date` · `announcement_id` · `announcement_title` · `pdf_url` · `source_endpoint` · `retrieval_time` · `raw_hash` · `lineage_status` · `quality_status` |
| **recommended（5）** | `company_name` · `adjunct_url` · `org_id` · `announcement_time` · `raw_metadata_json` |
| **removed（1）** | `notes` |

### report_period_snapshot

公司报告期覆盖读模型。表达期望报告期与实际 document 命中关系。

| 级别 | 字段 |
|------|------|
| **required（4）** | `company_code` · `year` · `report_type` · `document_id` |
| **recommended（3）** | `quarter` · `coverage_status` · `expected_period` |
| **future（1）** | `available_sections` |

### document_lineage

PDF URL 与检索谱系。Phase1 固定 `storage_status=not_attempted`。

| 级别 | 字段 |
|------|------|
| **required（5）** | `storage_status` · `version` · `source_endpoint` · `retrieval_time` · `lineage_status` |
| **recommended（5）** | `source_url` · `raw_hash` · `adjunct_url` · `pdf_url` |
| **future（3）** | `download_time` · `file_hash` · `file_size` |
| **removed（1）** | `mime_type` |

---

## Field Counts（freeze v1 提议）

| 级别 | 数量 |
|------|------|
| **required** | **22** |
| **recommended** | **13** |
| **future** | **4** |
| **removed** | **2** |

### 按对象

| 对象 | required | recommended | future | removed |
|------|----------|-------------|--------|---------|
| report_document | 13 | 5 | 0 | 1 |
| report_period_snapshot | 4 | 3 | 1 | 0 |
| document_lineage | 5 | 5 | 3 | 1 |

---

## Enum Contracts

| 维度 | 允许值 |
|------|--------|
| report_type | `annual_report` · `semi_annual_report` · `quarterly_report_q1` · `quarterly_report_q3` |
| lineage_status | `discovered` · `linked` · `needs_review` · `not_found` |
| quality_status | `pass` · `caveat` · `blocked` · `needs_review` |
| storage_status（Phase1） | `not_attempted` only |
| coverage_status | `found` · `not_found` · `caveat` |

---

## Offline Validation Evidence

| 项 | 结果 |
|----|------|
| Lint script | [lab/lint_cninfo_a_class_phase1_freeze_v1.py](../../lab/lint_cninfo_a_class_phase1_freeze_v1.py) |
| Lint gate | **`a_class_phase1_freeze_v1_lint_gate = PASS_OFFLINE`** |
| Checks | **10/10 PASS** |
| Fixtures | [fixtures/a_class/phase1/](../../fixtures/a_class/phase1/) |
| Original catalog | [cninfo_a_class_phase1_minimum_fields.csv](cninfo_a_class_phase1_minimum_fields.csv) **未修改** |

---

## Explicitly Out of Scope

- CNINFO live harvest
- PDF download / parse / OCR
- extractor / embeddings / RAG
- DB / MinIO
- verified / testing_stable_sample
- C-class / B-class output modification

---

## Parallel State

| 类 | 状态 |
|----|------|
| C-class | **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变） |
| B-class | **unchanged** |
| CNINFO calls（本回合） | **0** |

---

## Gate

```text
a_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL
```

**不是 PASS。** 人工 signoff 后进入 implementation 回合；gate 届时可更新为 `READY_FOR_IMPLEMENTATION`。

---

## Recommended Next Step（人工批准后 · offline only）

执行 [cninfo_a_class_phase1_freeze_v1_implementation_plan.md](../../plans/cninfo_a_class_phase1_freeze_v1_implementation_plan.md)：

1. 生成 freeze v1 field catalog CSV
2. 更新 A-class registry draft
3. 从 P1 coverage CSV 扩展 offline fixtures
4. 建立 benchmark validation 骨架

仍不 live、不 PDF。

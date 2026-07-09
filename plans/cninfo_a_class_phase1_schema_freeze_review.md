# CNINFO A 类 Phase 1 Schema Freeze Review

_最后更新：2026-07-09_

> **性质：** 离线设计评审；不调用 CNINFO；不 live；不下载 PDF；不写 verified。  
> **输入：** [cninfo_a_class_phase1_minimum_fields.csv](../outputs/validation/cninfo_a_class_phase1_minimum_fields.csv) · [cninfo_a_class_readiness_matrix.csv](../outputs/validation/cninfo_a_class_readiness_matrix.csv) · [cninfo_a_class_report_metadata_architecture_plan.md](cninfo_a_class_report_metadata_architecture_plan.md)  
> **约束：** 原始 minimum fields catalog **未修改**；决策见 [cninfo_a_class_phase1_field_decision_matrix.csv](../outputs/validation/cninfo_a_class_phase1_field_decision_matrix.csv)。

---

## 1. Purpose

本评审定义 A-class **Phase 1 freeze v1 schema**：仅覆盖 **定期报告 metadata**（年报 / 半年报 / 季报）与 **PDF URL lineage**，不冻结 PDF 正文、解析、embedding 或存储层实现。

Phase 1 要回答的问题是：

- 哪家公司、哪个报告期、哪类定期报告被发现了？
- `report_document` 的核心 metadata 字段是什么？
- `report_period_snapshot` 如何表达 company × report_type × expected_period 覆盖？
- `document_lineage` 如何登记 `adjunctUrl` → `pdf_url` 与检索谱系？

Phase 1 **不**回答 PDF 内容、章节结构（`available_sections`）、chunk、RAG 或数据库落库问题。

---

## 2. Object Model Review

### 2.1 report_document

定期报告主记录。一条 `report_document` 对应一份期望定期报告（company × report_type × report_period）。

| 字段 | catalog 级别 | freeze v1 提议 | 决策 |
|------|-------------|----------------|------|
| document_id | required | **required** | keep |
| company_code | required | **required** | keep |
| company_name | recommended | **recommended** | keep |
| report_type | required | **required** | keep |
| report_period | required | **required** | keep |
| publish_date | required | **required** | keep |
| announcement_id | required | **required** | keep |
| announcement_title | required | **required** | keep |
| pdf_url | required | **required** | keep（not_found 时字段存在、值可为 null） |
| adjunct_url | recommended | **recommended** | keep |
| source_endpoint | required | **required** | keep |
| retrieval_time | required | **required** | keep |
| raw_hash | recommended | **required** | upgrade — lineage 变更检测门禁 |
| lineage_status | required | **required** | keep |
| quality_status | required | **required** | keep |
| org_id | recommended | **recommended** | keep |
| announcement_time | recommended | **recommended** | keep |
| raw_metadata_json | recommended | **recommended** | keep |
| notes | future | **removed** | remove — 仅人工 QA 侧车，不进 Phase1 产出契约 |

**report_document freeze v1：required=13 · recommended=5 · removed=1**

### 2.2 report_period_snapshot

公司报告期覆盖读模型。表达期望报告期与实际 `document_id` 的映射。

| 字段 | catalog 级别 | freeze v1 提议 | 决策 |
|------|-------------|----------------|------|
| company_code | required | **required** | keep |
| year | required | **required** | keep |
| quarter | recommended | **recommended** | keep |
| report_type | required | **required** | keep |
| document_id | required | **required** | keep（未命中时 null） |
| available_sections | future | **future** | defer — 依赖 parser |
| coverage_status | recommended | **recommended** | keep |
| expected_period | recommended | **recommended** | keep |

**report_period_snapshot freeze v1：required=4 · recommended=3 · future=1**

### 2.3 document_lineage

PDF URL 与检索谱系登记。Phase 1 固定 `storage_status=not_attempted`。

| 字段 | catalog 级别 | freeze v1 提议 | 决策 |
|------|-------------|----------------|------|
| source_url | recommended | **recommended** | keep |
| download_time | future | **future** | defer |
| file_hash | future | **future** | defer |
| file_size | future | **future** | defer |
| mime_type | recommended | **removed** | remove — 未下载无法验证 |
| storage_status | required | **required** | keep |
| version | required | **required** | keep |
| source_endpoint | required | **required** | keep |
| retrieval_time | required | **required** | keep |
| raw_hash | recommended | **recommended** | keep |
| adjunct_url | recommended | **recommended** | keep |
| pdf_url | recommended | **recommended** | keep |
| lineage_status | required | **required** | keep |

**document_lineage freeze v1：required=5 · recommended=5 · future=3 · removed=1**

---

## 3. Enum Contracts（Phase 1 freeze v1）

### report_type

`annual_report` · `semi_annual_report` · `quarterly_report_q1` · `quarterly_report_q3`

### lineage_status

`discovered` · `linked` · `needs_review` · `not_found`

### quality_status

`pass` · `caveat` · `blocked` · `needs_review`

### storage_status（Phase 1）

`not_attempted`（唯一允许值；`stored` / `failed` 为 future）

### coverage_status

`found` · `not_found` · `caveat`

---

## 4. Object Relationship Rules

1. `report_period_snapshot.document_id` 必须引用同 `company_code` 下存在的 `report_document.document_id`，或为 `null`（not_found）。
2. `document_lineage` 通过 `document_id`（fixture 顶层或内嵌）与 `report_document` 关联；`lineage_status` 两处应一致。
3. `report_period_snapshot.report_type` + `expected_period` 必须与 `report_document.report_type` + `report_period` 可对齐。
4. Phase 1 禁止在 lineage 对象上填写 `download_time` / `file_hash` / `file_size` 非 null 值。

---

## 5. Boundary（重申）

- **不调用 CNINFO**
- **不 live harvest**
- **不下载 PDF**
- **不解析 / OCR / RAG**
- **不写 DB / MinIO**
- **不写 verified / testing_stable_sample**
- **不修改 C-class / B-class 输出**

---

## 6. Fixture Skeleton

离线 fixture 见 `fixtures/a_class/phase1/`：

| 文件 | 用途 |
|------|------|
| `report_document_fixture.json` | 合成 `report_document` 样例 |
| `report_period_snapshot_fixture.json` | 合成覆盖视图样例 |
| `document_lineage_fixture.json` | 合成 lineage 样例 |

全部为 **schema skeleton**；`_fixture_meta.cninfo_called = false`；URL 为合成占位符。

---

## 7. Lint

离线 lint：`lab/lint_cninfo_a_class_phase1_freeze_v1.py`

校验：required 字段存在 · 对象关系 · lineage 字段 · status enum · 无 parser 字段。

---

## 8. Field Count Summary（freeze v1 提议）

| 级别 | 数量 |
|------|------|
| **required** | **22** |
| **recommended** | **13** |
| **future** | **4** |
| **removed** | **2** |

明细见 [cninfo_a_class_phase1_schema_freeze_review_summary.md](../outputs/validation/cninfo_a_class_phase1_schema_freeze_review_summary.md)。

---

## 9. Gate

```text
a_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL
```

**不是 PASS。** 需人工批准后方可进入 offline fixture 扩展或 tiny live metadata 规划。

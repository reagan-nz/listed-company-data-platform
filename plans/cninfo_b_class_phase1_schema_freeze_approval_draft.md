# CNINFO B 类 Phase 1 Schema Freeze Approval Draft

_最后更新：2026-07-09_

> **性质：** 人工 signoff 记录；**不是** verified；**不**将 gate 改为 PASS；**未**修改 registry YAML。  
> **评审包：** [manual review checklist](../outputs/validation/cninfo_b_class_phase1_schema_freeze_manual_review_checklist.md) · [field decision matrix](../outputs/validation/cninfo_b_class_phase1_field_decision_matrix.csv) · [endpoint decision matrix](../outputs/validation/cninfo_b_class_phase1_endpoint_decision_matrix.csv) · [signoff summary](../outputs/validation/cninfo_b_class_phase1_schema_freeze_signoff_summary.md)

---

## Proposed Freeze Scope

### Phase 1 includes

- **announcement metadata** — `announcement_record` 核心字段（company · id · title · time/date）
- **document metadata** — `document_metadata`（document_id · retrieval_time · raw_hash · quality_status · raw_metadata_json lineage）
- **PDF URL lineage** — `pdf_reference`（pdf_url · adjunct_url · source_endpoint；download_status=not_attempted）
- **source lineage** — source_endpoint · retrieval_time · raw_hash · raw_metadata_json
- **quality status** — quality_status · retrieval_status（recommended）· lineage_status

### Phase 1 excludes

- PDF download
- PDF parsing / text extraction
- OCR
- embeddings / vector index
- RAG pipeline
- DB / MinIO implementation
- verified / testing_stable_sample upgrade
- C-class harvest output modification

---

## Human Signoff Decision

**Signoff 状态：** 已完成（2026-07-09 · 文档化 signoff · implementation 未启动）

### Approved scope

Phase 1 frozen scope:

- announcement metadata
- document metadata
- PDF URL lineage
- source lineage
- quality status

### Required fields（15）

| # | field_name | object |
|---|------------|--------|
| 1 | company_code | announcement_record |
| 2 | org_id | announcement_record |
| 3 | announcement_id | announcement_record |
| 4 | announcement_title | announcement_record |
| 5 | announcement_time | announcement_record |
| 6 | announcement_date | announcement_record |
| 7 | document_id | document_metadata |
| 8 | retrieval_time | document_metadata |
| 9 | raw_hash | document_metadata |
| 10 | quality_status | document_metadata |
| 11 | pdf_url | pdf_reference |
| 12 | adjunct_url | pdf_reference |
| 13 | source_endpoint | pdf_reference |
| 14 | lineage_status | document_evidence |
| 15 | announcement_category | announcement_category |

### Downgraded（2）

| field_name | from | to |
|------------|------|-----|
| timeline_company_code | required | recommended |
| timeline_announcement_date | required | recommended |

### Moved outside Phase 1（4）

- notes
- mime_type
- timeline_entry_id
- timeline_pdf_url

**原始** [minimum fields catalog](../outputs/validation/cninfo_b_class_phase1_minimum_fields.csv) **未修改**；freeze v1 catalog 在 implementation 回合生成。

---

## Endpoint Scope Decision

### Phase 1 in scope

| ID | name |
|----|------|
| EP001 | hisAnnouncement/query |
| EP002 | topSearch/query |
| EP004 | cninfo_periodic_report_pdf |
| EP005 | cninfo_general_announcement_pdf |

### Deferred Phase 2

| ID | name |
|----|------|
| EP006 | cninfo_inquiry_reply_pdf |
| EP007 | cninfo_meeting_notice_pdf |

### Removed

| ID | name |
|----|------|
| EP003 | disclosure/list/notice UI hint |

**Reason:** Phase 1 focuses on stable metadata lineage. EP003 is UI/Referer only (risk=high). EP006/EP007 have null endpoints in registry and require endpoint confirmation before inclusion.

---

## Human Signoff Block

| 项 | 记录 |
|----|------|
| 审阅日期 | 2026-07-09 |
| 审阅方式 | 基于 review package 文档化 signoff（approval/documentation only） |
| endpoint 决策批准 | [x] 批准 |
| field 决策批准 | [x] 批准 |
| freeze scope 批准 | [x] 批准 |
| 允许进入 freeze v1 implementation 规划 | [x] 是（**仍无 live** · registry YAML **本回合不改**） |
| 允许进入 tiny live metadata | [ ] 否（须 implementation 完成后再单独申请） |

---

## Approval Decision

```text
b_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL  (prior review gate — satisfied)
b_class_phase1_schema_freeze_signoff_gate = READY_FOR_IMPLEMENTATION
```

**不设为 PASS** — implementation（registry YAML · fixtures · lint · schema）尚未启动；不等于 verified 或 permanent production freeze.

---

## Post-Signoff Next Steps

见 [cninfo_b_class_phase1_freeze_v1_implementation_plan.md](cninfo_b_class_phase1_freeze_v1_implementation_plan.md)：

1. 更新 source registry YAML（**未来回合**）
2. 生成 fixtures
3. 创建 validation schema
4. 创建 offline schema lint
5. 创建 ready-case benchmark
6. 仅此后申请 live validation approval

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`: **untouched**
- No B-class live execution in this signoff round

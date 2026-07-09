# CNINFO B 类 Phase 1 Schema Freeze Review

_最后更新：2026-07-09_

> **性质：** 离线设计评审；不调用 CNINFO；不 live；不下载 PDF；不写 verified。  
> **输入：** [cninfo_b_class_endpoint_candidate_table.csv](../outputs/validation/cninfo_b_class_endpoint_candidate_table.csv) · [cninfo_b_class_phase1_minimum_fields.csv](../outputs/validation/cninfo_b_class_phase1_minimum_fields.csv) · [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml)

---

## 1. Purpose

本评审定义 B-class **Phase 1 最小 schema**：仅覆盖 **公告元数据** 与 **PDF URL lineage**，不冻结 PDF 正文、解析、embedding 或存储层实现。

Phase 1 要回答的问题是：

- 从哪个 endpoint / source 发现了哪条公告？
- 公告的核心 metadata 字段是什么？
- PDF 链接（`adjunctUrl` → `pdf_url`）如何登记与追溯？
- 质量与 lineage 状态如何标记？

Phase 1 **不**回答 PDF 内容、章节结构、chunk、RAG 检索或数据库落库问题。

---

## 2. Endpoint Candidate Review

明细见 [cninfo_b_class_endpoint_candidate_table.csv](../outputs/validation/cninfo_b_class_endpoint_candidate_table.csv)。

| endpoint_candidate_id | 类型 | endpoint 状态 | risk | priority | 评审结论 |
|----------------------|------|---------------|------|----------|----------|
| EP001_hisAnnouncement_query | API POST | 已记录 | medium | high | Phase 1 主检索 endpoint；继承 A-class；**不本轮 live 重验** |
| EP002_topSearch_query | API POST | 已记录 | medium | high | orgId 辅助；非公告列表；Phase 1 仅作 linkage helper |
| EP003_disclosure_list_notice_ui | UI / Referer | 非 API | **high** | medium | 仅 page_url 线索；**不得**作为 Phase 1 检索 endpoint |
| EP004_cninfo_periodic_report_pdf | registry source | 指向 EP001 | medium | high | Phase 1 优先源；title/period 规则已文档化 |
| EP005_cninfo_general_announcement_pdf | registry source | 指向 EP001 | medium | high | Phase 1 候选源；官方 category 对齐未完成 |
| EP006_cninfo_inquiry_reply_pdf | registry source | **null** | **high** | medium | endpoint 待补；title 正向模式已有；defer live |
| EP007_cninfo_meeting_notice_pdf | registry source | **null** | **high** | medium | endpoint 待补；股东大会/IR 边界待澄清 |

### 风险摘要

- **所有 `live_validation_status = not_run`**：本轮零 CNINFO 请求。
- **2 个 registry source endpoint 为 null**（inquiry / meeting）：须在 registry 中 `add_missing_endpoint` 或显式 defer，不可假装已验证。
- **1 个 UI-only 候选**（disclosure/list/notice）：risk=high，不得进入 Phase 1 harvest 主路径。

---

## 3. Minimum Field Review

明细见 [cninfo_b_class_phase1_minimum_fields.csv](../outputs/validation/cninfo_b_class_phase1_minimum_fields.csv)。

### announcement_record

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 公司主键之一 |
| org_id | **required** | live 检索必需 |
| announcement_id | **required** | 公告主键 |
| announcement_title | **required** | 原始标题 |
| announcement_time | **required** | 原始披露时间 |
| announcement_date | **required** | 规范化日期 |
| company_name | recommended | 可有缺失 |
| announcement_type | review_later | 用 document_type + category 替代 |

### document_metadata

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| document_id | **required** | 逻辑文档键 |
| retrieval_time | **required** | 抓取时间 |
| raw_hash | **required** | lineage 变更检测 |
| quality_status | **required** | QA 门控 |
| raw_metadata_json | raw_only | 完整 CNINFO 对象保留 |
| document_type | recommended | 路由结果 |
| retrieval_status | recommended | found / not_found 等 |
| report_period | review_later | 仅定期报告需要 |
| classification_* | review_later | 分类置信度后续冻结 |

### pdf_reference

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| pdf_url | **required** | 规范化完整 URL |
| adjunct_url | **required** | 原始 CNINFO 字段 |
| source_endpoint | **required** | 检索 endpoint lineage |
| file_type | recommended | Phase 1 默认 pdf |
| download_status | recommended | 固定 `not_attempted` |
| sha256_candidate / storage_uri_candidate | review_later | 下载后才有 |

### document_evidence

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| lineage_status | **required** | discovered / linked / needs_review |
| linked_document_id | recommended | 指向 document |
| evidence_role / linked_event_id | review_later | D-class / RAG 后续 |

### announcement_category

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| announcement_category | **required** | Phase 1 主类别 |
| category / category_route_group | recommended | 路由组与官方 code |
| sub_category | review_later | 细分类延后 |

### company_document_timeline

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| timeline_company_code | **required** | 聚合键 |
| timeline_announcement_date | **required** | 排序键 |
| timeline_document_id / timeline_announcement_id | recommended | 引用与 dedup |
| timeline_entry_id | optional | 读模型便利字段 |

### 用户指定最小字段覆盖检查

以下字段均已纳入 Phase 1 catalog 且为 **required**（分布在多个 object）：

`company_code` · `org_id` · `announcement_id` · `announcement_title` · `announcement_time` · `announcement_date` · `announcement_category` · `pdf_url` · `adjunct_url` · `source_endpoint` · `retrieval_time` · `raw_hash` · `lineage_status` · `quality_status`

`company_name` 定为 **recommended**（响应中可能缺失，不阻塞 Phase 1 metadata capture）。

`source_url` 定为 **recommended**（Referer / page_url 线索可选）。

---

## 4. Boundary

### Phase 1 includes

- announcement metadata
- PDF URL capture（`adjunctUrl` → `pdf_url`）
- source lineage（`source_endpoint` · `retrieval_time` · `raw_hash` · `raw_metadata_json`）
- quality status（`quality_status` · `retrieval_status`）

### Phase 1 excludes

- PDF download
- PDF parsing / text extraction
- embeddings / vector index
- RAG pipeline
- DB / MinIO implementation
- verified / testing_stable_sample upgrade
- C-class Phase 3 live harvest 输出修改

---

## 5. Registry Alignment Summary

明细见 [cninfo_b_class_source_registry_alignment_report.csv](../outputs/validation/cninfo_b_class_source_registry_alignment_report.csv)。

| source_name | endpoint | schema | fixture | 建议 |
|-------------|----------|--------|---------|------|
| cninfo_periodic_report_pdf | present | yes | yes (20 periodic) | **keep** |
| cninfo_general_announcement_pdf | present | yes | yes (13 non-periodic) | **revise** category alignment |
| cninfo_inquiry_reply_pdf | **null** | yes | partial | **add_missing_endpoint** + needs_fixture |
| cninfo_meeting_notice_pdf | **null** | yes | partial | **add_missing_endpoint** + needs_fixture |

---

## 6. Freeze Decision

本轮完成 **schema freeze review**，但**尚未最终冻结**。

```text
b_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL
```

**不是** `PASS` / `FROZEN` — 需人工审阅并批准后，方可进入 Phase 1 tiny sample metadata prototype（仍须单独 live approval）。

### 批准前检查清单

1. 确认 EP003 UI hint 不进入 harvest 主路径
2. 确认 EP006/EP007 endpoint null 源在 live 前必须补 endpoint 或显式 defer
3. 确认 Phase 1 required 字段集不引入 PDF 正文字段
4. 确认 registry 中 `cninfo_general_announcement_pdf` category 对齐计划
5. 确认不与 C-class Phase 3 live harvest 并发抢带宽

---

## 7. Next Step

人工 review / approve schema freeze v1 → 然后才可规划 tiny offline fixture expansion 或 tiny live metadata sample（需单独批准）。

**本轮未执行任何 live。**

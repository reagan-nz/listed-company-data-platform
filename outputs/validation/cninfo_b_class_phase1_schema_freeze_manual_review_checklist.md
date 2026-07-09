# CNINFO B 类 Phase 1 Schema Freeze 人工评审清单

_生成时间：2026-07-09_

> **性质：** 人工评审准备包；不调用 CNINFO；不 live；不永久 freeze；gate 保持 **`READY_FOR_APPROVAL`**。  
> **输入：** [endpoint 候选表](cninfo_b_class_endpoint_candidate_table.csv) · [minimum fields](cninfo_b_class_phase1_minimum_fields.csv) · [field decision matrix](cninfo_b_class_phase1_field_decision_matrix.csv) · [endpoint decision matrix](cninfo_b_class_phase1_endpoint_decision_matrix.csv) · [approval draft](../../plans/cninfo_b_class_phase1_schema_freeze_approval_draft.md)

---

## 评审前确认

- [ ] 已阅读 [cninfo_b_class_phase1_schema_freeze_review.md](../../plans/cninfo_b_class_phase1_schema_freeze_review.md)
- [ ] 已阅读 [cninfo_b_class_phase1_schema_freeze_review_summary.md](cninfo_b_class_phase1_schema_freeze_review_summary.md)
- [ ] 确认本轮 **不执行 live**、**不下载 PDF**、**不触碰** C-class Phase 3 输出根
- [ ] 确认 gate **不改为 PASS**（仅人工批准后另开回合）

---

## Endpoint Review

对 [cninfo_b_class_endpoint_candidate_table.csv](cninfo_b_class_endpoint_candidate_table.csv) 中每个候选逐项勾选：

### EP001 — hisAnnouncement/query

- [ ] endpoint purpose clear?（公司公告列表 + PDF metadata 主检索 API）
- [ ] source object clear?（API endpoint · 非 registry source_id）
- [ ] expected fields clear?（announcements[] · adjunctUrl · announcementId · announcementTime）
- [ ] registry name aligned?（registry defaults.query_endpoint 一致）
- [ ] endpoint null allowed?（N/A — endpoint 已记录）
- [ ] live validation postponed?（是 · live_validation_status=not_run）

### EP002 — topSearch/query

- [ ] endpoint purpose clear?（orgId 发现辅助 · 非公告列表）
- [ ] source object clear?（linkage helper API）
- [ ] expected fields clear?（records[] · orgId · code · zwjc）
- [ ] registry name aligned?（B-class corpus retrieval 脚本引用）
- [ ] endpoint null allowed?（N/A）
- [ ] live validation postponed?（是）

### EP003 — disclosure/list/notice UI hint

- [ ] endpoint purpose clear?（UI/Referer 线索 only）
- [ ] source object clear?（page_url · 非 API）
- [ ] expected fields clear?（unknown — HTML/UI）
- [ ] registry name aligned?（periodic source page_url）
- [ ] endpoint null allowed?（是 — 不作为检索 endpoint）
- [ ] live validation postponed?（是 · 建议 **remove** 出 Phase 1 主路径）

### EP004 — cninfo_periodic_report_pdf

- [ ] endpoint purpose clear?（定期报告 PDF metadata 源）
- [ ] source object clear?（registry source_id → EP001）
- [ ] expected fields clear?（title/date/id/adjunctUrl + period 规则）
- [ ] registry name aligned?（registry sources[0]）
- [ ] endpoint null allowed?（否 — 已指向 hisAnnouncement/query）
- [ ] live validation postponed?（是 · 继承 A-class 历史证据）

### EP005 — cninfo_general_announcement_pdf

- [ ] endpoint purpose clear?（非定期公告 PDF metadata 源）
- [ ] source object clear?（registry source_id → EP001）
- [ ] expected fields clear?（同上 · category 参数待对齐）
- [ ] registry name aligned?（registry sources[1]）
- [ ] endpoint null allowed?（否 — endpoint 已记录）
- [ ] live validation postponed?（是）

### EP006 — cninfo_inquiry_reply_pdf

- [ ] endpoint purpose clear?（问询函/回复 PDF 语料）
- [ ] source object clear?（registry source_id · endpoint **null**）
- [ ] expected fields clear?（title 正向模式已有 · API 未确认）
- [ ] registry name aligned?（registry sources[2]）
- [ ] endpoint null allowed?（是 — **defer Phase 2** 前须补 endpoint 或显式 defer）
- [ ] live validation postponed?（是）

### EP007 — cninfo_meeting_notice_pdf

- [ ] endpoint purpose clear?（说明会/会议通知/IR 活动）
- [ ] source object clear?（registry source_id · endpoint **null**）
- [ ] expected fields clear?（title 正向模式已有 · API 未确认）
- [ ] registry name aligned?（registry sources[3]）
- [ ] endpoint null allowed?（是 — **defer Phase 2**）
- [ ] live validation postponed?（是）

---

## Field Review

对 [cninfo_b_class_phase1_minimum_fields.csv](cninfo_b_class_phase1_minimum_fields.csv) 中每个字段确认（可结合 [field decision matrix](cninfo_b_class_phase1_field_decision_matrix.csv)）：

### 通用检查项（每条字段）

- [ ] field meaning clear?
- [ ] required / recommended / review_later / optional / raw_only 分级适当?
- [ ] lineage_needed 标注正确?
- [ ] quality_rule 已定义或明确 defer?
- [ ] dedup_role 清晰或标注 none?

### announcement_record（8 字段）

- [ ] company_code — required · universe 对齐
- [ ] company_name — recommended · 可缺失
- [ ] org_id — required · live 检索必需
- [ ] announcement_id — required · 主键
- [ ] announcement_title — required
- [ ] announcement_time — required · 原始时间
- [ ] announcement_date — required · 规范化日期
- [ ] announcement_type — review_later · 不冻结

### document_metadata（14 字段）

- [ ] document_id · retrieval_time · raw_hash · quality_status — required
- [ ] source_id · document_type · retrieval_status · created_from — recommended
- [ ] report_period · classification_* — review_later
- [ ] raw_metadata_json — raw_only · lineage 保留
- [ ] notes — optional

### pdf_reference（9 字段）

- [ ] pdf_url · adjunct_url · source_endpoint — required
- [ ] file_type · source_url · download_status — recommended
- [ ] sha256_candidate · storage_uri_candidate — review_later（下载/MinIO 后）
- [ ] mime_type — optional · 建议 remove_from_phase1

### document_evidence（5 字段）

- [ ] lineage_status — required
- [ ] linked_document_id — recommended
- [ ] evidence_role · linked_event_id · source_confidence — review_later

### announcement_category（5 字段）

- [ ] announcement_category — required
- [ ] category · category_route_group · title_route_source_id — recommended
- [ ] sub_category — review_later

### company_document_timeline（6 字段）

- [ ] timeline_company_code · timeline_announcement_date — 建议降为 recommended（读模型）
- [ ] timeline_document_id · timeline_announcement_id — recommended
- [ ] timeline_entry_id · timeline_pdf_url — optional · 建议 remove_from_phase1

---

## Object Review

确认六个逻辑对象在 Phase 1 的职责边界：

| object | Phase 1 职责 | 确认 |
|--------|-------------|------|
| announcement_record | CNINFO 公告列表原始/metadata 行 | [ ] |
| document_metadata | 业务文档单元 + QA + lineage 哈希 | [ ] |
| pdf_reference | PDF URL 登记 · 不下载 | [ ] |
| document_evidence | lineage 状态 · 不含 D-class/RAG 链接 | [ ] |
| announcement_category | 类别路由结果 | [ ] |
| company_document_timeline | 派生读模型 · 非主采集对象 | [ ] |

### Phase 1 禁止字段确认

- [ ] **无 PDF 正文字段**（text / page_text / ocr_text / extracted_content）
- [ ] **无 PDF 解析字段**（page_count · section_path · chunk_id · embedding）
- [ ] **无存储实现字段**（storage_uri 仅 review_later · MinIO deferred）
- [ ] **无 DB migration 字段**

---

## Registry Alignment Review

对照 [cninfo_b_class_source_registry_alignment_report.csv](cninfo_b_class_source_registry_alignment_report.csv)：

- [ ] cninfo_periodic_report_pdf → **keep**
- [ ] cninfo_general_announcement_pdf → **revise**（category 对齐）
- [ ] cninfo_inquiry_reply_pdf → **add_missing_endpoint** · defer Phase 2
- [ ] cninfo_meeting_notice_pdf → **add_missing_endpoint** · defer Phase 2

---

## 人工批准项

评审完成后由人工勾选（本回合不自动改 gate）：

- [ ] 批准 proposed freeze scope（见 approval draft）
- [ ] 批准 field decision matrix 建议
- [ ] 批准 endpoint decision matrix 建议
- [ ] 确认仍 **不 live** 直至单独批准
- [ ] 确认 gate 保持 `READY_FOR_APPROVAL` 或人工另记 signoff 日期

---

## Gate

```text
b_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL
```

**不在本清单执行中改为 PASS。**

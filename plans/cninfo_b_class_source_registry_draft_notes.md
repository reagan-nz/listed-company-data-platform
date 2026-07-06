# CNINFO B 类 Source Registry Draft Notes

_最后更新：2026-07-05_

> **YAML：** [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml)  
> **设计：** [cninfo_b_class_source_registry_design.md](cninfo_b_class_source_registry_design.md)

---

## 1. 目的

本文件说明 **B 类 document corpus source registry** YAML 草案的覆盖范围、与 D 类 registry 的边界，以及 Phase 1 继承关系。

**性质：** `status: design_only`；**不**下载 PDF、**不**解析、**不入库**、**不写 verified**。

---

## 2. 覆盖范围

初始 **4** 个 B 类 source（`source_layer: document_corpus`）：

| source_id | source_name | source_category | recommended_status |
|-----------|-------------|-----------------|-------------------|
| `cninfo_periodic_report_pdf` | 巨潮定期报告 PDF | `periodic_report_pdf` | `testing_stable_sample` |
| `cninfo_general_announcement_pdf` | 巨潮普通公告 PDF | `announcement_pdf` | `candidate` |
| `cninfo_inquiry_reply_pdf` | 巨潮问询函及回复 PDF | `inquiry_reply_pdf` | `candidate` |
| `cninfo_meeting_notice_pdf` | 巨潮说明会/会议通知 PDF | `meeting_notice_pdf` | `candidate` |

顶层还定义：

- `defaults` — 共用 CNINFO 公告检索字段名（`adjunctUrl`、`announcementTitle` 等）
- `retrieval_status_values` / `parse_status_values` / `chunk_status_values` / `embedding_status_values`
- `phase1_report_title_exclusions_shared` — 与 Phase 1 脚本对齐的排除短语列表

---

## 3. 与 D 类 registry 的区别

| 项 | B 类 YAML | D 类 YAML |
|----|-----------|-----------|
| 文件 | `cninfo_b_class_source_registry_draft.yaml` | `cninfo_d_class_source_registry_draft.yaml` |
| layer | `document_corpus` | `company_event` / `company_metric_*` / … |
| 核心 | `document_type_candidates`、title patterns、pdf 字段 | `records_path`、`target_logical_table`、`fields.mapping` |
| 输出对象 | B 类 `document`（见 document model） | `d_company_event` / metric rows |
| 验证 | Phase 1 coverage / 未来 corpus 口径 | Phase 2 endpoint + schema validation |

**禁止：** 将 `margin_trading`、`disclosure_schedule` 等 D 类 source 写入本 YAML；将 `cninfo_periodic_report_pdf` 写入 D 类 YAML。

---

## 4. Phase 1 继承

仅 **`cninfo_periodic_report_pdf`** 继承 Phase 1 A 类已验证证据：

| 证据 | 内容 |
|------|------|
| Endpoint | `https://www.cninfo.com.cn/new/hisAnnouncement/query` |
| Coverage | P1 **749/796 = 94.10%** effective found |
| 脚本 | `lab/validate_cninfo_report_coverage.py` |
| 总结 | `outputs/validation/cninfo_report_phase1_final_summary.md` |
| Title filter | `title_exclusion_patterns` 与脚本 `OFFICIAL_REPORT_TITLE_EXCLUSIONS` 对齐 |
| Title positive | 四类 `report_type` 的 `title_positive_patterns` 与 `REPORT_TYPES` 对齐 |

**含义：** `recommended_status: testing_stable_sample` 表示 **retrieval metadata 机制** 在小样本内稳定，**不等于** PDF 已入库或 corpus 已 parse。

---

## 5. title classification 原则

| 原则 | 说明 |
|------|------|
| **定期报告 exclusion** | 在 `cninfo_periodic_report_pdf` 中，问询函 / 说明会 / 摘要 / 延期披露等 **不得** 计为 effective found |
| **非定期 corpus 保留** | 同一标题可在 `cninfo_inquiry_reply_pdf` 或 `cninfo_meeting_notice_pdf` 中 **正向匹配** |
| **宽公告 corpus** | `cninfo_general_announcement_pdf` 可接收被定期报告踢出的标题，但 `document_type` 必须重新分类 |
| **禁止误判** | 问询函、说明会、延期披露 **不能** 标为 `annual_report` / `quarterly_report_q1` 等 |
| **审计保留** | `title_excluded` 行保留在 retrieval 审计中，不是物理删除 |

---

## 6. 当前 caveat

| caveat | 说明 |
|--------|------|
| 普通公告未验证 | `cninfo_general_announcement_pdf` 为 `candidate`；无 validation_artifacts |
| 问询函 / 会议通知未验证 | `query_endpoint: null` — 预期与 `hisAnnouncement/query` 相同，待独立 probe |
| 未下载 PDF | 所有 source `parse_status` 默认 `not_started` / `skipped` |
| 未解析 PDF | 无 parser pipeline |
| 无 B 类 fixtures | 尚无 `fixtures/b_class/`；Phase 1 CSV 仅作 metadata seed 参考 |
| 无 B 类 lint | 未实现 `lint_cninfo_b_class_registry.py` |
| verified 全为 false | Era C 红线 |

---

## 7. endpoint 填写策略

| source | query_endpoint | 原因 |
|--------|----------------|------|
| `cninfo_periodic_report_pdf` | 已填 `hisAnnouncement/query` | Phase 1 已验证 |
| `cninfo_general_announcement_pdf` | 已填（同 endpoint） | 合理推断，但 corpus 未验证 → status 仍为 candidate |
| `cninfo_inquiry_reply_pdf` | `null` | 用户要求 unknown 写 null；待 category/title probe |
| `cninfo_meeting_notice_pdf` | `null` | 同上 |

---

## 8. 下一步

1. 补 `cninfo_announcement_categories.yaml` 官方 category 码，与 `cninfo_general_announcement_pdf.params_template.category` 对齐。
2. 设计 B 类 validation 口径文档 + 改造 `validate_cninfo_announcement_categories.py`（corpus + known-event）。
3. 离线 seed Phase 1 `found` 行为 `fixtures/b_class/document/`（仅 metadata JSON，不下载 PDF）。
4. 可选：`lint_cninfo_b_class_registry.py` + `schemas/b_class/b_source_registry.schema.json`。
5. 后续再考虑 parser / chunker / `event_document_link` 实现。

---

## 9. 产物索引

| 文档 | 说明 |
|------|------|
| [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md) | Corpus 职责 |
| [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) | document 对象 |
| [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md) | B/D 边界 |
| [cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml) | D 类对照 |

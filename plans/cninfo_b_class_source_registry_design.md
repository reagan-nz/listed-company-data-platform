# CNINFO B 类 Document Corpus Source Registry 设计草案

_最后更新：2026-07-05_

> **性质：** 设计草案；不入库、不下载 PDF、不写 verified。  
> **前置：** [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md) · [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md)  
> **对照：** [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md) · [config/cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml)  
> **配置草案：** [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml)

---

## 1. 设计目标

Era C Phase 3 已完成 **D 类 fixed-table** source registry（JSON row → event/metric schema）。本草案为 **B 类 document corpus** 建立 **独立、平行** 的 source registry layer。

| Registry | 管理对象 | 核心关注点 |
|----------|----------|------------|
| **B 类（本文档）** | PDF / 公告 **document** corpus | discovery、classification、retrieval metadata、parse/chunk/embedding status |
| **D 类（已有）** | 固定表格 **JSON row** | `records_path`、field mapping、`raw_record_json`、logic schema |

**原则：**

1. **二者不能混用** — 同一 `source_id` 不得同时描述 document corpus 与 fixed-table API。
2. **`source_layer` 强制分离** — B 类恒为 `document_corpus`；D 类为 `company_event` / `company_metric_*` 等。
3. B 类 registry **不替代** [document model](cninfo_b_class_document_model_draft.md) 中的 `document` / `chunk` 对象；registry 描述 **如何发现与分类** 语料，document model 描述 **如何存储与引用** 语料。
4. **当前仅设计** — 无 ingestion 代码、无 PDF 下载、无 parser。

---

## 2. B 类 source_layer

### 2.1 固定值

```yaml
source_layer: document_corpus
```

所有 B 类 registry 条目 **必须** 使用此 layer。Lint / 未来 CI 应拒绝将 `document_corpus` 与 `records_path`、`target_logical_table`（D 类字段）混在同一 source。

### 2.2 source_category（可选枚举）

| source_category | 说明 |
|-----------------|------|
| `periodic_report_pdf` | 年报 / 半年报 / 季报全文 PDF |
| `announcement_pdf` | 通用公告 PDF corpus |
| `inquiry_reply_pdf` | 问询函及回复 |
| `meeting_notice_pdf` | 说明会 / 会议通知 |
| `board_resolution_pdf` | 董事会决议（可并入 announcement 或独立） |
| `shareholder_meeting_material_pdf` | 股东会材料 |
| `other_document_pdf` | 兜底 |

---

## 3. B 类 registry 核心字段

以下为逻辑 registry 记录建议字段（YAML / JSON / 未来 DB 均可承载）。

| 字段 | 类型 | 说明 |
|------|------|------|
| `source_id` | string | 唯一标识 |
| `source_name` | string | 中文展示名 |
| `source_layer` | enum | 固定 `document_corpus` |
| `source_category` | enum | §2.2 |
| `source_site` | string | 如 `cninfo.com.cn` |
| `discovery_method` | enum | 如 `cninfo_announcement_search`、`cninfo_category_browse` |
| `query_endpoint` | uri \| null | 检索 API；未知则 `null` |
| `page_url` | uri \| null | UI / Referer 页；未知则 `null` |
| `params_template` | object | 查询参数模板（stock、seDate、category 等） |
| `document_type_candidates` | array[enum] | 可产出 document_type 列表 |
| `title_positive_patterns` | object \| array | 按 document_type 的正向标题模式 |
| `title_exclusion_patterns` | array[string] | 标题排除（定期报告 source 用） |
| `period_required` | boolean | 是否要求 report_period 匹配 |
| `company_required` | boolean | 是否要求 company_code |
| `org_id_required` | boolean | 是否要求 orgId（A 类经验） |
| `url_field` | string | 响应中 PDF URL 字段，如 `adjunctUrl` |
| `title_field` | string | 如 `announcementTitle` |
| `announcement_date_field` | string | 如 `announcementTime` |
| `document_id_field` | string | 如 `announcementId` |
| `retrieval_status_values` | array | found / not_found / title_excluded / … |
| `classification_status_values` | array | 分类流水线状态（可选） |
| `parse_status_values` | array | not_started / parsed_text / … |
| `chunk_status_values` | array | not_started / chunked / … |
| `embedding_status_values` | array | not_started / skipped / … |
| `recommended_status` | enum | §7 |
| `stability_status` | string | 稳定性备注（可选） |
| `validation_artifacts` | array[path] | 指向 validation summary / CSV |
| `notes` | string | 自由文本 |

**B 类特有、D 类不应出现：**

- `title_positive_patterns` / `title_exclusion_patterns`
- `document_type_candidates`
- `parse_status_values` / `chunk_status_values` / `embedding_status_values`
- `period_required` / `classification` 相关字段

**D 类特有、B 类不应出现：**

- `api.records_path`
- `target_logical_table`
- `fields.confirmed` / `mapping.standard_fields`
- `supported_modes`（query param 组合，非 document discovery）

---

## 4. 与 D 类 registry 的区别

| 维度 | B 类 `document_corpus` | D 类 fixed-table |
|------|------------------------|------------------|
| **数据单元** | 一份 PDF document | 一条 JSON table row |
| **主输出** | document metadata + `pdf_url` | `d_company_event` / metric row |
| **分类** | title / category → `document_type` | field → standard column |
| **状态** | retrieval → parse → chunk → embed | fetch → map → schema validate |
| **验证** | corpus coverage、known-document、expected period | endpoint 稳定性、UI 字段、jsonschema |
| **配置文件** | `cninfo_b_class_source_registry_draft.yaml` | `cninfo_d_class_source_registry_draft.yaml` |
| **Phase 证据** | Phase 1 A 类 retrieval | Phase 2 D 类 table sources |

详见 [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md)。

---

## 5. 初始 B 类 source 建议

Phase 3 首批 **4** 个 source（见 YAML draft）：

### 5.1 `cninfo_periodic_report_pdf`

| 项 | 内容 |
|----|------|
| **用途** | `annual_report` / `semi_annual_report` / `quarterly_report_q1` / `quarterly_report_q3` |
| **discovery** | `hisAnnouncement/query`（Phase 1 已验证） |
| **recommended_status** | `testing_stable_sample`（继承 Phase 1 P1 **749/796**） |
| **title filter** | 继承 Phase 1 `OFFICIAL_REPORT_TITLE_EXCLUSIONS` |

### 5.2 `cninfo_general_announcement_pdf`

| 项 | 内容 |
|----|------|
| **用途** | 普通公告 PDF corpus：`announcement`、`board_resolution`、`shareholder_meeting_material`、`other` |
| **recommended_status** | `candidate` — **尚未** corpus 验证 |
| **endpoint** | 预期同为 `hisAnnouncement/query` 或 category 检索；**draft 中 query_endpoint 待填** |

### 5.3 `cninfo_inquiry_reply_pdf`

| 项 | 内容 |
|----|------|
| **用途** | 问询函 / 回复公告；**不得**误判为定期报告 |
| **recommended_status** | `candidate` |
| **分类注意** | Phase 1 exclusion 中的「问询函」「回复公告」在此 source **为正向保留** |

### 5.4 `cninfo_meeting_notice_pdf`

| 项 | 内容 |
|----|------|
| **用途** | 业绩说明会 / 投资者说明会 / 会议通知 |
| **recommended_status** | `candidate` |
| **分类注意** | Phase 1 exclusion 中的「说明会」在此 source **为正向保留** |

---

## 6. title filter 继承 Phase 1

Phase 1 A 类脚本（`lab/validate_cninfo_report_coverage.py`）为 **effective found** 定义了 **official title exclusion**，用于排除：

- 披露提示性公告、说明会、问询函、摘要、延期披露等 **非正式报告全文**

**B 类 registry 继承原则：**

| 场景 | 行为 |
|------|------|
| `cninfo_periodic_report_pdf` | `title_exclusion_patterns` = Phase 1 列表；命中 → `retrieval_status=title_excluded` 或继续 fallback |
| `cninfo_inquiry_reply_pdf` | exclusion 中的「问询函」「回复公告」→ **正向** `title_positive_patterns` |
| `cninfo_meeting_notice_pdf` | 「说明会」「业绩说明会」→ **正向** patterns |
| `cninfo_general_announcement_pdf` | 宽 corpus；被定期报告 exclusion 踢出的标题 **可重新进入** 本 source，但 `document_type ≠ annual_report` |

**关键：** 同一标题在不同 source 下 **分类不同**；exclusion 不是全局删除，而是 **路由到正确 corpus source**。

---

## 7. recommended_status

与 D 类 [ingestion status model](cninfo_d_class_ingestion_status_model.md) **枚举对齐**，语义适配 document corpus：

| 值 | 说明 |
|----|------|
| `candidate` | 已登记，未验证 |
| `testing` | 小样本探测中 |
| `testing_stable_sample` | 小样本 + 稳定性/audit 支撑（**非 verified**） |
| `partial` | 部分 document_type 或板块可用 |
| `blocked` | 入口不可用 / 需权限 |
| `deprecated` | 废弃 |

**禁止：** `verified`、full-market stable。

---

## 8. B 类 validation 方式

**禁止** 将「随机 N 家公司 × M 类公告 success rate」作为 B 类 **唯一** 主指标（见 [cninfo_announcement_acquisition_mechanism_summary.md](../outputs/validation/cninfo_announcement_acquisition_mechanism_summary.md)）。

| 验证类型 | 适用 source | 分母 / 分子要点 |
|----------|-------------|-----------------|
| **expected report period** | `cninfo_periodic_report_pdf` | company × report_type × expected_period；与 Phase 1 一致 |
| **category corpus** | `cninfo_general_announcement_pdf` | 时间窗 × category 下语料非空率、字段可得性% |
| **known-document** | 各 source | 已知存在某类公告的公司 / 日期，检是否 retrieval 到 |
| **known-event benchmark** | 事件类 corpus | 低频事件（增发、退市等）命中样本 |
| **title classification audit** | 全部 | 规则 high+medium 占比；定期报告假阳性率 |

定期报告继续用 Phase 1 **effective coverage%**；普通公告用 **corpus 可得性 + 分类置信度**。

---

## 9. 后续使用

B 类 registry 将驱动（**未来实现，非当前**）：

| 用途 | 说明 |
|------|------|
| **document discovery** | 按 source 配置调用 `hisAnnouncement/query` 或 category API |
| **corpus seeding** | Phase 1 `found` 行 → offline `document` fixture |
| **parse planning** | 按 `document_type` 选择 parser 策略 |
| **chunking planning** | report vs announcement 不同 chunk_strategy |
| **RAG / Wiki evidence** | `document_citation_span` 回溯 `source_id` |
| **D 类 `event_document_link`** | 从 D 类 event 反查应关联的 B 类 source / document_type |

---

## 10. 与 A / D 类 registry 共存

```
config/
  cninfo_b_class_source_registry_draft.yaml   # B 类 document_corpus
  cninfo_d_class_source_registry_draft.yaml   # D 类 fixed-table
```

应用层 / company timeline **可同时引用** 两份 registry，但 **不得合并为单表** 而不区分 layer。

---

## 11. 当前不做

| 不做 | 原因 |
|------|------|
| 下载 / 解析 PDF | Era C 红线 |
| 入库 / migration | 设计阶段 |
| 写 verified | 红线 |
| 修改 D 类 YAML | 边界要求 |
| B 类 lint 脚本 | 下一步可选 |

---

## 12. 产物索引

| 文件 | 说明 |
|------|------|
| [cninfo_b_class_source_registry_draft_notes.md](cninfo_b_class_source_registry_draft_notes.md) | YAML 说明 |
| [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) | document 逻辑对象 |
| [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) | A 类 retrieval 证据 |

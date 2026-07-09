# CNINFO B 类公告 / 文档元数据层架构计划

_最后更新：2026-07-09_

> **性质：** 规划文档 only；不调用 CNINFO；不下载 PDF；不写 verified；不入库。  
> **前置：** [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md) · [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) · [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md)  
> **并行约束：** C-class Phase 3 batch 500 live harvest 可能正在运行；本计划不触碰 `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`。

---

## 1. B-class Purpose

B-class 是 CNINFO **公告 / 文档元数据层**（announcement / document metadata layer）。

它负责把巨潮披露体系中的**可检索文档证据**结构化登记下来，为后续证据链、文档解析与 RAG 提供统一入口。B-class 的核心价值不是“拿到一份 PDF 正文”，而是：

- **company announcement discovery**：按公司、时间窗、类别发现公告列表；
- **announcement title / date / category metadata**：保留标题、披露日、公告类型与分类线索；
- **PDF URL lineage**：登记 `pdf_url`、来源 endpoint、检索时间与原始响应 hash，形成可追溯 lineage；
- **document evidence linkage**：把公告文档与 D-class 事件、C-class 公司画像建立引用关系；
- **later RAG / document parsing**：为 parse → chunk → embed 预留对象与状态字段，但**不在 Phase 0/1 执行**。

B-class **不是** C-class F10 / company profile 结构化数据层。C-class 回答“公司静态画像字段是什么”；B-class 回答“公司披露了哪些文档、PDF 链接在哪里、证据如何引用”。

---

## 2. Relationship With Other Classes

| 类 | 职责 | 数据单元 | 与 B-class 关系 |
|----|------|----------|-----------------|
| **A-class** | 定期/年报类报告检索与 PDF URL 层 | 公司 × 报告期 × 报告类型 | A-class Phase 1 的 `hisAnnouncement/query` 检索结果，是 B-class `periodic_report_pdf` 源的首批 metadata seed |
| **B-class** | 公告元数据与文档证据层 | 公告 / 文档 metadata + PDF URL lineage | 本层；承接 A-class 定期报告，并扩展非定期公告 corpus |
| **C-class** | 公司 profile / F10 结构化画像层 | profile JSON 字段 | 提供 `company_code` / `org_id` / `company_name` 等身份与画像上下文；**不替代**公告检索 |
| **D-class** | 固定结构化 CNINFO 表格层 | JSON table row | 结构化 event/metric 留在 D-class；B-class 通过 `document_evidence` / `event_document_link` 挂接 PDF 证据 |

边界原则：

1. A-class 专注**定期报告 coverage%**；B-class 专注**公告 corpus 可得性与 known-document benchmark**。
2. C-class snapshot 可引用 B-class 文档 ID，但不在 C-class harvest 中混抓公告列表。
3. D-class 事件行可缺 PDF；B-class 负责补“证据文档”侧。

---

## 3. Core Data Objects

以下为 B-class Phase 0/1 目标逻辑对象（当前仅设计，不建表）：

### announcement_record

公告列表层主记录。对应 CNINFO 公告检索 API 返回的一条公告摘要。

- 主键候选：`announcement_id`（CNINFO `announcementId`）
- 关联：`company_code`、`org_id`、`announcement_title`、`announcement_date`
- 用途：discovery 结果的标准化承载对象

### document_metadata

业务文档元数据层。把 `announcement_record` 提升为可进入 corpus 的 `document` 单元。

- 含 `document_type`、`category`、`sub_category`、`retrieval_status`、`quality_status`
- 可关联 A-class 定期报告或 B-class 非定期公告

### pdf_reference

PDF URL 与文件类型登记层。当前阶段**只登记 URL，不下载正文**。

- 字段：`pdf_url`、`file_type`、`source_url`、`source_endpoint`
- 与 `raw_file` 逻辑对象对齐，但 `download_status = not_attempted`

### document_evidence

证据引用层。用于把文档与业务事实、D-class 事件或后续 RAG citation 连接。

- 含 `lineage_status`、来源置信度、引用理由
- 当前仅定义 lineage，不执行 merge / verified

### announcement_category

公告分类与路由层。承接 `cninfo_announcement_categories.yaml` 与 title routing 规则。

- 含官方 category code、路由组、`document_type` 映射
- 支持 periodic / non-periodic / inquiry / meeting 等分轨

### company_document_timeline

公司文档时间线视图。按 `company_code` 聚合 `announcement_date` 排序的文档序列。

- 服务 QA、dedup、后续增量 harvest 窗口设计
- Phase 0 仅作为读模型设计，不生成全市场 timeline

---

## 4. Minimum Fields

B-class Phase 1 metadata 最小字段集如下：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `company_code` | string | yes | 证券代码 |
| `company_name` | string | no | 公司简称 |
| `org_id` | string | no | CNINFO orgId；A/B 检索通常需要 |
| `announcement_id` | string | yes | CNINFO `announcementId` |
| `announcement_title` | string | yes | 公告标题 |
| `announcement_date` | date/datetime | yes | 披露日 |
| `announcement_type` | string | no | 公告类型粗分类 |
| `category` | string | no | 官方或路由后的主类别 |
| `sub_category` | string | no | 子类别 / 路由组 |
| `pdf_url` | uri | no | CNINFO `adjunctUrl` 派生完整 URL |
| `file_type` | string | no | 默认 `pdf` |
| `source_url` | uri | no | 页面或 referer URL |
| `source_endpoint` | uri | no | 如 `hisAnnouncement/query` |
| `retrieval_time` | datetime | yes | 元数据抓取时间 |
| `raw_hash` | string | no | 原始响应或规范化 metadata 的 hash |
| `lineage_status` | enum | yes | 如 `discovered` / `linked` / `needs_review` |
| `quality_status` | enum | yes | 如 `pass` / `caveat` / `blocked` |
| `notes` | string | no | 人工或规则备注 |

与既有 B-class schema 对齐：

- `document` 级字段见 [schemas/b_class/b_document.schema.json](../schemas/b_class/b_document.schema.json)
- `raw_file` 级字段见 [schemas/b_class/b_raw_file.schema.json](../schemas/b_class/b_raw_file.schema.json)
- registry 字段映射见 [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml)

---

## 5. Boundary

### Phase 0 / Phase 1 明确不做

- **不下载 PDF**
- **不解析 PDF 正文**
- **不 chunk / embed / 建 vector index**
- **不接 DB / MinIO / RAG**
- **不写 verified**
- **不升级 `testing_stable_sample`**
- **不触碰 C-class Phase 3 live harvest 输出根**

### Phase 0 / Phase 1 仅做

1. **metadata discovery**：梳理 endpoint、参数模板、类别路由；
2. **PDF URL capture**：从公告 API 响应登记 `adjunctUrl` → `pdf_url`；
3. **lineage tracking**：保留 `source_endpoint`、`retrieval_time`、`raw_hash`、`raw_metadata_json`；
4. **quality review**：基于 fixture、ready-case、offline lint 与 tiny sample review 做质量口径设计。

### 与既有 B-class corpus 工作的关系

仓库中已有 corpus design、document model、registry YAML、JSON Schema、category routing、5-case live metadata v1 等历史草案。本架构计划把它们**收敛到“公告元数据层”主线**，明确：

- 历史 corpus / parse / chunk 设计保留为**后续 Phase**参考；
- 当前新一轮 B-class 重启点 = **metadata + PDF URL lineage + readiness**；
- live metadata v1（5/5 PASS）是**小样本验证证据**，不是全市场 harvest 批准。

---

## 6. Recommended Phase Sequence

| Phase | 名称 | 内容 | Gate |
|-------|------|------|------|
| **Phase 0** | source discovery + schema design | 离线盘点 A/B 既有产物；冻结最小字段；补 readiness matrix | `DESIGN_STARTED` |
| **Phase 1** | metadata prototype | tiny offline/sample review；endpoint candidate 表；dedup / rate-limit 政策草案 | `READY_FOR_TINY_SAMPLE_REVIEW` |
| **Phase 2** | controlled live metadata | 显式批准后的小样本 live metadata harvest（仍不下载 PDF） | `READY_FOR_APPROVAL` |
| **Later** | PDF download / parse / RAG | 独立批准；不在本计划范围 | deferred |

---

## 7. Gate

```text
b_class_initial_planning_gate = DESIGN_STARTED
```

下一步见 [cninfo_b_class_source_discovery_plan.md](cninfo_b_class_source_discovery_plan.md) 与 [cninfo_b_class_existing_artifact_inventory_summary.md](../outputs/validation/cninfo_b_class_existing_artifact_inventory_summary.md)。

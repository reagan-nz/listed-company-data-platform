# CNINFO B 类 Corpus 设计草案

_最后更新：2026-07-05_

> **性质：** 设计草案；不下载 PDF、不解析、不入库、不写 verified。  
> **前置：** [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md)（A 类）· [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md)（D 类）  
> **关联：** [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) · [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md) · [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) §5

---

## 1. 设计目标

Era C 已将 CNINFO 数据源按 **A–F 分层**管理。本草案聚焦 **B 类 document corpus**，明确其如何承接：

| 层 | 已解决问题 | 本草案范围 |
|----|-----------|-----------|
| **A 类** | 定期报告 PDF **retrieval**（`pdf_url`、标题、报告期匹配） | B 类 **消费** A 类 retrieval 结果作为 document metadata seed |
| **B 类** | 公告 / 报告 **语料库**（metadata → 未来 parse → chunk → RAG / LLM Wiki） | **本文档核心** |
| **D 类** | 固定表格 JSON **结构化 row**（event / metric / schedule） | **不混淆**；见 [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md) |

**设计原则：**

1. **A 类解决「能不能找到报告 PDF」**；B 类解决「找到之后如何组织成可检索、可引用、可问答的 document corpus」。
2. **D 类解决「结构化表格 row」**；B 类解决「非结构化 PDF / 公告文本」。
3. 本文档 **只设计 corpus 逻辑模型与状态机**，不做 PDF 下载、解析、向量化或真实 ingestion 代码。

---

## 2. B 类 corpus 的职责

B 类 corpus 是 **document-centric** 的中间层，介于 retrieval（A/B 入口）与下游应用（RAG / LLM Wiki / company profile）之间。

| 职责 | 说明 |
|------|------|
| **存储公告 / 报告 / 文档 metadata** | 标题、类型、公司、日期、URL、检索状态、分类置信度 |
| **关联 raw file** | 逻辑上绑定 `pdf_url` → 未来 `raw_file` 对象（当前可不实际下载） |
| **记录 document type** | `annual_report`、`announcement`、`inquiry_reply` 等；区分高价值 report corpus 与普通事件公告 |
| **支持 chunking** | 为 parse 后的 `document_section` → `document_chunk` 预留层级 |
| **支持 RAG** | chunk + citation span 作为 retrieval 单元与 evidence 锚点 |
| **支持 LLM Wiki 证据引用** | `document_citation_span` 提供可回溯 quote / page |
| **与 D 类结构化 event 对齐** | 通过 `event_document_link` 将 equity_pledge 等 D 类 event 关联到源公告 PDF（未来） |

**产品视角：** B 类 corpus 是 **「可读证据层」**；D 类是 **「可算结构化层」**。两者在 company timeline / LLM Wiki 汇合，但对象模型不同。

---

## 3. B 类不负责什么

| 不负责 | 原因 |
|--------|------|
| 保存 D 类 fixed-table row | 那是 `d_company_event` / `d_company_metric_*` 的职责 |
| 公司事件标准化（解禁股数、质押比例等） | 属 D 类 mapper + schema |
| 替代 `d_company_event` / metric 逻辑表 | abnormal_trading、margin_trading 等 **不是 document** |
| 直接承担 D 类 source registry 状态管理 | D 类用 `testing_stable_sample` 等；B 类用 corpus 专属 status（见 §7） |
| 全量公告抓取与 OCR | Era C 红线；当前仅设计 |

---

## 4. 文档对象层级

自底向上七层（详见 [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md)）：

| # | 对象 | 作用 |
|---|------|------|
| 1 | **raw_file** | 物理或逻辑文件层：`source_url`、`sha256`、`mime_type`、下载状态；当前可为「仅 URL、未下载」 |
| 2 | **document** | 业务文档单元：一家公司的一份公告或报告；绑定 metadata 与 `document_type` |
| 3 | **document_version** | 同一逻辑文档的修订 / 更正 / 替换版本（如补充公告、修订年报） |
| 4 | **document_section** | 解析后的章节 / 板块（目录项、「第三节 管理层讨论」等） |
| 5 | **document_chunk** | RAG 检索单元：section 切分后的 text block；含 `chunk_strategy`、quality flags |
| 6 | **document_embedding_candidate** | chunk 的向量表示候选（**当前不生成**）；关联 embedding model / 维度 |
| 7 | **document_citation_span** | 可引用证据片段：页码 + 起止偏移 + `quote_text`；供 LLM Wiki / Q&A 回溯 |

**数据流（未来，非当前实现）：**

```
retrieval (A/B) → document metadata
    → raw_file download (optional)
    → parse_run → document_section
    → chunker → document_chunk
    → embedder → document_embedding_candidate
    → RAG / Wiki ← document_citation_span
```

---

## 5. document 类型

建议 `document_type` 枚举（可扩展）：

| document_type | 说明 | 优先级 |
|---------------|------|--------|
| `annual_report` | 年度报告 | **高** — Phase 1 A 类核心 |
| `semi_annual_report` | 半年度报告 | **高** |
| `quarterly_report_q1` | 一季度报告 | **高** |
| `quarterly_report_q3` | 三季度报告 | **高** |
| `announcement` | 通用公告（未细分子类） | 中 |
| `inquiry_reply` | 问询函及回复 | 中 — **不得**误判为定期报告 |
| `meeting_notice` | 股东大会 / 董事会会议通知 | 中 |
| `shareholder_meeting_material` | 股东会材料 | 中 |
| `board_resolution` | 董事会决议公告 | 中 |
| `other` | 兜底 | 低 |

**分类注意：**

- Phase 1 的 `annual_report` / `semi_annual_report` / `quarterly_report_q1` / `quarterly_report_q3` 构成 **高价值 report corpus**；应与 A 类 `report_type` 对齐。
- **问询函 / 说明会 / 业绩预告** 等可作为 `announcement` 或独立子类型的 **普通事件 corpus 候选**，但 **不能** 因标题含「报告」就归入 `annual_report`。
- A 类 **title filter**（排除摘要、英文版、取消类等）应映射为 B 类 `retrieval_status=title_excluded` 或低 `classification_confidence`，而非丢弃审计记录。

---

## 6. metadata 字段

逻辑 **document** 层建议字段（与 model draft 对齐）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `document_id` | string | 逻辑主键 |
| `source_id` | string | 来源 registry（如 `cninfo_his_announcement`、`cninfo_report_retrieval`） |
| `company_code` | string | 证券代码 |
| `company_name` | string | 简称 |
| `org_id` | string | CNINFO orgId；桥接 A 类 / F10 |
| `report_period` | date | 报告期末日（报告类）；公告可为空 |
| `announcement_date` | date | 公告披露日 |
| `title` | string | 公告 / 报告标题 |
| `document_type` | enum | §5 |
| `pdf_url` | uri | CNINFO 静态 PDF 链接 |
| `page_count_candidate` | int | 解析前可为空；parse 后填充 |
| `language` | string | 默认 `zh-CN`；英文版单独标记 |
| `retrieval_status` | enum | §7 |
| `parse_status` | enum | §7 |
| `chunk_status` | enum | §7 |
| `embedding_status` | enum | §7 |
| `source_confidence` | enum | `high` / `medium` / `low` / `unknown` |
| `created_at` | datetime | 记录创建时间 |

**Lineage：** 每个 document 应能追溯到 retrieval run（A 类 coverage row 或 B 类 corpus pull），保留 `raw_metadata_json`（CNINFO 原始公告字段）。

---

## 7. corpus status

四套独立状态机（类比 D 类 [ingestion_status_model](cninfo_d_class_ingestion_status_model.md)，但语义不同）：

### 7.1 retrieval_status

| 值 | 说明 |
|----|------|
| `found` | 检索到匹配 PDF URL + 基本 metadata |
| `not_found` | 预期应有报告 / 公告但未返回 |
| `title_excluded` | 有结果但被 title filter 排除（摘要、英文版等） |
| `period_mismatch` | 标题或元数据与预期报告期不一致 |
| `empty_response` | API 200 但 records 为空 |
| `network_error` | HTTP / 超时错误 |

### 7.2 parse_status

| 值 | 说明 |
|----|------|
| `not_started` | 默认；未下载 / 未解析 |
| `parsed_text` | 全文或主体文本已提取 |
| `parsed_partial` | 部分页 / 部分章节成功 |
| `parse_failed` | 解析失败 |
| `skipped` | 刻意跳过（如仅要 metadata） |

### 7.3 chunk_status

| 值 | 说明 |
|----|------|
| `not_started` | 默认 |
| `chunked` | 已生成 `document_chunk` |
| `chunk_failed` | 切分失败 |

### 7.4 embedding_status

| 值 | 说明 |
|----|------|
| `not_started` | 默认 |
| `embedded` | 已写入向量库（未来） |
| `embedding_failed` | 失败 |
| `skipped` | 当前阶段默认 |

**禁止：** 将 `retrieval_status=found` 写成 **verified** 或等同于「生产可用 corpus」。

---

## 8. 与 Phase 1 A 类关系

| 维度 | Phase 1 A 类 | B 类 corpus（本设计） |
|------|--------------|----------------------|
| 已做 | `hisAnnouncement/query` **retrieval**；P1 **749/796 = 94.10%** found | 承接 found 行为 **document seed** |
| 未做 | PDF 下载、正文解析、chunk | 本设计预留 parse / chunk 层，**当前不实现** |
| title filter | 排除非正式报告标题 | 映射为 `title_excluded` 或 `classification_confidence` 降级 |
| 负样本 | `not_found`、`empty_response` | **保留审计记录** — corpus 不仅存成功文档 |
| 计行口径 | company × report_type × expected_period | B 类 document 一行 ≈ 一份逻辑文档（可含 version） |

**迁移路径：** Phase 1 `cninfo_report_p1_coverage_validation.csv` 中 `found` 行 → 未来脚本离线生成 `document` draft（**不在本阶段实现**）。

---

## 9. 与 D 类 fixed-table 关系

| 关系 | 说明 |
|------|------|
| **证据引用** | D 类 `equity_pledge` event 可 `event_document_link` → 披露质押的 **公告 PDF**（B 类 document） |
| **RAG evidence** | B 类 chunk 作为问答证据；D 类 row 作为 **结构化事实** 补充 |
| **关联键** | `company_code`、`announcement_date` / `event_date`、`title` 模糊匹配、`pdf_url`、`org_id` |
| **禁止** | 把 D 类 `raw_record_json` 当作 `document_chunk`；把 `disclosure_schedule` 行当作 B 类 document |

详见 [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md)。

---

## 10. RAG / LLM Wiki 用途

| 用途 | B 类提供 | D 类补充 |
|------|----------|----------|
| **company wiki profile** | 年报 MD&A、公司治理章节 chunk | 股东人数、高管持股变动等 metric |
| **report timeline** | report corpus 按 `report_period` 排序 | `disclosure_schedule` 预约披露日 |
| **event timeline** | 公告标题 + 摘要 chunk | block_trade、shareholder_change 等 event feed |
| **evidence-backed Q&A** | `document_citation_span` + chunk retrieval | 数值题可查 D 类 metric |
| **citation span** | 页码 + quote 回溯 PDF | event 可链接源公告 document |

**LLM Wiki 原则：** 叙事与引用走 **B 类**；筛选、告警、量化表走 **D 类**。

---

## 11. 当前不做的事情

| 不做 | 原因 |
|------|------|
| 下载 PDF | Era C 红线；设计阶段 |
| 解析 PDF | 无 parser 实现 |
| 建立向量库 | 无 embedding 管道 |
| 生成 embedding | 同上 |
| 接 PostgreSQL / MinIO / MongoDB | 不入库 |
| 全量 corpus 抓取 | 仅设计口径 |
| 写 **verified** | Era C 红线 |

---

## 12. 产物索引

| 文档 | 说明 |
|------|------|
| [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) | 逻辑对象与字段 |
| [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md) | B / D 边界与反模式 |
| [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) | A–F 权威分层 |
| [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md) | D 类 registry（对照） |

---

## 13. 下一步（设计延续，非本文件实现）

1. 补 B 类官方 `category` 码到 `cninfo_announcement_categories.yaml`（不改本阶段 D 类文件）。
2. 定义 B 类 source registry layer（与 D 类 `source_layer=document_corpus` 区分）。
3. 起草 `b_document.schema.json` 逻辑 schema（类比 `schemas/d_class/`）。
4. 改造 `validate_cninfo_announcement_categories.py` 为 corpus + known-event 口径（**未来脚本阶段**）。

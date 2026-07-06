# CNINFO B 类 Corpus 与 D 类 Fixed-table 边界

_最后更新：2026-07-05_

> **上级：** [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md) · [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md)  
> **权威分层：** [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md)

---

## 1. 核心区别

| 维度 | **B 类** | **D 类** |
|------|----------|----------|
| **数据形态** | 文档 — PDF / 公告全文 | 固定表格 JSON rows |
| **结构化程度** | 非结构化文本（未来 parse 后 semi-structured） | 已结构化字段（SECCODE、F001N…） |
| **核心对象** | `document` → `chunk` → `citation_span` | `d_company_event` / `d_company_metric_*` / `d_disclosure_schedule` |
| **主要入口** | `hisAnnouncement/query`、公告 category 检索 | `data20/*` JSON API |
| **下游用途** | RAG、LLM Wiki、证据引用、叙事摘要 | 结构化 timeline、筛选、告警、量化表 |
| **Registry layer** | `document_corpus`（待建） | `company_event` / `company_metric_*` / `disclosure_schedule` / `industry_aggregate` |
| **验证口径** | corpus 非空率、字段可得性、known-event 命中 | endpoint 稳定性、字段 UI 确认、schema validation |
| **Phase 状态** | 设计启动（本批文档） | Phase 2 十源 `testing_stable_sample` + Phase 3 schema |

**一句话：** B 类是 **「读文档」**；D 类是 **「读表格」**。

---

## 2. 举例

### B 类（document corpus）

| 示例 | document_type | 说明 |
|------|---------------|------|
| 平安银行 2024 年年度报告 PDF | `annual_report` | Phase 1 A 类 retrieval 目标 |
| 某公司 2024 半年度报告 PDF | `semi_annual_report` | 同上 |
| 交易所问询函回复公告 | `inquiry_reply` | 事件公告 corpus；**不是**定期报告 |
| 董事会决议公告 | `board_resolution` | 普通 announcement 子类 |
| 股东大会召开通知 | `meeting_notice` | 会议类 corpus |

### D 类（fixed-table records）

| 示例 | source_id | target 表 |
|------|-----------|-----------|
| 泰福泵业 2026-06-08 限售解禁 row | `restricted_shares_unlock` | `d_company_event` |
| 贵州茅台 2026-07-03 大宗交易 row | `block_trade` | `d_company_event` |
| 平安银行融资余额日度 row | `margin_trading` | `d_company_metric_daily` |
| 股东人数报告期 row | `shareholder_data` | `d_company_metric_periodic` |
| 基金行业配置行业 row | `fund_industry_allocation` | `d_industry_aggregate` |
| 预约披露日程 row | `disclosure_schedule` | `d_disclosure_schedule` |

---

## 3. 不要混淆的情况

| 反模式 | 正确理解 |
|--------|----------|
| `abnormal_trading` 的 `detail[]` 营业部明细 | D 类嵌套 JSON → 未来 `d_event_party_detail`；**不是** PDF document chunk |
| `disclosure_schedule` 预约披露 row | D 类 **schedule** 表；不是 B 类 document（无 PDF 全文语料） |
| Phase 1 检出的 `pdf_url` | B 类 **document seed**；检索行为属 A 类，语料组织属 B 类 |
| D 类 `equity_pledge` event row | 结构化事件；**可 link** 到披露质押的 B 类公告 PDF，但 row 本身不是公告 |
| 公告标题含「报告」的业绩预告 | 可能是 B 类 `announcement`；**不能**默认归入 `annual_report` |
| `shareholder_change` inc/desc row | D 类 event；源公告 PDF 在 B 类另存 |
| 把 `raw_record_json` 当作文本 chunk | D 类 lineage 字段；RAG 应读 B 类 parse 后的 `document_chunk.text` |

---

## 4. 连接方式

跨层关联建议键（可多键组合 + `link_confidence`）：

| 关联键 | B 类字段 | D 类字段 | 强度 |
|--------|----------|----------|------|
| 公司 | `company_code` | `company_code` | 必要非充分 |
| 公司名 | `company_name` | `company_name` | 弱 |
| 披露日 | `announcement_date` | `announcement_date` / `event_date` | 中 |
| 报告期 | `report_period` | `report_period`（metric） | 中（报告类） |
| 标题 | `title` | — | 规则 / 模糊匹配 |
| URL | `pdf_url` | — | 强（若 event 存源 URL） |
| 源 | `source_id` | `source_id` | 区分 CNINFO 入口 |
| 事件类型 | `document_type` | `event_type` | 需映射表 |

**标准 linkage：** `event_document_link`（见 [document model §10](cninfo_b_class_document_model_draft.md#10-与-d-类-event-的-linkage)）。

---

## 5. 产品层用途

### B 类适合

| 场景 | 说明 |
|------|------|
| RAG answer evidence | chunk + citation 回溯原文 |
| Company wiki narrative | 年报 MD&A、治理描述 |
| Report summary | 跨报告期文本摘要 |
| Quote / citation | 投资者问答、合规引用 |

### D 类适合

| 场景 | 说明 |
|------|------|
| Structured timeline | 解禁、质押、增减持日期序列 |
| Alerts | 融资融券异动、异常交易 |
| Screening | 股东人数变化、行业基金配置 |
| Quantitative table | 融资余额、大宗交易金额 |
| Event feed | 公司行为流（非全文） |

**汇合点：** Company Timeline / LLM Wiki 页面可同时展示 D 类 event 卡片 + B 类 document 链接。

---

## 6. 后续架构建议

```
                    ┌─────────────────┐
                    │  A 类 retrieval │
                    │  (report PDF)   │
                    └────────┬────────┘
                             │ metadata seed
                             ▼
┌──────────────┐      ┌─────────────────┐      ┌──────────────────┐
│ B 类 corpus  │      │ Company / Wiki  │      │ D 类 fixed-table │
│ document     │─────▶│ Timeline / RAG  │◀─────│ event / metric   │
│ chunk/cite   │ link │                 │ feed │                  │
└──────────────┘      └─────────────────┘      └──────────────────┘
       │                                                │
       │ parser/chunker                                   │ row mapper
       ▼                                                ▼
  (future pipeline)                              schemas/d_class/
```

| 建议 | 说明 |
|------|------|
| **双 registry layer** | B 类与 D 类均进 source registry，但 `source_layer` 不同：`document_corpus` vs `company_event` 等 |
| **B 类管道** | retrieval → document metadata → download → parse → section → chunk → embed |
| **D 类管道** | endpoint → raw row → mapper → schema validate → logical table |
| **禁止混管道** | 不要用 D 类 mapper 处理 PDF；不要用 B 类 chunker 处理 JSON table row |
| **状态模型分离** | B 类：`retrieval_status` / `parse_status` / `chunk_status`；D 类：`testing_stable_sample` 等（见 ingestion status model） |
| **最终汇合** | `company_code` + 时间轴 + `event_document_link` 在应用层 join |

---

## 7. Era C 阶段边界（重申）

| 允许（本阶段） | 禁止 |
|----------------|------|
| B 类 corpus / document 逻辑设计 | 下载 / 解析 PDF |
| B vs D 边界文档 | 修改 D 类 registry / schema / fixtures |
| 更新导航指向 B 类设计 | 写 verified、入库、全量抓取 |

---

## 8. 产物索引

| 文档 | 说明 |
|------|------|
| [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md) | Corpus 职责与状态 |
| [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) | 逻辑对象字段 |
| [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) | D 类逻辑表（对照） |
| [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md) | D 类十源总结 |
| [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) | A 类 retrieval 总结 |

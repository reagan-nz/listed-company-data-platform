# CNINFO B 类 JSON Schema Draft Notes

_最后更新：2026-07-05_

> **性质：** 逻辑 schema 草案；不是数据库 migration；不写 verified。  
> **上级：** [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) · [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md)

---

## 1. 目的

为 B 类 document corpus 建立与 D 类 `schemas/d_class/` 同级的 **JSON Schema draft-07** 逻辑记录形状，用于：

- 离线校验 Phase 1 → B 类 metadata fixture；
- 约束未来 parser / chunker / linkage 产出；
- 与 registry、category routing 对齐，但不替代二者。

**当前阶段：** 仅 metadata 层；不下载、不解析 PDF。

---

## 2. Schema 覆盖范围

| Schema 文件 | 逻辑对象 | 当前 fixture |
|-------------|----------|--------------|
| `b_document.schema.json` | document 元数据 | ✅ 20 条 periodic report JSONL |
| `b_raw_file.schema.json` | 物理/逻辑文件层 | 待 seed |
| `b_document_version.schema.json` | 修订/更正版本 | 待 seed |
| `b_document_section.schema.json` | 解析章节 | 待 parse |
| `b_document_chunk.schema.json` | RAG chunk | 待 chunk |
| `b_document_citation_span.schema.json` | 引用 span | 待 citation |
| `b_document_parse_run.schema.json` | 解析审计 | 待 parse |
| `b_event_document_link.schema.json` | B↔D 事件关联 | 待 linkage |

目录：`schemas/b_class/`（8 个 `.schema.json`）。

---

## 3. Required 字段原则

1. **metadata 最小闭包：** `b_document` required 仅含 identity + classification + lineage（`document_id`, `source_id`, `title`, `document_type`, `retrieval_status`, `classification_status`, `raw_metadata_json`, `created_from`）。
2. **宽松兼容 not_found：** `pdf_url`、`report_period`、`announcement_date` **非 required**，以容纳 retrieval 失败或 title_excluded 元数据行。
3. **found fixture 惯例：** Phase 1 seed 的 `found` 行通常带 `pdf_url`、`company_code`、`source_confidence`；由 fixture 作者保证，不由 schema 强制。
4. **parse/chunk 层：** section / chunk / citation required 仅覆盖结构键；`text`、`page_*` 等内容字段在 parse 前可为空或缺失。
5. **无 verified enum：** 使用 `source_confidence`（registry 层级）与 `classification_confidence`（分类层级），**不出现** `verified`。

---

## 4. 与 B 类 registry 的关系

| 层级 | 职责 |
|------|------|
| **registry** (`cninfo_b_class_source_registry_draft.yaml`) | 定义 `source_id`、检索模式、`source_confidence` 默认值、category 路由入口 |
| **document schema** | 定义单条 `document` 逻辑记录形状；`source_id` 必须来自 registry |
| **category routing** (`cninfo_announcement_categories.yaml`) | title → `document_type` / route；产出写入 `classification_status` |

Registry 描述「如何发现」；schema 描述「发现后如何存储元数据」。

---

## 5. 与 D 类 schema 的区别

| 维度 | D 类 | B 类 |
|------|------|------|
| 核心对象 | `d_company_event`、metric、schedule | `b_document`、chunk、citation |
| 数据来源 | 固定表格 API 行 | 公告 PDF metadata + 未来全文 |
| raw 层 | `d_raw_record_snapshot` | `b_raw_file`（URL + download_status） |
| 成功口径 | 字段可得性%、入口稳定 | corpus 可得性 + known-document benchmark |
| 关联 | 事件表为主 | `b_event_document_link` → `d_company_event` |
| 当前 validation | 11 fixture PASS | 20 document metadata PASS |

B 类 schema **不复制** D 类 event 字段；交叉引用通过 `event_id` + link 表。

---

## 6. 当前未实现

- `b_raw_file` / version / section / chunk / citation / parse_run / event_link **fixture 与 validation**
- PDF 下载（`download_status` 停留在 `not_started`）
- Parser / chunker / embedder
- inquiry / meeting / general announcement document seed
- 官方 CNINFO `category_code` 锁定后回填 routing YAML
- 数据库 migration / ORM model

---

## 7. 下一步

1. **raw_file fixture：** 从 20 条 document 的 `pdf_url` 派生 `download_status=not_started` 行。
2. **parser / chunker plan：** 独立设计文档，不急于实现。
3. **扩展 document seed：** inquiry_reply、meeting_notice、general_announcement。
4. **schema validation 扩展：** 每新增 fixture 类型，在 `validate_cninfo_b_class_document_schema.py` 或姊妹脚本中增加对应用例。
5. **暂不下载 PDF。**

---

## 参考

| 文档 | 路径 |
|------|------|
| Document model | [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) |
| Validation design | [cninfo_b_class_validation_design.md](cninfo_b_class_validation_design.md) |
| Schema validation summary | [cninfo_b_class_document_schema_validation_summary.md](../outputs/validation/cninfo_b_class_document_schema_validation_summary.md) |
| D 类 schema 先例 | [schemas/d_class/](../schemas/d_class/) |

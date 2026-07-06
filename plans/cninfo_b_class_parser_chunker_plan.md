# CNINFO B 类 Parser / Chunker Plan

_最后更新：2026-07-05_

> **性质：** 设计草案；不下载 PDF、不解析 PDF、不生成 chunk、不写 verified。  
> **前置：** [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) · [schemas/b_class/](../schemas/b_class/) · [cninfo_b_class_json_schema_draft_notes.md](cninfo_b_class_json_schema_draft_notes.md)  
> **关联：** [cninfo_b_class_chunking_strategy.md](cninfo_b_class_chunking_strategy.md) · [cninfo_b_class_parse_quality_model.md](cninfo_b_class_parse_quality_model.md)

---

## 1. 目标

定义 B 类 document corpus **未来**从物理文件到可检索文本单元的解析链路：

```
b_raw_file
  → b_document_parse_run
  → b_document_section
  → b_document_chunk
  → b_document_citation_span
```

**本阶段只是设计，不执行 PDF 解析。**

当前已有：
- 20 条 `b_document` metadata fixture（schema PASS）
- 20 条 `b_raw_file` metadata fixture（`download_status=not_started`，schema PASS）

解析实现、fixture 生成、embedding 均 **不在本阶段范围**。

---

## 2. 输入对象

解析流水线的逻辑输入来自已登记的 metadata，不要求 PDF 已落盘。

| 对象 | 来源 | 关键字段 |
|------|------|----------|
| `b_raw_file` | `fixtures/b_class/raw_file/` | `raw_file_id`, `source_url`, `download_status`, `document_id` |
| `b_document` | `fixtures/b_class/document/` | `document_id`, `document_type`, `title`, `report_period`, `company_code`, `pdf_url` |

**解析触发前最低条件（未来）：**

| 条件 | 说明 |
|------|------|
| `download_status = downloaded` | `source_url` 已拉取到 `storage_uri_candidate` |
| `document.retrieval_status = found` | 非 title_excluded / not_found 元数据 |
| `mime_type = application/pdf` | 当前 corpus 仅设计 PDF 路径 |

**输入上下文（denormalized，供 parser 路由）：**

- `source_url` / `pdf_url` — CNINFO 静态链接
- `document_type` — annual_report / inquiry_reply / …
- `report_period` — 报告类归一化期末日
- `company_code` / `company_name` — 公司标识
- `title` — 用于 section 启发式与质量校验（title_period_match）

---

## 3. 输出对象

| 对象 | Schema | 职责 |
|------|--------|------|
| `b_document_parse_run` | `b_document_parse_run.schema.json` | **一次解析执行的审计记录**；记录 parser 版本、页数、文本长度、整体 parse_status、错误信息 |
| `b_document_section` | `b_document_section.schema.json` | **结构化章节**；目录/标题/页码边界；供 chunk 不跨章切分 |
| `b_document_chunk` | `b_document_chunk.schema.json` | **RAG 检索基本单元**；带 page range、chunk_index、quality_flags |
| `b_document_citation_span` | `b_document_citation_span.schema.json` | **可引用证据片段**；LLM Wiki / Q&A 回答溯源 |

**关系（逻辑外键）：**

```
document (1) ──< parse_run (N)
document (1) ──< section (N)
document (1) ──< chunk (N)
section (1) ──< chunk (N)     # chunk 通常归属 section
chunk (1) ──< citation_span (N)
raw_file (1) ──< parse_run (N)  # parse_run 应记录 raw_file_id（schema 扩展项，见 §6）
```

`b_document` 上的 `parse_status` / `chunk_status`（document model 扩展字段）由最新 parse_run 与 chunk 流水线 **派生更新**，不在本计划中单独立表。

---

## 4. Parser 选择原则

未来 parser **候选能力**（不绑定唯一库）：

| 能力 | 适用场景 | 备注 |
|------|----------|------|
| PDF text extraction | 数字 born-digital PDF | 首选路径 |
| table-aware parser | 财务报表、附注表格 | 保留表格结构或 table_heavy 标记 |
| OCR fallback | 扫描件、图片型 PDF | 质量通常低于 text extraction |

**当前阶段约束：**

- **不选择**具体库作为唯一方案（如 PyMuPDF / pdfplumber / unstructured 等留待实施阶段评估）
- **不跑** OCR
- **不处理**真实 PDF
- parser 名称以 `parser_name` + `parser_version` 字符串登记，便于 A/B 与回放

**选型原则（未来实施时）：**

1. 先 text extraction，失败或 `low_text_density` 再考虑 OCR
2. 定期报告优先 table-aware 路径处理财务报表 section
3. 短公告（inquiry_reply、meeting_notice）可用轻量 paragraph parser
4. 同一 `document_id` 允许多次 parse_run（重跑、换 parser），以 `created_at` 区分

---

## 5. Parse status

与 `b_document_parse_run.parse_status` enum 对齐：

| 状态 | 含义 |
|------|------|
| `not_started` | 已登记 metadata，尚未发起解析（**当前全体 fixture 状态**） |
| `parsed_text` | 全文或绝大部分页面成功提取为可用文本 |
| `parsed_partial` | 部分页面/章节成功；仍有可用 section/chunk，但带 quality_flags |
| `parse_failed` | 无法产生可用文本；保留 document/raw_file metadata，不删行 |
| `skipped` | 主动跳过（如 duplicate、policy block、非 PDF） |

**document 级 `parse_status` 建议映射：** 取该 document **最新** parse_run 的 `parse_status`；无 parse_run 时为 `not_started`。

---

## 6. Parse run metadata

`b_document_parse_run` 核心字段（与 schema 对齐；`raw_file_id` 为实施期建议扩展）：

| 字段 | 说明 |
|------|------|
| `parse_run_id` | 逻辑主键（如 hash(document_id, parser_name, parser_version, created_at)） |
| `document_id` | 父 document |
| `raw_file_id` | 本次解析使用的 raw_file（**实施时写入**；当前 schema 可后续扩展） |
| `parser_name` | 如 `cninfo_pdf_text_v1`、`table_aware_v1` |
| `parser_version` | 语义化版本号 |
| `parse_status` | 见 §5 |
| `page_count` | 解析识别总页数 |
| `text_length` | 提取字符数（或 Unicode 码点数） |
| `error_message` | `parse_failed` / `parsed_partial` 时的错误摘要 |
| `created_at` | parse run 时间戳 |

**parse_run 不替代 chunk：** 即使 `parsed_text`，仍需独立 chunk 步骤生成 `b_document_chunk`。

---

## 7. Section 抽取策略

定期报告（annual / semi / quarterly）建议 **先 section、后 chunk**。

**信号来源（优先级从高到低）：**

1. PDF 内置 outline / bookmark（若有）
2. 中文章节标题正则（如「第三节 管理层讨论与分析」）
3. 页码断点 + 字体/字号启发式
4. 兜底：整篇 `other` section

**常见 `section_type`（与 document model 对齐，实施时可扩展 enum）：**

| section_type | 典型标题关键词 |
|--------------|----------------|
| `management_discussion` | 管理层讨论与分析、经营情况讨论与分析 |
| `financial_statement` | 财务报表、合并资产负债表、利润表 |
| `audit_report` | 审计报告、注册会计师 |
| `corporate_governance` | 公司治理、董事会报告 |
| `risk_factor` | 风险因素、风险提示 |
| `shareholder_information` | 股本变动、股东情况 |
| `other` | 无法分类或兜底 |

每条 section 记录：`section_id`, `document_id`, `section_title`, `section_path`, `page_start`, `page_end`, `parse_confidence`。

**公告类（inquiry_reply、meeting_notice）：** 可退化为 1–3 个粗粒度 section（标题块 / 正文 / 附件说明），不强制年报级目录深度。

---

## 8. Chunk 生成策略

详见 [cninfo_b_class_chunking_strategy.md](cninfo_b_class_chunking_strategy.md)。摘要：

- **在 section 内切 chunk**，不跨越 `management_discussion` ↔ `financial_statement` 等重要章节边界
- 每个 chunk 保留 `document_id`, `section_id`, `page_start`, `page_end`, `chunk_index`
- narrative 段落保留足够上下文（标题 + 首句）供 RAG 召回
- `table_heavy` section 单独策略：较小 chunk 或保留表格标记，不强行纯文本化

**chunk 输出字段：** `chunk_id`, `text`, `token_count_candidate`, `chunk_strategy`, `quality_flags[]`

---

## 9. Citation span

`b_document_citation_span` 为 **证据层**，连接 chunk 与可展示引用。

**用途：** LLM Wiki、RAG answer evidence、监管问答溯源。

| 字段 | 说明 |
|------|------|
| `citation_id` | 逻辑主键 |
| `document_id` | 父 document |
| `chunk_id` | 来源 chunk（可选但推荐） |
| `page_no` | PDF 页码（用户可见） |
| `span_start` / `span_end` | chunk 内字符偏移 |
| `quote_text` | 引用摘录（可截断） |
| `citation_confidence` | high / medium / low / unknown |

**生成时机：** chunk 完成后，由检索命中或 LLM 生成阶段写入；也可对高价值 section 预生成 anchor span。

---

## 10. 错误与质量处理

质量 flags 写入 `b_document_chunk.quality_flags` 与 parse_run 级摘要；定义见 [cninfo_b_class_parse_quality_model.md](cninfo_b_class_parse_quality_model.md)。

| flag | 触发条件（草案） |
|------|------------------|
| `scanned_pdf_candidate` | 页级文本极少、OCR 路径触发 |
| `table_heavy` | 表格行占比高 |
| `image_heavy` | 图片块占比高 |
| `title_mismatch` | 提取标题与 document.title 显著不一致 |
| `period_mismatch` | 正文报告期与 document.report_period 不一致 |
| `duplicate_candidate` | 与同源已解析 document 高度相似 |
| `low_text_density` | 字符数 / 页数低于阈值 |
| `parse_failed` | 该 chunk 或 section 解析失败 |

**原则：**

- `parse_failed` **不删除** document / raw_file metadata
- `parsed_partial` 仍保留可用 section/chunk
- `low` confidence chunk 不直接进入高置信 RAG 索引（策略层，非本阶段实现）

---

## 11. 当前不做

| 项 | 状态 |
|----|------|
| 下载 PDF | ❌ `download_status=not_started` |
| 解析 PDF | ❌ |
| 生成 section / chunk fixture | ❌ |
| 生成 embedding | ❌ |
| 接 MinIO / MongoDB / PostgreSQL | ❌ |
| 入库 / migration | ❌ |
| 写 verified | ❌ |
| 绑定具体 parser 库 | ❌ |
| 跑 OCR | ❌ |

---

## 12. 下一步（实施顺序建议）

1. **允许下载时：** 更新 `b_raw_file.download_status` / `sha256_candidate` / `storage_uri_candidate`
2. **parse_run fixture：** 对 1–2 条样本 document 做 dry-run metadata（`parse_status=skipped`，仍不解析）
3. **选定 parser 候选** 并在 lab 做小样本试跑（脱离 Era C 主线路径）
4. **section/chunk fixture + schema validation**
5. **chunk quality offline validation**（见 chunking strategy §7）

---

## 参考

| 文档 | 路径 |
|------|------|
| Document model | [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) |
| Chunking strategy | [cninfo_b_class_chunking_strategy.md](cninfo_b_class_chunking_strategy.md) |
| Parse quality model | [cninfo_b_class_parse_quality_model.md](cninfo_b_class_parse_quality_model.md) |
| JSON Schema | [schemas/b_class/](../schemas/b_class/) |
| Raw file validation | [cninfo_b_class_raw_file_schema_validation_summary.md](../outputs/validation/cninfo_b_class_raw_file_schema_validation_summary.md) |

# CNINFO B 类 Chunking Strategy Draft

_最后更新：2026-07-05_

> **性质：** 设计草案；不生成真实 chunk、不绑定 embedding 模型、不写 verified。  
> **上级：** [cninfo_b_class_parser_chunker_plan.md](cninfo_b_class_parser_chunker_plan.md) · [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md)

---

## 1. 目标

定义 B 类 **chunk** 作为 RAG 检索与 LLM context 的 **逻辑单元**。

**chunk ≠ 数据库 row：** 它是带丰富 metadata 的文本片段对象（`b_document_chunk`），未来可存于向量库、文档库或对象存储旁路索引；当前阶段仅定义形状与切分原则。

---

## 2. Chunk 粒度建议

| 文档类型 | 切分策略 |
|----------|----------|
| **普通公告**（inquiry_reply、meeting_notice、general） | 按段落 / 标题块切；单节公告可 1 section → 多 chunk |
| **定期报告**（annual / semi / quarterly） | **先 section，再 chunk**；尊重财报章节边界 |
| **表格密集部分** | 单独标记 `table_heavy`；不强行压成 narrative 纯文本 |
| **重要数字段落** | 保留前后 1–2 句上下文（科目名、单位、报告期） |

**禁止：**

- 跨 `financial_statement` 与 `management_discussion` 合并为一个 chunk
- 将目录页与正文混在同一 chunk（目录应剔除或单独低权重 section）

---

## 3. Chunk size 草案

建议字段（`b_document_chunk`）：

| 字段 | 说明 |
|------|------|
| `token_count_candidate` | 估算 token 数（**不绑定**具体 embedding 模型） |
| `chunk_strategy` | 策略标识，如 `section_fixed_token_v1`、`paragraph_atomic_v1` |
| `overlap_candidate` | 可选；相邻 chunk 重叠 token 数（实施期扩展字段） |

**尺寸建议（字符/token 粗算，实施时校准）：**

| 内容类型 | 目标规模 | 说明 |
|----------|----------|------|
| narrative text | **500–900 tokens** | 管理层讨论、风险因素等叙述段 |
| table-heavy text | **更小 chunk**（约 200–400 tokens） | 避免单 chunk 过大且表格截断 |
| title / summary sections | **atomic** | 整节一节一 chunk（如「重要提示」「公司简介」） |

**overlap：** narrative 相邻 chunk 建议 **50–100 tokens** 重叠，减少边界截断；table-heavy 通常 **不 overlap**。

**注意：** 不对接具体 embedding model（如 text-embedding-3、BGE、m3e）；`token_count_candidate` 可用通用 tokenizer 粗算或字符数 / 4 启发式。

---

## 4. Metadata 保留

每个 chunk **必须**（逻辑上）可追溯到源 document 与披露上下文。以下字段来自 chunk 自身或 join document/section：

| 字段 | 来源 | 必填性 |
|------|------|--------|
| `chunk_id` | chunk | required |
| `document_id` | chunk | required |
| `section_id` | chunk | 推荐 |
| `company_code` | document（denormalize 或 join） | 推荐写入 chunk 扩展 metadata |
| `document_type` | document | 推荐 |
| `report_period` | document | 报告类推荐 |
| `page_start` / `page_end` | chunk | 推荐 |
| `section_path` | section | 推荐 |
| `source_url` / `pdf_url` | document / raw_file | 引用溯源 |

**RAG 过滤维度：** `company_code`, `document_type`, `report_period`, `quality_flags` 应可在检索前过滤，无需回表多次 join。

---

## 5. RAG 用途

chunk 支撑的产品场景（设计层）：

| 场景 | 典型 query | chunk 要求 |
|------|------------|------------|
| **Company wiki** | 「某公司 2024 主营业务是什么？」 | 高 recall；MDA section |
| **Report summary** | 「总结年报风险提示」 | `risk_factor` section；过滤 low confidence |
| **Event explanation** | 「这次问询函问了什么？」 | inquiry_reply chunks + D 类 event link |
| **Citation-backed Q&A** | 需附页码引用 | citation_span 必填 |

**检索链路（未来）：** embed(chunk.text) → vector search → rerank → citation_span 组装 answer evidence。

---

## 6. 不适合 chunk 的内容

以下内容应在 section/chunk 阶段 **剔除或降权**，不进入主索引：

| 类型 | 处理 |
|------|------|
| 页眉页脚 | 规则剔除 |
| 重复目录 | 仅保留一份 TOC section，低权重 |
| 无意义水印 | 剔除 |
| OCR 噪声 | `low_text_density` / `parse_failed` flag |
| 过短碎片 | 少于 ~50 tokens 且无语义 → 合并或丢弃 |
| 法律 boilerplate | 可保留但单独 `section_type`，低优先级召回 |

---

## 7. 后续 validation

未来可对 chunk fixture / 解析产出做 **离线 validation**（不需联网）：

| 检查项 | 规则 |
|--------|------|
| `document_id` 存在 | 每条 chunk 非空 |
| page range | `page_start <= page_end`；报告类建议有值 |
| text 非空 | `parse_failed` chunk 除外 |
| `token_count_candidate` | 在合理范围（如 50–1200）；异常记入 report |
| `quality_flags` | 已知 enum；`table_heavy` 与 `chunk_strategy` 一致 |
| section 不跨界 | chunk 的 page range 落在 parent section 内 |
| schema | `b_document_chunk.schema.json` PASS |

**脚本占位：** `lab/validate_cninfo_b_class_chunk_schema.py`（待 chunk fixture 存在后实现）。

---

## 8. 当前不做

- 不生成 chunk fixture
- 不跑 parser / chunker 代码
- 不计算真实 `token_count_candidate`
- 不生成 embedding
- 不写 verified

---

## 参考

| 文档 | 路径 |
|------|------|
| Parser / chunker plan | [cninfo_b_class_parser_chunker_plan.md](cninfo_b_class_parser_chunker_plan.md) |
| Parse quality model | [cninfo_b_class_parse_quality_model.md](cninfo_b_class_parse_quality_model.md) |
| Chunk schema | [schemas/b_class/b_document_chunk.schema.json](../schemas/b_class/b_document_chunk.schema.json) |

# CNINFO B 类 Parse Quality Model

_最后更新：2026-07-05_

> **性质：** 质量模型设计草案；不运行 parser、不实际打分、不写 verified。  
> **上级：** [cninfo_b_class_parser_chunker_plan.md](cninfo_b_class_parser_chunker_plan.md) · [cninfo_b_class_chunking_strategy.md](cninfo_b_class_chunking_strategy.md)

---

## 1. 目标

定义 B 类 PDF 解析与切分的 **质量判断框架**。

**核心原则：** 并非所有 PDF 解析结果都应视为高质量文本。质量信息必须进入 `parse_run`、`section.parse_confidence`、`chunk.quality_flags`、`citation_span.citation_confidence`，供下游 RAG / Wiki **过滤与降权**，而非事后人工发现。

当前阶段 **只定义模型**，不跑 parser、不对 20 条 fixture 打分。

---

## 2. Quality dimensions

质量评估从以下 **维度** 观察（实施时可组合为规则或启发式分数）：

| 维度 | 观察对象 | 说明 |
|------|----------|------|
| `text_density` | 全文 / 页 | 每页提取字符数；过低 → scanned 或 parse 失败 |
| `page_coverage` | parse_run | 成功提取文本的页占比 |
| `table_density` | section / chunk | 表格行、制表符占比 |
| `image_density` | 页 | 图片块面积或数量占比 |
| `section_detection_quality` | section | 目录匹配率、标题与正文一致性 |
| `title_period_match` | document vs 正文 | title、report_period 与正文首段是否一致 |
| `duplicate_risk` | document | 与同源历史 document 文本相似度 |
| `citation_usability` | citation_span | 引用是否含完整句子、页码是否可信 |

**不追求单一总分：** 各维度映射到 `quality_flags` 与 confidence enum，便于可解释过滤。

---

## 3. Quality flags

与 `b_document_chunk.quality_flags` enum 对齐：

| flag | 含义 | 典型触发 |
|------|------|----------|
| `scanned_pdf_candidate` | 疑似扫描件，文本来自 OCR 或极稀疏 | 页均字符 < 阈值；无文字层 |
| `table_heavy` | 表格密集 | 表格行占比 > 阈值 |
| `image_heavy` | 图片为主 | 图片面积占比 > 阈值 |
| `title_mismatch` | 文档 title 与正文标题不一致 | 正则 / 相似度 < 阈值 |
| `period_mismatch` | 报告期不一致 | 正文「2023年度」vs metadata `2024-12-31` |
| `duplicate_candidate` | 疑似重复披露 | 与已有 document 文本 hash 相近 |
| `low_text_density` | 整体文本过少 | `text_length / page_count` 过低 |
| `parse_failed` | 该 chunk/section 解析失败 | parser 异常或空文本 |

**粒度：**

- **document / parse_run 级：** 汇总 `low_text_density`、`page_coverage` 等
- **section 级：** `parse_confidence` on `b_document_section`
- **chunk 级：** `quality_flags[]` on `b_document_chunk`

---

## 4. Parse confidence

用于 `b_document_section.parse_confidence` 及 parse_run 级摘要。

| 值 | 含义 |
|----|------|
| `high` | 章节边界清晰；文本完整；与 document metadata 一致 |
| `medium` | 部分边界模糊或表格多；仍可用于 RAG |
| `low` | 严重噪声、OCR 可疑、标题不匹配 |
| `unknown` | 尚未评估或规则未覆盖 |

**与 `parse_status` 区别：** `parse_status` 描述 **是否完成解析**；`parse_confidence` 描述 **结果可信度**。

---

## 5. Chunk confidence

实施期可在 chunk 上增加 `chunk_confidence`（或从 `quality_flags` 派生）。逻辑与 parse confidence 同级 enum：

| 值 | 含义 |
|----|------|
| `high` | 无负面 flag；token 数合理；section 已知 |
| `medium` | 含 `table_heavy` 等可接受 flag |
| `low` | 含 `scanned_pdf_candidate`、`title_mismatch`、`low_text_density` |
| `unknown` | 未评估 |

**RAG 策略（未来）：** 默认检索 `high` + `medium`；`low` 仅显式深度检索时包含。

---

## 6. Citation confidence

用于 `b_document_citation_span.citation_confidence`（schema 已定义）。

| 值 | 含义 |
|----|------|
| `high` | 完整句子；页码与 chunk page range 一致；来源 chunk confidence ≥ medium |
| `medium` | 截断引用但语义完整 |
| `low` | OCR 噪声、跨页截断、表格单元格碎片 |
| `unknown` | 未评估 |

**产品要求：** 面向用户的 citation-backed answer 默认只展示 `high` / `medium` citation。

---

## 7. Failure handling

| 情况 | 处理 |
|------|------|
| `parse_failed` | **保留** document / raw_file metadata；parse_run 记 `error_message`；不生成 chunk |
| `parsed_partial` | 保留成功 section/chunk；失败页记入 flags |
| `low` confidence chunk | 不进入默认 RAG 索引；可进「低置信」冷存储 |
| 质量问题 | 必须写入 `parse_run` 摘要 + `chunk.quality_flags`；不可静默丢弃 |
| `title_mismatch` / `period_mismatch` | 不自动改 document metadata；供人工或规则复核 |

**与 retrieval 层关系：** Phase 1 `found` 只保证 **URL 与标题检索**；parse quality 是 **正文层** 的独立验证，二者不混为 verified。

---

## 8. 当前不做

| 项 | 状态 |
|----|------|
| 运行 parser | ❌ |
| 对 20 条 fixture 实际打分 | ❌ |
| 写 quality score 数值列 | ❌（仅 enum + flags 设计） |
| 自动修复 metadata | ❌ |
| 写 verified | ❌ |
| embedding / 向量索引 | ❌ |

---

## 9. 下一步

1. 实施 parser 后，对 **1–2 份样本 PDF** 跑通 parse_run → section → chunk，人工标注期望 quality_flags
2. 起草 offline **known-chunk benchmark**（类似 known-document routing，标题级期望）
3. 将 chunk validation 并入 `outputs/validation/` 报告体系
4. 与 D 类 event link 联动：inquiry_reply 低质量 chunk 仍保留 metadata，但 RAG 降权

---

## 参考

| 文档 | 路径 |
|------|------|
| Parser / chunker plan | [cninfo_b_class_parser_chunker_plan.md](cninfo_b_class_parser_chunker_plan.md) |
| Chunking strategy | [cninfo_b_class_chunking_strategy.md](cninfo_b_class_chunking_strategy.md) |
| Chunk schema (quality_flags) | [schemas/b_class/b_document_chunk.schema.json](../schemas/b_class/b_document_chunk.schema.json) |
| Citation schema | [schemas/b_class/b_document_citation_span.schema.json](../schemas/b_class/b_document_citation_span.schema.json) |

# CNINFO B 类 Retrieval Validation Next Steps

_最后更新：2026-07-05_

> **设计：** [cninfo_b_class_corpus_retrieval_validation_design.md](cninfo_b_class_corpus_retrieval_validation_design.md)  
> **Fixture：** [fixtures/b_class/retrieval_validation/](../fixtures/b_class/retrieval_validation/)

---

## 1. 当前状态

| 项 | 状态 |
|----|------|
| `cninfo_periodic_report_pdf` | **testing_stable_sample**；Phase 1 expected-period 749/796 = 94.10% |
| `cninfo_inquiry_reply_pdf` | **candidate**；offline title routing PASS；retrieval **未** live 验证 |
| `cninfo_meeting_notice_pdf` | **candidate**；同上 |
| `cninfo_general_announcement_pdf` | **candidate**；同上 |
| Offline title routing | 16/16 PASS（[known_document_benchmark.yaml](../fixtures/b_class/known_documents/known_document_benchmark.yaml)） |
| Document / raw_file / parse_run schema | PASS（33 / 20 / 33 fixtures） |
| Registry lint | 23 rules PASS |
| Retrieval validation fixture | **design_only**（12 known-document + 9 category-sample cases） |
| Live CNINFO 请求 | **未执行** |

---

## 2. 进入 live validation 前需要补什么

每条 case 从 `design_only` → `ready` 前须补齐：

| 字段 / 项 | known-document | category-sample |
|-----------|----------------|-----------------|
| `company_code` | 推荐必填（窄窗检索） | 可选；可用分层样本公司列表 |
| `company_name` | 推荐 | 可选 |
| `title_pattern` | 确认为真实标题子串 | 确认为 corpus 关键词 |
| `date_start` / `date_end` | **必填**窄窗（如 ±7 天） | **必填**（如 1 个月） |
| `expected_document_type` | 人工核对 | 审计抽样分类 |
| `endpoint` / `params` | 确认 `hisAnnouncement/query` + stock/orgId/column | 同上 |
| `pdf_url` 字段 | 确认 `adjunctUrl` 非空 | 抽样行非空率% |
| `category_code` | 若 probe 完成可填入 YAML | 同上 |
| Case `status` | `design_only` → `ready` | 同上 |

**禁止：** 捏造公司代码或披露日期填入 production case。

---

## 3. 小样本 live validation 原则

| 原则 | 说明 |
|------|------|
| **少量 case** | 每 source 先 5–15 条 known-document + 3–5 条 category-sample |
| **速率限制** | `sleep_seconds` ≥ 0.6；`timeout_seconds` ≤ 15；单脚本串行 |
| **只请求 metadata** | `hisAnnouncement/query` JSON；**不下载** PDF 正文 |
| **不解析** | 不做 OCR / chunk / embedding |
| **记录 empty_response** | 区分「合理无公告」vs「参数错误」 |
| **分类审计** | 每条命中行跑 offline routing 规则对照 `expected_route_to` |
| **false-positive guard** | periodic_guard case 必须单独跑并记入 report |
| **不写 verified** | pass 最多标 `testing`；不自动升 `testing_stable_sample`（non-periodic） |

---

## 4. 成功标准

### 4.1 known-document

- `case_result = pass`：命中预期 `title_pattern` + `pdf_url_available = yes` + `classified_correctly`
- `ambiguous`：多行命中或 document_type 边界模糊 → 人工复核
- `fail`：not_found 且窗内应有披露 / misclassified / 误入 periodic

### 4.2 category-sample

- 返回行数 ≥ `expected_min_results`（guard case 允许 0 若窗内确实无匹配）
- `expected_document_types` 占比 ≥ **80%**（可调）
- `false_positive_guard_patterns` 命中行 **零** 误入 `cninfo_periodic_report_pdf`

### 4.3 汇总

- 报告写入 `outputs/validation/cninfo_b_class_corpus_retrieval_validation_report.csv`
- Summary MD 含 by-source pass/fail/ambiguous 与 **不代表 verified** 声明

---

## 5. 不做的事

| 项 | 状态 |
|----|------|
| 下载 PDF | ❌ |
| 解析 PDF / OCR | ❌ |
| 生成 chunk / embedding | ❌ |
| 入库 / migration | ❌ |
| 写 verified | ❌ |
| 全市场扫库 | ❌ |
| candidate → testing_stable_sample 自动升级 | ❌ |

---

## 6. 建议实施顺序

1. **人工选取 3–5 条真实 known-document**（inquiry + meeting + general 各 1）填入 YAML `ready`
2. 实现 `lab/validate_cninfo_b_class_corpus_retrieval.py`（仅 `status=ready` case）
3. 跑小样本 → 写 report → 评审是否扩 case
4. Probe 官方 `category_code` 回填 `cninfo_announcement_categories.yaml`
5. 扩至完整 12 + 9 case 集；仍保持小样本原则
6. 有 `pdf_url` 后更新 raw_file / parse_run（仍可不下载）

---

## 参考

| 文档 | 路径 |
|------|------|
| Corpus retrieval design | [cninfo_b_class_corpus_retrieval_validation_design.md](cninfo_b_class_corpus_retrieval_validation_design.md) |
| B 类 validation 总设计 | [cninfo_b_class_validation_design.md](cninfo_b_class_validation_design.md) |
| Registry | [cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml) |

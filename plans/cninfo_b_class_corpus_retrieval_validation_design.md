# CNINFO B 类 Corpus Retrieval Validation Design

_最后更新：2026-07-05_

> **性质：** 设计草案；本阶段不请求 CNINFO、不下载 PDF、不写 verified。  
> **前置：** [cninfo_b_class_validation_design.md](cninfo_b_class_validation_design.md) · [cninfo_b_class_source_registry_design.md](cninfo_b_class_source_registry_design.md) · [cninfo_b_class_category_routing_rules.md](cninfo_b_class_category_routing_rules.md)  
> **Fixture 草案：** [fixtures/b_class/retrieval_validation/](../fixtures/b_class/retrieval_validation/)  
> **下一步：** [cninfo_b_class_retrieval_validation_next_steps.md](cninfo_b_class_retrieval_validation_next_steps.md)

---

## 1. 目的

本设计用于验证 B 类 **document corpus retrieval**（发现 + metadata + 分类），**不是** D 类 fixed-table row validation，也 **不是** PDF 解析或 RAG corpus 可用性验证。

| 重点 | 说明 |
|------|------|
| `cninfo_periodic_report_pdf` | 已有 Phase 1 **expected-period** 证据（749/796 = 94.10% effective found） |
| `cninfo_inquiry_reply_pdf` | **candidate**；需 known-document + category-sample 小样本 |
| `cninfo_meeting_notice_pdf` | **candidate**；同上 |
| `cninfo_general_announcement_pdf` | **candidate**；category-sample + false-positive guard |
| **本阶段** | 只定义验证结构与 benchmark fixture 草案；**不发起 CNINFO 请求** |

---

## 2. Validation 方法

### 2.1 expected-period validation

| 项 | 内容 |
|----|------|
| **适用** | `annual_report`, `semi_annual_report`, `quarterly_report_q1`, `quarterly_report_q3` |
| **source** | `cninfo_periodic_report_pdf` |
| **来源** | Phase 1 `lab/validate_cninfo_report_coverage.py` |
| **核心单位** | **company × report_type × expected_period** |
| **分子** | effective found：`pdf_url` + period match + positive pattern + 非 exclusion |
| **状态** | registry `testing_stable_sample`（继承 Phase 1，非本设计新增 live 跑） |

### 2.2 known-document retrieval validation

| 项 | 内容 |
|----|------|
| **适用** | `inquiry_reply`, `regulatory_inquiry`, `meeting_notice`, `investor_relations_activity`, `board_resolution`, `shareholder_meeting_material` |
| **source** | `cninfo_inquiry_reply_pdf`, `cninfo_meeting_notice_pdf`, `cninfo_general_announcement_pdf`（按路由） |
| **核心单位** | 一条 **已知** document case：company（可选）+ title pattern + date window |
| **用途** | 验证能否检索到 **特定已知公告**（title 匹配 + `pdf_url` + `document_type` 正确） |
| **Fixture** | [known_document_retrieval_cases.yaml](../fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml) |

**通过条件（未来 live 跑）：**

1. `query_status = success`（HTTP 200 + 非空 records 或合理解释的 `empty_response`）
2. 命中行 `matched_title` 含 `title_pattern`
3. `matched_document_type == expected_document_type`
4. `classification_status = classified_correctly`
5. `pdf_url_available = yes`（若 `expected_pdf_url_available: true`）

### 2.3 category-sample validation

| 项 | 内容 |
|----|------|
| **适用** | `general_announcement` corpus、宽窗 inquiry/meeting 抽样 |
| **source** | 主要为 `cninfo_general_announcement_pdf`；可含 inquiry/meeting |
| **核心单位** | **source_category × date_window × title_pattern** |
| **用途** | 验证某类公告 corpus **能稳定返回** + 分类准确率 + false-positive guard |
| **Fixture** | [category_sample_cases.yaml](../fixtures/b_class/retrieval_validation/category_sample_cases.yaml) |

**通过条件（未来 live 跑）：**

1. 返回行数 ≥ `expected_min_results`
2. 抽样行中 `expected_document_types` 占比达阈值（建议 ≥ 80% classified_correctly）
3. `false_positive_guard_patterns` 命中行 **不得** 误入 `cninfo_periodic_report_pdf` 路由

---

## 3. 为什么不用随机 success rate

| 问题 | 说明 |
|------|------|
| 随机公司 × 随机关键词 | 命中率受公司披露频率影响，**不能**代表 corpus 工程化能力 |
| 普通公告非每日必有 | `not_found` 可能是 **合理结果**，不应简单计 fail |
| 一行 ≠ 一份文档 | 与 Phase 1 旧 `368/780` 混计同类错误 |
| 定期报告 found% 不可推广 | 94.10% **仅**适用于 expected-period；不得当作 inquiry/meeting 基准 |

**必须用** known-document（点验证）或 category-sample（类验证）解释 retrieval 质量。

---

## 4. Validation case 字段

### 4.1 known-document case

| 字段 | 类型 | 说明 |
|------|------|------|
| `case_id` | string | 唯一标识 |
| `source_id` | string | 目标 B 类 registry source |
| `company_code` | string / null | 证券代码；placeholder 可为 null |
| `company_name` | string / null | 简称 |
| `title_pattern` | string | 标题须包含的子串或正则（实施期） |
| `expected_document_type` | enum | 与 `b_document.document_type` 对齐 |
| `date_start` | date / null | 检索窗起点 |
| `date_end` | date / null | 检索窗终点 |
| `expected_route_to` | string | 应与 `source_id` 或 category routing 一致 |
| `expected_pdf_url_available` | boolean | 是否要求 `pdf_url` |
| `notes` | string | 设计说明；placeholder 须注明待替换 |

### 4.2 category-sample case

| 字段 | 类型 | 说明 |
|------|------|------|
| `case_id` | string | 唯一标识 |
| `source_id` | string | 主查询 source |
| `source_category` | string | registry `source_category` |
| `title_pattern` | string | 检索关键词 / 标题模式 |
| `date_start` | date / null | 时间窗 |
| `date_end` | date / null | 时间窗 |
| `expected_min_results` | integer | 最少返回行数 |
| `expected_document_types` | list | 期望 document_type 集合 |
| `false_positive_guard_patterns` | list | 不得误入 periodic 的短语 |
| `notes` | string | 设计说明 |

---

## 5. Validation 输出字段

未来 `cninfo_b_class_corpus_retrieval_validation_report.csv` 建议列：

| 字段 | 说明 |
|------|------|
| `case_id` | 对应 benchmark case |
| `source_id` | 实际查询 source |
| `query_status` | success / http_error / timeout / skipped |
| `retrieval_status` | found / not_found / empty_response / … |
| `matched_title` | 命中标题 |
| `matched_document_type` | 规则分类结果 |
| `classification_status` | classified_correctly / misclassified / ambiguous / … |
| `pdf_url_available` | yes / no |
| `false_positive_reason` | 若误入 periodic 或其它 source |
| `case_result` | **pass** / **fail** / **ambiguous** / **skipped** |
| `notes` | 审计备注 |

---

## 6. Status 规则

**允许** registry `recommended_status`：

- `candidate`
- `testing`
- `testing_stable_sample`
- `partial`
- `blocked`
- `deprecated`

**禁止：**

- `verified`（Era C 红线）

**升级原则：**

- 小样本 live validation **全部 pass** 最多支持将 source 标为 `testing` 或维持 `testing_stable_sample`（仅 periodic 已继承 Phase 1）。
- **不得**因 12 条 known-document pass 自动将 inquiry/meeting/general 升为 `testing_stable_sample`。
- 升级须单独评审 + 更大样本 + 多日期复测。

---

## 7. 质量边界

| 边界 | 说明 |
|------|------|
| Retrieval validation | 只验证 **discovery / metadata / classification** |
| 不代表 | PDF 已下载、已解析、chunk/embedding 已生成 |
| 不代表 | RAG corpus 已可用于生产 |
| offline fixture | 当前 YAML 为 **design_only**；`company_code`/`date_*` 多为 null placeholder |
| 不写 verified | 全阶段禁止 |

---

## 8. 后续脚本建议

未来可新增（**本阶段不实现**）：

| 脚本 | 职责 |
|------|------|
| `lab/validate_cninfo_b_class_corpus_retrieval.py` | 读取 retrieval_validation YAML；对 `status=ready` case 发起 hisAnnouncement/query；写 report CSV + summary MD |
| 改造 `validate_cninfo_announcement_categories.py` | 对齐新 category YAML 结构；调用同上 case 驱动逻辑 |

**Live 跑前置：** 见 [cninfo_b_class_retrieval_validation_next_steps.md](cninfo_b_class_retrieval_validation_next_steps.md)。

---

## 参考

| 文档 | 路径 |
|------|------|
| B 类 validation 总设计 | [cninfo_b_class_validation_design.md](cninfo_b_class_validation_design.md) |
| Known-document routing benchmark | [known_document_benchmark.yaml](../fixtures/b_class/known_documents/known_document_benchmark.yaml) |
| Registry lint | [cninfo_b_class_registry_lint_summary.md](../outputs/validation/cninfo_b_class_registry_lint_summary.md) |
| Phase 1 总结 | [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) |

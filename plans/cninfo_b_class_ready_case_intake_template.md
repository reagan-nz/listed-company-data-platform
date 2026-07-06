# CNINFO B 类 Retrieval Ready Case Intake Template

_最后更新：2026-07-05_

> **用途：** 人工补充真实 known-document / category-sample case，供未来 live metadata validation 使用。  
> **规则：** [cninfo_b_class_retrieval_ready_case_rules.md](cninfo_b_class_retrieval_ready_case_rules.md)  
> **审核：** [cninfo_b_class_ready_case_review_checklist.md](cninfo_b_class_ready_case_review_checklist.md)  
> **示例（勿跑）：** [ready_case_examples_do_not_run.yaml](../fixtures/b_class/retrieval_validation/ready_case_examples_do_not_run.yaml)

---

## 1. 目的

本模板用于将 retrieval validation case 从 `placeholder` 升级为 **`ready`**。

- **只登记 metadata 检索条件**，不下载 PDF、不解析、不写 verified。
- 填写完成后须经 [review checklist](cninfo_b_class_ready_case_review_checklist.md) 审核。
- 审核通过后写入 `known_document_retrieval_cases.yaml` 或 `category_sample_cases.yaml`，再跑 selector 确认 `invalid_ready=0`。

**禁止：** 捏造 `company_code` / 披露日期；未审核即标 `ready`。

---

## 2. known-document case 填写模板

将以下内容复制到 YAML `cases[]` 中（审核通过后再改 `case_status`）：

```yaml
- case_id: inquiry_known_XXX          # 唯一；建议 {type}_{序号}
  case_status: ready                  # 仅审核通过后填写 ready
  source_id: cninfo_inquiry_reply_pdf # B 类 registry source_id
  company_code: "000001"              # 真实证券代码（字符串）
  company_name: "平安银行"             # 与代码对应的公司简称
  title_pattern: "关于年报问询函的回复"  # 标题须包含的子串；尽量接近真实标题
  expected_document_type: inquiry_reply
  date_start: "2024-03-01"            # YYYY-MM-DD；检索窗起点
  date_end: "2024-03-31"              # YYYY-MM-DD；检索窗终点
  expected_route_to: cninfo_inquiry_reply_pdf
  expected_pdf_url_available: true
  notes: >-
    来源：人工在 CNINFO 站内核对公告标题与日期（YYYY-MM-DD）。
    审核人：XXX；审核日期：YYYY-MM-DD。
```

### 字段说明

| 字段 | 填法 |
|------|------|
| `case_id` | 全文件唯一；建议前缀表明类型（`inquiry_known_`、`meeting_known_`） |
| `case_status` | 草稿阶段用 `placeholder`；**审核通过后**改为 `ready` |
| `source_id` | 目标 B 类 registry source（inquiry → `cninfo_inquiry_reply_pdf` 等） |
| `company_code` | 6 位证券代码；北交所注意 query code 与 mapping 一致 |
| `company_name` | 与 identity mapping / 站内显示一致 |
| `title_pattern` | 真实公告标题中的**可区分**子串；见 §5 |
| `expected_document_type` | `b_document` enum；与 routing 一致 |
| `date_start` / `date_end` | 窄窗包住披露日；见 §4 |
| `expected_route_to` | 通常与 `source_id` 相同；general 路由时写明 |
| `expected_pdf_url_available` | 一般 `true`；仅 metadata 探针可为 `false`（需 notes 说明） |
| `notes` | **必填**来源说明、审核人、核对方式 |

---

## 3. category-sample case 填写模板

```yaml
- case_id: general_sample_XXX
  case_status: ready
  source_id: cninfo_general_announcement_pdf
  source_category: announcement_pdf
  title_pattern: "董事会决议公告"
  date_start: "2024-06-01"
  date_end: "2024-06-07"
  expected_min_results: 1
  expected_document_types:
    - board_resolution
    - announcement
  false_positive_guard_patterns:
    - 年度报告
    - 半年度报告
    - 第一季度报告
  notes: >-
    类别抽样：主板样本公司池 + 1 周窗口。审核人：XXX。
    不用于单公司 known-document 断言。
```

### 字段说明

| 字段 | 填法 |
|------|------|
| `case_id` | 唯一；建议 `{category}_sample_XXX` |
| `case_status` | 审核通过后 `ready` |
| `source_id` | 主查询 source |
| `source_category` | registry `source_category`（如 `announcement_pdf`） |
| `title_pattern` | 类别级关键词；可比 known-document 略宽 |
| `date_start` / `date_end` | 见 §4；category-sample 可略宽但仍需有界 |
| `expected_min_results` | 窗内期望最少命中行数；guard case 可为 `0` |
| `expected_document_types` | 允许的类型列表；用于分类审计 |
| `false_positive_guard_patterns` | 不得误入 `cninfo_periodic_report_pdf` 的短语 |
| `notes` | 抽样口径、公司池、审核记录 |

---

## 4. 日期窗口建议

| 类型 | 建议窗口 | 说明 |
|------|----------|------|
| **known-document** | 披露日前后 **1–3 天**（总窗 3–7 天） | 以站内 `announcementTime` 为锚点 |
| **category-sample** | **1–7 天** | 需配合样本公司池或板块，避免全市场扫窗 |
| **禁止** | 跨年宽窗、整月无锚点 | false positive 过多，无法解释 pass/fail |

示例：公告日 2024-03-15 → `date_start: 2024-03-13`, `date_end: 2024-03-17`。

---

## 5. title_pattern 建议

| 原则 | 说明 |
|------|------|
| **够具体** | 避免单独「公告」「报告」「通知」 |
| **known-document** | 尽量接近真实标题子串（从 CNINFO 列表复制关键词） |
| **category-sample** | 可用类别关键词（如「董事会决议」「权益分派」） |
| **与 routing 一致** | 含「年度报告」的 guard case 应走 general，不应标 periodic |
| **区分 reply vs inquiry** | 「问询函」vs「问询函回复」分 case 填 |

---

## 6. 不允许 ready 的情况

以下任一成立则 **不得** 标 `ready`：

| 情况 | 原因 |
|------|------|
| `company_code` 为空（known-document） | 无法构造 query |
| `date_start` / `date_end` 为空 | 无法构造 seDate |
| 只有泛泛 title（如「公告」） | 误匹配 |
| `expected_document_type` 不明确或不在 enum | 无法审计 |
| 缺少 `expected_route_to`（known-document） | 无法对照路由 |
| 只是离线 title routing 样例 | 见 `known_document_benchmark.yaml` |
| 未经过人工审核 | 违反 ready-case 流程 |
| 捏造公司/日期 | 违反证据原则 |

---

## 7. 提交流程（简要）

1. 按本模板起草 case（`case_status: placeholder`）
2. 完成 [review checklist](cninfo_b_class_ready_case_review_checklist.md)
3. 改为 `case_status: ready` 并入 YAML
4. 运行 `lab/select_cninfo_b_class_retrieval_ready_cases.py`
5. 确认 `invalid_ready=0` 且 `ready>0`
6. **仍不**直接跑 live retrieval，除非下一阶段显式批准

---

## 参考

| 文档 | 路径 |
|------|------|
| Ready case rules | [cninfo_b_class_retrieval_ready_case_rules.md](cninfo_b_class_retrieval_ready_case_rules.md) |
| Corpus retrieval design | [cninfo_b_class_corpus_retrieval_validation_design.md](cninfo_b_class_corpus_retrieval_validation_design.md) |
| Next steps | [cninfo_b_class_retrieval_validation_next_steps.md](cninfo_b_class_retrieval_validation_next_steps.md) |

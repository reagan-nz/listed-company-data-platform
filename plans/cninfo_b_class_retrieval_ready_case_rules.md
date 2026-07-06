# CNINFO B 类 Retrieval Ready Case Rules

_最后更新：2026-07-05_

> **Selector 脚本：** `lab/select_cninfo_b_class_retrieval_ready_cases.py`  
> **设计：** [cninfo_b_class_corpus_retrieval_validation_design.md](cninfo_b_class_corpus_retrieval_validation_design.md)  
> **Fixture：** [fixtures/b_class/retrieval_validation/](../fixtures/b_class/retrieval_validation/)

---

## 1. 目的

**ready-case 机制**防止 `design_only` placeholder 被误用于 live CNINFO retrieval validation。

未来 `lab/validate_cninfo_b_class_corpus_retrieval.py`（尚未实现）**只应**消费 `case_status: ready` 的 case。本阶段 selector **不请求 CNINFO**，仅做字段完备性检查与 ready 集合导出。

---

## 2. case_status 定义

| 值 | 含义 |
|----|------|
| `placeholder` | 设计草案；缺真实 company/date 或仅为离线标题样例；**不得** live 跑 |
| `ready` | 字段完备、人工确认可 live 检索；未来 validation 唯一执行集 |
| `retired` | 曾 ready 但已失效（公司退市、链接失效、规则变更）；保留审计、不执行 |

**默认：** 新建 case 一律 `placeholder`，直至人工审核后改为 `ready`。

---

## 3. known-document ready 条件

`case_status: ready` 时 **必填** 且非空：

| 字段 | 要求 |
|------|------|
| `case_id` | 唯一 |
| `case_status` | `ready` |
| `source_id` | 存在于 B 类 registry |
| `company_code` | 非 null、非空字符串 |
| `company_name` | 非 null、非空字符串 |
| `title_pattern` | 非空；须为真实公告标题可匹配子串 |
| `expected_document_type` | 合法 `b_document` enum |
| `date_start` | ISO date `YYYY-MM-DD` |
| `date_end` | ISO date `YYYY-MM-DD`，≥ date_start |
| `expected_route_to` | 与 category routing / source_id 一致 |
| `expected_pdf_url_available` | boolean |

**质量要求：**

- 日期窗建议窄（如披露日前后 7–30 天）
- `title_pattern` 须能区分同类公告，避免过宽（如单独「公告」）
- `notes` 应记录案例来源（如 CNINFO 公告 ID 或人工核对日期）

---

## 4. category-sample ready 条件

`case_status: ready` 时 **必填** 且非空：

| 字段 | 要求 |
|------|------|
| `case_id` | 唯一 |
| `case_status` | `ready` |
| `source_id` | 存在于 B 类 registry |
| `source_category` | 合法 registry `source_category` |
| `title_pattern` | 非空 |
| `date_start` | ISO date |
| `date_end` | ISO date |
| `expected_min_results` | integer ≥ 0 |
| `expected_document_types` | 非空 list |

**质量要求：**

- 时间窗须明确（如单月或单季度），不可 null
- `false_positive_guard_patterns` 推荐填写（guard case 尤其重要）
- 说明抽样公司范围或全市场窗口径

---

## 5. 不允许 ready 的情况

以下任一成立则 **不得** 标为 `ready`（selector 报 `invalid_ready`）：

| 情况 | 原因 |
|------|------|
| `company_code` 为空（known-document） | 无法构造 stock 参数 |
| `date_start` / `date_end` 为空 | 无法构造 seDate |
| 仅模糊标题（如「公告」「报告」） | 误匹配风险过高 |
| 缺少 `expected_document_type` | 无法审计分类 |
| 缺少 `expected_route_to`（known-document） | 无法对照路由 |
| 仅为离线 title routing 样例 | 见 `known_document_benchmark.yaml`，非 retrieval case |
| 捏造公司/日期填入 ready | 违反 Era C 证据原则 |
| 标 `ready` 但未填 required 字段 | selector `invalid_ready` |

---

## 6. 输出与脚本行为

`lab/select_cninfo_b_class_retrieval_ready_cases.py`：

1. 读取两个 YAML 的 `cases[]`
2. 对每条输出 `ready_status`：`placeholder` | `ready` | `retired` | `invalid_ready`
3. `case_status: ready` 时校验 required 字段；缺则 `invalid_ready` + `missing_fields`
4. 写 CSV + MD summary
5. **不** 发起 CNINFO 请求

**未来 live validation 脚本应：**

```text
ready_cases = selector output where ready_status == "ready"
if not ready_cases: exit NO_READY_CASES
for case in ready_cases: ... hisAnnouncement/query ...
```

`--strict`：存在 `invalid_ready` 时 exit code 1。

---

## 7. 当前状态

| 指标 | 数值 |
|------|------|
| total cases | 21（12 known-document + 9 category-sample） |
| `placeholder` | **21** |
| `ready` | **0** |
| `retired` | **0** |
| `invalid_ready` | **0** |

**无 live-ready case。** 须人工补 3–5 条真实 known-document 后再改 `case_status: ready`。

---

## 参考

| 文档 | 路径 |
|------|------|
| Next steps | [cninfo_b_class_retrieval_validation_next_steps.md](cninfo_b_class_retrieval_validation_next_steps.md) |
| Ready case report | [cninfo_b_class_retrieval_ready_case_summary.md](../outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md) |

# CNINFO B 类 Ready Case Review Checklist

_最后更新：2026-07-05_

> **Intake 模板：** [cninfo_b_class_ready_case_intake_template.md](cninfo_b_class_ready_case_intake_template.md)  
> **规则：** [cninfo_b_class_retrieval_ready_case_rules.md](cninfo_b_class_retrieval_ready_case_rules.md)  
> **Selector：** `lab/select_cninfo_b_class_retrieval_ready_cases.py`

---

## 1. 审核目标

确保 case 可以 **安全进入未来 live metadata validation**，且：

- 不是 placeholder / 离线标题样例误标 ready
- 字段完备、日期窗合理、路由与 registry 一致
- **不**在本阶段下载 PDF、不请求 CNINFO（审核为人工站内核对或既有证据）

---

## 2. known-document 审核项

审核人逐项勾选（全部通过方可改 `case_status: ready`）：

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | `company_code` 是否真实 | 可在 identity mapping / 交易所名录核对 |
| 2 | `company_name` 是否与 `company_code` 对应 | 与 mapping 或站内简称一致 |
| 3 | `title_pattern` 是否足够具体 | 非单独「公告/报告」；能区分同类公告 |
| 4 | `date_start` / `date_end` 是否合理 | 窄窗（通常 3–7 天）包住已知披露日 |
| 5 | `expected_document_type` 是否属于 b_document enum | 见 `schemas/b_class/b_document.schema.json` |
| 6 | `expected_route_to` 是否存在于 B registry | 见 `cninfo_b_class_source_registry_draft.yaml` |
| 7 | `source_id` 是否存在于 B registry | 与 `expected_route_to` 一致或合理 |
| 8 | `expected_pdf_url_available` 是否合理 | 全文公告一般为 `true`；摘要类应为 general + `announcement` |
| 9 | `case_status` 是否仅在审核通过后改为 `ready` | 草稿阶段保持 `placeholder` |
| 10 | `notes` 是否说明来源 | 含核对方式、审核人、日期；**非**「placeholder」敷衍句 |

**额外：**

- [ ] 该标题 **不应** 误入 `cninfo_periodic_report_pdf`（含摘要/延期披露等）
- [ ] `case_id` 在 YAML 内唯一

---

## 3. category-sample 审核项

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | `source_category` 是否合法 | 属于 registry 七种 `source_category` 之一 |
| 2 | `title_pattern` 是否能代表类别 | 可略宽于 known-document，但仍可区分 |
| 3 | `date window` 是否不过宽 | 建议 ≤7 天；说明抽样公司池 |
| 4 | `expected_min_results` 是否现实 | guard case 可为 0；常规模块 ≥1 |
| 5 | `expected_document_types` 是否合法 | 均在 b_document enum 内 |
| 6 | `false_positive_guard_patterns` 是否合理 | periodic guard case **必须**填写 |
| 7 | `source_id` 在 B registry | 已注册 |
| 8 | `notes` 说明抽样口径 | 非 placeholder 敷衍 |

---

## 4. 运行 selector 前检查

每次将 case 改为 `ready` 并 merge 进 YAML 后，**必须先**运行：

```bash
python lab/select_cninfo_b_class_retrieval_ready_cases.py \
  --known-cases fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml \
  --category-cases fixtures/b_class/retrieval_validation/category_sample_cases.yaml \
  --output-csv outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv \
  --output-md outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md
```

**通过标准：**

| 指标 | 要求 |
|------|------|
| `invalid_ready` | **= 0** |
| `ready` | **> 0**（至少新增 1 条 ready） |
| `result` | 非 `FAIL` |

可选严格模式（CI / 预检）：

```bash
python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict
```

**禁止：** selector 通过后 **直接** 运行 live retrieval；须等 `validate_cninfo_b_class_corpus_retrieval.py` 实现与批准。

---

## 5. 质量边界

| 陈述 | 是否成立 |
|------|----------|
| ready case 可尝试 live **metadata** validation | ✅ |
| ready 代表一定能检索成功 | ❌ |
| ready 代表 PDF 已下载 | ❌ |
| ready 代表 PDF 已解析 / chunk 已生成 | ❌ |
| ready 可写 verified 或升 testing_stable_sample | ❌ **禁止** |

---

## 6. 审核记录模板（可选）

```text
Case ID:
Reviewer:
Review date:
CNINFO 核对方式: [站内搜索 / 已知公告 ID / 其他]
Checklist: [全部通过 / 退回修改]
Selector run: [日期] invalid_ready=0 ready=N
```

---

## 参考

| 文档 | 路径 |
|------|------|
| Intake template | [cninfo_b_class_ready_case_intake_template.md](cninfo_b_class_ready_case_intake_template.md) |
| Ready case summary | [cninfo_b_class_retrieval_ready_case_summary.md](../outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md) |

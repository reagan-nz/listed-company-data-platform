# CNINFO C-Class Snapshot Conflict Resolution

_生成时间：2026-07-08_

> **性质：** Company Snapshot 冲突消解规则（规划）。配合 [source priority rules](cninfo_c_class_snapshot_source_priority_rules.md)。

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

---

## 1. 冲突类型总览

| 类型 | 示例 | 默认策略 |
|------|------|----------|
| 同字段多来源 | company_name F10 vs 年报 | `latest_valid_source` |
| 时间冲突 | 旧年报 vs 新 F10 | `timestamp_desc_valid_first` |
| 数值冲突 | 注册资本 F10 vs 年报 | `numeric_tolerance_with_preferred_source` |
| 文本冲突 | business_scope 长度/措辞差异 | `longest_valid_text_with_source_preference` |
| 数组冲突 | 高管列表版本差异 | `array_merge_by_key` |
| 质量冲突 | parsed vs needs_review | `manual_review_rule` |

---

## 2. 同字段多来源冲突

### 2.1 company_name / legal_name

| 项 | 规则 |
|----|------|
| **preferred_source** | legal_name: `annual_report`；company_name: `cninfo_f10` |
| **fallback_source** | 互为 fallback |
| **timestamp_rule** | 取 `source_retrieved_at` 最新且 `parse_status=parsed` |
| **manual_review_rule** | 两源均有效但编辑距离 > 30% → `conflict` 标签 + 保留双值 |

### 2.2 business_scope

| 项 | 规则 |
|----|------|
| **preferred_source** | `annual_report` |
| **fallback_source** | `cninfo_f10` business_scope derived |
| **timestamp_rule** | 年报对应最新报告期 |
| **manual_review_rule** | 文本相似度 < 0.6 → 主展示 annual_report，F10 进 `alternates[]` |

### 2.3 industry

| 项 | 规则 |
|----|------|
| **preferred_source** | `annual_report` 行业分类 |
| **fallback_source** | `cninfo_f10` F032V |
| **timestamp_rule** | 年报报告期优先 |
| **manual_review_rule** | 分类体系不一致（证监会 vs 申万）→ 分开展示，不强制合并 |

---

## 3. 时间冲突

### 3.1 旧年报 vs 最新 F10

| 场景 | 规则 |
|------|------|
| 静态身份字段（成立日期） | **不变字段** — 取最早可信日期或一致则合并 |
| 动态字段（注册资本、股本） | **timestamp_desc_valid_first** — 新报告期优先 |
| 高管列表 | F10 列表为 **current snapshot**；年报为 **as_of_report** 子对象 |

```json
{
  "executive_profile": {
    "current": [...],
    "as_of_annual_report_2024": [...],
    "conflict_notes": []
  }
}
```

---

## 4. 数值冲突

### 4.1 financial_snapshot

| 字段 | preferred_source | tolerance | manual_review_rule |
|------|------------------|-----------|-------------------|
| registered_capital | annual_report | 相对误差 ≤ 1% 视为一致 | 超差 → conflict + 双值 |
| total_share_capital | cninfo_f10 share_capital | 单位统一为股后比较 | 单位不明 → needs_review |
| holding_ratio | cninfo_f10 | 求和≠100% 不自动修正 | 标注 `ratio_sum_caveat` |

**timestamp_rule：** `report_date` / `report_period` 降序取最新一期。

---

## 5. 文本冲突

### 5.1 business description

| 项 | 规则 |
|----|------|
| **preferred_source** | `annual_report`（更长、更正式） |
| **fallback_source** | `cninfo_f10` company_profile_text |
| **timestamp_rule** | 公告日 / 报告期最新 |
| **manual_review_rule** | `longest_valid_text_with_source_preference`；短文本不覆盖长文本除非 preferred 源更新 |

### 5.2 dividend_plan_text

| 项 | 规则 |
|----|------|
| **preferred_source** | `cninfo_f10` parsed event |
| **fallback_source** | raw `dividend_plan_text` |
| **manual_review_rule** | `dividend_parse_status=needs_review` → 不进主数值槽，仅文本 + queue |

---

## 6. 数组/列表冲突

### 6.1 shareholder_profile

| 项 | 规则 |
|----|------|
| **merge key** | `shareholder_name` + `report_period` + `scope` |
| **rule** | 同报告期同名股东取 holding 较大者（防重复行） |
| **empty_but_valid** | 空数组合法 → 模块 `source_partial` 非 `missing` |

### 6.2 executive_profile

| 项 | 规则 |
|----|------|
| **merge key** | `person_name` + `position` |
| **rule** | F10 当前列表为准；年报职务差异记入 `governance_diff` |

---

## 7. 质量冲突与人工复核

| 条件 | snapshot 行为 |
|------|---------------|
| `parse_status=parsed` | 入主槽 |
| `null_but_valid` | 主槽 null + 灰态说明 |
| `needs_review` | `manual_review_queue`；保留 raw 文本 |
| `observe_only` | 不进主 snapshot；进 `observe_sidecar` |
| `raw_only` | 仅 `document_evidence` 指针 |

**dividend 实证：** 10 条 manual review queue（QA closure 已分类）；002019/002060 open parser patch。

---

## 8. 冲突输出结构（规划）

```json
{
  "field": "registered_capital",
  "resolved_value": "257921.3965",
  "preferred_source": "cninfo_f10",
  "fallback_source": null,
  "conflict_status": "none",
  "alternates": [],
  "timestamp_rule_applied": "latest_valid_source",
  "manual_review_required": false
}
```

---

## 9. Gate

```
snapshot_conflict_resolution_gate = PASS
```

**本轮：** 规则文档化 only；无 builder 执行。

**禁止：** verified · DB 实现

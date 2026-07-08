# CNINFO C-Class Snapshot Quality Model

_生成时间：2026-07-08_

> **性质：** Company Snapshot 质量状态模型（规划）。对齐 [product quality rules](cninfo_c_class_product_quality_rules_draft.md)。

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

---

## 1. 三层质量模型

```
company snapshot_status
  └── module_status (per 18 modules)
        └── field_status (per normalized_field)
              └── source_status (per source_id lineage)
```

---

## 2. Company Snapshot 状态

| 状态 | 含义 | 863 适用 |
|------|------|----------|
| **complete** | 所有主模块 available；无 blocked 源 | 理论值（无 caveat 时） |
| **complete_with_caveat** | 主模块齐全；存在 accepted empty_but_valid / partial / needs_review | **推荐映射**（863 全 complete harvest） |
| **partial** | 关键模块 missing 或 blocked | 当前 863 无 |
| **source_partial** | 某模块因源级 source_partial 导致覆盖不完整 | share_capital · top_float · dividend empty |
| **missing_module** | 模块 not_modeled 或全源不可达 | technology · risk（not_modeled） |

### 863 判定规则

```
IF company_harvest_status = complete
AND harvest_full_gate = PASS_WITH_RESUME
AND EXISTS accepted_caveat (empty_but_valid | needs_review | source_partial)
THEN snapshot_status = complete_with_caveat
```

---

## 3. 模块状态

| 状态 | 含义 | snapshot 行为 |
|------|------|---------------|
| **available** | normalized_core 覆盖 ≥ 主字段阈值 | 主模块展示 |
| **candidate** | 含 review_later 或 formerly candidate 字段 | 侧车 `review_queue` |
| **review_later** | 字段未升格；待 mapper/定义 | 默认不展示 |
| **raw_only** | 仅 raw 证据 | `document_evidence` 指针 |
| **observe_only** | security 等观察源 | `observe_sidecar` |

### 模块状态映射（863 规划）

| 模块 | 规划状态 | 依据 |
|------|----------|------|
| company_identity | available | basic 853/863 + establishment_date 100% |
| business_profile | available | derived 满 fill |
| industry_profile | candidate | index_or_plate_labels review_later |
| financial_snapshot | available | share_capital source_partial caveat |
| technology_profile | missing_module | not_modeled |
| organization_profile | available | contact derived |
| shareholder_profile | available | empty_but_valid 政策已接受 |
| executive_profile | available | 1 empty_but_valid residual |
| governance_profile | candidate | term_* review_later |
| dividend_profile | available | needs_review 事件侧车 |
| capital_action_profile | candidate | change_* review_later |
| risk_profile | observe_only | security 侧轨 |
| event_timeline | available | dividend 日期字段 |
| market_behavior | observe_only | security |
| investor_relation | available | contact |
| document_evidence | available | lineage 全源 |
| data_quality | available | source_status 已升格 |

---

## 4. 字段状态

| 状态 | 含义 | 用户可见 |
|------|------|----------|
| **present** | normalized 有有效值 | 是 |
| **null_but_valid** | 源端显式空；合理缺失 | 可选灰态 |
| **missing** | 源不可达或公司级缺口 | 是（缺失提示） |
| **conflict** | 多源冲突未自动消解 | 是（冲突标签） |
| **needs_review** | 结构化 partial；如 dividend parse | 是（复核标签） |

### 与 current_status 映射

| catalog current_status | field_status 默认 |
|------------------------|-------------------|
| normalized_core | present（有值）或 null_but_valid（空） |
| review_later | missing（主槽）+ review_queue 侧车 |
| raw_only | missing（主槽）+ evidence 指针 |
| observe_only | missing（主槽）+ observe_sidecar |

---

## 5. Source 级质量输入

来自 `outputs/harvest/cninfo_c_class/quality/`：

| 文件 | 用途 |
|------|------|
| company_harvest_status.csv | 公司级 complete / partial |
| source_quality.csv | 源级 endpoint_found / empty_but_valid |
| field_fill_rate.csv | 字段级 fill 监控 |

### source_status 展示映射（继承 product rules）

| retrieval_status | module 影响 |
|------------------|-------------|
| endpoint_found | 正常 |
| empty_but_valid_response | 模块 source_partial；字段 null_but_valid |
| blocked / http_error | 模块 partial |

---

## 6. Rollup 算法（规划）

```python
def rollup_snapshot_status(module_statuses):
    if any(m == "partial" for m in module_statuses.values()):
        return "partial"
    if any(m in {"candidate", "observe_only", "source_partial"} for m in module_statuses.values()):
        return "complete_with_caveat"
    if all(m == "available" for m in primary_modules):
        return "complete"
    return "complete_with_caveat"
```

**primary_modules：** identity, business, industry, financial, shareholder, executive, dividend, investor_relation, document_evidence, data_quality。

---

## 7. 与 QA closure 对齐

| QA 分类 | quality model 处理 |
|---------|-------------------|
| close_as_accepted_source_caveat（54） | 不降级 snapshot；标注 caveat |
| manual_review_queue（10 dividend） | field_status=needs_review |
| open_parser_issue（002019, 002060） | 待 patch；暂 needs_review |

---

## 8. Gate

```
snapshot_quality_model_gate = PASS
```

**禁止：** verified · testing_stable_sample

**本轮：** 模型文档化 only；无 runtime 计算。

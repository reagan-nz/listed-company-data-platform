# CNINFO C-Class Product Quality Rules（Draft）

_生成时间：2026-07-08_

> **性质：** 产品层质量展示规则**初稿**。基于 863 harvest QA、QA queue closure classification、field 复判与 promotion approval。**不写 verified** · **不升级 testing_stable_sample**。

**依据：** `outputs/validation/cninfo_c_class_full_harvest_qa_review.md` · `cninfo_c_class_qa_review_queue_closure_classification.csv` · `cninfo_c_class_review_later_promotion_candidate_approval.csv`

---

## 1. Source Status Display Rules

| 状态 | internal meaning | product meaning | 用户侧解释（中文） | visible to user | blocks company profile |
|------|------------------|-----------------|-------------------|-----------------|------------------------|
| **success** | `endpoint_found` + 有结构化/业务数据 | 源可用且有内容 | 该模块数据已成功获取。 | 是（有数据时） | 否 |
| **empty_but_valid** | HTTP 200 + 空表/空数组；`retrieval_status=empty_but_valid_response` | 源可达但该公司无记录 | 该字段来源可访问，但当前公司无对应记录。 | 是（空态提示） | 否 |
| **source_partial** | 源整体可用但部分公司 empty_but_valid 或字段稀疏 | 模块可用但覆盖不完整 | 该模块可用，但部分公司存在合理为空或源端缺失。 | 是（带 caveat 标签） | 否 |
| **blocked** | 采集被 gate/政策阻断 | 不可用 | 该模块当前无法获取，请稍后再试。 | 是（错误态） | 是（该模块） |
| **http_error** | 非 200 或网络失败 | 不可用 | 数据源暂时无法访问。 | 是（错误态） | 是（该模块） |
| **observe_only** | `cninfo_company_security_profile`；不绑定主 gate | 侧轨观察数据 | 该信息仅供内部观察，不纳入公司主档案。 | 默认**否** | 否 |
| **needs_review** | 结构化 partial；如 dividend `needs_review` 事件 | 已保留证据待复核 | 该字段已保留原始证据，但结构化结果需要人工复核。 | 是（复核标签） | 否 |

**C-class 863 实证：**

- `empty_but_valid`：54 条已 `close_as_accepted_source_caveat`
- `source_partial`：share_capital · top_float
- dividend `needs_review`：10 条在 manual review queue；2 条 open parser patch

---

## 2. Field Status Display Rules

| 状态 | internal meaning | product meaning | 用户侧解释（中文） | visible to user |
|------|------------------|-----------------|-------------------|-----------------|
| **present** | normalized_core 有值 | 正常展示 | （直接展示字段值） | 是 |
| **missing** | 源不可达或公司级缺口（非 empty_but_valid） | 缺失 | 暂无该字段数据。 | 是 |
| **null_but_valid** | 源端 JSON 显式 null；basic source missing | 合理为空 | 源站未披露该字段，属于正常情况。 | 可选（灰态/不展示） |
| **raw_only** | `include_in_normalized_snapshot=no` | 仅证据层 | 该字段仅保留原始证据，不提供结构化展示。 | 否（默认） |
| **review_later** | `include=review`；未升格 | 待确认 | 该字段尚未纳入标准公司档案。 | 否 |
| **normalized_core_candidate** | promotion `approved_as_candidate` | 候选字段 | 该字段已通过内部候选审核，尚未正式发布。 | 否（发布前） |
| **manual_review_queue** | QA closure `manual_review_queue` | 人工复核队列 | 该字段已保留原始证据，但结构化结果需要人工复核。 | 是（标签） |

**863 示例：**

- P0 nullable gap（6 家 F032V 等）：产品层用 **null_but_valid**
- 9 字段 **normalized_core_candidate**：发布前不对用户展示为“正式字段”

---

## 3. Company Status Rules

| 状态 | internal meaning | product meaning | 用户侧解释（中文） | blocks profile |
|------|------------------|-----------------|-------------------|----------------|
| **complete** | `company_harvest_status=complete`；gate PASS | 主模块齐全 | 公司档案主模块已采集完成。 | 否 |
| **complete_with_caveat** | complete + accepted caveat / partial dividend | 完成但有说明 | 公司档案已采集完成，部分模块存在合理空缺或待复核项。 | 否 |
| **partial** | 关键源失败或 blocked | 不完整 | 公司档案部分模块未能获取。 | 是 |
| **excluded_hold** | 26 all6 hold universe | 未纳入本轮 | 该公司暂未纳入当前采集范围。 | N/A |
| **side_track_pending** | BSE legacy / BSE 920 / abnormal | 侧轨待处理 | 该公司属于特殊板块，档案规则尚未确定。 | N/A |

**C-class 863：** 全部 `complete`；产品层应映射为 **complete_with_caveat**（因 54 empty_but_valid + 10 dividend manual queue 已接受）。

---

## 4. 用户侧解释文本（模板）

| 场景 | 中文解释 |
|------|----------|
| empty_but_valid | 该字段来源可访问，但当前公司无对应记录。 |
| source_partial | 该模块可用，但部分公司存在合理为空或源端缺失。 |
| needs_review | 该字段已保留原始证据，但结构化结果需要人工复核。 |
| null_but_valid | 源站未披露该字段，属于正常情况。 |
| observe_only | 该信息仅供内部观察，不纳入公司主档案。 |
| complete_with_caveat | 档案已采集完成，部分字段存在合理空缺或待复核说明。 |
| manual_review_queue | 分红/公告类历史文本存在少量无法自动解析的记录，已保留原文。 |

---

## 5. 不应直接对用户展示的状态

以下仅内部/运维可见，**不对终端用户展示**：

| 类别 | 示例 |
|------|------|
| internal parser status | `dividend_parse_status=partial` · `needs_review` 事件计数 |
| raw endpoint status | `retrieval_status` · `http_status` · `business_code` |
| traceback / exception | harvest runner 异常栈 |
| internal source_id | `cninfo_top_float_shareholders_profile` |
| internal retry_count | partial-fail retry 次数 |
| orgId fallback detail | `org_id` 解析路径 |
| field_confidence hardcoded | `medium` 占位（未定义 per-field 规则前） |
| harvest gate tokens | `PASS_WITH_RESUME` |

---

## 6. 禁止声明

产品层与对外文案**禁止**使用：

| 禁止用语 | 原因 |
|----------|------|
| **verified** | C-class 未进入 verified 阶段 |
| **stable** / testing_stable_sample | 未升级 stable |
| **complete coverage** | 863 存在 empty_but_valid · partial dividend |
| **official truth** / 官方权威 | CNINFO 为第三方源；存在 caveat |
| **100% 准确** | needs_review · manual queue 仍存在 |

**允许：** “采集完成（含说明）” · “候选字段” · “待复核”

---

## 7. Gate

```
product_quality_rules_draft_gate = PASS
```

| 项 | 值 |
|----|------|
| 覆盖 | source · field · company 三层规则 |
| 用户文案 | 已提供中文模板 |
| C-class status | **`HARVEST_COMPLETED_QA_ONGOING`** |
| 本轮 | **draft only**；未写入 registry · 未改 inventory |

---

## 红线确认

- 未请求 CNINFO · 未改 harvest 产物
- 未写 verified · 未升级 testing_stable_sample

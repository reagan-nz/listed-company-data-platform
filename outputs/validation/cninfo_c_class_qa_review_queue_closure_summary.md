# CNINFO C-Class QA Review Queue Closure Summary

_生成时间：2026-07-08_

> 离线 closure classification 落账。**无 CNINFO** · **无 live** · **无 harvest 重跑** · **无 raw/normalized 修改** · **无 verified** · **无 DB/MinIO/RAG**

## 1. Overall Result

**QA queue closure classification completed.**

| 指标 | 值 |
|------|-----|
| Queue total | **72** |
| Closed / accepted caveat count | **60** |
| Manual review queue count | **10** |
| Open follow-up issue count | **2** |

**产物：**

- 规划输入：[cninfo_c_class_qa_review_queue_closure_plan.csv](cninfo_c_class_qa_review_queue_closure_plan.csv)
- 正式落账：[cninfo_c_class_qa_review_queue_closure_classification.csv](cninfo_c_class_qa_review_queue_closure_classification.csv)

---

## 2. Tier Summary

| Tier | flag 数 | closure_action | closure_status | 说明 |
|------|---------|----------------|----------------|------|
| **P0** | **6** | `close_as_accepted_nullable_gap` | `accepted_caveat` | 6 家 / 12 字段缺口；basic source null |
| **P1** | **12** | `close_as_manual_review_queue` ×10 · `open_parser_patch_issue` ×2 | `manual_review_queue` ×10 · `open_followup_issue` ×2 | dividend needs_review 事件 |
| **P2** | **54** | `close_as_accepted_source_caveat` | `accepted_caveat` | empty_but_valid / source_partial |

### closure_status 分布

| closure_status | 数量 |
|----------------|------|
| accepted_caveat | **60** |
| manual_review_queue | **10** |
| open_followup_issue | **2** |

### closure_action 分布

| closure_action | 数量 |
|----------------|------|
| close_as_accepted_nullable_gap | **6** |
| close_as_manual_review_queue | **10** |
| open_parser_patch_issue | **2** |
| close_as_accepted_source_caveat | **54** |

---

## 3. Remaining Follow-ups

### Dividend long-tail manual review（10 条）

| company_code | company_name | F007V 摘要 |
|--------------|--------------|------------|
| 000011 | 深物业A | 10送1派1.00元 |
| 000655 | 金岭矿业 | 94和95未分配利润均结转至上市后分配 |
| 000905 | 厦门港务 | 10转增8 股 |
| 002041 | 登海种业 | 10送14转増1股派3.5元(含税) |
| 600702 | 舍得酒业 | 95年度利润滚存至96年度一并分配 |
| 600716 | 凤凰股份 | 95年7月至12月利润全部上交 |
| 600728 | 佳都科技 | 95年度利润只对老股东分配 |
| 600777 | *ST新潮 | 未分配利润滚存96年度合并派发 |
| 600877 | 电科芯片 | 10送3.5元 |
| 603023 | 威帝股份 | 10送5转增15派1.5元(含税) |

### Parser patch later issues（2 条）

| company_code | company_name | F007V | 原因 |
|--------------|--------------|-------|------|
| **002019** | 亿帆医药 | `10派1.5 元（含税）` | 空格含税变体 |
| **002060** | 广东建工 | `10派1.2 元（含税）` | 空格含税变体 |

**本轮未实施 parser patch。**

---

## 4. What This Means

- **no harvest rerun required** — P0 缺口为源端 null；P2 为政策内 empty_but_valid；无 data corruption。
- **no data repair required** — raw/normalized 产物保持不动；`needs_data_repair=false`（72/72）。
- **C-class QA queue is classified** — 72 flags 均已 `current_status=closed` 并分配 `closure_status`。
- **C-class not yet fully completed** — QA queue 已收口，仍有 8 项 open issues（review_later / raw_only / snapshot 等）。
- **next open issue: review_later 31 field reclassification** — open issues plan P1 工作包。

---

## 5. Gate

```
qa_queue_closure_classification_gate = PASS
```

| 项 | 值 |
|----|-----|
| C-class status | **`HARVEST_COMPLETED_QA_ONGOING`** |
| harvest_full_gate | **PASS_WITH_RESUME**（不变） |
| QA conclusion | **PASS_WITH_CAVEAT**（不变） |

**禁止：** verified · testing_stable_sample

---

## 红线确认

- 未请求 CNINFO · 未重跑 live harvest
- 未修改 raw / normalized 数据
- 未 YAML backfill · 未入库 / MinIO / RAG
- 未写 verified · 未升级 testing_stable_sample

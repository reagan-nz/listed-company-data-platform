# CNINFO D 类 Phase 1 Schema Freeze 摘要

_生成时间：2026-07-09_

> **性质：** 离线规划快照；CNINFO 请求 **0**；不 live；不 harvest；不修改 A/B/C-class 输出。

---

## Gate

```text
d_class_phase1_schema_freeze_gate = READY_FOR_APPROVAL
```

**不是 PASS** — 须人工批准后进入 Phase 1 implementation。

```text
d_class_phase1_schema_lint_gate = PASS
```

离线 lint **10/10 PASS**（见 [cninfo_d_class_phase1_schema_lint_summary.md](cninfo_d_class_phase1_schema_lint_summary.md)）。

---

## Counts

| 指标 | 值 |
|------|-----|
| **component count** | **7** |
| **field matrix rows** | **79** |
| **required** | **49** |
| **recommended** | **25** |
| **future** | **3** |
| **removed** | **2** |
| **phase1 fixtures** | **3**（合成示例） |
| **lint checks** | **10/10 PASS** |

### Components

| component | source_id | required fields (payload) |
|-----------|-----------|---------------------------|
| margin_trading | margin_trading | 8 |
| block_trade | block_trade | 7 |
| restricted_shares_unlock | restricted_shares_unlock | 5 |
| disclosure_schedule | disclosure_schedule | 4 |
| equity_pledge | equity_pledge | 5 |
| shareholder_change | shareholder_change | 6 |
| executive_shareholding | executive_shareholding | 5 |

另加 `market_event` 信封 **8** 个 required 字段（+ lineage recommended）。

---

## Deliverables

| 交付物 | 路径 |
|--------|------|
| Schema freeze review | [cninfo_d_class_phase1_schema_freeze_review.md](../../plans/cninfo_d_class_phase1_schema_freeze_review.md) |
| Field decision matrix | [cninfo_d_class_phase1_field_decision_matrix.csv](cninfo_d_class_phase1_field_decision_matrix.csv) |
| Event object schema | [cninfo_d_class_event_object_schema.md](../../plans/cninfo_d_class_event_object_schema.md) |
| Fixtures | [fixtures/d_class/phase1/](../../fixtures/d_class/phase1/) |
| Lint script | [lab/lint_cninfo_d_class_phase1_schema.py](../../lab/lint_cninfo_d_class_phase1_schema.py) |
| Lint summary | [cninfo_d_class_phase1_schema_lint_summary.md](cninfo_d_class_phase1_schema_lint_summary.md) |

---

## Risk List

| # | 风险 | 级别 | Phase 1 处理 |
|---|------|------|--------------|
| 1 | block_trade 无 buyer/seller 明细 endpoint | high | 标 **future**；汇总字段仍 required |
| 2 | margin_trading F00xN 单位语义未 fully freeze | medium | 保留 raw_record_json；quality_status=caveat 可用 |
| 3 | equity_pledge pledge_status 映射不确定 | high | 标 **future** |
| 4 | executive_shareholding varyType / 职位字段分散 | medium | position **recommended** |
| 5 | disclosure_schedule change_history 结构 | medium | **recommended** JSON array |
| 6 | restricted_shares_unlock tradable_amount (F008N) | medium | **recommended** |
| 7 | 仅 3/7 组件有 phase1 fixture | low | 其余 4 组件靠 matrix + registry 覆盖；扩 fixture 为下一离线任务 |

---

## Future Fields（3）

| field | component | 原因 |
|-------|-----------|------|
| buyer | block_trade | Phase 2 statistics endpoint 无买卖双方 |
| seller | block_trade | 同上 |
| pledge_status | equity_pledge | 状态规范化未 freeze |

---

## No Live Execution

- **CNINFO calls = 0**
- **no live / harvest / PDF / DB / MinIO / RAG**
- **no verified / testing_stable_sample upgrade**
- **C-class status unchanged:** `SNAPSHOT_GENERATED_QA_REVIEW`
- **A/B/C-class outputs untouched**

---

## Recommended Next Task

人工 review schema freeze → 批准后：扩余下 4 组件 phase1 fixtures + harvest architecture dry-run 规划。仍不 live。

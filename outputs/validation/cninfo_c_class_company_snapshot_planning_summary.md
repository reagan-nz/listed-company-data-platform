# CNINFO C-Class Company Snapshot Planning Summary

_生成时间：2026-07-08_

> 离线 snapshot architecture planning。**无 CNINFO** · **无 harvest** · **无 DB/API 实现**

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

## 1. 当前 C-class 数据资产情况

| 项 | 值 |
|----|-----|
| harvest companies | **863** |
| company_harvest_status | **complete**（863/863） |
| normalized_core fields | **74** |
| review_later | **19** |
| raw_only | **13** |
| observe_only | **14** |
| source-level normalized 产物 | basic · contact · business · industry · executive · share_capital · shareholders · dividend · security(observe) |
| quality 产物 | field_fill_rate · source_quality · company_harvest_status |

## 2. Snapshot 一级模块数量

**18** 个一级模块（company object 视角，不按 source 分类）：

1. `company_identity` — catalog 映射 **12** 行
2. `securities_profile` — catalog 映射 **10** 行
3. `business_profile` — catalog 映射 **6** 行
4. `industry_profile` — catalog 映射 **4** 行
5. `financial_snapshot` — catalog 映射 **7** 行
6. `technology_profile` — catalog 映射 **0** 行
7. `organization_profile` — catalog 映射 **0** 行
8. `shareholder_profile` — catalog 映射 **15** 行
9. `executive_profile` — catalog 映射 **8** 行
10. `governance_profile` — catalog 映射 **5** 行
11. `dividend_profile` — catalog 映射 **2** 行
12. `capital_action_profile` — catalog 映射 **4** 行
13. `risk_profile` — catalog 映射 **2** 行
14. `event_timeline` — catalog 映射 **2** 行
15. `market_behavior` — catalog 映射 **5** 行
16. `investor_relation` — catalog 映射 **10** 行
17. `document_evidence` — catalog 映射 **14** 行
18. `data_quality` — catalog 映射 **14** 行

## 3. Normalized field 映射数量

| 指标 | 值 |
|------|-----|
| field mapping 总行数 | **120** |
| 去重 (module, normalized_field) | **71** |
| normalized_core 映射行 | **74** |

## 4. candidate / review / raw / observe 处理策略

| current_status | snapshot 策略 |
|----------------|---------------|
| normalized_core | 进入 snapshot 主展示层 |
| review_later | 保留侧车 `review_queue`；默认不主展示 |
| raw_only | 仅 `document_evidence` 追溯；不进主字段槽 |
| observe_only | `securities_profile` / `market_behavior` 观察侧轨；不进主 gate |

## 5. Source priority 总结

- **identity / shareholder / dividend / capital_action**：`cninfo_f10` 优先（当前唯一已 harvest 源）
- **business / industry / financial / governance**：未来 `annual_report` 优先，`cninfo_f10` 兜底
- **event / risk**：未来 `announcement` 优先
- **document_evidence**：`raw_source` 永远最高优先级

详见 [cninfo_c_class_snapshot_source_priority_rules.md](../../plans/cninfo_c_class_snapshot_source_priority_rules.md)。

## 6. Conflict resolution 总结

- 同字段多源：`latest_valid_source` + 模块级 preferred_source
- 时间冲突：报告期 / 公告日 `timestamp_desc_valid_first`
- 数值冲突：financial 模块 `numeric_tolerance_with_annual_report_preferred`
- 文本冲突：business 模块 `longest_valid_text_with_source_preference`
- 人工复核：dividend `needs_review` 保留 manual_review_queue

详见 [cninfo_c_class_snapshot_conflict_resolution.md](../../plans/cninfo_c_class_snapshot_conflict_resolution.md)。

## 7. 当前不实现

- database（PostgreSQL）
- API
- frontend
- RAG
- MinIO
- registry backfill
- harvest rerun

## Gate

```
company_snapshot_planning_gate = PASS
```

## 推荐下一步

1. **snapshot builder prototype**（离线只读 normalized 聚合 PoC）
2. **security observe 决策**
3. **BSE/abnormal 侧轨文档化**

## 红线确认

- 未请求 CNINFO · 未重跑 harvest
- raw / normalized / field_inventory **未修改**
- 未写 verified · 未升级 testing_stable_sample

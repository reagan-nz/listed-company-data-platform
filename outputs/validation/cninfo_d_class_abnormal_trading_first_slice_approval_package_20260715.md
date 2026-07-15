# CNINFO D 类 abnormal_trading First-Slice — Approval Package

_生成时间：2026-07-15 09:02:09 UTC_

> **性质：** Era D 离线 first-slice package · **CNINFO calls = 0** · **无 live** · **无 commit** · **无 push**
>
> **任务 ID：** D-FM-03
>
> **Standing auth：** full-market shareholder / capital · **Level-2 phrase NOT required** · **不** IDLE

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | full-market shareholder / capital |
| level2_phrase_required | **false** |
| offline / S4 dry-run | **authorized** under standing D |
| first-slice live | **NOT APPROVED**（须另批 + controller_execution_allowed） |
| CNINFO calls (this package) | **0** |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `abnormal_trading` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event`（detail[] → `d_event_party_detail` deferred） |
| endpoint | `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData` |
| query mode | **single_day_paged** · sdate=edate=**2026-07-03** |
| universe | **5** rows · **DAT001–DAT005**（locked） |
| request cap | per-case **≤ 1** · total **≤ 20** · planned **5** |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/abnormal_trading/sample_raw.json` |

---

## 3. Gate Status

```text
d_class_abnormal_trading_next_component_planning_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_abnormal_trading_first_slice_live_gate = NOT_APPROVED
d_class_abnormal_trading_first_slice_runner_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_execution_gate = NOT_APPLICABLE
abnormal_trading_component_approved = standing_scope
```

---

## 4. Universe Lock（DAT001–DAT005）

**正式锁定：** [cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv](cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv)

| case_id | company_code | company_name | market | expected_behavior |
|---------|--------------|--------------|--------|-------------------|
| DAT001 | 000004 | 国华退 | szse_main | captured_normal_or_needs_review |
| DAT002 | 000895 | 双汇发展 | szse_main | captured_normal_or_empty_but_valid |
| DAT003 | 600000 | 浦发银行 | sse_main | captured_normal_or_empty_but_valid |
| DAT004 | 002415 | 海康威视 | szse_main | captured_normal_or_empty_but_valid |
| DAT005 | 601988 | 中国银行 | sse_main | empty_but_valid |

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen**

---

## 5. Artifacts

| 项 | 路径 |
|----|------|
| planning | [plans/cninfo_d_class_abnormal_trading_next_component_planning_20260715.md](../../plans/cninfo_d_class_abnormal_trading_next_component_planning_20260715.md) |
| matrix | [cninfo_d_class_abnormal_trading_next_component_candidate_matrix_20260715.csv](cninfo_d_class_abnormal_trading_next_component_candidate_matrix_20260715.csv) |
| recommendation | [cninfo_d_class_abnormal_trading_next_component_recommendation_20260715.md](cninfo_d_class_abnormal_trading_next_component_recommendation_20260715.md) |
| VR | [cninfo_d_class_abnormal_trading_validation_rules_20260715.md](cninfo_d_class_abnormal_trading_validation_rules_20260715.md) |
| sample prep | [cninfo_d_class_abnormal_trading_sample_prep_20260715.md](cninfo_d_class_abnormal_trading_sample_prep_20260715.md) |
| command draft | [cninfo_d_class_abnormal_trading_first_slice_command_draft_20260715.md](cninfo_d_class_abnormal_trading_first_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_abnormal_trading_offline_prep_checklist_20260715.csv](cninfo_d_class_abnormal_trading_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/abnormal_trading_first_slice/` |

---

## 6. Red Lines

No CNINFO · No live · No DLC006R reopen · No verified · No commit · No push · No A/B/C touch

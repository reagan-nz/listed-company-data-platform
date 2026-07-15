# CNINFO D 类 shareholder_data First-Slice — Approval Package

_生成时间：2026-07-15 17:52:00 +0800_

> **性质：** Era D 离线 first-slice package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push**
>
> **任务 ID：** D-FM-07
>
> **Standing auth：** full-market shareholder / capital · **Level-2 phrase NOT required** · **不** IDLE

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | full-market shareholder / capital |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--shareholder-data-first-slice` 未实现） |
| first-slice live | **NOT APPROVED**（须另批 + approve flag） |
| CNINFO calls (this package) | **0** |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `shareholder_data` |
| source_layer | `company_metric_periodic` |
| target_logical_table | `d_company_metric_periodic` |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/data` |
| query mode | **rdate_report_period** · rdate=**20260331** |
| universe | **5** rows · **DSD001–DSD005**（locked） |
| request model | prefer **1 shared** rdate · total cap **≤ 5** |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/shareholder_data/sample_raw.json` |
| Tier-1 fixtures | **9** files under `fixtures/d_class/shareholder_data_first_slice/` |

---

## 3. Gate Status

```text
d_class_shareholder_data_next_component_planning_gate = READY_FOR_APPROVAL
d_class_shareholder_data_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED
d_class_shareholder_data_first_slice_runner_gate = NOT_APPROVED
d_class_shareholder_data_first_slice_execution_gate = NOT_APPLICABLE
d_class_shareholder_data_fixture_vr_gate = PASS_OFFLINE
shareholder_data_component_approved = standing_scope
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DSD001–DSD005）

**正式锁定：** [cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv](cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_shareholder_data_first_slice_universe_draft_sketch_20260715.csv](cninfo_d_class_shareholder_data_first_slice_universe_draft_sketch_20260715.csv)

| case_id | company_code | company_name | market | expected_behavior |
|---------|--------------|--------------|--------|-------------------|
| DSD001 | 000001 | 平安银行 | szse_main | captured_normal |
| DSD002 | 000895 | 双汇发展 | szse_main | captured_normal_or_empty_but_valid |
| DSD003 | 600000 | 浦发银行 | sse_main | captured_normal_or_empty_but_valid |
| DSD004 | 002415 | 海康威视 | szse_main | captured_normal_or_empty_but_valid |
| DSD005 | 000004 | 国华退 | szse_main | empty_but_valid |

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen**

---

## 5. Artifacts

| 项 | 路径 |
|----|------|
| planning | [plans/cninfo_d_class_shareholder_data_next_component_planning_20260715.md](../../plans/cninfo_d_class_shareholder_data_next_component_planning_20260715.md) |
| matrix | [cninfo_d_class_shareholder_data_next_component_candidate_matrix_20260715.csv](cninfo_d_class_shareholder_data_next_component_candidate_matrix_20260715.csv) |
| recommendation | [cninfo_d_class_shareholder_data_next_component_recommendation_20260715.md](cninfo_d_class_shareholder_data_next_component_recommendation_20260715.md) |
| VR | [cninfo_d_class_shareholder_data_validation_rules_20260715.md](cninfo_d_class_shareholder_data_validation_rules_20260715.md) |
| sample prep | [cninfo_d_class_shareholder_data_sample_prep_20260715.md](cninfo_d_class_shareholder_data_sample_prep_20260715.md) |
| command draft | [cninfo_d_class_shareholder_data_first_slice_command_draft_20260715.md](cninfo_d_class_shareholder_data_first_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_shareholder_data_offline_prep_checklist_20260715.csv](cninfo_d_class_shareholder_data_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/shareholder_data_first_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_shareholder_data_fixtures.py` |

---

## 6. Red Lines

No CNINFO · No live · No runner implement · No DLC006R reopen · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE

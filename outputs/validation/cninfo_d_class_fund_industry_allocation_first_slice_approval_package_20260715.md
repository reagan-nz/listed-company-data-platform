# CNINFO D 类 fund_industry_allocation First-Slice — Approval Package

_生成时间：2026-07-15 20:09:00 +0800_

> **性质：** Era D 离线 first-slice package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push**
>
> **任务 ID：** D-FM-11
>
> **Standing auth：** full-market shareholder / capital · **Level-2 phrase NOT required** · **不** IDLE

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | full-market shareholder / capital |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--fund-industry-allocation-first-slice` 未实现） |
| first-slice live | **NOT APPROVED**（须另批 + approve flag） |
| CNINFO calls (this package) | **0** |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `fund_industry_allocation` |
| source_layer | `industry_aggregate` |
| target_logical_table | `d_industry_aggregate` |
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` |
| query mode | **default**（无参）· **rdate**（`rdate=YYYYMMDD`） |
| universe | **5** rows · **DFIA001–DFIA005**（locked） |
| request model | prefer **≤3 shared probes** · total cap **≤ 5** |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/fund_industry_allocation/sample_raw.json` |
| Tier-1 fixtures | **7** files under `fixtures/d_class/fund_industry_allocation_first_slice/` |

---

## 3. Gate Status

```text
d_class_fund_industry_allocation_next_component_planning_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_first_slice_runner_gate = NOT_APPROVED
d_class_fund_industry_allocation_first_slice_execution_gate = NOT_APPLICABLE
d_class_fund_industry_allocation_fixture_vr_gate = PASS_OFFLINE
fund_industry_allocation_component_approved = standing_scope
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DFIA001–DFIA005）

**正式锁定：** [cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv](cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_fund_industry_allocation_first_slice_universe_draft_sketch_20260715.csv](cninfo_d_class_fund_industry_allocation_first_slice_universe_draft_sketch_20260715.csv)

| case_id | industry_code | query_mode | anchor_rdate | expected_behavior |
|---------|---------------|------------|--------------|-------------------|
| DFIA001 | C26 | default | （空） | captured_normal_or_empty_but_valid |
| DFIA002 | * | default | （空） | captured_normal |
| DFIA003 | * | rdate | 20260331 | captured_normal |
| DFIA004 | C26 | rdate | 20260331 | captured_normal_or_empty_but_valid |
| DFIA005 | * | rdate | 20251231 | captured_normal_or_empty_but_valid |

> **D-FM-17 lock amend：** 仅 DFIA001 `expected_behavior` → `captured_normal_or_empty_but_valid`（对齐 DFIA004 · 保持 C26/default）。草案 sketch 仍为只读历史。
>
> **D-FM-19 lock amend：** 仅 DFIA005 `expected_behavior` → `captured_normal_or_empty_but_valid`（D-FM-18 探针 found=19 · 空控锚点过期 · 保持 rdate=20251231）。DFIA001–DFIA004 本批未改。草案 sketch 仍为只读历史。

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen** · **no company event/metric schema**

---

## 5. Artifacts

| 项 | 路径 |
|----|------|
| planning | [plans/cninfo_d_class_fund_industry_allocation_next_component_planning_20260715.md](../../plans/cninfo_d_class_fund_industry_allocation_next_component_planning_20260715.md) |
| matrix | [cninfo_d_class_fund_industry_allocation_next_component_candidate_matrix_20260715.csv](cninfo_d_class_fund_industry_allocation_next_component_candidate_matrix_20260715.csv) |
| recommendation | [cninfo_d_class_fund_industry_allocation_next_component_recommendation_20260715.md](cninfo_d_class_fund_industry_allocation_next_component_recommendation_20260715.md) |
| VR | [cninfo_d_class_fund_industry_allocation_validation_rules_20260715.md](cninfo_d_class_fund_industry_allocation_validation_rules_20260715.md) |
| sample prep | [cninfo_d_class_fund_industry_allocation_sample_prep_20260715.md](cninfo_d_class_fund_industry_allocation_sample_prep_20260715.md) |
| command draft | [cninfo_d_class_fund_industry_allocation_first_slice_command_draft_20260715.md](cninfo_d_class_fund_industry_allocation_first_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_fund_industry_allocation_offline_prep_checklist_20260715.csv](cninfo_d_class_fund_industry_allocation_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/fund_industry_allocation_first_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_fund_industry_allocation_fixtures.py` |

---

## 6. Red Lines

No CNINFO · No live · No runner implement · No DLC006R reopen · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE · No company_code schema write

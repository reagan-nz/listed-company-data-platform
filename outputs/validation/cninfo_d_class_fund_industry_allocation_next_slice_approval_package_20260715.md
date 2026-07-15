# CNINFO D 类 fund_industry_allocation Next-Slice — Approval Package

_生成时间：2026-07-15 21:32:00 +0800_

> **性质：** Era D 离线 next-slice approval package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **任务 ID：** D-FM-24
>
> **Standing auth：** full-market shareholder / capital · **Level-2 phrase NOT required** · **不** IDLE
>
> **Prior：** D-FM-23 planning gate `READY_FOR_APPROVAL` · sketch DFIA101–105 · first-slice lock **frozen**

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | full-market shareholder / capital |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--fund-industry-allocation-next-slice` 未实现） |
| next-slice live | **NOT APPROVED**（须另批 + approve flag） |
| CNINFO calls (this package) | **0** |
| first-slice FIA/ES/AT/SD live roots | **未 mutate** |
| ESS H3/H4 | **未探**（禁止） |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `fund_industry_allocation` |
| source_layer | `industry_aggregate` |
| target_logical_table | `d_industry_aggregate` |
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` |
| query mode | **default**（无参）· **rdate**（`rdate=YYYYMMDD`） |
| universe | **5** rows · **DFIA101–DFIA105**（locked） |
| industry anchors | **A / B / C / \***（coarse · live-observed） |
| request model | prefer **≤3 shared probes** · total cap **≤ 5** |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/fund_industry_allocation/sample_raw.json` |
| Tier-1 fixtures | **8** files under `fixtures/d_class/fund_industry_allocation_next_slice/` |
| live evidence cite | D-FM-13 DFIA002/003 samples · D-FM-18 DFIA005 sample（只读 · 不 mutate） |

---

## 3. Gate Status

```text
d_class_fund_industry_allocation_next_slice_scale_planning_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_next_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_next_slice_runner_gate = NOT_APPROVED
d_class_fund_industry_allocation_next_slice_execution_gate = NOT_APPLICABLE
d_class_fund_industry_allocation_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_fund_industry_allocation_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_executive_shareholding_summary_endpoint_probe_gate = FAIL_REVIEW_REQUIRED
fund_industry_allocation_component_approved = standing_scope
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DFIA101–DFIA105）

**正式锁定：** [cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv](cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_fund_industry_allocation_next_slice_universe_draft_sketch_20260715.csv](cninfo_d_class_fund_industry_allocation_next_slice_universe_draft_sketch_20260715.csv)

| case_id | industry_code | query_mode | anchor_rdate | expected_behavior |
|---------|---------------|------------|--------------|-------------------|
| DFIA101 | A | default | （空） | captured_normal_or_empty_but_valid |
| DFIA102 | C | default | （空） | captured_normal_or_empty_but_valid |
| DFIA103 | * | rdate | 20260331 | captured_normal |
| DFIA104 | B | rdate | 20260331 | captured_normal |
| DFIA105 | C | rdate | 20251231 | captured_normal_or_empty_but_valid |

**First-slice freeze（未触碰）：**

```text
first_slice_universe_lock_sha256 = 49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c
```

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen** · **no company event/metric schema** · **no C26 sole found anchor**

---

## 5. Fixtures

| case_id | files | 覆盖 |
|---------|-------|------|
| DFIA101 | `DFIA101_found.json` · `DFIA101_industry_filtered_empty.json` | mixed found/empty |
| DFIA102 | `DFIA102_found.json` · `DFIA102_industry_filtered_empty.json` | mixed found/empty |
| DFIA103 | `DFIA103_found.json` | cross-section captured |
| DFIA104 | `DFIA104_found.json` | coarse B captured |
| DFIA105 | `DFIA105_found.json` · `DFIA105_empty_but_valid_synthetic.json` | mixed found/empty |

数值来自 D-FM-13/18 **只读** live sample（fixture 仍标 `synthetic=true` · `cninfo_called=false`）。

---

## 6. Artifacts

| 项 | 路径 |
|----|------|
| planning（prior） | [plans/cninfo_d_class_fund_industry_allocation_next_slice_scale_planning_20260715.md](../../plans/cninfo_d_class_fund_industry_allocation_next_slice_scale_planning_20260715.md) |
| universe lock | [cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv](cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv) |
| VR | [cninfo_d_class_fund_industry_allocation_next_slice_validation_rules_20260715.md](cninfo_d_class_fund_industry_allocation_next_slice_validation_rules_20260715.md) |
| command draft | [cninfo_d_class_fund_industry_allocation_next_slice_command_draft_20260715.md](cninfo_d_class_fund_industry_allocation_next_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_fund_industry_allocation_next_slice_offline_prep_checklist_20260715.csv](cninfo_d_class_fund_industry_allocation_next_slice_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/fund_industry_allocation_next_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_fund_industry_allocation_next_slice_fixtures.py` |
| evidence | [cninfo_d_class_fund_industry_allocation_dfm24_next_slice_approval_package_20260715.md](cninfo_d_class_fund_industry_allocation_dfm24_next_slice_approval_package_20260715.md) |

---

## 7. Red Lines

No CNINFO · No live · No runner implement · No first-slice mutate · No ESS H3/H4 · No DLC006R reopen · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE · No company_code schema write

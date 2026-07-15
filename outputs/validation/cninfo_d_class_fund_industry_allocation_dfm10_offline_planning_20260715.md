# CNINFO D 类 fund_industry_allocation — D-FM-10 Offline Next-Component Start

_生成时间：2026-07-15 · D-FM-10_

> **性质：** next capital component offline planning start · **CNINFO = 0** · **无 live** · **无 runner** · **不是 verified**

## Scope

在 shareholder_data D-FM-09 shared live-path offline mock 已提交（`0761c90`）、真实 live 仍 `NOT_APPROVED` 且 `controller_execution_allowed=false` 前提下，启动下一资本组件 **`fund_industry_allocation`** 离线规划包（standing full-market shareholder / capital）。

| 项 | 值 |
|----|-----|
| primary | `fund_industry_allocation` |
| planning gate | `d_class_fund_industry_allocation_next_component_planning_gate = READY_FOR_APPROVAL` |
| standing_scope | full-market shareholder / capital · Level-2 **NOT** required |
| universe sketch | DFIA001–DFIA005 · default + rdate 20260331/20251231 · **not locked** |
| runner / live | **not implemented / not run** |

## Artifacts

| 类型 | 路径 |
|------|------|
| planning | `plans/cninfo_d_class_fund_industry_allocation_next_component_planning_20260715.md` |
| matrix | `outputs/validation/cninfo_d_class_fund_industry_allocation_next_component_candidate_matrix_20260715.csv` |
| recommendation | `outputs/validation/cninfo_d_class_fund_industry_allocation_next_component_recommendation_20260715.md` |
| summary | `outputs/validation/cninfo_d_class_fund_industry_allocation_next_component_planning_summary_20260715.md` |
| universe sketch | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_universe_draft_sketch_20260715.csv` |
| checklist stub | `outputs/validation/cninfo_d_class_fund_industry_allocation_offline_prep_checklist_stub_20260715.csv` |
| next step | `outputs/validation/cninfo_d_class_fund_industry_allocation_next_component_next_step_recommendation_20260715.md` |
| offline test | `lab/test_cninfo_d_class_fund_industry_allocation_offline_prep.py` |

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_fund_industry_allocation_offline_prep.py` | **6/6 PASS**（`.venv/bin/python`） |

断言：sample_raw → 3 metrics · schema validate · sketch excludes company-event schema · **无** `requests` / CNINFO。

## Explicit Non-Claims

- 不 claim fund_industry_allocation first-slice approved / locked
- 不实现 runner · 不跑真实 live
- 不推进 shareholder_data / abnormal_trading 真实 live（controller 未允许）
- 不 reopen DLC006R / closed tracks
- 不 touch A/B/C · 不 commit / push（executor）

```text
task_id = D-FM-10
phase = fund_industry_allocation_next_component_offline_planning
ready_for_commit = true
cninfo_calls = 0
live = NOT_APPROVED
allow_list = none_this_round
```

# CNINFO D 类 shareholder_data — D-FM-06 Offline Next-Component Start

_生成时间：2026-07-15 · D-FM-06_

> **性质：** next capital component offline planning start · **CNINFO = 0** · **无 live** · **无 runner** · **不是 verified**

## Scope

在 abnormal_trading D-FM-05 live-path offline mock 已提交、真实 live 仍 `NOT_APPROVED` 且 `controller_execution_allowed=false` 前提下，启动下一资本组件 **`shareholder_data`** 离线规划包（standing full-market shareholder / capital）。

| 项 | 值 |
|----|-----|
| primary | `shareholder_data` |
| planning gate | `d_class_shareholder_data_next_component_planning_gate = READY_FOR_APPROVAL` |
| standing_scope | full-market shareholder / capital · Level-2 **NOT** required |
| universe sketch | DSD001–DSD005 · `rdate=20260331` · **not locked** |
| runner / live | **not implemented / not run** |

## Artifacts

| 类型 | 路径 |
|------|------|
| planning | `plans/cninfo_d_class_shareholder_data_next_component_planning_20260715.md` |
| matrix | `outputs/validation/cninfo_d_class_shareholder_data_next_component_candidate_matrix_20260715.csv` |
| recommendation | `outputs/validation/cninfo_d_class_shareholder_data_next_component_recommendation_20260715.md` |
| summary | `outputs/validation/cninfo_d_class_shareholder_data_next_component_planning_summary_20260715.md` |
| universe sketch | `outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_draft_sketch_20260715.csv` |
| checklist stub | `outputs/validation/cninfo_d_class_shareholder_data_offline_prep_checklist_stub_20260715.csv` |
| next step | `outputs/validation/cninfo_d_class_shareholder_data_next_component_next_step_recommendation_20260715.md` |
| offline test | `lab/test_cninfo_d_class_shareholder_data_offline_prep.py` |

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_shareholder_data_offline_prep.py` | **6/6 PASS**（`.venv/bin/python`） |

断言：sample_raw → 6 metrics · schema validate · sketch excludes 301259/688671 · **无** `requests` / CNINFO。

## Explicit Non-Claims

- 不 claim shareholder_data first-slice approved / locked
- 不实现 runner · 不跑真实 live
- 不推进 abnormal_trading 真实 live（controller 未允许）
- 不 reopen DLC006R / closed tracks
- 不 touch A/B/C · 不 commit / push（executor）

```text
task_id = D-FM-06
phase = shareholder_data_next_component_offline_planning
ready_for_commit = true
cninfo_calls = 0
```

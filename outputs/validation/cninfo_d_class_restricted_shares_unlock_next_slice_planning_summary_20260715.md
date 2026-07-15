# CNINFO D 类 restricted_shares_unlock（ES / 限售解禁）— Next-Slice Planning Summary

_生成时间：2026-07-15 · D-FM-45_

| 项 | 值 |
|----|-----|
| task_id | D-FM-45 |
| phase | `restricted_shares_unlock_next_slice_offline_planning` |
| ES alias | 限售解禁 / equity structure（**非** executive_shareholding） |
| CNINFO | **0** |
| live | **not run** |
| runner | **not implemented** |
| planning gate | `READY_FOR_APPROVAL` |
| readiness rank | ES/RSU **#1** · shareholder_change **#2** · executive_shareholding **#3** |
| RSU first-slice | frozen · closure `PASS_WITH_CAVEAT` 5/5 · all empty_but_valid on `2026-06-08` |
| denser-day cite | `2026-07-03` · multidate rows=9 · sample_raw 结构 cite（tdate≠ denser） |
| sketch | DRU101–DRU105 · shared prefer=1 · **draft_not_locked** |
| EP next-slice | D-FM-44 `PASS_OFFLINE` · **untouched** · live `NOT_APPROVED` |
| FIA/AT/SD first/next dry-run | **untouched** |
| lock | **not locked** |
| verified | **no** |
| production_ready | **no** |
| bare PASS | **no** |
| commit/push | **forbidden**（executor） |

## Key Design Delta vs First-Slice

| 维度 | RSU first-slice (DRU001–005) | RSU next-slice sketch (DRU101–105) |
|------|------------------------------|-------------------------------------|
| anchor_tdate | `2026-06-08`（公司级全空） | **`2026-07-03`**（offline denser cite rows=9） |
| found-path live | **未证明** | mixed · company-level live 仍 `NOT_PROVEN` |
| DRU004-style needs_review | sole mismatch risk | **excluded** |
| CNINFO shape | 多 probe / case | prefer **1** shared day |
| case namespace | DRU001–005 | **DRU101–105** |
| code mix | 300009 + 蓝筹 + 688981 | **300992** 结构 cite + 蓝筹 + empty control |

## Artifacts

- `plans/cninfo_d_class_restricted_shares_unlock_next_slice_planning_20260715.md`
- `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_*`
- `outputs/validation/cninfo_d_class_es_shareholder_change_next_slice_candidate_matrix_20260715.csv`
- `outputs/validation/cninfo_d_class_restricted_shares_unlock_dfm45_next_slice_planning_20260715.md`
- `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_planning_offline.py`

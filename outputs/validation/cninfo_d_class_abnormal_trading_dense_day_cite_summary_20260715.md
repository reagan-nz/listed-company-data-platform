# CNINFO D 类 abnormal_trading — Dense-Day Cite Summary

_生成时间：2026-07-15 · D-FM-29_

| 项 | 值 |
|----|-----|
| task_id | D-FM-29 |
| phase | `abnormal_trading_dense_day_offline_cite` |
| prefer taken | AT denser-day offline cite |
| cited_anchor_tdate | **2026-07-02** |
| cite strength | offline multidate `observed_total_rows=173` |
| cite gate | `READY_FOR_APPROVAL` |
| at_dense_day_status | `OFFLINE_PROVISIONAL_CITE_2026_07_02` |
| universe lock | **draft_not_locked** |
| CNINFO | **0** |
| live / runner | **none** |

## Before → After

| 维度 | D-FM-28 | D-FM-29 |
|------|---------|---------|
| AT sketch anchor | `PENDING_DENSE_DAY_CITE` | **`2026-07-02`** |
| dense-day status | `blocked_until_dense_day_cite` | `OFFLINE_PROVISIONAL_CITE_2026_07_02` |
| lock | draft_not_locked | draft_not_locked（仍未 lock） |
| live found | not proven | still not proven |

## Artifacts

- `plans/cninfo_d_class_abnormal_trading_dense_day_cite_20260715.md`
- `outputs/validation/cninfo_d_class_abnormal_trading_dense_day_candidate_matrix_20260715.csv`
- `outputs/validation/cninfo_d_class_abnormal_trading_next_slice_universe_draft_sketch_20260715.csv`（updated）
- `outputs/validation/cninfo_d_class_abnormal_trading_dense_day_cite_decision_20260715.md`
- `outputs/validation/cninfo_d_class_abnormal_trading_dense_day_next_step_recommendation_20260715.md`
- `outputs/validation/cninfo_d_class_abnormal_trading_dense_day_final_caveat_ledger.csv`
- `outputs/validation/cninfo_d_class_abnormal_trading_dfm29_dense_day_cite_offline_20260715.md`
- `lab/test_cninfo_d_class_abnormal_trading_dense_day_cite_offline.py`

# CNINFO D 类 AT/SD — Next-Slice Scale Planning Summary

_生成时间：2026-07-15 · D-FM-28_

| 项 | 值 |
|----|-----|
| task_id | D-FM-28 |
| phase | `at_sd_next_slice_scale_offline_planning` |
| CNINFO | **0** |
| live | **not run** |
| runner | **not implemented** |
| planning gate | `READY_FOR_APPROVAL` |
| AT first-slice | frozen · execution `PASS_WITH_CAVEAT` 4/5 |
| SD first-slice | frozen · execution `PASS_WITH_CAVEAT` 5/5 |
| FIA next-slice | closed D-FM-27 · **untouched** |
| AT sketch | DAT101–DAT105 · `PENDING_DENSE_DAY_CITE` · shared prefer=1 |
| SD sketch | DSD101–DSD105 · rdate 20260331/20251231 · shared prefer=2 |
| lock | **not locked** |
| verified | **no** |
| production_ready | **no** |
| bare PASS | **no** |
| commit/push | **forbidden**（executor） |

## Key Design Delta vs First-Slice

| 维度 | AT first-slice (DAT001–005) | AT next-slice sketch (DAT101–105) |
|------|------------------------------|-----------------------------------|
| anchor_tdate | `2026-07-03`（稀疏 · 全空） | **`PENDING_DENSE_DAY_CITE`** |
| found-path live | **未证明** | mixed · lock 前须 denser cite |
| DAT001-style needs_review | sole mismatch | **excluded** |
| CNINFO shape | 5× per-case | prefer **1** shared day |
| case namespace | DAT001–005 | **DAT101–105** |

| 维度 | SD first-slice (DSD001–005) | SD next-slice sketch (DSD101–105) |
|------|------------------------------|-----------------------------------|
| rdate | 仅 `20260331` | `20260331` + `20251231`（mixed） |
| VR-008 | 禁 multi-rdate | next-slice **允许**（first-slice VR 不变） |
| cohort | 固定五码 | 引入 **600519** diversify |
| case namespace | DSD001–005 | **DSD101–105** |

## Artifacts

- `plans/cninfo_d_class_at_sd_next_slice_scale_planning_20260715.md`
- `outputs/validation/cninfo_d_class_at_sd_next_slice_*`
- `outputs/validation/cninfo_d_class_{abnormal_trading,shareholder_data}_next_slice_universe_draft_sketch_20260715.csv`
- `lab/test_cninfo_d_class_at_sd_next_slice_scale_offline.py`

# CNINFO D 类 restricted_shares_unlock（ES / 限售解禁）Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-47_

> **性质：** command draft · runner **已接线** · S4 dry-run **PASS_OFFLINE** · live **未授权** · **CNINFO = 0** · **不是 verified**
>
> Live 命令 **勿执行**，直至 explicit approve + `controller_execution_allowed`。

## S4 dry-run（已实现 · 本回合已执行 · CNINFO=0）

```bash
cd listed_company_data_collector
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --restricted-shares-unlock-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice
```

## Live（草稿 · 门禁未开 · 禁止本回合）

```bash
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --restricted-shares-unlock-next-slice \
  --approve-d-class-restricted-shares-unlock-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice
```

> **禁止** 无另批执行。`live_gate=NOT_APPROVED`。prefer shared CNINFO=1（同日截面 · 离线按 SECCODE 过滤 DRU101–105）。

## Request Model（locked contract）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/liftBan/detail` |
| query mode | `tdate_daily` |
| shared probe | **1** · tdate=`2026-07-03` |
| company filter | 离线按 `SECCODE` 过滤 DRU101–105 |
| total cap | ≤ **5** |
| planned shared | **1** |
| schema | `d_company_event` |
| forbidden sole found anchor | **2026-06-08** |
| denser-day cite | D-FM-45 · multidate rows=9 · **≠** company-level live found |

## Status This Task（D-FM-47）

| 项 | 状态 |
|----|------|
| `--restricted-shares-unlock-next-slice` | **已实现** |
| `--approve-d-class-restricted-shares-unlock-next-slice` | **已接线 / 未授权** |
| S4 dry-run | **PASS_OFFLINE**（5/5 planned_ok · shared=1） |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_extension_gate | **READY_FOR_APPROVAL** |
| live_path_gate | **READY_FOR_APPROVAL** |
| live_gate | **NOT_APPROVED** |
| CNINFO this task | **0** |
| RSU first-slice live root | **frozen · 未 mutate** |
| EP / FIA / AT / SD frozen roots | **frozen · 未 mutate** |

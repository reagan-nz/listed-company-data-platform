# CNINFO D 类 restricted_shares_unlock（ES / 限售解禁）Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-46_

> **性质：** command **草稿 only** · runner **未实现** · live **未授权** · **CNINFO = 0** · **不是 verified**
>
> Live / dry-run 命令 **勿执行**，直至 runner extension + explicit approve + `controller_execution_allowed`。

## S4 dry-run（草稿 · 未实现 · 禁止本回合执行）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --restricted-shares-unlock-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice
```

## Live（草稿 · 门禁未开 · 禁止本回合）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
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

## Status This Task（D-FM-46）

| 项 | 状态 |
|----|------|
| `--restricted-shares-unlock-next-slice` | **未实现**（草稿 flag 名） |
| `--approve-d-class-restricted-shares-unlock-next-slice` | **未接线 / 未授权** |
| S4 dry-run | **blocked_until_runner** |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_gate | **NOT_APPROVED** |
| live_gate | **NOT_APPROVED** |
| CNINFO this task | **0** |
| RSU first-slice live root | **frozen · 未 mutate** |
| EP / FIA / AT / SD frozen roots | **frozen · 未 mutate** |

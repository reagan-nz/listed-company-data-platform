# CNINFO D 类 abnormal_trading Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-30 起草_

> **性质：** runner **未实现** · S4 / live **未授权** · **CNINFO = 0** · **不是 verified**
>
> **勿执行** 下列命令，直至 runner 扩展 + 另批 approve。

## S4 dry-run（draft only · 未实现 · 勿跑）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --abnormal-trading-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_next_slice
```

## Live（draft only · 未实现 · 禁止本回合）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --abnormal-trading-next-slice \
  --approve-d-class-abnormal-trading-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_next_slice
```

> **禁止** 无另批执行。live_gate / runner_gate 均为 `NOT_APPROVED`。

## Request Model（locked contract · offline）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData` |
| query mode | `single_day_paged` |
| shared probe | **1** · sdate=edate=`2026-07-02` · page=1 · rows=30 |
| company filter | 离线按 `secCode` 过滤 DAT101–105 |
| total cap | ≤ **5** |
| planned shared | **1** |
| schema | `d_company_event` · detail[] deferred |
| forbidden anchor | **2026-07-03** 作 sole found |

## Status This Task（D-FM-30）

| 项 | 状态 |
|----|------|
| `--abnormal-trading-next-slice` | **未实现** |
| `--approve-d-class-abnormal-trading-next-slice` | **未实现 / 未授权** |
| S4 dry-run | **blocked_until_runner** |
| bounded live | **NOT_APPROVED** |
| CNINFO this task | **0** |
| AT first-slice live root | **frozen · 未 mutate** |
| SD / FIA closed roots | **frozen · 未 mutate** |

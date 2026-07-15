# CNINFO D 类 abnormal_trading Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-31 更新（D-FM-30 起草）_

> **性质：** runner **已实现** · S4 dry-run **已跑 offline** · live **未授权** · **CNINFO = 0** · **不是 verified**
>
> **勿执行** live 命令，直至另批 approve + `controller_execution_allowed`。

## S4 dry-run（implemented · D-FM-31 已跑 · CNINFO=0）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --abnormal-trading-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_next_slice
```

## Live（draft only · 路径已接线 · 禁止本回合）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --abnormal-trading-next-slice \
  --approve-d-class-abnormal-trading-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_next_slice
```

> **禁止** 无另批执行。`live_gate=NOT_APPROVED`。prefer shared CNINFO=1。

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

## Status This Task（D-FM-31）

| 项 | 状态 |
|----|------|
| `--abnormal-trading-next-slice` | **已实现** |
| `--approve-d-class-abnormal-trading-next-slice` | **已实现 / 未授权 live** |
| S4 dry-run | **PASS_OFFLINE** · planned_ok 5/5 · CNINFO=0 |
| runner_extension_gate | **READY_FOR_APPROVAL** |
| live_path_gate | **READY_FOR_APPROVAL** |
| bounded live | **NOT_APPROVED** |
| CNINFO this task | **0** |
| AT first-slice live root | **frozen · 未 mutate** |
| SD / FIA closed roots | **frozen · 未 mutate** |

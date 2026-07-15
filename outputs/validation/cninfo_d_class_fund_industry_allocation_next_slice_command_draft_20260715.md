# CNINFO D 类 fund_industry_allocation Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-24 起草 · D-FM-25 更新 · D-FM-26 live 更新_

> **性质：** runner **已实现**（D-FM-25）· S4 dry-run **已执行** · bounded live **已执行**（D-FM-26 · CNINFO=3 · 5/5）· **不是 verified**

## S4 dry-run（D-FM-25 · 已跑 · CNINFO=0）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --fund-industry-allocation-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice
```

## Live（D-FM-26 · 已跑 · CNINFO=3 · acceptable 5/5）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --fund-industry-allocation-next-slice \
  --approve-d-class-fund-industry-allocation-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice
```

> **勿无另批重跑。** live_gate 常量仍为 `NOT_APPROVED`（单次任务授权）。

## Request Model（locked contract · offline）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` |
| query modes | `default`（无参）· `rdate`（`rdate=YYYYMMDD`） |
| prefer | **≤3 shared probes**：default · rdate=`20260331` · rdate=`20251231` · 离线按 F001V 过滤 DFIA101–105 |
| total cap | ≤ **5** |
| planned shared | **3** |
| schema | `d_industry_aggregate` only · **no** company_code |
| industry filter | coarse **A / B / C / \*** · **不**以 C26 作唯一 found 锚 |

## Status This Task（D-FM-26）

| 项 | 状态 |
|----|------|
| `--fund-industry-allocation-next-slice` | **已实现**（D-FM-25） |
| `--approve-d-class-fund-industry-allocation-next-slice` | **本任务已用**（单次） |
| S4 dry-run | **PASS_OFFLINE** · planned_ok 5/5 · CNINFO=0 |
| bounded live | **EXECUTED** · acceptable **5/5** · execution_gate=`PASS_WITH_CAVEAT` |
| CNINFO this task | **3** |
| first-slice live root | **frozen · 未 mutate** |

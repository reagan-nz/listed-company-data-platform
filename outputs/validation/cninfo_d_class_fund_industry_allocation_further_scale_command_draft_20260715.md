# CNINFO D 类 fund_industry_allocation Further-Scale — Command Draft（D-FM-39 更新）

_生成时间：2026-07-15 · D-FM-39_

> **性质：** 命令草稿 · **flags 已实现** · **S4 dry-run 已跑** · **live 仍禁** · **CNINFO = 0** · **不是 verified**

## S4 dry-run（已实现 · 本回合已执行 · CNINFO=0）

```bash
cd listed_company_data_collector
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --fund-industry-allocation-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale
```

## Future Live（已接线 · 勿执行 · controller_execution_allowed=false）

```bash
# 须另批 standing approve + controller_execution_allowed · 本回合禁止
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --fund-industry-allocation-further-scale \
  --approve-d-class-fund-industry-allocation-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale
```

## Request Model（locked contract · offline）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` |
| query modes | `default`（无参）· `rdate`（`rdate=YYYYMMDD`） |
| prefer | **≤3 shared probes**：default · rdate=`20260331` · rdate=`20251231` · 离线按 F001V 过滤 DFIA201–205 |
| total cap | ≤ **5** |
| planned shared | **3** |
| schema | `d_industry_aggregate` only · **no** company_code |
| industry filter | coarse **A / B / \*** · **不**以 C26 作唯一 found 锚 |

## Status This Task（D-FM-39）

| 项 | 状态 |
|----|------|
| `--fund-industry-allocation-further-scale` | **已实现** |
| `--approve-d-class-fund-industry-allocation-further-scale` | **已实现**（live 仍须显式批准） |
| S4 dry-run | **PASS_OFFLINE** · planned_ok **5/5** · CNINFO=0 |
| runner_extension_gate | **READY_FOR_APPROVAL** |
| live_path_gate | **READY_FOR_APPROVAL** |
| live_gate | **NOT_APPROVED** · controller_execution_allowed=false |
| CNINFO this task | **0** |
| FIA first/next · AT/SD dry-run | **frozen · 未 mutate** |

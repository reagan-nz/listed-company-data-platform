# CNINFO D 类 fund_industry_allocation Further-Scale — Command Draft

_生成时间：2026-07-15 · D-FM-38_

> **性质：** 命令草稿 only · **flags 未实现** · **无 dry-run** · **无 live** · **CNINFO = 0** · **不是 verified**

## Future S4 dry-run（未实现 · 勿执行）

```bash
cd listed_company_data_collector
# 以下 flags 尚未实现 — 本回合禁止运行
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --fund-industry-allocation-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale
```

## Future Live（未实现 · 勿执行 · controller_execution_allowed=false）

```bash
# 须另批 standing approve + controller_execution_allowed · 本回合禁止
python lab/run_cninfo_d_class_tiny_live_validation.py \
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

## Status This Task（D-FM-38）

| 项 | 状态 |
|----|------|
| `--fund-industry-allocation-further-scale` | **未实现** |
| `--approve-d-class-fund-industry-allocation-further-scale` | **未实现** |
| S4 dry-run | **blocked_until_runner** |
| bounded live | **NOT_APPROVED** · controller_execution_allowed=false |
| CNINFO this task | **0** |
| FIA first/next · AT/SD dry-run | **frozen · 未 mutate** |

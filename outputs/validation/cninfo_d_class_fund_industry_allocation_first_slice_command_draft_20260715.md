# CNINFO D 类 fund_industry_allocation First-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-11_

> **性质：** 命令草案 · **runner 未实现** · **CNINFO = 0** · **真实 live 未授权**

## S4 dry-run（未来 · CNINFO=0 · runner 另批）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --fund-industry-allocation-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice
```

## Live（NOT authorized this task）

```bash
# DO NOT RUN until runner + approve flag + live gate
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --fund-industry-allocation-first-slice \
  --approve-d-class-fund-industry-allocation-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice
```

## Request Model（locked contract）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` |
| query modes | `default`（无参）· `rdate`（`rdate=YYYYMMDD`） |
| prefer | **≤3 shared probes**：default · rdate=`20260331` · rdate=`20251231` · 离线按 F001V 过滤 DFIA |
| total cap | ≤ **5** |
| planned shared | **3**（`SHARED_PROBE`） |
| schema | `d_industry_aggregate` only · **no** company_code |

## Status This Task

| 项 | 状态 |
|----|------|
| `--fund-industry-allocation-first-slice` | **未实现**（blocked_until_runner） |
| S4 dry-run | **blocked_until_runner** |
| live path | **NOT_APPROVED** |
| live | **NOT_APPROVED** |
| CNINFO this task | **0** |

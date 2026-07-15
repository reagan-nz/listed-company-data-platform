# CNINFO D 类 fund_industry_allocation First-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-12 更新_

> **性质：** runner **已实现** · S4 dry-run **已跑** · **CNINFO = 0** · **真实 live 未授权**

## S4 dry-run（已实现 · CNINFO=0）

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
# DO NOT RUN until live gate + human approve
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
| `--fund-industry-allocation-first-slice` | **已实现**（D-FM-12） |
| S4 dry-run | **PASS_OFFLINE** · CNINFO=0 · planned_shared=3 |
| live path | **READY_FOR_APPROVAL**（代码就绪 · 须 approve flag） |
| live | **NOT_APPROVED** |
| CNINFO this task | **0** |

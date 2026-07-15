# CNINFO D 类 fund_industry_allocation Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-24_

> **性质：** **草稿 only** · runner **未实现** · S4 / live **未执行** · **CNINFO = 0** · **不是 verified**

## S4 dry-run（未来 · 本任务不跑）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --fund-industry-allocation-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice
```

## Live（未来 · 须另批 standing approve · prefer CNINFO≤3）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --fund-industry-allocation-next-slice \
  --approve-d-class-fund-industry-allocation-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice
```

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

## Status This Task（D-FM-24）

| 项 | 状态 |
|----|------|
| `--fund-industry-allocation-next-slice` | **未实现** |
| `--approve-d-class-fund-industry-allocation-next-slice` | **未实现** |
| S4 dry-run | **blocked_until_runner** |
| bounded live | **NOT_APPROVED** |
| CNINFO this task | **0** |
| first-slice live root | **frozen · 未 mutate** |

# CNINFO D 类 executive_shareholding Next-Slice — Command Draft

_生成时间：2026-07-16 · D-FM-01 / R19（更新自 D-FM-54 draft）_

> **性质：** command draft · runner **已实现** · S4 dry-run **PASS_OFFLINE** · bounded live **已执行**（R19 standing scope）· **不是 verified**

## S4 dry-run（已执行 · CNINFO=0）

```bash
cd listed_company_data_collector
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --executive-shareholding-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_next_slice
```

## Live（已执行 · R19 standing-scope · CNINFO=1 shared）

```bash
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --executive-shareholding-next-slice \
  --approve-d-class-executive-shareholding-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_next_slice
```

> prefer shared CNINFO=1（同模式截面 · 离线按 SECCODE 过滤 DES101–105）。

## Request Model（locked contract）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/leader/detail` |
| query mode | `timeMark_threeMonth_varyType_b` |
| timeMark | **threeMonth** |
| varyType | **b** |
| shared probe | **1** · timeMark=`threeMonth` · varyType=`b` |
| company filter | 离线按 `SECCODE` 过滤 DES101–105 |
| total cap | ≤ **5** |
| planned shared | **1** |
| schema | `d_company_event` |
| forbidden sole found anchor | **timeMark=oneMonth** + **varyType=b** |
| ESS H3/H4 | **禁止**（detail ≠ summary reopen） |

## Status This Task（D-FM-01 / R19）

| 项 | 状态 |
|----|------|
| `--executive-shareholding-next-slice` | **已实现** |
| `--approve-d-class-executive-shareholding-next-slice` | **已接线** |
| S4 dry-run | **PASS_OFFLINE** · CNINFO=0 |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_extension_gate | **READY_FOR_APPROVAL** |
| execution_gate | **PASS_WITH_CAVEAT**（5/5 acceptable） |
| live executed | **true** · CNINFO=1 |
| ESH first-slice live / dry-run root | **frozen · 未 mutate** |
| SC / RSU / EP / FIA / AT / SD frozen roots | **frozen · 未 mutate** |
| ESS H3/H4 | **paused · 未探** |

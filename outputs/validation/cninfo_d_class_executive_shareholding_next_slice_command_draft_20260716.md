# CNINFO D 类 executive_shareholding Next-Slice — Command Draft

_生成时间：2026-07-16 · D-FM-54_

> **性质：** command draft · runner **未实现** · S4 dry-run **blocked_until_runner** · live **未授权** · **CNINFO = 0** · **不是 verified**
>
> Live / dry-run 命令 **勿执行**，直至 runner 接线 + explicit approve + `controller_execution_allowed`。

## S4 dry-run（草稿 · 本回合未实现 · 禁止执行）

```bash
cd listed_company_data_collector
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --executive-shareholding-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_next_slice
```

## Live（草稿 · 门禁未开 · 禁止本回合）

```bash
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --executive-shareholding-next-slice \
  --approve-d-class-executive-shareholding-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_next_slice
```

> **禁止** 无另批执行。`live_gate=NOT_APPROVED`。prefer shared CNINFO=1（同模式截面 · 离线按 SECCODE 过滤 DES101–105）。

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
| denser-mode cite | D-FM-53 · priority2 rows=1862 · **≠** company-level live found |
| ESS H3/H4 | **禁止**（detail ≠ summary reopen） |

## Status This Task（D-FM-54）

| 项 | 状态 |
|----|------|
| `--executive-shareholding-next-slice` | **未实现** |
| `--approve-d-class-executive-shareholding-next-slice` | **未接线** |
| S4 dry-run | **blocked_until_runner** |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_extension_gate | **NOT_APPROVED** |
| live_gate | **NOT_APPROVED**（未翻转） |
| CNINFO this task | **0** |
| ESH first-slice live / dry-run root | **frozen · 未 mutate** |
| SC / RSU / EP / FIA / AT / SD frozen roots | **frozen · 未 mutate** |
| ESS H3/H4 | **paused · 未探** |

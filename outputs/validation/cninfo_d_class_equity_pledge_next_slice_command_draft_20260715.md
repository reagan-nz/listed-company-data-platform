# CNINFO D 类 equity_pledge Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-42_

> **性质：** runner **未实现** · S4 dry-run **未跑** · live **未授权** · **CNINFO = 0** · **不是 verified**
>
> **勿执行** 下列命令，直至另批 runner 实现 +（live 时）explicit approve + `controller_execution_allowed`。

## S4 dry-run（draft only · 未实现 · 禁止本回合执行）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --equity-pledge-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_equity_pledge_next_slice
```

> **D-FM-42：** `--equity-pledge-next-slice` **尚未接线**。上列为未来形状草案。

## Live（draft only · 路径未接线 · 禁止本回合）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --equity-pledge-next-slice \
  --approve-d-class-equity-pledge-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_equity_pledge_next_slice
```

> **禁止** 无另批执行。`live_gate=NOT_APPROVED`。prefer shared CNINFO=1（同日截面 · 离线按 SECCODE 过滤 DEP101–105）。

## Request Model（locked contract · offline）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/equityPledge/list` |
| query mode | `tdate_daily` |
| shared probe | **1** · tdate=`2026-07-02` |
| company filter | 离线按 `SECCODE` 过滤 DEP101–105 |
| total cap | ≤ **5** |
| planned shared | **1** |
| schema | `d_company_event` |
| forbidden anchor | **2026-07-03** 作 sole found |

## Status This Task（D-FM-42）

| 项 | 状态 |
|----|------|
| `--equity-pledge-next-slice` | **未实现** |
| `--approve-d-class-equity-pledge-next-slice` | **未实现 / 未授权 live** |
| S4 dry-run | **blocked_until_runner** |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_gate | **NOT_APPROVED** |
| live_gate | **NOT_APPROVED** |
| CNINFO this task | **0** |
| EP first-slice live root | **frozen · 未 mutate** |
| FIA / AT / SD frozen roots | **frozen · 未 mutate** |

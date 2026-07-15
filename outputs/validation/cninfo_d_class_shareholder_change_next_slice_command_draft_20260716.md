# CNINFO D 类 shareholder_change Next-Slice — Command Draft

_生成时间：2026-07-16 · D-FM-50_

> **性质：** command draft · runner **未实现** · live **未授权** · **CNINFO = 0** · **不是 verified**
>
> Live / dry-run 命令 **勿执行**，直至 runner 接线 + explicit approve + `controller_execution_allowed`。

## S4 dry-run（草稿 · 未实现 · 禁止本回合）

```bash
cd listed_company_data_collector
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --shareholder-change-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_next_slice
```

## Live（草稿 · 门禁未开 · 禁止本回合）

```bash
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --shareholder-change-next-slice \
  --approve-d-class-shareholder-change-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_next_slice
```

> **禁止** 无另批执行。`live_gate=NOT_APPROVED` · `runner_gate=NOT_APPROVED`。prefer shared CNINFO=1（同日同模式截面 · 离线按 SECCODE 过滤 DSC101–105）。

## Request Model（locked contract）

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| query mode | `type_desc_tdate_daily` |
| query type | **desc** |
| shared probe | **1** · type=`desc` · tdate=`2026-07-03` |
| company filter | 离线按 `SECCODE` 过滤 DSC101–105 |
| total cap | ≤ **5** |
| planned shared | **1** |
| schema | `d_company_event` |
| forbidden sole found anchor | **type=inc** + **2026-07-03** |
| denser-mode cite | D-FM-49 · priority2 rows=16 · **≠** company-level live found |

## Status This Task（D-FM-50）

| 项 | 状态 |
|----|------|
| `--shareholder-change-next-slice` | **未实现** |
| `--approve-d-class-shareholder-change-next-slice` | **未接线** |
| S4 dry-run | **blocked_until_runner** |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_gate | **NOT_APPROVED** |
| live_gate | **NOT_APPROVED** |
| CNINFO this task | **0** |
| SC first-slice live / dry-run root | **frozen · 未 mutate** |
| RSU / EP / FIA / AT / SD frozen roots | **frozen · 未 mutate** |

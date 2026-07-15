# CNINFO D 类 shareholder_data Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-34 更新（D-FM-32 起草 · D-FM-33 S4）_

> **性质：** 命令草稿 · S4 dry-run **已实现并 offline closed** · **勿执行** live · **CNINFO=0 本包**
>
> **勿执行** live 命令，直至另批 approve + `controller_execution_allowed`。
>
> **勿重跑** dry-run 覆盖 frozen SD next-slice dry-run 根（D-FM-34 freeze）。

## S4 dry-run（implemented · D-FM-33 已跑 · D-FM-34 frozen · CNINFO=0）

```bash
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --shareholder-data-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_next_slice
```

> **D-FM-34：** 上述命令 **不要** 再对正式根执行；产物已 sha256 freeze。

## Bounded live（draft · NOT APPROVED · do not run）

```bash
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --shareholder-data-next-slice \
  --approve-d-class-shareholder-data-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_next_slice
```

> **禁止** 无另批执行。`live_gate=NOT_APPROVED`。prefer shared CNINFO≈2（rdate `20260331` + `20251231`）。

## Request Model

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/data` |
| query mode | `rdate_report_period` |
| shared probes | prefer **2** · `rdate=20260331` · `rdate=20251231` |
| company filter | 离线按 `SECCODE` 过滤 DSD101–105 |
| per-case budget | ≤ 1 |
| total cap | ≤ 5 |
| success | ≥3/5 acceptable → `PASS_WITH_CAVEAT` |

## Status This Task（D-FM-34）

| 项 | 状态 |
|----|------|
| `--shareholder-data-next-slice` | **已实现**（D-FM-33） |
| `--approve-d-class-shareholder-data-next-slice` | **已实现 / 未授权 live** |
| S4 dry-run | **PASS_OFFLINE** · planned_ok 5/5 · shared=2 · CNINFO=0 |
| S4 dry-run closure | **PASS_OFFLINE**（D-FM-34 · freeze + caveat） |
| universe lock | **locked** · DSD101–105 · frozen |
| dry-run root | **frozen** · 禁止本包重写 |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_extension_gate | **READY_FOR_APPROVAL** |
| live_path_gate | **READY_FOR_APPROVAL** |
| live_gate | **NOT_APPROVED** |
| execution_gate | **NOT_APPLICABLE** |
| AT next-slice live | **未翻转** |
| commit / push | **未执行** |

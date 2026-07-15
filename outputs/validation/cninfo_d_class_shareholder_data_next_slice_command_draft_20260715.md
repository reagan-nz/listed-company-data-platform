# CNINFO D 类 shareholder_data Next-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-32_

> **性质：** 命令草稿 only · **flags 未实现** · **勿执行** live · **CNINFO=0 本包**
>
> **勿执行** live 命令，直至另批 approve + `controller_execution_allowed`。

## S4 dry-run（draft · not implemented）

```bash
.venv/bin/python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --shareholder-data-next-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_next_slice
```

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

## Status This Task（D-FM-32）

| 项 | 状态 |
|----|------|
| `--shareholder-data-next-slice` | **未实现**（draft only） |
| `--approve-d-class-shareholder-data-next-slice` | **未实现 / 未授权 live** |
| universe lock | **locked** · DSD101–105 |
| approval_gate | **STANDING_SCOPE_AUTHORIZED** |
| fixture_vr_gate | **PASS_OFFLINE** |
| runner_gate | **NOT_APPROVED** |
| live_gate | **NOT_APPROVED** |
| AT next-slice live | **未翻转**（本包 honest skip） |

# CNINFO C 类 — Snapshot Exclusion Prep · Builder Command Draft

_生成时间：2026-07-15 · Run 12 Wave 1 · **PLAN ONLY** · CNINFO **0**_

> **不执行** · **不写生产 snapshot** · **execute_production_snapshot_rebuild=false** · **no commit/push**

**上级：** [mock rebuild plan](../outputs/validation/cninfo_c_class_snapshot_mock_rebuild_plan_20260714.md) · [Run 11 exclusion reconcile](../outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/dryrun_summary.md)

---

## 1. 目的

将 Run 11 `exclusion_reconcile.csv`（或 exclusion manifest）接入 snapshot **preparation dry-run** 路径，而不修改 / 启用 `build_cninfo_c_class_snapshot_batch.py` 的生产 execute 能力。

本轮采用 **offline adapter**（避免对 batch builder 做跨切面改动）：

| 组件 | 路径 |
|------|------|
| 过滤纯逻辑 | `lab/cninfo_c_class_snapshot_exclusion_filter.py` |
| prep adapter | `lab/run_cninfo_c_class_snapshot_exclusion_prep_adapter_dryrun.py` |
| 单测 | `lab/test_cninfo_c_class_snapshot_exclusion_filter.py` |

---

## 2. 输入

| 项 | 路径 |
|----|------|
| universe | `lab/eval_companies_c_class_fuller_market_slice1_200.yaml` |
| exclusion（Run 11） | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv` |
| exclusion（manifest 备选） | `outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv` |

---

## 3. Adapter 命令（已实现 · 可离线运行）

```bash
python3 lab/run_cninfo_c_class_snapshot_exclusion_prep_adapter_dryrun.py \
  --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
  --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv \
  --output-root outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/
```

**预期：** included=190 · excluded=10 · gate=`PASS_OFFLINE` · CNINFO=0 · snapshot JSON=0

---

## 4. 未来 batch builder 接线草案（注释态 · 不执行）

### 4.1 Option A — 原始 universe + `--exclusion-csv`（待 batch 接线）

```bash
# PLAN ONLY — 须另批 c_class_erad_snapshot_rebuild_dryrun_gate
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --sample-file lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
#   --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun/ \
#   --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv
```

### 4.2 Option B — 适配器已过滤 universe（当前可用 · 无 batch 接线依赖）

```bash
# PLAN ONLY
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --sample-file outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml \
#   --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun/
```

---

## 5. 安全边界

| 禁止项 | 状态 |
|--------|------|
| `execute_production_snapshot_rebuild=true` | **禁止** |
| batch builder `--execute` / `approve-*` | **禁止** |
| 写入 `full/` · phase3 · phase35 生产 snapshot 根 | **禁止** |
| CNINFO / PDF / OCR / DB / MinIO / RAG | **禁止** |

`refuse_exclusion_with_execute`：`--exclusion-csv` 与 execute 模式互斥（硬失败，无静默）。

---

## 6. 产出位置

| 产物 | 路径 |
|------|------|
| adapter 摘要 | `outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/prep_adapter_summary.md` |
| filtered universe | `.../filtered_universe_included.yaml` |
| filter report | `.../exclusion_filter_report.csv` |
| command draft（副本） | `.../builder_command_draft.sh` |
| 证据包 | `outputs/validation/cninfo_c_class_snapshot_exclusion_prep_adapter_20260715.md` |

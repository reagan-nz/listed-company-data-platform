# CNINFO C 类 — Snapshot Mock-Root Dry-Run Rebuild Plan

_生成时间：2026-07-14 · Task **C-GEN-20260714-06** · **plan only** · CNINFO **0**_

> **不执行** · **不写生产 snapshot 根** · **不复制 prod 树** · **no commit/push**

**上级：** [progression package](cninfo_c_class_snapshot_progression_package_20260714.md) · [readiness plan](../../plans/cninfo_c_class_erad_snapshot_rebuild_readiness_plan.md) · [command draft](../../plans/cninfo_c_class_erad_resume_stability_command_draft.md) §4

---

## 1. 目的与边界

| 项 | 值 |
|----|-----|
| 目的 | 在 **mock 隔离根** 下验证 snapshot builder dry-run 路径 · exclusion manifest · cleanup guard — **不**改变生产产物 |
| AQ-C-SNAP | 解锁 preparation；本文件为 **设计计划** |
| `rebuild_candidate` | 全 cohort **no** → mock dry-run 为 **可选就绪路径**，非 production rebuild 前置条件 |
| `execute_production_snapshot_rebuild` | **false**（保持不变） |

---

## 2. Mock 根路径约定

所有 dry-run / 未来测试写入 **必须** 使用 `_mock_erad_rebuild_*` 前缀（protected roots [C-ROOT-MOCK](cninfo_c_class_erad_protected_output_roots.csv)）：

| mock_root_id | 路径 | 用途 |
|--------------|------|------|
| MOCK-491 | `outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_phase35_491_dryrun/` | Phase 3.5 expanded 491 cohort dry-run |
| MOCK-863 | `outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_863_primary_dryrun/` | 863 primary full cohort dry-run |
| MOCK-SLICE1 | `outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun/` | fuller-market slice1 200（若单独验证排除逻辑） |
| MOCK-VAL | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/` | dry-run 报告 · manifest · gate 摘要（无 JSON） |

**禁止指向：**

- `outputs/snapshot/cninfo_c_class/full/`（C-ROOT-005）
- `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/`（C-ROOT-004）
- 任意 phase35 success / smoke 生产根

---

## 3. Exclusion manifest（输入）

dry-run universe 构建时 **必须** 联立排除：

| 家族 | 行数 | 来源 |
|------|------|------|
| partial7 | 7 | [exclusion universe CSV](cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv) · DLVR-P04 |
| empty_dividend3 | 3 | 同上 · DLVR-E01–E05 |
| holdout9 | 9 | 同上 · SR-03 · holdout ledger |

合计 **19** 家不得进入「complete snapshot pool」候选；mock manifest 应输出 `excluded_count=19` 与 `included_complete_pool` 对账。

---

## 4. 计划命令草案（注释状态 · 不执行）

### 4.1 Phase 3.5 — 491 expanded（MOCK-491）

```bash
# PLAN ONLY — 须另批 c_class_erad_snapshot_rebuild_dryrun_gate
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --harvest-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
#   --resume-harvest-root outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume \
#   --universe-yaml lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_phase35_491_dryrun/ \
#   --exclusion-csv outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv
```

**预期：** dry-run summary · 0 snapshot JSON · CNINFO **0** · gate 写入 MOCK-VAL 或 mock 根内 `dryrun_summary.md`。

### 4.2 863 primary full（MOCK-863）

```bash
# PLAN ONLY
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --harvest-root outputs/harvest/cninfo_c_class/ \
#   --universe-yaml lab/eval_companies_c_class_harvest_863_non_bse.yaml \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_863_primary_dryrun/ \
#   --exclusion-csv outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv
```

**注意：** harvest 根只读；`--execute` **禁止**直至 `execute_production_snapshot_rebuild=true` 且输出根仍为 `_mock_*`。

### 4.3 Slice1 200 排除逻辑抽检（MOCK-SLICE1 · 可选）

```bash
# PLAN ONLY — 验证 partial7 + empty-dividend3 双层排除
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun/ \
#   --exclusion-csv outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv
```

---

## 5. Guard 与验证清单（执行前 · 本包仅文档化）

| # | 检查项 | 参考 |
|---|--------|------|
| G1 | `assert_safe_erad_audit_write_path` / cleanup guard 允许 `_mock_*` | [cleanup hardening](cninfo_c_class_erad_cleanup_hardening_summary.md) |
| G2 | protected roots CSV 无 mock 路径误分类为 production | [protected_output_roots.csv](cninfo_c_class_erad_protected_output_roots.csv) |
| G3 | holdout 9 未出现在 491 YAML success universe | [readiness plan](../../plans/cninfo_c_class_erad_snapshot_rebuild_readiness_plan.md) §1.2 |
| G4 | dry-run 默认 · 无 `--execute` | `build_cninfo_c_class_snapshot_batch.py` |
| G5 | exclusion CSV 19 行与 dual-layer / holdout ledger 一致 | [progression package](cninfo_c_class_snapshot_progression_package_20260714.md) |
| G6 | CNINFO 调用数 = **0** | 硬性约束 |

---

## 6. 预期产出（未来执行时）

| 产物 | 位置 | 说明 |
|------|------|------|
| dryrun_summary.md | mock 根或 MOCK-VAL | builder 框架输出 |
| exclusion_reconcile.csv | MOCK-VAL | included vs excluded 对账 |
| gate 行 | MOCK-VAL summary | `c_class_erad_snapshot_rebuild_dryrun_gate = PASS_OFFLINE` 或 `FAIL_REVIEW_REQUIRED` |

**本任务不生成上述执行产物**（plan only）。

---

## 7. 磁盘与清理

| 项 | 策略 |
|----|------|
| mock 根 | ephemeral · `delete_ok_tests_only` per C-ROOT-MOCK |
| 禁止 | 复制 ~70M 生产 snapshot 树入 mock 根 |
| 清理 | 仅 `_mock_*` 下允许测试后删除；生产根 **never** |

---

## 8. 与 Option A HOLD 的关系

| 场景 | 建议 |
|------|------|
| 当前（matrix all no） | **Option A HOLD** — 无需执行 §4 命令 |
| 团队要验证 builder 就绪 | **Option B** — 人批 dryrun_gate 后按 §4 在 mock 根执行 |
| 未来 matrix 出现 yes | 仍须 **separate execute approval** · 不得用 mock 结果冒充 production |

---

## 9. Gate（本包）

```
c_class_erad_snapshot_rebuild_dryrun_gate = NOT_EXECUTED（plan only）
mock_rebuild_plan_gate = PLAN_COMPLETE
cninfo_calls = 0
production_roots_touched = false
```

---

## 10. 红线

No CNINFO · no `--execute` · no production root writes · no prod tree copy · no holdout promotion · no commit/push

# C-FM-01 — Snapshot Dry-run 输出根隔离与可复现指纹

_生成时间：2026-07-15 · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-01** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

扩展 C 类 snapshot **标准 dry-run** 写根安全：默认落到隔离 mock 根，拒绝覆盖生产 snapshot quality；补齐隔离 dry-run 可复现指纹工具；硬化相关测试不再污染生产根。

## Capability gain

1. `assert_safe_c_class_snapshot_dryrun_write_root` / `resolve_standard_snapshot_dryrun_output_root`：生产 snapshot 根默认拒绝
2. 标准 `--dry-run` 默认写 `outputs/validation/_mock_snapshot_batch_standard_dryrun_isolated/`
3. `--allow-production-dryrun-scaffold` 显式放行生产 scaffold（人控）
4. `--output-root` 在标准 dry-run 路径生效（与 exclusion / phase35 对齐）
5. `fingerprint_isolated_snapshot_dryrun` + repro check runner：连续两次 dry-run 指纹一致
6. 既有 batch / phase2 / phase3 测试改为隔离写根

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_erad_cleanup_guard.py` | dry-run 写根守卫 · 指纹 |
| `lab/build_cninfo_c_class_snapshot_batch.py` | 默认隔离 · allow 旗标 · fingerprint 输出 |
| `lab/test_cninfo_c_class_snapshot_dryrun_output_root_isolation.py` | **新增** 7 cases |
| `lab/run_cninfo_c_class_isolated_snapshot_dryrun_repro_check.py` | **新增** repro tooling |
| `lab/test_cninfo_c_class_erad_cleanup_hardening.py` | case8 守卫回归 |
| `lab/test_cninfo_c_class_snapshot_batch_runner.py` | bare dry-run 断言隔离 |
| `lab/test_cninfo_c_class_phase2_smoke_188_snapshot_builder_extension.py` | dry-run 用 mock 根 |
| `lab/test_cninfo_c_class_phase3_success_snapshot_approval.py` | dry-run 用 mock 根 |
| `lab/test_cninfo_c_class_snapshot_batch_exclusion_csv.py` | 文档说明更新 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK3 |

## Tests / reports

| 项 | 结果 |
|----|------|
| `test_cninfo_c_class_snapshot_dryrun_output_root_isolation.py` | **7/7 PASS** |
| `test_cninfo_c_class_erad_cleanup_hardening.py` | **8/8 PASS** |
| `test_cninfo_c_class_snapshot_batch_exclusion_csv.py` | **8/8 PASS** |
| `test_cninfo_c_class_snapshot_batch_runner.py` | **6/6 PASS** |
| `test_cninfo_c_class_phase2_smoke_188_snapshot_builder_extension.py` | **9/9 PASS** |
| `test_cninfo_c_class_phase3_success_snapshot_approval.py` | **12/12 PASS** |
| `run_cninfo_c_class_isolated_snapshot_dryrun_repro_check.py` | **reproducible=True · PASS_OFFLINE** |

报告：
- `outputs/validation/cninfo_c_class_snapshot_dryrun_output_root_isolation_test_summary_20260715.md`
- `outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.md`
- `outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json`

## Allow-list

| 允许 | 禁止 |
|------|------|
| 隔离 mock / validation dry-run 写 | 生产 snapshot EXECUTE |
| `--allow-production-dryrun-scaffold`（显式） | CNINFO live |
| offline QA / fingerprint | commit/push（本包未执行） |
| | verified / production_ready 声称 |

## Wall / gate

```
c_fm_01_snapshot_dryrun_output_root_isolation_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
reproducible_isolated_dryrun = true
ready_for_commit = true
```

## Next

- Controller 可 commit 本包
- 生产 snapshot EXECUTE 仍 human-gated
- 后续可选：更大 evidence cohort / lineage 自动化（独立 scope）

# C-FM-05 — Cross-FM Mock Cohort Integrity + Write-guard Battery

_生成时间：2026-07-15T09:31:20Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-05** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-04 之上，补齐 **Cross-FM mock cohort 完整性注册表**、**指纹链只读核验**、**保护根写守卫 battery**、以及 **FM-01..04 gate battery**；产物写入隔离 mock cohort。

## Capability gain

1. `cninfo_c_class_cross_fm_mock_cohort_integrity`：五层完整性 matrix
2. FM-01..04 mock cohort 注册（存在 · `_mock_*` 隔离 · 必要产物 · 非生产分类）
3. 指纹链：dry-run / 863 ledger / lineage 与 gate JSON 对齐（不重跑 dry-run）
4. 写守卫 battery：harvest slice1 / snapshot full / 权威 dual-layer 拒绝；mock 放行
5. protected CSV：MOCK3–7 + AUTH1 注册一致性
6. FM-01..04 PASS_OFFLINE battery（含 FM-04）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_cross_fm_mock_cohort_integrity.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_cross_fm_mock_cohort_integrity.py` | **新增** runner |
| `lab/test_cninfo_c_class_cross_fm_mock_cohort_integrity.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK7 |
| `outputs/validation/_mock_c_fm05_cross_fm_mock_cohort_integrity/` | 隔离完整性产物 |
| `outputs/validation/cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* 完整性矩阵 / 指纹 / registry / battery | 生产 snapshot EXECUTE |
| 只读 FM gate JSON / mock cohort / harvest status / protected CSV | CNINFO live |
| offline QA | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |

## Wall / gate

```
c_fm_05_cross_fm_mock_cohort_integrity_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
ready_for_commit = true
```

## Next

- Controller 可 commit 本包
- 生产 snapshot EXECUTE 仍 human-gated

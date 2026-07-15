# C-FM-13 — Non-seal Cross-FM Mock Cohort Integrity Extension

_生成时间：2026-07-15T12:16:13Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-13** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-12 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力：**Cross-FM mock cohort 注册表扩展（FM-01..05 + FM-12）**、**冻结 MOCK3–14 写隔离**、**harvest/exclusion 一致性交叉指纹**；产物写入隔离 MOCK15（不覆盖 MOCK3–14；不新增 seal 层）。

## Capability gain

1. `default_nonseal_cohort_specs`：在 FM-05 注册表上追加 FM-05 / FM-12
2. `integrity_matrix` / `isolation_matrix` 指纹链只读复算
3. 冻结写隔离扩展至 MOCK14；本任务 MOCK15 放行
4. harvest/exclusion FM-03 一致性层
5. FM-01..05 + FM-12 gate battery（显式跳过 seal FM06–11）
6. protected CSV：MOCK15 注册

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_nonseal_cross_fm_mock_cohort_extension.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_nonseal_cross_fm_mock_cohort_extension.py` | **新增** runner |
| `lab/test_cninfo_c_class_nonseal_cross_fm_mock_cohort_extension.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK15 |
| `outputs/validation/_mock_c_fm13_nonseal_cross_fm_mock_cohort_extension/` | 隔离 extension 产物 |
| `outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_extension_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_extension_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* extension 矩阵 / 指纹 / registry / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12 gate JSON / mock cohort / harvest status / protected CSV | CNINFO live |
| offline QA · 指纹重算（不覆盖 MOCK3–14） | 覆盖 MOCK3–14 |
| | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_13_nonseal_cross_fm_mock_cohort_extension_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
approved_for_snapshot_rebuild = false
cninfo_calls = 0
ready_for_execute = false
hold_recommendation = KEEP_EXECUTE_FALSE
decision_status = AWAITING_HUMAN_EXECUTE_DECISION
idle_not_required_while_awaiting = true
seal_chain_extended = false
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（non-seal mock cohort tooling only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-10 checklist 做 EXECUTE 决策（本包不翻转 approved）

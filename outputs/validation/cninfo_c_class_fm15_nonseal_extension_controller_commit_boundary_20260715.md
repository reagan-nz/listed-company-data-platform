# C-FM-15 — Non-seal Extension Controller Commit-Boundary

_生成时间：2026-07-15T12:27:28Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-15** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-14 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力：**Cross-FM mock cohort 扩展 controller commit-boundary**、**MOCK15/MOCK16 连续性**、**MOCK3–16 写隔离**；产物写入隔离 MOCK17（不覆盖 MOCK3–16；不新增 seal 层）。

## Capability gain

1. FM-01..05 + FM-12 + FM-13 + FM-14 gate battery（显式跳过 seal FM06–11）
2. MOCK15 扩展指纹 + MOCK16 漂移指纹连续性锚点
3. 双层 EXECUTE hold seal（FM13 packet · FM14 drift seal）
4. Controller commit-boundary readiness：ready_for_commit ≠ ready_for_execute
5. 冻结写隔离扩展至 MOCK16；本任务 MOCK17 放行
6. protected CSV：MOCK17 注册

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_nonseal_extension_controller_commit_boundary.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_nonseal_extension_controller_commit_boundary.py` | **新增** runner |
| `lab/test_cninfo_c_class_nonseal_extension_controller_commit_boundary.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK17 |
| `outputs/validation/_mock_c_fm15_nonseal_extension_controller_commit_boundary/` | 隔离 commit-boundary 产物 |
| `outputs/validation/cninfo_c_class_nonseal_extension_controller_commit_boundary_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_nonseal_extension_controller_commit_boundary_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* boundary 矩阵 / 指纹 / battery / readiness packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–14 gate JSON / MOCK15–16 产物 / protected CSV | CNINFO live |
| offline QA · nonseal-chain 只读核验（不覆盖 MOCK3–16） | 覆盖 MOCK3–16 |
| | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_15_nonseal_extension_controller_commit_boundary_gate = PASS_OFFLINE
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

- Controller 可 commit 本包（non-seal controller commit-boundary only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-10 checklist 做 EXECUTE 决策（本包不翻转 approved）

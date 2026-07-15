# C-FM-20 — Non-seal Cross-FM Mock Cohort Third Extension

_生成时间：2026-07-15T13:25:40Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-20** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-19 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力：**Cross-FM mock cohort 三次完整性扩展（FM-01..05 + FM-12..19）**、**MOCK20–21 锚点零漂移**、**MOCK3–21 写隔离 / 保护根扩展**；产物写入隔离 MOCK22（不覆盖 MOCK3–21；不新增 seal / decision-await / commit-boundary 层）。

## Capability gain

1. `default_nonseal_third_extension_cohort_specs`：cohort 11→13（追加 FM18–19）
2. 二次扩展 / 二次漂移矩阵指纹链只读复算
3. MOCK20–21 冻结锚点零漂移连续性
4. 冻结写隔离扩展至 MOCK21；本任务 MOCK22 放行
5. harvest/exclusion FM-03 一致性 + 生产写守卫 battery
6. FM-01..05 + FM-12..19 gate battery（显式跳过 seal FM06–11）
7. protected CSV：MOCK22 注册（output-root protection extension）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_nonseal_cross_fm_mock_cohort_third_extension.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_nonseal_cross_fm_mock_cohort_third_extension.py` | **新增** runner |
| `lab/test_cninfo_c_class_nonseal_cross_fm_mock_cohort_third_extension.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK22 |
| `outputs/validation/_mock_c_fm20_nonseal_cross_fm_mock_cohort_third_extension/` | 隔离 third-extension 产物 |
| `outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_third_extension_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_third_extension_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* extension 矩阵 / 指纹 / registry / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–19 gate JSON / MOCK20–21 产物 / harvest status / protected CSV | CNINFO live |
| offline QA · 指纹重算（不覆盖 MOCK3–21） | 覆盖 MOCK3–21 |
| | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_20_nonseal_cross_fm_mock_cohort_third_extension_gate = PASS_OFFLINE
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

- Controller 可 commit 本包（non-seal third cohort extension only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-17 checklist 做 EXECUTE 决策（本包不翻转 approved）

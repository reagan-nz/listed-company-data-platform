# C-FM-18 — Non-seal Cross-FM Mock Cohort Second Extension

_生成时间：2026-07-15T13:17:23Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-18** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-17 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力：**Cross-FM mock cohort 二次完整性扩展（FM-01..05 + FM-12..17）**、**MOCK15–19 锚点零漂移**、**MOCK3–19 写隔离 / 保护根扩展**；产物写入隔离 MOCK20（不覆盖 MOCK3–19；不新增 seal / decision-await 层）。

## Capability gain

1. `default_nonseal_second_extension_cohort_specs`：cohort 6→11（追加 FM13–17）
2. extension/drift/boundary/attestation/readiness 矩阵指纹链只读复算
3. MOCK15–19 冻结锚点零漂移连续性
4. 冻结写隔离扩展至 MOCK19；本任务 MOCK20 放行
5. harvest/exclusion FM-03 一致性 + 生产写守卫 battery
6. FM-01..05 + FM-12..17 gate battery（显式跳过 seal FM06–11）
7. protected CSV：MOCK20 注册（output-root protection extension）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension.py` | **新增** runner |
| `lab/test_cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK20 |
| `outputs/validation/_mock_c_fm18_nonseal_cross_fm_mock_cohort_second_extension/` | 隔离 second-extension 产物 |
| `outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* extension 矩阵 / 指纹 / registry / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–17 gate JSON / MOCK15–19 产物 / harvest status / protected CSV | CNINFO live |
| offline QA · 指纹重算（不覆盖 MOCK3–19） | 覆盖 MOCK3–19 |
| | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_18_nonseal_cross_fm_mock_cohort_second_extension_gate = PASS_OFFLINE
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

- Controller 可 commit 本包（non-seal second cohort extension only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-17 checklist 做 EXECUTE 决策（本包不翻转 approved）

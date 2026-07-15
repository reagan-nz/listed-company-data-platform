# C-FM-19 — Non-seal Second Extension Post-Commit Drift Recheck

_生成时间：2026-07-15T13:21:18Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-19** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-18 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力：**Cross-FM mock cohort 二次扩展 post-commit 漂移复核**、**MOCK20 冻结产物零漂移**、**MOCK3–20 写隔离**；产物写入隔离 MOCK21（不覆盖 MOCK3–20；不新增 seal / decision-await 层）。

## Capability gain

1. FM-01..05 + FM-12..18 gate battery（显式跳过 seal FM06–11）
2. MOCK20 冻结产物存在性（matrix / fingerprint / registry / battery / packet）
3. 二次扩展指纹零漂移：常量 · gate JSON · 冻结矩阵 · builder 重算对齐
4. 冻结写隔离扩展至 MOCK20；本任务 MOCK21 放行
5. harvest/exclusion FM-03 一致性层
6. EXECUTE hold seal（不得因 AWAITING 而 IDLE）
7. protected CSV：MOCK21 注册

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck.py` | **新增** runner |
| `lab/test_cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK21 |
| `outputs/validation/_mock_c_fm19_nonseal_second_extension_post_commit_drift_recheck/` | 隔离 drift 产物 |
| `outputs/validation/cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* drift 矩阵 / 指纹 / battery / seal packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–18 gate JSON / MOCK20 产物 / harvest / protected CSV | CNINFO live |
| offline QA · 二次扩展指纹重算（不覆盖 MOCK3–20） | 覆盖 MOCK3–20 |
| | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_19_nonseal_second_extension_post_commit_drift_recheck_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
approved_for_snapshot_rebuild = false
cninfo_calls = 0
ready_for_execute = false
hold_recommendation = KEEP_EXECUTE_FALSE
decision_status = AWAITING_HUMAN_EXECUTE_DECISION
idle_not_required_while_awaiting = true
seal_chain_extended = false
drift_detected = false
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（non-seal second-extension post-commit drift recheck only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-17 checklist 做 EXECUTE 决策（本包不翻转 approved）

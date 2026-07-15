# C-FM-26 — Scale Residual Status Triage + Surface Delta Safety

_生成时间：2026-07-15T14:00:58Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-26** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-25 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**failed/partial residual 精确代码台账（9/106）**、**surface−harvest delta 对账（Δ2=dry863 extras）**、**resume-same hold（301212）**、**FM25 连续 + MOCK28 隔离**；产物写入隔离 MOCK28（不覆盖 MOCK3–27）。

## Capability gain

1. FM25 packet/fingerprint/gate 零漂移连续（unique=2249 · 2134/106/9）
2. failed residual 精确台账：9 码 + winning-batch（p35=6 · p3=3）指纹冻结
3. partial residual 精确台账：106 码 + winning-batch 计数指纹冻结
4. surface−harvest delta：2251−2249={000037,000055} · pending 隔离
5. resume-same hold：301212 partial→partial · KEEP_EXECUTE_FALSE · 写拒绝
6. output-root：MOCK3–27 冻结 · MOCK28 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..25 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_residual_status_triage_surface_delta_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_residual_status_triage_surface_delta_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_residual_status_triage_surface_delta_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK28 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm26_scale_residual_status_triage_surface_delta_safety/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_residual_status_triage_surface_delta_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_residual_status_triage_surface_delta_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* residual/surface-delta/resume-same ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–25 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · residual/delta/hold 重算（不覆盖 MOCK3–27） | 覆盖 MOCK3–27 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_26_scale_residual_status_triage_surface_delta_safety_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
approved_for_snapshot_rebuild = false
cninfo_calls = 0
ready_for_execute = false
hold_recommendation = KEEP_EXECUTE_FALSE
decision_status = AWAITING_HUMAN_EXECUTE_DECISION
idle_not_required_while_awaiting = true
seal_chain_extended = false
scale_tier_count = 7
company_coverage_sum = 3314
harvest_unique_union = 2249
union_complete = 2134
union_partial = 106
union_failed = 9
surface_harvest_delta_n = 2
resume_same = 1
surface_unique = 2251
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（residual triage + surface-delta + resume-same only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

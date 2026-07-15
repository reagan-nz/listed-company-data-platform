# C-FM-36 — Scale Failed/Resume Membership + Residual Formula + Hold Identity

_生成时间：2026-07-15T15:20:49Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-36** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-35 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**failed_codes membership freeze（9）**、**resume_same/worse membership freeze（1/0）**、**residual_formula identity lock（117=106+9+2）**、**hold_decision identity lock**、**FM35 连续 + MOCK38 隔离**；产物写入隔离 MOCK38（不覆盖 MOCK3–37）。

## Capability gain

1. FM35 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 1053 · Δ2 · 2134/106/9 · resume 28/1/0 · risk 75/14/12/5）
2. failed_codes_membership_freeze：精确 9 码 · inject/drop/replace 拒绝
3. resume_same_worse_membership_freeze：same={301212} · worse=∅
4. residual_formula_identity_lock：117=106+9+2 · 公式/覆盖变异拒绝
5. hold_decision_identity_lock：KEEP_EXECUTE_FALSE + AWAITING + approved=false + seal=false · 翻转拒绝
6. output-root：MOCK3–37 冻结 · MOCK38 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..35 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK38 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm36_cli_test_tmp/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* failed/resume membership / residual-formula / hold-identity ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–35 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · failed/resume membership / residual-formula / hold-identity 重算（不覆盖 MOCK3–37） | 覆盖 MOCK3–37 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_36_scale_failed_resume_membership_residual_formula_hold_identity_safety_gate = PASS_OFFLINE
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
harvest_additive = 2261
surface_unique = 2251
combined_dryrun_coverage = 1053
union_complete = 2134
union_partial = 106
union_failed = 9
overlap_delta = 12
resume_improved = 28
resume_same = 1
resume_worse = 0
surface_harvest_delta_n = 2
residual_safety_coverage = 117
residual_formula = 106+9+2=117
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（failed/resume membership + residual-formula + hold-identity only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

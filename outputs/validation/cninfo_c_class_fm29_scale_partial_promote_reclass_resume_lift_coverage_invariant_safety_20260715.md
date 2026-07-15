# C-FM-29 — Scale Partial Promote/Reclass + Resume Lift + Coverage Invariant

_生成时间：2026-07-15T14:18:27Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-29** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-28 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**partial promote/reclass denial（106）**、**resume-same hold write-boundary（301212）**、**residual lift denial（9+2）**、**coverage invariant lock（117）**、**FM28 连续 + MOCK31 隔离**；产物写入隔离 MOCK31（不覆盖 MOCK3–30）。

## Capability gain

1. FM28 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 2134/106/9 · Δ2 · cov=117）
2. partial promote/reclass denial：106 码 × promote→complete + 跨带 reclass 显式拒绝
3. resume-same hold write-boundary：301212 × harvest/force_improve/promote 显式拒绝
4. residual lift denial：quarantine(9)+fence(Δ2) lift 显式拒绝
5. coverage invariant lock：9+2+106=117 · mutation_allowed=false
6. output-root：MOCK3–30 冻结 · MOCK31 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..28 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK31 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* promote/reclass/resume/lift/coverage ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–28 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · promote/reclass/lift/coverage 重算（不覆盖 MOCK3–30） | 覆盖 MOCK3–30 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety_gate = PASS_OFFLINE
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
partial_risk_bands = p35_heavy=75;p3_mid=14;p2_mid=12;fu_light=5
residual_safety_coverage = 117
surface_unique = 2251
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（promote/reclass + resume-same + lift + coverage-lock only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

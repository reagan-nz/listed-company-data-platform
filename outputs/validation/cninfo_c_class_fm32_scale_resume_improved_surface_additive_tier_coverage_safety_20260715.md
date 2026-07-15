# C-FM-32 — Scale Resume-Improved + Surface + Additive + Tier Coverage

_生成时间：2026-07-15T14:41:34Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-32** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-31 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**resume-improved write-boundary（28）**、**surface uniqueness cardinality freeze（2251）**、**harvest additive cardinality freeze（2261/2249）**、**scale-tier/coverage-sum invariant lock（7/3314）**、**FM31 连续 + MOCK34 隔离**；产物写入隔离 MOCK34（不覆盖 MOCK3–33）。

## Capability gain

1. FM31 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 2134/106/9 · 28/1/0）
2. resume-improved write-boundary：28 码 × force_regress/rewrite/reclass 显式拒绝
3. surface uniqueness cardinality freeze：2251 · inject/drop/mutation 拒绝
4. harvest additive cardinality freeze：2261/2249 · additive/unique 变异拒绝
5. scale-tier/coverage-sum lock：7/3314 · mutation_allowed=false
6. output-root：MOCK3–33 冻结 · MOCK34 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..31 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK34 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm32_cli_test_tmp/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* resume-improved/surface/additive/tier ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–31 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · resume-improved/surface/additive/tier 重算（不覆盖 MOCK3–33） | 覆盖 MOCK3–33 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_32_scale_resume_improved_surface_additive_tier_coverage_safety_gate = PASS_OFFLINE
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
union_complete = 2134
union_partial = 106
union_failed = 9
overlap_delta = 12
resume_improved = 28
resume_same = 1
resume_worse = 0
residual_safety_coverage = 117
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（resume-improved + surface + additive + tier-coverage only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

# C-FM-40 — Scale Dry863/Unique/Surface/Cross-Formula-Bundle

_生成时间：2026-07-15T16:00:03Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-40** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-39 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**dry863_extras membership freeze（Δ2 {000037,000055}）**、**unique_union composition identity lock（2249=2134+106+9）**、**surface_unique composition identity lock（2251=2249+2）**、**cross_formula_bundle identity lock（七公式捆绑）**、**FM39 连续 + MOCK42 隔离**；产物写入隔离 MOCK42（不覆盖 MOCK3–41）。

## Capability gain

1. FM39 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 1053 · Δ2 · 2134/106/9 · resume 28/1/0 · residual 117=106+9+2 · risk 75/14/12/5 · risk_band/resume formulas）
2. dry863_extras_membership_freeze：{000037,000055} · sha256 锁 · inject/drop/replace 拒绝
3. unique_union_composition_identity_lock：2249=2134+106+9 · 组成身份锁
4. surface_unique_composition_identity_lock：2251=2249+2 · 组成身份锁
5. cross_formula_bundle_identity_lock：七公式捆绑 · 公式变异拒绝
6. output-root：MOCK3–41 冻结 · MOCK42 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..39 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK42 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm40_cli_test_tmp/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* dry863/unique/surface/cross-formula ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–39 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · dry863/unique/surface/cross-formula 重算（不覆盖 MOCK3–41） | 覆盖 MOCK3–41 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_40_scale_dry863_unique_surface_cross_formula_bundle_safety_gate = PASS_OFFLINE
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
union_formula = 2134+106+9=2249
surface_formula = 2249+2=2251
additive_formula = 2249+12=2261
tier_coverage_formula = tiers=7;coverage_sum=3314
risk_band_formula = 75+14+12+5=106
resume_formula = 28+1+0=29
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（dry863/unique/surface/cross-formula-bundle only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

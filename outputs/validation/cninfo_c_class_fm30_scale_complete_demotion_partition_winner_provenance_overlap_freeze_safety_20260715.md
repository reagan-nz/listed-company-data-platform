# C-FM-30 — Scale Complete Demotion + Partition + Winner + Overlap Freeze

_生成时间：2026-07-15T14:24:49Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-30** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-29 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**complete demotion denial（2134）**、**status partition invariant（2134+106+9=2249）**、**winner provenance lock（2249）**、**overlap-delta/surface-injection freeze（Δ12）**、**FM29 连续 + MOCK32 隔离**；产物写入隔离 MOCK32（不覆盖 MOCK3–31）。

## Capability gain

1. FM29 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 2134/106/9 · Δ2 · cov=117）
2. complete demotion denial：2134 码 × demote→partial/failed 显式拒绝
3. status partition invariant lock：2134+106+9=2249 · mutation_allowed=false
4. winner provenance lock：2249 码 × winning-batch reassign 显式拒绝
5. overlap-delta / surface-injection freeze：Δ12 + dry863 extras 注入拒绝
6. output-root：MOCK3–31 冻结 · MOCK32 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..29 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK32 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* demotion/partition/winner/overlap ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–29 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · demotion/partition/winner/overlap 重算（不覆盖 MOCK3–31） | 覆盖 MOCK3–31 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety_gate = PASS_OFFLINE
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
overlap_delta = 12
surface_harvest_delta_n = 2
resume_same = 1
residual_safety_coverage = 117
surface_unique = 2251
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（complete-demotion + partition + winner + overlap-freeze only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

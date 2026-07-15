# C-FM-33 — Scale Union Partition + Overlap + Residual + Resume Same/Worse

_生成时间：2026-07-15T14:53:12Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-33** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-32 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**union status partition cardinality freeze（2134/106/9）**、**overlap_delta cardinality freeze（12）**、**residual_safety_coverage lock（117）**、**resume_same/worse write-boundary（1/0）**、**FM32 连续 + MOCK35 隔离**；产物写入隔离 MOCK35（不覆盖 MOCK3–34）。

## Capability gain

1. FM32 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 2134/106/9 · surface=2251 · additive=2261 · 7/3314）
2. union status partition cardinality freeze：2134/106/9 · mutation/rebalance 拒绝
3. overlap_delta cardinality freeze：12 · inflate/deflate 拒绝
4. residual_safety_coverage lock：117 · mutation_allowed=false
5. resume_same/worse write-boundary：1/0（301212）· force_improve/reclass/inject_worse 拒绝
6. output-root：MOCK3–34 冻结 · MOCK35 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..32 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK35 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm33_cli_test_tmp/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* union/overlap/residual/same-worse ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–32 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · union/overlap/residual/same-worse 重算（不覆盖 MOCK3–34） | 覆盖 MOCK3–34 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_33_scale_union_partition_overlap_residual_resume_same_worse_safety_gate = PASS_OFFLINE
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

- Controller 可 commit 本包（union-partition + overlap + residual + resume_same/worse only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

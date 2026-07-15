# C-FM-24 — Scale Unique-Coverage + Resume Lineage Safety

_生成时间：2026-07-15T13:49:48Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-24** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-23 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**harvest unique-coverage 对账（2249/2261/Δ12）**、**pairwise 交集矩阵指纹**、**dryrun∪harvest 表面 2251**、**phase35 resume lineage 安全（29⊆p35）**、**FM23 连续 + MOCK26 隔离**；产物写入隔离 MOCK26（不覆盖 MOCK3–25）。

## Capability gain

1. unique vs additive 对账：`harvest_unique_union=2249` · `additive=2261` · `delta=12`
2. pairwise 交集矩阵冻结指纹（相对五 harvest batch）
3. dryrun∪harvest 表面 unique=2251；dry863 extras={000037,000055}
4. phase35 resume lineage：n=29 ⊆ p35 · 结构 + 写拒绝（C-ROOT-002）
5. FM23 packet/fingerprint 零漂移连续（3314 / 7 tiers）
6. 七层 repro 指纹再确认 + combined dryrun 1053
7. output-root：MOCK3–25 冻结 · MOCK26 放行；harvest/resume 写拒绝
8. FM-01..05 + FM-12..23 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_unique_coverage_resume_lineage_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_unique_coverage_resume_lineage_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_unique_coverage_resume_lineage_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK26 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm24_scale_unique_coverage_resume_lineage_safety/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_unique_coverage_resume_lineage_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_unique_coverage_resume_lineage_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* unique-coverage / pairwise / ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–23 gate JSON / harvest / resume / dryrun status | CNINFO live |
| offline QA · unique/pairwise 重算（不覆盖 MOCK3–25） | 覆盖 MOCK3–25 |
| resume harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_24_scale_unique_coverage_resume_lineage_safety_gate = PASS_OFFLINE
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
surface_unique = 2251
resume_total = 29
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（unique-coverage + resume lineage safety only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

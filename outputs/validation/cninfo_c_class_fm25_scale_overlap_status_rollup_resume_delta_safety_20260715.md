# C-FM-25 — Scale Overlap Status Rollup + Resume Delta Safety

_生成时间：2026-07-15T13:56:03Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-25** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-24 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**精确 overlap 代码台账（Δ12）**、**unique-union status rollup（2134/106/9）**、**resume vs base delta（28/1/0）**、**dry863 extras 隔离**、**FM24 连续 + MOCK27 隔离**；产物写入隔离 MOCK27（不覆盖 MOCK3–26）。

## Capability gain

1. FM24 packet/fingerprint 零漂移连续（unique=2249 · surface=2251）
2. 精确 overlap 台账：p35∩fu={000003} · p2∩fu=11 码冻结指纹
3. harvest unique status rollup：complete=2134 · partial=106 · failed=9
4. resume vs base delta：improved=28 · same=1(301212) · worse=0 · 写拒绝
5. dry863 extras={000037,000055} 相对 harvest/exclusion 隔离（pending）
6. output-root：MOCK3–26 冻结 · MOCK27 放行；harvest/resume 写拒绝
7. FM-01..05 + FM-12..24 gate battery（跳过 seal FM06–11）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK27 + C-ROOT-002 说明 |
| `outputs/validation/_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* overlap/status/resume-delta ledger / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–24 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |
| offline QA · overlap/status/delta 重算（不覆盖 MOCK3–26） | 覆盖 MOCK3–26 |
| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_25_scale_overlap_status_rollup_resume_delta_safety_gate = PASS_OFFLINE
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
resume_improved = 28
resume_same = 1
surface_unique = 2251
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（overlap ledger + status rollup + resume delta only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）

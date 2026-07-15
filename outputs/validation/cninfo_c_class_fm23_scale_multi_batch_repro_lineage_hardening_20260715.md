# C-FM-23 — Scale Multi-Batch Repro Lineage Hardening

_生成时间：2026-07-15T13:42:09Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-23** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-22 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** 规模/安全能力（非 extension↔drift / seal-chain）：**七层多 batch repro 指纹（863/190/861/500/500/200/200）**、**隔离 dry-run 合标 1053**、**lineage 加固**、**output-root 保护（MOCK25 + C-ROOT-011）**；产物写入隔离 MOCK25（不覆盖 MOCK3–24）。

## Capability gain

1. 多 cohort repro 扩展：+phase3×500 +phase2×200 +fuller×200
2. 规模 lineage registry：`scale_tier_count=7` · `company_coverage_sum=3314`
3. 多 batch harvest×exclusion dual-layer（phase3/phase2/fuller + phase35 不变式）
4. 隔离 snapshot dry-run 合标规模指纹（863+190=1053，不 EXECUTE）
5. lineage 加固：FM22 packet 零漂移连续 + 跨 batch 不相交 / 已知小交集
6. output-root 保护：phase3/phase2/fuller/phase35 写拒绝 + MOCK3–24 冻结
7. FM-01..05 + FM-12..22 gate battery（跳过 seal FM06–11）
8. protected CSV：MOCK25 + fuller harvest C-ROOT-011

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK25 + C-ROOT-011 |
| `outputs/validation/_mock_c_fm23_scale_multi_batch_repro_lineage_hardening/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_multi_batch_repro_lineage_hardening_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_multi_batch_repro_lineage_hardening_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* scale 矩阵 / 指纹 / registry / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–22 gate JSON / harvest / exclusion / protected CSV | CNINFO live |
| offline QA · 多尺度指纹重算（不覆盖 MOCK3–24） | 覆盖 MOCK3–24 |
| fuller harvest 只读登记（C-ROOT-011） | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_23_scale_multi_batch_repro_lineage_hardening_gate = PASS_OFFLINE
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
combined_dryrun_coverage = 1053
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（scale multi-batch repro lineage hardening only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-17 checklist 做 EXECUTE 决策（本包不翻转 approved）

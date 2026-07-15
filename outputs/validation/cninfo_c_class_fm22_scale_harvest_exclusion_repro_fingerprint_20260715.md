# C-FM-22 — Scale Harvest-Exclusion Repro Fingerprint

_生成时间：2026-07-15T13:36:04Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-22** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-21 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力（非第四次 extension→drift 循环）：**phase35×500 harvest/exclusion 规模 dual-layer**、**多 cohort 可复现指纹（863/190/861/500）**、**output-root 保护加固**；产物写入隔离 MOCK24（不覆盖 MOCK3–23）。

## Capability gain

1. phase35×500 × exclusion manifest 规模 dual-layer（holdout9 9/9 partial）
2. 多 cohort 可复现指纹：FM01(863)+FM02(190)+FM03(861)+phase35(500)
3. 规模 lineage registry：`scale_tier_count=4` · `company_coverage_sum=2414`
4. 863 harvest 与 caveat10 不相交（规模不变式）
5. output-root 保护加固：phase35/863 harvest 写拒绝 + MOCK3–23 冻结
6. FM-01..05 + FM-12..21 gate battery（跳过 seal FM06–11）
7. protected CSV：MOCK24 注册

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_scale_harvest_exclusion_repro_fingerprint.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_scale_harvest_exclusion_repro_fingerprint.py` | **新增** runner |
| `lab/test_cninfo_c_class_scale_harvest_exclusion_repro_fingerprint.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK24 |
| `outputs/validation/_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint/` | 隔离 scale 产物 |
| `outputs/validation/cninfo_c_class_scale_harvest_exclusion_repro_fingerprint_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_scale_harvest_exclusion_repro_fingerprint_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* scale 矩阵 / 指纹 / registry / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–05 / FM12–21 gate JSON / harvest / exclusion / protected CSV | CNINFO live |
| offline QA · 多尺度指纹重算（不覆盖 MOCK3–23） | 覆盖 MOCK3–23 |
| | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_22_scale_harvest_exclusion_repro_fingerprint_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
approved_for_snapshot_rebuild = false
cninfo_calls = 0
ready_for_execute = false
hold_recommendation = KEEP_EXECUTE_FALSE
decision_status = AWAITING_HUMAN_EXECUTE_DECISION
idle_not_required_while_awaiting = true
seal_chain_extended = false
scale_tier_count = 4
company_coverage_sum = 2414
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（scale harvest-exclusion repro fingerprint only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-17 checklist 做 EXECUTE 决策（本包不翻转 approved）

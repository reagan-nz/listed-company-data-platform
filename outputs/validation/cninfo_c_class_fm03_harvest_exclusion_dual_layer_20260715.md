# C-FM-03 — Harvest/Exclusion/Dual-layer 一致性 + 863 结构 Mock

_生成时间：2026-07-15T09:08:10Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-03** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-02 lineage 之上，新增 **家族感知 harvest/exclusion 一致性**、**dual-layer cohort 交叉核验**、**manifest↔reconcile（holdout9 不膨胀）**、以及 **863 harvest ledger 更大 mock 结构指纹**。

## Capability gain

1. `cninfo_c_class_harvest_exclusion_dual_layer_consistency`：四层 consistency matrix
2. partial7/empty3 家族 ↔ ledger status ↔ pool_decision 机器核验
3. dual-layer empty3+partial7 索引并集 = caveat10 · coverage 10/10（只读，不覆盖权威索引）
4. holdout9 隔离于 slice1（除 partial 重叠 000003）
5. 863 ledger 861 complete 结构指纹写入 validation/_mock_*

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_harvest_exclusion_dual_layer_consistency.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py` | **新增** runner |
| `lab/test_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK5 |
| `outputs/validation/_mock_c_fm03_cli_test_tmp/` | 隔离一致性产物 |
| `outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* 一致性矩阵 / 指纹 | 生产 snapshot EXECUTE |
| 只读 harvest / exclusion / dual-layer 索引 | CNINFO live |
| offline QA | 覆盖 empty3/partial7 权威索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |

## Wall / gate

```
c_fm_03_harvest_exclusion_dual_layer_consistency_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
ready_for_commit = true
```

## Next

- Controller 可 commit 本包
- 生产 snapshot EXECUTE 仍 human-gated

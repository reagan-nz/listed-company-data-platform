# C-FM-04 — Ledger↔Resume-audit Dual-layer Lineage + Index Isolation + FM Battery

_生成时间：2026-07-15T09:14:10Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-04** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-03 之上，补齐 **status-ledger ↔ resume-audit** 双层语义 lineage、**权威 dual-layer 索引写隔离**、以及 **FM-01/02/03 gate battery** 只读聚合；产物写入隔离 mock cohort。

## Capability gain

1. `cninfo_c_class_dual_layer_ledger_resume_lineage`：四层 lineage matrix
2. empty3：ledger=complete / resume=needs_review / sources_present=9（合法分歧）
3. partial7：ledger=partial / resume=partial / live=deferred_targeted_live_after_approval
4. resume 聚合 190/7/3 + needs_review≡empty3 + holdout9 不膨胀
5. `assert_authoritative_dual_layer_index_write_forbidden` 硬化
6. FM-01/02/03 PASS_OFFLINE battery（不重跑 dry-run）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_dual_layer_ledger_resume_lineage.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_dual_layer_ledger_resume_lineage.py` | **新增** runner |
| `lab/test_cninfo_c_class_dual_layer_ledger_resume_lineage.py` | **新增** 测试 |
| `lab/cninfo_c_class_erad_cleanup_guard.py` | 权威 dual-layer 索引写拒绝 |
| `lab/test_cninfo_c_class_erad_cleanup_hardening.py` | case9 索引隔离 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK6 · C-ROOT-AUTH1 |
| `outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage/` | 隔离 lineage 产物 |
| `outputs/validation/cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* lineage / 指纹 / battery | 生产 snapshot EXECUTE |
| 只读 harvest / resume-audit / dual-layer 索引 / 既有 FM gate JSON | CNINFO live |
| offline QA | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |

## Wall / gate

```
c_fm_04_dual_layer_ledger_resume_lineage_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
ready_for_commit = true
```

## Next

- Controller 可 commit 本包
- 生产 snapshot EXECUTE 仍 human-gated

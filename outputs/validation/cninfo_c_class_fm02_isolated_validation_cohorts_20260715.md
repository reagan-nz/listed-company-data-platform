# C-FM-02 — 隔离 Snapshot 校验 Cohort + Dry-run Lineage

_生成时间：2026-07-15T09:01:28Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-02** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-01 隔离 dry-run / 指纹能力之上，新增 **隔离 snapshot 校验 cohort** 与 **dry-run lineage 自动化**：universe ↔ status ↔ harvest ledger ↔ exclusion reconcile；含 caveat10 负对照与标准隔离根只读指纹核验。

## Capability gain

1. `cninfo_c_class_isolated_snapshot_validation_cohorts`：多 cohort 规格 + lineage 矩阵
2. slice1_190 included 隔离 dry-run（validation/_mock_*）+ 双次指纹可复现
3. caveat10 负对照：排除码不得泄漏进 included dry-run status
4. harvest ledger / exclusion pool_decision 交叉 lineage 检查
5. C-FM-01 标准隔离根只读指纹复算（不重跑 863）

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_isolated_snapshot_validation_cohorts.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_isolated_snapshot_validation_cohorts.py` | **新增** runner |
| `lab/test_cninfo_c_class_isolated_snapshot_validation_cohorts.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK4 |
| `outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json` | 报告 JSON |
| `outputs/validation/_mock_c_fm02_slice1_190_validation_cohort/` | 隔离 cohort 产物 |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* dry-run / lineage | 生产 snapshot EXECUTE |
| 只读 harvest ledger / exclusion | CNINFO live |
| offline QA / fingerprint | commit/push（本包未执行） |
| | verified / production_ready 声称 |

## Wall / gate

```
c_fm_02_isolated_snapshot_validation_cohorts_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
ready_for_commit = true
```

## Next

- Controller 可 commit 本包
- 生产 snapshot EXECUTE 仍 human-gated


# C-FM-12 — Dry-run Fingerprint Lineage Extension + Frozen Mock Isolation

_生成时间：2026-07-15T12:12:06Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-12** |
| track | C |
| result | **DONE** |
| CNINFO live | **0** |
| prod snapshot EXECUTE | **not invoked** |
| commit / push | **无**（待 controller） |
| ready_for_commit | **true** |

## Task

在 C-FM-11 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力：**dry-run 指纹 lineage 扩展**、**冻结 mock cohort 写隔离**、**harvest/exclusion dual-layer 交叉指纹 QA**；产物写入隔离 MOCK14（不覆盖 MOCK3–13）。

## Capability gain

1. `fingerprint_isolated_snapshot_dryrun(lineage_artifacts=True)`：扩展指纹 API
2. `assert_frozen_mock_cohort_write_forbidden`：MOCK3–13 冻结写拒绝
3. FM-01/FM-02 base 指纹零漂移复核（不重跑 dry-run）
4. FM-02 lineage 扩展 ≠ base 且可复算；FM-01 缺失 lineage 仍可扩展
5. FM-03 harvest_863 + FM-04 lineage 交叉指纹与 gate 对齐
6. protected CSV：MOCK14 注册

## Files

| 路径 | 变更 |
|------|------|
| `lab/cninfo_c_class_erad_cleanup_guard.py` | lineage 指纹扩展 + 冻结 mock 写守卫 |
| `lab/test_cninfo_c_class_erad_cleanup_hardening.py` | case10/11 |
| `lab/cninfo_c_class_dryrun_fingerprint_lineage_isolation.py` | **新增** 核心 |
| `lab/run_cninfo_c_class_dryrun_fingerprint_lineage_isolation.py` | **新增** runner |
| `lab/test_cninfo_c_class_dryrun_fingerprint_lineage_isolation.py` | **新增** 测试 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK14 |
| `outputs/validation/_mock_c_fm12_dryrun_fingerprint_lineage_isolation/` | 隔离 lineage/isolation 产物 |
| `outputs/validation/cninfo_c_class_dryrun_fingerprint_lineage_isolation_20260715.md` | 报告 |
| `outputs/validation/cninfo_c_class_dryrun_fingerprint_lineage_isolation_20260715.json` | 报告 JSON |

## Allow-list

| 允许 | 禁止 |
|------|------|
| validation/_mock_* isolation 矩阵 / 指纹 / battery / packet | 生产 snapshot EXECUTE |
| 只读 FM01–04 gate JSON / dry-run mock / harvest status / protected CSV | CNINFO live |
| offline QA · lineage 扩展指纹重算（不覆盖 MOCK3–13） | 覆盖 MOCK3–13 |
| | 覆盖权威 dual-layer 索引 |
| | commit/push（本包未执行） |
| | verified / production_ready 声称 |
| | 翻转 approved_for_snapshot_rebuild |
| | 新增 seal-chain MOCK 层 |
| | 仅因 AWAITING 而 IDLE |

## Wall / gate

```
c_fm_12_dryrun_fingerprint_lineage_isolation_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
approved_for_snapshot_rebuild = false
cninfo_calls = 0
ready_for_execute = false
hold_recommendation = KEEP_EXECUTE_FALSE
decision_status = AWAITING_HUMAN_EXECUTE_DECISION
idle_not_required_while_awaiting = true
seal_chain_extended = false
ready_for_commit = true
```

## Next

- Controller 可 commit 本包（non-seal isolation/fingerprint only）
- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）
- Human 仍可用 C-FM-10 checklist 做 EXECUTE 决策（本包不翻转 approved）

# CNINFO D 类 Tiny Live V2 Bounded Probe — Design Summary

_生成时间：2026-07-09_

> **性质：** Option B 离线设计摘要 · **NOT APPROVED** · **无 CNINFO** · **不是 verified**

---

## 1. Context

| 项 | 值 |
|----|-----|
| Phase 1 boundary commit | `7a62539`（pushed） |
| boundary gate | `d_class_phase1_boundary_gate = PASS_WITH_CAVEAT` |
| calibration gate | `d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION` |
| v1 tiny live | **5/7 acceptable** · **2 expectation mismatches** |
| human direction | **Option B** — bounded probe extension design |

---

## 2. Problem Statement

| case | component | company | v1 probes | observed |
|------|-----------|---------|-----------|----------|
| DLC003 | restricted_shares_unlock | 300009 安科生物 | 8 tdate | empty_but_valid |
| DLC006 | shareholder_change | 000550 江铃汽车 | 5 mode/date | empty_but_valid |

**不是 schema failure** — API 可用 · 全市场有行 · quality policy 口径正确。

---

## 3. Proposed Bounded Extension

### DLC003 — date-window probing

| 维度 | 新增上限 |
|------|----------|
| recent_12m_monthly | 12 |
| recent_24m_quarterly | 8 |
| reporting_window_quarterly | dedup with quarterly |
| **bounded_union_cap** | **24（硬顶）** |

### DLC006 — mode/date probing

| 维度 | 新增上限 |
|------|----------|
| v1_modes_expanded_dates | 10 |
| recent_12m_quarterly_inc | 4 |
| recent_24m_quarterly_both | 16 |
| **bounded_union_cap** | **20（硬顶）** |

**不猜测事件日** · **不发明 replacement 公司** · **early stop on first hit**

---

## 4. Safety

| 项 | 值 |
|----|-----|
| cases probed | DLC003 · DLC006 only |
| baseline preserved | DLC001/002/004/005/007 v1 reference |
| v2 output root | `outputs/validation/cninfo_d_class_tiny_live_validation_v2/` |
| v1 mutation | **no** |
| DB / MinIO / RAG | **0** |
| harvest | **no** |

---

## 5. Artifacts

| 文档 | 路径 |
|------|------|
| bounded probe design | [cninfo_d_class_dlc003_dlc006_bounded_probe_extension_design.md](../plans/cninfo_d_class_dlc003_dlc006_bounded_probe_extension_design.md) |
| probe matrix | [cninfo_d_class_dlc003_dlc006_bounded_probe_matrix.csv](cninfo_d_class_dlc003_dlc006_bounded_probe_matrix.csv) |
| command draft | [cninfo_d_class_tiny_live_v2_bounded_probe_command_draft.md](../plans/cninfo_d_class_tiny_live_v2_bounded_probe_command_draft.md) |
| runner modification plan | [cninfo_d_class_tiny_live_v2_runner_modification_plan.md](../plans/cninfo_d_class_tiny_live_v2_runner_modification_plan.md) |
| approval checklist | [cninfo_d_class_tiny_live_v2_bounded_probe_approval_checklist.md](cninfo_d_class_tiny_live_v2_bounded_probe_approval_checklist.md) |

---

## 6. Request Budget Summary

| case | v1 used | v2 cap |
|------|---------|--------|
| DLC003 | 8 | **24** |
| DLC006 | 5 | **20** |
| **v2 total** | — | **≤44** |

---

## 7. Approval Path（未来）

1. 评审本设计包 + checklist
2. 实现 runner modification plan
3. 用户显式 `--approve-d-class-tiny-live-v2-bounded-probe`
4. 执行 v2 dry-run → 再批准 live
5. 生成 v2 report + v1 comparison report

**当前：NOT APPROVED · 不执行**

---

## 8. Gate

```text
d_class_tiny_live_v2_bounded_probe_design_gate = READY_FOR_APPROVAL
```

| 声明 | 值 |
|------|-----|
| PASS | **no** |
| live_ready | **no** |
| verified | **false** |
| production_ready | **false** |
| testing_stable_sample upgrade | **no** |
| CNINFO calls（本回合） | **0** |

---

## 9. Parallel Safety

- C-class: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- A/B-class outputs: **unchanged**
- v1 execution reports: **unchanged**

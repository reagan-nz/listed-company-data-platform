# CNINFO D 类 DLC003 / DLC006 Expectation Calibration — Summary

_生成时间：2026-07-09_

> **性质：** 离线决策包摘要；**无 CNINFO** · **无 live** · **无 rerun** · **不是 verified**

---

## Context

| 项 | 值 |
|----|-----|
| v1 input cases | **7** |
| v1 acceptable | **5** |
| v1 failed expectation | **2**（DLC003 · DLC006） |
| v1 execution gate | `PASS_WITH_CAVEAT` |
| v1 closure gate | `PASS_WITH_CAVEAT` |
| interpretation | **expectation mismatch / probe-window limitation** — **not schema failure** |

---

## Failed Expectation Cases

| case | component | company | expected | observed |
|------|-----------|---------|----------|----------|
| DLC003 | restricted_shares_unlock | 300009 安科生物 | captured_normal | empty_but_valid · 8 tdate probes |
| DLC006 | shareholder_change | 000550 江铃汽车 | captured_normal | empty_but_valid · 5 mode probes |

---

## Decision Package Artifacts

| 文档 | 路径 |
|------|------|
| detailed review | [cninfo_d_class_dlc003_dlc006_calibration_review.md](../plans/cninfo_d_class_dlc003_dlc006_calibration_review.md) |
| decision matrix | [cninfo_d_class_dlc003_dlc006_calibration_decision_matrix.csv](cninfo_d_class_dlc003_dlc006_calibration_decision_matrix.csv) |
| universe v2 draft | [cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv](cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv) |
| v2 rerun planning | [cninfo_d_class_tiny_live_v2_rerun_planning_note.md](../plans/cninfo_d_class_tiny_live_v2_rerun_planning_note.md) |

---

## Recommended Defaults

| case | 推荐 | 不推荐立即 |
|------|------|------------|
| **DLC003** | **Option B 或 C** | Option A |
| **DLC006** | **Option B 或 C** | Option A |

**共同理由：** `restricted_shares_unlock` 与 `shareholder_change` 在 tiny live 中 **尚无** 成功 `captured_normal` 样本；应先获得 captured 证据，再考虑将 expectation 稳定为 `empty_but_valid`。

### Option Summary

| 选项 | DLC003 | DLC006 |
|------|--------|--------|
| A | Reclassify → empty_but_valid | Reclassify → empty_but_valid |
| B | Extend date-window probing | Extend mode/date probing |
| C | Replace with known unlock case | Replace with known shareholder-change case |

---

## Universe v2 Draft

- **Size = 7**
- **Unchanged：** DLC001 · DLC002 · DLC004 · DLC005 · DLC007
- **Placeholders：** `DLC003_V2_CANDIDATE_REQUIRED` · `DLC006_V2_CANDIDATE_REQUIRED`
- `requires_human_candidate = true` · **no invented company codes**

---

## v2 Rerun

| 项 | 状态 |
|----|------|
| approved | **NOT APPROVED** |
| output root | `outputs/validation/cninfo_d_class_tiny_live_validation_v2/` |
| flag | `--approve-d-class-tiny-live-v2-validation` |
| v1 overwrite | **禁止** |

---

## Gate

```text
d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION
```

**不是 PASS** · **不是 approved** · **不是 live_ready** · **不是 verified**

---

## Safety Confirmation

| 项 | 值 |
|----|-----|
| CNINFO calls（本回合） | **0** |
| live / rerun / harvest | **未执行** |
| DB / MinIO / RAG | **0** |
| execution report modified | **no** |
| A/B/C outputs touched | **no** |
| C-class status | `SNAPSHOT_GENERATED_QA_REVIEW` |

---

## Next Step（人工）

1. Review [decision matrix](cninfo_d_class_dlc003_dlc006_calibration_decision_matrix.csv)
2. 为 DLC003/DLC006 选择 B/C（或说明选 A 的理由）
3. 若选 C：填写 universe v2 draft placeholder（**人工提供** company_code）
4. 批准后另行申请 v2 rerun（仍 **NOT APPROVED**）

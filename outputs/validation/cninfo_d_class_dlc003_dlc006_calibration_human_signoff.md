# CNINFO D 类 DLC003 / DLC006 Calibration — Human Signoff Record

_决策日期：2026-07-09_

> **性质：** 人工 signoff 记录 · **无 CNINFO** · **无 live rerun** · **不是 verified** · **不是 production_ready**

---

## 1. Approved Option

**Option A approved** for current tiny-live universe closure.

**Option C** remains a **future task** (component-level `captured_normal` validation).

---

## 2. DLC003 Decision

| 项 | 值 |
|----|-----|
| case_id | DLC003 |
| company | 300009 安科生物 |
| component | restricted_shares_unlock |
| old expected_behavior | `captured_normal` |
| new expected_behavior | **`empty_but_valid`** |
| calibration_status | `human_signed_off` |
| calibration_evidence | `v1_v2_bounded_probe_empty` |

---

## 3. DLC006 Decision

| 项 | 值 |
|----|-----|
| case_id | DLC006 |
| company | 000550 江铃汽车 |
| component | shareholder_change |
| old expected_behavior | `captured_normal` |
| new expected_behavior | **`empty_but_valid`** |
| calibration_status | `human_signed_off` |
| calibration_evidence | `v1_v2_bounded_probe_empty` |

---

## 4. Evidence Basis

| 来源 | 内容 |
|------|------|
| v1 tiny live | DLC003 **8** probes · DLC006 **5** probes · 均 **0** company rows · `empty_but_valid` |
| v2 bounded probe | DLC003 **21** probes · DLC006 **19** probes · 均 **0** company rows · `empty_but_valid` |
| combined | DLC003 **29** total · DLC006 **24** total · stable empty |
| interpretation | `stable_empty_but_valid_after_bounded_probe` |
| schema_failure | **`false`** |

**关联证据：** [v1-v2 evidence matrix](cninfo_d_class_dlc003_dlc006_v1_v2_evidence_matrix.csv) · [final calibration decision](cninfo_d_class_dlc003_dlc006_final_calibration_decision_summary.md) · [closure summary](cninfo_d_class_tiny_live_v2_bounded_probe_closure_summary.md)

---

## 5. Operational Constraints

| 约束 | 状态 |
|------|------|
| CNINFO calls（本回合） | **0** |
| live / rerun | **no** |
| v1 execution report modified | **no** |
| v2 execution report modified | **no** |
| original v1 universe file modified | **no** |
| invented company codes | **no** |
| DB / MinIO / RAG | **0** |
| harvest | **no** |
| verified / production_ready | **no** |

---

## 6. Production Claim

**无 production claim。** 本 signoff 仅校准 tiny-live universe 预期行为，不构成组件生产就绪或 schema verified 声明。

---

## 7. Future Option C

组件级 `captured_normal` 验证 **仍需要** 人工选定的 known-event replacement cases：

- DLC003：`restricted_shares_unlock` known captured_normal company（**待人工提供**）
- DLC006：`shareholder_change` known captured_normal company（**待人工提供**）

见 [known event replacement planning note](../plans/cninfo_d_class_known_event_replacement_case_planning_note.md)。

---

## 8. Applied Artifacts

| 文档 | 路径 |
|------|------|
| calibrated universe | [cninfo_d_class_phase1_tiny_live_universe_calibrated.csv](cninfo_d_class_phase1_tiny_live_universe_calibrated.csv) |
| application summary | [cninfo_d_class_dlc003_dlc006_calibration_application_summary.md](cninfo_d_class_dlc003_dlc006_calibration_application_summary.md) |

---

## 9. Gate

```text
d_class_dlc003_dlc006_final_calibration_gate = HUMAN_SIGNED_OFF_WITH_CAVEAT
```

**不是 PASS** · **不是 verified** · **不是 production_ready**

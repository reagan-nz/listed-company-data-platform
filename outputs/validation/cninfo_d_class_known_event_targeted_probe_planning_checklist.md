# CNINFO D 类 Known Event Targeted Probe — Planning Checklist

_生成时间：2026-07-09_

> **approval_status = NOT_APPROVED** · **approved_for_live = false** · **无 CNINFO**

---

## 1. Failure Review Complete

- [x] replacement live failure reviewed → [live failure review](../plans/cninfo_d_class_known_event_replacement_live_failure_review.md)
- [x] evidence reconciliation matrix reviewed → [matrix](cninfo_d_class_known_event_replacement_evidence_reconciliation_matrix.csv)
- [x] execution gate remains **FAIL_REVIEW_REQUIRED**（**不是 PASS_WITH_CAVEAT**）
- [x] human evidence **不等于** component-level captured_normal

---

## 2. Scope Controls

- [x] old DLC003 (300009) blocked from targeted probe
- [x] old DLC006 (000550) blocked from targeted probe
- [x] only DLC003R / DLC006R eligible
- [x] full tiny-live rerun **not approved**
- [x] v2 bounded probe rerun **not approved**
- [x] replacement live reports **not mutated** this round

---

## 3. Targeted Probe Design（Option A · 未实现）

- [x] DLC003R anchor date documented：**2024-02-19**
- [x] DLC006R anchor date documented：**2024-07-16**
- [x] DLC003R request cap suggestion：**≤ 12**
- [x] DLC006R request cap suggestion：**≤ 12**
- [x] total future request cap：**≤ 24**
- [x] output root isolated：`outputs/validation/cninfo_d_class_known_event_targeted_probe/`
- [x] approval flag suggestion：`--approve-d-class-known-event-targeted-probe`
- [ ] runner extension implemented（**未实现**）
- [ ] dry-run passed（**未执行**）

---

## 4. Safety

- [x] no PDF download
- [x] no OCR
- [x] no extraction
- [x] no DB write
- [x] no MinIO write
- [x] no RAG run
- [x] no verified / production_ready / testing_stable_sample

---

## 5. Explicit Approval Required

- [x] explicit human approval required before any **implementation**
- [x] explicit human approval required before any **live run**
- [ ] user provides `--approve-d-class-known-event-targeted-probe`（**待未来**）
- [x] checklist completion **不等于** live 批准

---

## 6. Gate

```text
approval_status = NOT_APPROVED
approved_for_live = false
d_class_known_event_replacement_live_failure_review_gate = READY_FOR_HUMAN_DECISION
d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED
d_class_known_event_targeted_probe_planning_gate = NOT_STARTED
```

**NOT PASS** · **NOT verified** · **NOT production_ready**

**CNINFO calls（本回合）：0**

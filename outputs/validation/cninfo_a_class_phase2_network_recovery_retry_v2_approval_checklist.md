# CNINFO A 类 Phase 2 Network Recovery Retry v2 批准检查清单

_生成时间：2026-07-09 · 更新：runner extension + dry-run 完成_

> **批准状态：NOT_APPROVED**  
> **approved_for_live：false**  
> **不是 verified** · **不是 production_ready** · **不是 live_ready**

---

## Universe 确认

- [x] **8 unresolved cases confirmed** — A2M005 · A2M010 · A2M011 · A2M012 · A2M013 · A2M018 · A2M019 · A2M020
- [x] **12 successful cases excluded** — A2M001–A2M004 · A2M006–A2M009 · A2M014–A2M017
- [x] **retry_v2 universe size = 8** — [universe CSV](cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv)
- [ ] **no replacement cases added**（人工 live 前复核）
- [ ] **report_type / report_period unchanged** vs Phase 2 original universe（人工 live 前复核）

---

## 输出隔离

- [x] **output root isolated** — `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/`
- [x] **original Phase 2 reports write-blocked** — `cninfo_a_class_phase2_metadata_expansion/`
- [x] **first retry (v1) reports write-blocked** — `cninfo_a_class_phase2_metadata_retry/`
- [x] **Phase 1 baseline write-blocked**

---

## Offline 准备（已完成）

- [x] **retry_v2 runner support implemented**
- [x] **retry_v2 approval flag required** — `--approve-a-class-phase2-network-recovery-retry-v2`
- [x] **successful 12 rejected** — runner validation
- [x] **universe column aliases supported** — `retry_v2_include` · `report_period`
- [x] **dry-run completed** — 8/8 planned_ok
- [x] **CNINFO calls during dry-run = 0**
- [x] **runner tests PASS** — 18/18 v2 · 12/12 v1 回归 · 16/16 expansion 回归

---

## Schema / Matching

- [x] **no schema change**
- [x] **no matching logic change** — v2 unchanged
- [x] **no universe replacement**

---

## 红线确认

- [x] **no PDF download**
- [x] **no PDF parse**
- [x] **no OCR / extraction**
- [x] **no DB write**
- [x] **no MinIO write**
- [x] **no RAG run**
- [x] **no verified mark**
- [x] **no production_ready mark**
- [x] **no testing_stable_sample upgrade**

---

## 执行前条件（live 仍待完成）

- [ ] **network recovery confirmed**（人工判断 CNINFO 可达）
- [ ] **explicit human approval required before live**

---

## 人工批准

- [ ] approver name: _______________
- [ ] approval date: _______________
- [ ] approval flag acknowledged: `--approve-a-class-phase2-network-recovery-retry-v2`

---

## 当前 Gate 状态

```text
a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED
a_class_phase2_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED
a_class_phase2_metadata_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED
a_class_phase2_network_recovery_retry_v2_planning_gate = READY_FOR_APPROVAL
a_class_phase2_network_recovery_retry_v2_runner_extension_gate = READY_FOR_APPROVAL
```

**approval_status = NOT_APPROVED**  
**approved_for_live = false**

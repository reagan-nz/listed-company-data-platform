# CNINFO A 类 Phase 2 Failed Retry — 批准检查清单

_生成时间：2026-07-09_

> **性质：** isolated retry 人工批准检查清单；**无 CNINFO** · **无 live** · **NOT APPROVED**

---

## Phase 2 前置条件

- [ ] **Phase 2 execution reviewed**
  - `a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED`
  - [failed cases review](cninfo_a_class_phase2_failed_cases_review.md) 已读
  - wrong_report_type = **0**

- [ ] **failed 8 cases confirmed**
  - A2M005, A2M010, A2M011, A2M012, A2M013, A2M018, A2M019, A2M020
  - 6 network_error · 2 not_found（proxy 503）

- [ ] **successful 12 cases excluded**
  - A2M001–A2M004, A2M006–A2M009, A2M014–A2M017 **不在** retry universe

---

## Retry Universe 审阅

- [ ] **retry universe reviewed**
  - [failed retry universe](cninfo_a_class_phase2_failed_retry_universe.csv)（**8** 行）
  - retry_include = **yes** for all 8
  - report_type / expected_period 与 Phase 2 live 一致

- [ ] **retry root isolated**
  - 专用根：`outputs/validation/cninfo_a_class_phase2_metadata_retry/`
  - 不覆盖 `cninfo_a_class_phase2_metadata_expansion/` live 报告

- [ ] **same v2 matching logic preserved**
  - `MATCHING_LOGIC_VERSION = "v2"`
  - 无 matching logic 修改

- [ ] **no schema change**
- [ ] **no universe replacement**

---

## 输出与安全

- [ ] **no PDF download**
- [ ] **no PDF parse**
- [ ] **no DB**
- [ ] **no MinIO**
- [ ] **no RAG**

---

## 批准与执行

- [ ] **explicit user approval required**
  - flag：`--approve-a-class-phase2-failed-retry`
  - **当前状态：NOT APPROVED**

- [ ] **no verified / production_ready / testing_stable_sample**

---

## 签核

| 项 | 签核人 | 日期 | 备注 |
|----|--------|------|------|
| Phase 2 execution | | | |
| failed 8 cases | | | |
| successful 12 excluded | | | |
| retry isolation | | | |
| explicit approval | | | **待批准** |

---

**Gate：** `a_class_phase2_failed_retry_planning_gate = READY_FOR_APPROVAL`

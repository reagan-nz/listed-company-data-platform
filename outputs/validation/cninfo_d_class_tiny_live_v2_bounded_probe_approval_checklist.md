# CNINFO D 类 Tiny Live V2 Bounded Probe — Approval Checklist

_生成时间：2026-07-09_

> **状态：NOT APPROVED** · **无 CNINFO** · **无 live** · **不是 verified**

---

## 1. Phase 1 Boundary Reviewed

- [ ] `d_class_phase1_boundary_gate = PASS_WITH_CAVEAT` 已阅读 [boundary signoff](../plans/cninfo_d_class_phase1_boundary_signoff.md)
- [ ] boundary commit `7a62539` 已确认 pushed
- [ ] v1 tiny live **5/7 acceptable** · **2 expectation mismatches** 已理解
- [ ] C-class `SNAPSHOT_GENERATED_QA_REVIEW` 不变

---

## 2. DLC003 / DLC006 Calibration Reviewed

- [ ] [calibration review](../plans/cninfo_d_class_dlc003_dlc006_calibration_review.md) 已阅读
- [ ] `d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION` 保持
- [ ] Option B（bounded probe）与 Option C（人工 replacement）并行关系已理解
- [ ] **不立即** Option A（reclassify to empty_but_valid）

---

## 3. Bounded Probe Scope Approved

- [ ] [bounded probe design](../plans/cninfo_d_class_dlc003_dlc006_bounded_probe_extension_design.md) 已评审
- [ ] [probe matrix](cninfo_d_class_dlc003_dlc006_bounded_probe_matrix.csv) 维度已确认
- [ ] **仅 DLC003 · DLC006** — 其余 case 保持 v1 baseline
- [ ] **不猜测**事件日期 · **不发明** replacement 公司代码
- [ ] universe v2 `*_CANDIDATE_REQUIRED` 行 **skip** 已确认

---

## 4. Request Cap Approved

| case | cap | 确认 |
|------|-----|------|
| DLC003 | **24** | [ ] |
| DLC006 | **20** | [ ] |
| v2 合计 | **≤44** | [ ] |
| inter-request delay | 0.5s | [ ] |
| retry | **0** | [ ] |

---

## 5. Output Root Isolated

- [ ] v2 root = `outputs/validation/cninfo_d_class_tiny_live_validation_v2/`
- [ ] v1 root `cninfo_d_class_tiny_live_validation/` **只读**
- [ ] v2 报告前缀 `d_class_tiny_live_v2_*` 已确认
- [ ] comparison report 将生成 v1 vs v2 对照

---

## 6. No V1 Overwrite

- [ ] v1 `d_class_tiny_live_report.csv` **不修改**
- [ ] v1 live snapshots **不覆盖**
- [ ] runner v1 写保护将在实现时启用
- [ ] 本批准包 **不执行** v2 live

---

## 7. No DB / MinIO / RAG

- [ ] DB write = **0**
- [ ] MinIO write = **0**
- [ ] RAG run = **0**
- [ ] harvest = **no**
- [ ] verified = **false**
- [ ] production_ready = **false**
- [ ] testing_stable_sample upgrade = **no**

---

## 8. Explicit User Approval Required

- [ ] [command draft](../plans/cninfo_d_class_tiny_live_v2_bounded_probe_command_draft.md) 已阅读
- [ ] [runner modification plan](../plans/cninfo_d_class_tiny_live_v2_runner_modification_plan.md) 已阅读
- [ ] 用户将显式提供 `--approve-d-class-tiny-live-v2-bounded-probe`
- [ ] runner v2 实现完成前 **禁止 live**
- [ ] 本 checklist 全部勾选 **不等于** live 批准

---

## 9. Gate

```text
d_class_tiny_live_v2_bounded_probe_design_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

**CNINFO calls（本回合）：0**

# CNINFO D 类 Known Event Candidate Intake Summary

_生成时间：2026-07-09_

> **性质：** intake 校验完成摘要 · **CNINFO calls = 0** · **web lookup = 0** · **live/rerun/harvest = 0**

---

## 1. Intake Validation

| 项 | 路径 |
|----|------|
| intake instructions | [cninfo_d_class_known_event_candidate_intake_instructions.md](../plans/cninfo_d_class_known_event_candidate_intake_instructions.md) |
| intake schema | [cninfo_d_class_known_event_candidate_intake_schema.csv](cninfo_d_class_known_event_candidate_intake_schema.csv) |
| candidate template | [cninfo_d_class_known_event_replacement_candidate_template.csv](cninfo_d_class_known_event_replacement_candidate_template.csv) |
| validation script | [lab/validate_cninfo_d_class_known_event_candidates.py](../../lab/validate_cninfo_d_class_known_event_candidates.py) |
| validation report | [cninfo_d_class_known_event_candidate_validation_report.csv](cninfo_d_class_known_event_candidate_validation_report.csv) |
| validation summary | [cninfo_d_class_known_event_candidate_validation_summary.md](cninfo_d_class_known_event_candidate_validation_summary.md) |
| tests | [lab/test_cninfo_d_class_known_event_candidate_validation.py](../../lab/test_cninfo_d_class_known_event_candidate_validation.py) |

---

## 2. Candidate Status

| slot | company_code | company_name | event_evidence_type | 原始 CNINFO 标签（description/notes） | validation |
|------|--------------|--------------|---------------------|--------------------------------------|------------|
| DLC003R | 688671 | 碧兴物联 | unlock_schedule_record | CNINFO 限售股上市流通公告 | **validated** |
| DLC006R | 301259 | 艾布鲁 | shareholder_change_announcement | CNINFO 简式权益变动报告书 | **validated** |

```text
candidate_validation_status = HUMAN_CANDIDATE_VALIDATED
```

**Evidence type 规范化：** 原始 CNINFO 中文披露标签保留于 `event_evidence_description` / `notes`；`event_evidence_type` 使用既有内部枚举（未扩展白名单）。

---

## 3. Gates

| gate | value |
|------|-------|
| `d_class_known_event_candidate_intake_gate` | **HUMAN_CANDIDATE_VALIDATED** |
| `d_class_known_event_replacement_case_planning_gate` | READY_FOR_HUMAN_CANDIDATES（保持） |
| `d_class_dlc003_dlc006_final_calibration_gate` | HUMAN_SIGNED_OFF_WITH_CAVEAT（保持） |
| `d_class_phase1_boundary_gate` | PASS_WITH_CAVEAT（保持） |

**不是 PASS** · **不是 ready_for_live** · **不是 verified** · **不是 production_ready**

---

## 4. Safety

| 项 | 状态 |
|----|------|
| CNINFO calls | **0** |
| web lookup | **0** |
| live / rerun / harvest | **0** |
| invented company codes | **none** |
| company code changes | **none** |
| original v1 universe | **untouched** |
| calibrated universe | **untouched** |
| v1/v2 execution reports | **untouched** |
| DB / MinIO / RAG | **0** |

---

## 5. Next Step

进入 replacement approval package 评审（[approval checklist](cninfo_d_class_known_event_replacement_approval_checklist.md)）→ 人工批准后准备 replacement universe 与 tiny live validation 命令草案（**NOT APPROVED** · **无自动执行**）

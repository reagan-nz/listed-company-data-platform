# CNINFO D 类 Known Event Replacement — Approval Checklist

_生成时间：2026-07-09_

> **approval_status = NOT_APPROVED** · **无 CNINFO** · **不是 verified** · **不是 live_ready**

---

## 1. Human Candidate Company Codes Provided

- [x] candidate template filled
- [x] DLC003R `company_code` 已人工填写（**688671** · **非 agent 发明**）
- [x] DLC003R `company_name` 已人工填写（**碧兴物联**）
- [x] DLC006R `company_code` 已人工填写（**301259** · **非 agent 发明**）
- [x] DLC006R `company_name` 已人工填写（**艾布鲁**）
- [x] placeholder 行 `*_CANDIDATE_REQUIRED` 已替换为 DLC003R / DLC006R

---

## 2. Event Evidence Provided

- [x] DLC003R candidate validated（intake **24/24 PASS**）
- [x] DLC006R candidate validated（intake **24/24 PASS**）
- [x] evidence_type normalized（`unlock_schedule_record` · `shareholder_change_announcement`）
- [x] raw CNINFO labels preserved in descriptions（CNINFO 限售股上市流通公告 · CNINFO 简式权益变动报告书）
- [x] DLC003R `event_evidence_type` 已填写
- [x] DLC003R `event_evidence_description` 已填写
- [x] DLC003R `event_date_or_period` 已填写
- [x] DLC003R `source_reference` 已填写（人工内部记录 · **非 web 抓取**）
- [x] DLC006R 同上四项已填写
- [x] `human_provided=true` on candidate template

---

## 3. Replacement Universe Reviewed

- [x] replacement universe filled → [filled universe](cninfo_d_class_tiny_live_replacement_universe_filled.csv)
- [x] [replacement universe draft](cninfo_d_class_tiny_live_replacement_universe_draft.csv) 保留为历史草稿（**未删除**）
- [x] DLC003R · DLC006R `expected_behavior=captured_normal`
- [x] baseline cases DLC001/002/004/005/007 保持 reference only

---

## 4. Prior Artifacts Preserved

- [x] original v1 universe untouched → [original v1 universe](cninfo_d_class_phase1_tiny_live_universe.csv) **未修改**
- [x] calibrated universe untouched → [calibrated universe](cninfo_d_class_phase1_tiny_live_universe_calibrated.csv) **未修改**
- [x] v1 execution report **未修改**
- [x] v2 execution report **未修改**
- [x] historical DLC003/DLC006 evidence **保留**（300009 · 000550 校准记录不撤销）

---

## 5. Output Root Isolated

- [x] 未来输出根 = `outputs/validation/cninfo_d_class_known_event_replacement_validation/`
- [x] v1/v2 输出根 **写保护**

---

## 6. Request Cap Defined

- [x] replacement validation request cap 已定义（见 [runner extension design](../plans/cninfo_d_class_known_event_replacement_runner_extension_design.md)）
- [x] bounded probe 策略已文档化
- [x] early stop 规则已确认

---

## 7. No DB / MinIO / RAG

- [x] no CNINFO during approval preparation
- [x] no web lookup during approval preparation
- [x] DB write = **0**
- [x] MinIO write = **0**
- [x] RAG run = **0**
- [x] harvest = **no**
- [x] verified / production_ready = **no**

---

## 8. Live Path Implementation（Offline Prep）

- [x] live path implemented（dry-run + bounded probe live logic）
- [x] approval flag required for `--live`
- [x] request caps enforced（DLC003R ≤ 24 · DLC006R ≤ 20 · total ≤ 44）
- [x] only DLC003R/DLC006R probed in live mode
- [x] baseline rows reference-only（0 CNINFO）
- [x] original DLC003/DLC006 blocked in replacement universe
- [x] output root isolated
- [x] v1/v2 reports write-blocked
- [x] live-path tests passed（**22/22** · mock CNINFO only）
- [x] CNINFO calls during implementation = **0**
- [x] DB/MinIO/RAG disabled

---

## 9. Explicit Approval Required

- [x] [command draft](../plans/cninfo_d_class_known_event_replacement_validation_command_draft.md) 已更新（live command · **NOT APPROVED**）
- [x] [live implementation summary](cninfo_d_class_known_event_replacement_live_implementation_summary.md) 已准备
- [x] [planning document](../plans/cninfo_d_class_known_event_replacement_case_plan.md) 已阅读
- [ ] 用户将显式提供 `--approve-d-class-known-event-replacement-validation`（**待未来真实 live 前**）
- [x] live 路径已实现 · **本回合未执行真实 live**
- [x] explicit human approval still required before live validation
- [x] 本 checklist 全部勾选 **不等于** live 批准

---

## 10. Gate

```text
approval_status = NOT_APPROVED
approved_for_live = false
d_class_known_event_replacement_case_planning_gate = READY_FOR_HUMAN_CANDIDATES
d_class_known_event_candidate_intake_gate = HUMAN_CANDIDATE_VALIDATED
d_class_known_event_replacement_validation_package_gate = READY_FOR_APPROVAL
d_class_known_event_replacement_runner_extension_gate = READY_FOR_APPROVAL
d_class_known_event_replacement_live_implementation_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

**approved_for_live = false**

**CNINFO calls（本回合）：0** · **web lookup = 0** · **live/rerun/harvest = 0**

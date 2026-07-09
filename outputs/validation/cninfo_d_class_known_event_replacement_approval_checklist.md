# CNINFO D 类 Known Event Replacement — Approval Checklist

_生成时间：2026-07-09_

> **状态：NOT APPROVED** · **无 CNINFO** · **不是 verified**

---

## 1. Human Candidate Company Codes Provided

- [ ] DLC003R `company_code` 已人工填写（**非 agent 发明**）
- [ ] DLC003R `company_name` 已人工填写
- [ ] DLC006R `company_code` 已人工填写（**非 agent 发明**）
- [ ] DLC006R `company_name` 已人工填写
- [ ] placeholder 行 `*_CANDIDATE_REQUIRED` 已替换或标记 skip

---

## 2. Event Evidence Provided

- [ ] DLC003R `event_evidence_type` 已填写
- [ ] DLC003R `event_evidence_description` 已填写
- [ ] DLC003R `event_date_or_period` 已填写
- [ ] DLC003R `source_reference` 已填写（人工内部记录 · **非 web 抓取**）
- [ ] DLC006R 同上四项已填写
- [ ] `human_provided=true` on candidate template

---

## 3. Replacement Universe Reviewed

- [ ] [replacement universe draft](cninfo_d_class_tiny_live_replacement_universe_draft.csv) 已审核
- [ ] DLC003R · DLC006R `expected_behavior=captured_normal`
- [ ] baseline cases DLC001/002/004/005/007 保持 reference only

---

## 4. Prior Artifacts Preserved

- [ ] [calibrated universe](cninfo_d_class_phase1_tiny_live_universe_calibrated.csv) **未修改**
- [ ] [original v1 universe](cninfo_d_class_phase1_tiny_live_universe.csv) **未修改**
- [ ] v1 execution report **未修改**
- [ ] v2 execution report **未修改**

---

## 5. Output Root Isolated

- [ ] 未来输出根 = `outputs/validation/cninfo_d_class_known_event_replacement_validation/`
- [ ] v1/v2 输出根 **写保护**

---

## 6. Request Cap Defined

- [ ] replacement validation request cap 已定义（未来 runner）
- [ ] bounded probe 策略已文档化
- [ ] early stop 规则已确认

---

## 7. No DB / MinIO / RAG

- [ ] DB write = **0**
- [ ] MinIO write = **0**
- [ ] RAG run = **0**
- [ ] harvest = **no**
- [ ] verified / production_ready = **no**

---

## 8. Explicit Approval Required

- [ ] [command draft](../plans/cninfo_d_class_known_event_replacement_validation_command_draft.md) 已阅读
- [ ] [planning document](../plans/cninfo_d_class_known_event_replacement_case_plan.md) 已阅读
- [ ] 用户将显式提供 `--approve-d-class-known-event-replacement-validation`
- [ ] runner 实现完成前 **禁止 live**
- [ ] 本 checklist 全部勾选 **不等于** live 批准

---

## 9. Gate

```text
d_class_known_event_replacement_case_planning_gate = READY_FOR_HUMAN_CANDIDATES
```

**NOT APPROVED** · **NOT PASS** · **NOT live_ready** · **NOT verified**

**CNINFO calls（本回合）：0**

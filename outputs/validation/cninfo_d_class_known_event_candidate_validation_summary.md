# CNINFO D 类 Known Event Candidate Intake Validation Summary

_生成时间：2026-07-09 08:36:31 UTC_

> **性质：** 离线 intake 校验 · **CNINFO calls = 0** · **web lookup = 0** · **live/rerun/harvest = 0** · **输入文件未修改**

## Result

| 指标 | 值 |
|------|-----|
| candidate_validation_status | **HUMAN_CANDIDATE_VALIDATED** |
| intake_gate | **d_class_known_event_candidate_intake_gate = HUMAN_CANDIDATE_VALIDATED** |
| candidates | 2 |
| checks PASS | 24 |
| checks FAIL | 0 |
| CNINFO calls | **0** |
| web lookup | **0** |
| live / rerun / harvest | **0** |

## Evidence Type Normalization

原始 CNINFO 中文披露标签保留在 `event_evidence_description` 与 `notes` 中；`event_evidence_type` 使用既有内部枚举，**未扩展** `ALLOWED_EVIDENCE_TYPES` 白名单。

| replacement_case_id | 原始 CNINFO 标签（保留于 description/notes） | 规范化 event_evidence_type |
|---------------------|---------------------------------------------|---------------------------|
| DLC003R | CNINFO 限售股上市流通公告 | `unlock_schedule_record` |
| DLC006R | CNINFO 简式权益变动报告书 | `shareholder_change_announcement` |

## Per-Case

| replacement_case_id | company_code | company_name | event_evidence_type | candidate_status | validation |
|---------------------|--------------|--------------|---------------------|------------------|------------|
| DLC003R | 688671 | 碧兴物联 | unlock_schedule_record | human_candidate_provided | **validated** |
| DLC006R | 301259 | 艾布鲁 | shareholder_change_announcement | human_candidate_provided | **validated** |

## Gate

```text
d_class_known_event_candidate_intake_gate = HUMAN_CANDIDATE_VALIDATED
```

**不是 PASS** · **不是 ready_for_live** · **不是 verified** · **不是 production_ready**

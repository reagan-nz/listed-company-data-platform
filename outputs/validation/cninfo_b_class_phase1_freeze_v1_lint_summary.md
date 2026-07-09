# CNINFO B 类 Phase 1 Freeze v1 Lint Summary

_生成时间：2026-07-09 03:35:54 UTC_

> **性质：** 离线 lint；无 CNINFO；无 live；无 PDF 下载。

## Gate

```text
b_class_phase1_freeze_v1_implementation_gate = PASS_OFFLINE
```

## Results

| 指标 | 值 |
|------|-----|
| checks run | 9 |
| passed | 9 |
| failed | 0 |

## Rule Details

| rule_id | description | result | detail |
|---------|-------------|--------|--------|
| R-P1-001 | required field count = 15 | PASS | found 15 required rows |
| R-P1-002 | all signoff required fields appear in field catalog | PASS | all 15 present |
| R-P1-003 | no PDF body parsing / embedding fields in Phase1 catalog | PASS | none found |
| R-P1-004 | endpoint catalog has exactly 4 phase1_in_scope endpoints | PASS | count=4 ids=['EP001', 'EP002', 'EP004', 'EP005'] |
| R-P1-005 | all endpoint live_validation_status = not_run | PASS | all not_run |
| R-P1-006 | registry YAML contains Phase1 in_scope source entries | PASS | cninfo_periodic_report_pdf and cninfo_general_announcement_pdf present |
| R-P1-007 | no registry source marked verified | PASS | all verified=false |
| R-P1-008 | no registry source marked testing_stable_sample | PASS | none |
| R-P1-009 | phase1 fixture skeleton files exist | PASS | 3 fixtures present |


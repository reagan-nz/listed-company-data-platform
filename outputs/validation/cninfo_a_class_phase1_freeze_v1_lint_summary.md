# CNINFO A 类 Phase 1 Freeze v1 Lint Summary

_生成时间：2026-07-09 06:15:15 UTC_

> **性质：** 离线 lint（freeze v1 implementation）；无 CNINFO；无 live；无 PDF 下载。

## Gate

```text
a_class_phase1_freeze_v1_lint_gate = PASS_OFFLINE
```

## Results

| 指标 | 值 |
|------|-----|
| checks run | 14 |
| passed | 14 |
| failed | 0 |

## Rule Details

| rule_id | description | result | detail |
|---------|-------------|--------|--------|
| R-AF1-001 | field catalog counts match freeze v1 contract | PASS | required=22 recommended=12 future=4 removed=2 |
| R-AF1-002 | field catalog covers exactly 3 objects | PASS | objects=['document_lineage', 'report_document', 'report_period_snapshot'] |
| R-AF1-003 | registry YAML defines 3 object mappings | PASS | objects=['document_lineage', 'report_document', 'report_period_snapshot'] |
| R-AF1-004 | registry has 3 phase1_in_scope sources | PASS | count=3 ids=['cninfo_a_class_periodic_report_annual', 'cninfo_a_class_periodic_report_semi_annual', 'cninfo_a_class_periodic_report_quarterly'] |
| R-AF1-005 | no registry source marked verified | PASS | all verified=false |
| R-AF1-006 | registry live_validation_status = not_run | PASS | registry=not_run |
| R-AF1-007 | no registry source marked testing_stable_sample | PASS | none |
| R-AF1-008 | fixtures contain all freeze v1 required fields per object | PASS | all required fields present |
| R-AF1-009 | removed fields (notes, mime_type) absent from fixtures | PASS | none |
| R-AF1-010 | future fields absent from phase1 normalized fixture payloads | PASS | none |
| R-AF1-011 | object relationships valid (document_id and company_code aligned) | PASS | linked via a_doc_fixture_999001_2024_annual |
| R-AF1-012 | status enums valid for Phase1 freeze v1 | PASS | all enums valid |
| R-AF1-013 | fixtures declare offline freeze_v1 validation metadata | PASS | all 3 fixtures ok |
| R-AF1-014 | no PDF parser / embedding fields in fixtures | PASS | none found |


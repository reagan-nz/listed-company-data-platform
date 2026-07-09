# CNINFO D-class Phase 1 Freeze v1 Lint Summary

_Generated: 2026-07-09 06:27:44 UTC_

**Gate:** `d_class_phase1_freeze_v1_lint_gate = PASS`
**Checks:** 12/12 PASS
**CNINFO calls:** 0

| Rule | Description | Result | Detail |
|------|-------------|--------|--------|
| R-D-FV1-001 | freeze v1 field catalog counts match matrix | PASS | rows=79 levels={'required': 49, 'recommended': 25, 'future': 3, 'removed': 2} |
| R-D-FV1-002 | field catalog aligns with decision matrix | PASS | missing=0 extra=0 |
| R-D-FV1-003 | removed fields absent from all fixtures | PASS | none |
| R-D-FV1-004 | future fields absent from all fixtures | PASS | none |
| R-D-FV1-005 | DC001-DC007 ready-case fixtures exist | PASS | count=7 |
| R-D-FV1-006 | captured fixtures include component required fields | PASS | all captured cases ok |
| R-D-FV1-007 | empty_but_valid fixtures follow quality policy | PASS | DC001+DC004 ok |
| R-D-FV1-008 | event/quality/lineage enums valid on ready cases | PASS | all valid |
| R-D-FV1-009 | lineage required fields valid on ready cases | PASS | all ok |
| R-D-FV1-010 | registry phase1_freeze_v1 mapping valid | PASS | registry ok |
| R-D-FV1-011 | DC007 needs_review case valid | PASS | DC007 captured+needs_review |
| R-D-FV1-012 | all fixtures declare cninfo_called=false | PASS | cninfo_called=0 |

---

Offline only; no live; no harvest.

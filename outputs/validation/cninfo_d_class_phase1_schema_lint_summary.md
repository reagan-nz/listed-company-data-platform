# CNINFO D 类 Phase 1 Schema Lint 摘要

_生成时间：2026-07-09 06:06:30 UTC_

> **性质：** 离线 lint；CNINFO 请求 **0**

## 结果

| 指标 | 值 |
|------|-----|
| checks | 10 |
| pass | 10 |
| fail | 0 |
| gate | **`d_class_phase1_schema_lint_gate = PASS`** |

## 规则明细

| rule_id | description | pass | detail |
|---------|-------------|------|--------|
| R-D-P1-001 | field matrix covers all 7 Phase1 components | PASS | components=7 |
| R-D-P1-002 | quality_status required on all 7 components | PASS | all required |
| R-D-P1-003 | no verified/testing_stable_sample fields in contract | PASS | none |
| R-D-P1-004 | phase1 fixture files exist | PASS | count=3 |
| R-D-P1-005 | market_event envelope required fields present | PASS | 3/3 fixtures ok |
| R-D-P1-006 | component required fields present in fixtures | PASS | 3 fixture payloads ok |
| R-D-P1-007 | event envelope aligns with component payload | PASS | relations valid |
| R-D-P1-008 | quality_status enum valid | PASS | enum=['blocked', 'caveat', 'needs_review', 'pass'] |
| R-D-P1-009 | event_status enum valid | PASS | enum=['captured', 'empty_but_valid', 'failed', 'pending'] |
| R-D-P1-010 | source endpoint mapping matches registry and fixtures | PASS | 7 registry + 3 fixtures aligned |

## 红线

- **CNINFO calls = 0**
- **no live / harvest / PDF**

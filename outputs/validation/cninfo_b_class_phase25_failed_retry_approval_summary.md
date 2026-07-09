# CNINFO B 类 Phase 2.5 Failed-case Isolated Retry — Approval Summary

_生成时间：2026-07-09_

> **性质：** 5-case isolated retry 批准包准备完成；**无 CNINFO** · **无 live** · **NOT APPROVED for execution**

---

## Gate

```text
b_class_phase25_failed_retry_planning_gate = READY_FOR_APPROVAL
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Context

| 项 | 值 |
|----|-----|
| Phase 2.5 cases | **50** |
| acceptable | **45** |
| failed | **5** |
| closure gate | `PASS_WITH_CAVEAT` |
| schema_impact | **none** |
| quality_impact | **retry_needed** |

---

## Retry Scope

| case_id | company | failure_type | retry_priority |
|---------|---------|--------------|----------------|
| B25E003 | 工商银行 | network_timeout | high |
| B25E008 | 中兴通讯 | proxy_503 | high |
| B25E032 | 传音控股 | network_timeout | high |
| B25E039 | 比亚迪 | ep002_orgid_resolution_failed | medium |
| B25E040 | 牧原股份 | ep002_orgid_resolution_failed | medium |

**45 successful cases excluded** — no rerun

---

## Deliverables

| 文档 | 路径 |
|------|------|
| retry universe | [cninfo_b_class_phase25_failed_retry_universe.csv](cninfo_b_class_phase25_failed_retry_universe.csv) |
| command draft | [cninfo_b_class_phase25_failed_retry_command_draft.md](../plans/cninfo_b_class_phase25_failed_retry_command_draft.md) |
| approval checklist | [cninfo_b_class_phase25_failed_retry_approval_checklist.md](cninfo_b_class_phase25_failed_retry_approval_checklist.md) |
| package summary | [cninfo_b_class_phase25_failed_retry_package_summary.md](cninfo_b_class_phase25_failed_retry_package_summary.md) |
| dry-run report | [b_class_phase25_failed_retry_dryrun_report.csv](cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_dryrun_report.csv) |
| dry-run summary | [b_class_phase25_failed_retry_dryrun_summary.md](cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_dryrun_summary.md) |

---

## Configuration

| 项 | 值 |
|----|-----|
| runner | `lab/run_cninfo_b_class_phase25_expansion_validation.py` |
| mode flag | `--retry-failed-only` |
| approval flag | `--approve-b-class-phase25-failed-retry` |
| output root | `outputs/validation/cninfo_b_class_phase25_failed_retry/` |
| dry-run result | **5/5 planned_ok** · CNINFO **0** |
| tests | **14/14 PASS** |

---

## Safety

- metadata + URL lineage only
- PDF download **0** · PDF parse **0** · OCR **0** · extraction **0**
- DB **0** · MinIO **0** · RAG **0**
- verified **false** · production_ready **false**

---

## Next Step（须人工）

1. 审阅 dry-run report（5 cases · all `planned_ok`）
2. 批准 retry scope + output isolation
3. 未来回合：`--retry-failed-only --live --approve-b-class-phase25-failed-retry`

**Never：** verified · production_ready · 45-case rerun · 100-company expansion

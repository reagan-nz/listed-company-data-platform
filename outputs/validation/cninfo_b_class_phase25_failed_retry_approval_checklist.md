# CNINFO B 类 Phase 2.5 Failed-case Isolated Retry — Approval Checklist

_生成时间：2026-07-09_

> **性质：** 人工批准前检查清单 · **NOT APPROVED** · **无 live**

---

## Closure Prerequisites

- [x] Phase 2.5 closure reviewed（[closure review](../plans/cninfo_b_class_phase25_expansion_closure_review.md)）
- [x] `b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT`
- [x] `b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT`
- [x] 5 failed cases confirmed（[triage](cninfo_b_class_phase25_failed_case_triage.csv)）
- [x] 45 successful cases excluded from retry universe
- [x] schema_impact = **none**（非 schema failure）
- [x] quality_impact = **retry_needed**

---

## Retry Universe

- [x] Universe size = **5** only
- [x] Case IDs: B25E003 · B25E008 · B25E032 · B25E039 · B25E040
- [x] `retry_include = yes` for all 5
- [x] Original `announcement_type` and `target_endpoint` preserved
- [x] No replacement cases invented
- [x] No successful-case inclusion

---

## Output Isolation

- [x] Retry output root: `outputs/validation/cninfo_b_class_phase25_failed_retry/`
- [x] Phase 2.5 original output root write-blocked
- [x] Phase 1 / TLC002 / Phase 2 / C-class outputs untouched

---

## Safety Boundaries

- [x] metadata only
- [x] URL lineage only
- [x] No PDF download
- [x] No PDF parse
- [x] No OCR
- [x] No section extraction
- [x] No DB write
- [x] No MinIO write
- [x] No RAG
- [x] No verified
- [x] No production_ready
- [x] No testing_stable_sample upgrade

---

## Runner & Tests

- [x] Runner extended with `--retry-failed-only`
- [x] Approval flag placeholder: `--approve-b-class-phase25-failed-retry`
- [x] Dry-run completed（CNINFO **0**）
- [x] Tests **14/14 PASS**

---

## Explicit User Approval Required

- [ ] Human signoff on 5-case retry scope
- [ ] Human signoff on isolated output root
- [ ] Human signoff on metadata-only boundary
- [ ] `--approve-b-class-phase25-failed-retry` issued for live retry

**Until all checked:** **NOT APPROVED for live execution**

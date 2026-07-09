# CNINFO B 类 Phase 2.5 Expansion — Closure Summary

_生成时间：2026-07-09_

> **性质：** Phase 2.5（50 家）**收口完成**；**无 CNINFO** · **无 live** · **不是 verified**

---

## Final Result

| 指标 | 值 |
|------|-----|
| cases | **50** |
| acceptable | **45** |
| failed | **5** |
| needs_review | **5** |
| empty_but_valid | **0** |
| CNINFO requests (live batch) | **93** |
| CNINFO requests (closure round) | **0** |

---

## Endpoint Validation

| Endpoint | Hits |
|----------|------|
| EP001 hisAnnouncement/query | **45** |
| EP002 topSearch/query | **48** |
| EP004 cninfo_periodic_report_pdf | **25** |
| EP005 cninfo_general_announcement_pdf | **25** |

---

## URL Lineage（acceptable cases）

| 指标 | 值 |
|------|-----|
| pdf_url_present | **45/45** |
| adjunct_url_present | **45/45** |
| Acceptable status | found / pass / discovered |

---

## Failed Cases（5）

| case_id | company | failure |
|---------|---------|---------|
| B25E003 | 工商银行 | network_timeout |
| B25E008 | 中兴通讯 | proxy_503 |
| B25E032 | 传音控股 | network_timeout |
| B25E039 | 比亚迪 | ep002_orgid_resolution_failed |
| B25E040 | 牧原股份 | ep002_orgid_resolution_failed |

**Triage：** schema_impact **none** · quality_impact **retry_needed** · **非 schema failure**

---

## Markets Covered

SSE主板 **27** · SZSE主板 **13** · 创业板 **5** · 科创板 **5**

---

## Safety

| 项 | 值 |
|----|-----|
| PDF download | **0** |
| PDF parsing | **0** |
| DB | **0** |
| MinIO | **0** |
| RAG | **0** |
| verified | **false** |
| production_ready | **false** |
| testing_stable_sample upgrade | **none** |

---

## Output Isolation

| 根 | 状态 |
|----|------|
| `cninfo_b_class_phase25_expansion/` | Phase 2.5 live 产物 |
| Phase 1 tiny live | **unchanged** |
| TLC002 retry | **unchanged** |
| Phase 2 expansion | **unchanged** |
| C-class | **`SNAPSHOT_GENERATED_QA_REVIEW`** |

---

## Gates

```text
b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT
b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT  (保持)
b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT       (保持)
b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT       (保持)
```

### Reason for PASS_WITH_CAVEAT

- **45/50** acceptable meets threshold
- failures are network/proxy/orgId resolution issues — **no schema failure**
- all endpoint families covered（EP001 · EP002 · EP004 · EP005）
- URL lineage discovered for all **45** acceptable cases
- no PDF download · no PDF parsing
- no DB / MinIO / RAG
- still **limited Phase 2.5 expansion only**（50 家）
- **not verified** · **not production_ready**

**Never use：** `PASS` · `verified` · `production_ready` · `testing_stable_sample`

---

## Artifacts

| 文档 | 路径 |
|------|------|
| closure review | [cninfo_b_class_phase25_expansion_closure_review.md](../plans/cninfo_b_class_phase25_expansion_closure_review.md) |
| failed-case triage | [cninfo_b_class_phase25_failed_case_triage.csv](cninfo_b_class_phase25_failed_case_triage.csv) |
| retry planning note | [cninfo_b_class_phase25_failed_retry_planning_note.md](../plans/cninfo_b_class_phase25_failed_retry_planning_note.md) |
| closure metrics | [cninfo_b_class_phase25_expansion_closure_metrics.csv](cninfo_b_class_phase25_expansion_closure_metrics.csv) |
| execution report | [b_class_phase25_expansion_report.csv](cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_report.csv) |
| execution summary | [b_class_phase25_expansion_summary.md](cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_summary.md) |
| next-step recommendation | [cninfo_b_class_phase25_next_step_recommendation.md](../plans/cninfo_b_class_phase25_next_step_recommendation.md) |

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- A-class: unchanged
- D-class: unchanged
- CNINFO calls during closure: **0**

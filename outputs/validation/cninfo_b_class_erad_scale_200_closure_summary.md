# CNINFO B 类 Era D ~200 — Closure Summary

_生成时间：2026-07-10_

> **性质：** offline closure review · **无 CNINFO** · **无 live rerun** · **不是 verified** · **不是 production_ready**

---

## Effective Result

| 指标 | 值 |
|------|-----|
| universe executed | **200/200** |
| **effective accepted** | **198/200** |
| **unresolved** | **2**（network_error） |
| CNINFO（live，已发生） | **397**（cap ≤480） |
| closure review CNINFO | **0** |

---

## Cohort Split

| Cohort | Total | Effective accepted | Unresolved |
|--------|-------|-------------------|------------|
| retained_phase3（BD2E001–100 · live_refresh） | **100** | **98** | **2**（BD2E090 · BD2E092） |
| new_expansion（BD2E101–200 · fresh_metadata） | **100** | **100** | **0** |

---

## Unresolved Cases

| case_id | company_code | cohort | failure_class | phase3_source |
|---------|--------------|--------|---------------|---------------|
| BD2E090 | 000807 | retained_phase3 | network_error | B3E090 |
| BD2E092 | 300033 | retained_phase3 | network_error | B3E092 |

详见 [unresolved ledger](cninfo_b_class_erad_scale_200_unresolved_case_ledger.csv)。

---

## Live Artifacts（reference only）

- [live report](cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_report.csv)
- [live summary](cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_summary.md)
- [quality report](cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_quality_report.csv)
- [live execution summary](cninfo_b_class_erad_scale_200_live_execution_summary.md)
- raw_metadata × **200** under `cninfo_b_class_erad_scale_200/raw_metadata/`

---

## Isolation & Red Lines

- Phase 3 expansion / failed-retry / retry_v2 production roots: **untouched**
- A/C/D live roots: **untouched**
- PDF / OCR / extraction / DB / MinIO / RAG: **0**
- verified: **no**
- production_ready: **no**

---

## Gates

```text
b_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT
b_class_erad_scale_200_closure_gate = PASS_WITH_CAVEAT
```

**NOT bare PASS** · **NOT verified** · **NOT production_ready**

---

## Closure Decision

见 [closure decision](cninfo_b_class_erad_scale_200_closure_decision.md)：**close Era D scale-200 track with caveat NOW**。

Optional 2-case retry：**deferred**（separate approval · 见 [optional retry brief](cninfo_b_class_erad_scale_200_optional_retry_brief.md)）。

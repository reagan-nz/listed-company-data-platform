# CNINFO B 类 Era D ~200 — Live Execution Summary

_生成时间：2026-07-10_

> **Human approval phrase present** · **isolated live executed** · **不是 verified** · **不是 production_ready**

---

## Approval

```
approval_status = APPROVED_FOR_LIVE_EXECUTION
approved_for_live = true
approval_phrase = I approve B-class Era D scale-200 live metadata validation.
```

---

## Execution

| 指标 | 值 |
|------|-----|
| mode | `erad_scale_200_live` |
| universe | **200**（BD2E001–BD2E200） |
| executed | **200/200** |
| retained cohort | **100**（live_refresh） |
| new cohort | **100**（fresh_metadata） |
| CNINFO requests | **397**（cap ≤480） |
| found | **198** |
| acceptable | **198** |
| failed | **2**（network_error） |
| PDF / OCR / extraction / DB / MinIO / RAG | **0** |

**Failed cases:**

| case_id | company_code | cohort | failure |
|---------|--------------|--------|---------|
| BD2E090 | 000807 | retained_phase3 | network_error |
| BD2E092 | 300033 | retained_phase3 | network_error |

---

## Artifacts

- [live report](cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_report.csv)
- [live summary](cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_summary.md)
- [quality report](cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_quality_report.csv)
- raw_metadata × **200** under `outputs/validation/cninfo_b_class_erad_scale_200/raw_metadata/`

---

## Isolation

- Phase 3 expansion / failed-retry / retry_v2 production roots: **untouched**
- A/C/D live roots: **untouched**
- Output root: `outputs/validation/cninfo_b_class_erad_scale_200/` only

---

## Gate

```text
b_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT
```

Threshold **≥180/200 acceptable** → **198/200** met.

**NOT PASS** · **NOT verified** · **NOT production_ready**

---

## Next Step

Optional isolated retry for **BD2E090** / **BD2E092** (network_error) · closure review · explicit-path commit decision.

# CNINFO A 类 Era D ~200 — Live Execution Summary

_生成时间：2026-07-10_

> **isolated live metadata validation** · **CNINFO 423** · **无 PDF** · **不是 verified** · **不是 production_ready**

---

## Approval

| 项 | 值 |
|----|-----|
| approval phrase | **I approve A-class Era D scale-200 live execution.** |
| approval_status | **APPROVED**（this session） |
| approved_for_live | **true**（executed） |

---

## Execution Result

| 指标 | 值 |
|------|-----|
| mode | `erad_a_scale_200_live` |
| universe | **200**（50 retained + 150 new） |
| acceptable | **192/200** |
| failed (`not_found`) | **8** |
| retained acceptable | **50/50** |
| new acceptable | **142/150** |
| CNINFO requests | **423**（cap ≤ **480**） |
| matching_logic | **v2** |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |
| runtime | ~**12.6 min** |
| exit code | **0** |

---

## Execution Gate

```text
a_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT
```

Threshold: ≥180/200 acceptable → **PASS_WITH_CAVEAT**（192 ≥ 180）

**不是 PASS** · **不是 verified** · **不是 production_ready**

---

## Failed Cases（8 · all new_erad）

| case_id | company_code | report_type | expected_period | notes |
|---------|--------------|-------------|-----------------|-------|
| AD2E066 | 600930 | annual_report | 2024-12-31 | no v2 matching periodic report; records=0 |
| AD2E088 | 001393 | annual_report | 2024-12-31 | no v2 matching periodic report; records=0 |
| AD2E119 | 603370 | annual_report | 2024-12-31 | no v2 matching periodic report; records=0 |
| AD2E121 | 603737 | annual_report | 2024-12-31 | no v2 matching periodic report; records=1 |
| AD2E122 | 688636 | annual_report | 2024-12-31 | no v2 matching periodic report; records=1 |
| AD2E146 | 688755 | annual_report | 2024-12-31 | no v2 matching periodic report; records=0 |
| AD2E185 | 600849 | quarterly_report_q1 | 2024-03-31 | no v2 matching periodic report; records=2 |
| AD2E190 | 603409 | quarterly_report_q1 | 2024-03-31 | no v2 matching periodic report; records=0 |

---

## Output Artifacts

| 产物 | 路径 |
|------|------|
| live report | `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_report.csv` |
| quality report | `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_quality_report.csv` |
| live summary | `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_summary.md` |
| raw metadata | `outputs/validation/cninfo_a_class_erad_scale_200/raw_metadata/AD2E*.json`（**200** files） |

---

## Safety Confirmations

| 检查项 | 状态 |
|--------|------|
| Phase 1 / Phase 2 / Phase 3 production roots | **untouched** |
| A3M017 retry root | **untouched** |
| amend bbc15c3 / cb9f3fc | **no** |
| B / C / D mutation | **no** |
| PDF / OCR / extraction / DB / MinIO / RAG | **no** |
| verified / production_ready | **no** |

---

## Next Step

**Era D ~200 failed-case triage + optional isolated retry planning**（8 `not_found` · new_erad only · offline · separate approval）

# CNINFO A 类 Phase 2 Reachability Precheck Live 摘要

_生成时间：2026-07-09 10:13:33 UTC_

> **性质：** live precheck · orgId only · **不是 verified** · **不是 retry_v3**

## 摘要

| 项 | 值 |
|----|-----|
| mode | precheck_live |
| candidates | **3** |
| orgId resolved | **2** |
| orgId failed | **1** |
| reachable | **2** |
| CNINFO requests | **2** |
| PDF / OCR / extraction / DB / MinIO / RAG | **0** |
| execution gate | **`a_class_phase2_cninfo_reachability_precheck_execution_gate = PASS_WITH_CAVEAT`** |

## Per-Candidate

- APC001 A2M005 (SSE): reachability=reachable · orgId=resolved
- APC002 A2M010 (ChiNext): reachability=unreachable · orgId=failed
- APC003 A2M018 (STAR): reachability=reachable · orgId=resolved

## Interpretation

- CNINFO/orgId reachability **partially recovered** (≥2/3 resolved)
- Next: retry_v3 isolated **planning** for 8 unresolved cases only (**NOT APPROVED**)

**不是 PASS** · **不是 verified** · **不是 production_ready**

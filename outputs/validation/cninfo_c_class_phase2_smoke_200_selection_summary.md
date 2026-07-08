# CNINFO C-Class Phase 2 Smoke 200 Selection Summary

_生成时间：2026-07-08_

> Phase 2 smoke universe 离线选股摘要。**无 CNINFO** · **harvest not started**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Input Pool

| 指标 | count |
|------|-------|
| refreshed_candidate_count | **6124** |
| matched_active_count | **4647** |
| eligible_non_bse_count | **4643** |
| eligible_before_bse_exclusion | **4647** |
| bse_excluded_from_pool | **4** |

---

# Selection

| 项 | 值 |
|----|-----|
| target_size | **200** |
| selected_count | **200** |
| seed | **20260708** |

---

# Distribution

## exchange

| 值 | count |
|-----|-------|
| SZSE | **113** |
| SSE | **87** |

## board

| 值 | count |
|-----|-------|
| sse_main | **66** |
| szse_main | **61** |
| chinext | **52** |
| star | **21** |

## listing_status

| 值 | count |
|-----|-------|
| listed | **193** |
| delisted | **7** |

## security_type

| 值 | count |
|-----|-------|
| __MISSING__ | **200** |

## company_code_prefix

| 值 | count |
|-----|-------|
| 300 | **36** |
| 002 | **35** |
| 600 | **31** |
| 000 | **23** |
| 688 | **21** |
| 603 | **20** |
| 301 | **16** |
| 601 | **12** |
| 605 | **3** |
| 001 | **2** |
| 003 | **1** |

---

# Exclusion Check

| 检查项 | count |
|--------|-------|
| already_in_c_class included | **0** |
| hold included | **0** |
| BSE included | **0** |
| identity_conflict included | **0** |
| manual_review included | **0** |
| duplicate company_code | **0** |

---

# Expected Future Harvest Size

**200 companies × 7 live source calls = 1400 planned cases**

Security source remains observe-only.

---

# Gate

**`phase2_smoke_universe_selection_gate = PASS`**

---

# Execution Status

Harvest not started.

Snapshot not started.

---

# 产物

- [smoke YAML](../../lab/eval_companies_c_class_phase2_smoke_200.yaml)
- [selection matrix](cninfo_c_class_phase2_smoke_200_selection_matrix.csv)

# CNINFO C-Class Phase 3 Batch 500 Selection Summary

_生成时间：2026-07-09_

> Phase 3 batch 500 universe 离线选股摘要。**无 CNINFO** · **harvest not started**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Input Pool

| 指标 | count |
|------|-------|
| refreshed_candidate_count | **6124** |
| primary_pool_count | **4643** |
| eligible_after_exclusions_count | **4145** |

---

# Exclusions

| 类别 | count |
|------|-------|
| already_in_c_class | **863** |
| phase2_smoke_200 | **200** |
| phase2_all_direct_failure | **12** |
| delisted_or_inactive_caveat (in primary) | **316** |
| matched_hold | **26** |
| matched_bse_supported_candidate | **320** |
| matched_bse_legacy_hold | **242** |
| identity_conflict | **10** |
| needs_manual_review | **16** |
| BSE in matched_active | **4** |

---

# Selection

| 项 | 值 |
|----|-----|
| target_size | **500** |
| selected_count | **500** |
| seed | **20260709** |
| batch_id | **phase3_batch_500_001** |

---

# Distribution

## exchange

| 值 | count |
|-----|-------|
| SZSE | **281** |
| SSE | **219** |

## board

| 值 | count |
|-----|-------|
| sse_main | **164** |
| szse_main | **148** |
| chinext | **133** |
| star | **55** |

## listing_status

| 值 | count |
|-----|-------|
| listed | **500** |

## security_type

| 值 | count |
|-----|-------|
| __MISSING__ | **500** |

## company_code_prefix

| 值 | count |
|-----|-------|
| 002 | **91** |
| 300 | **91** |
| 600 | **72** |
| 688 | **55** |
| 603 | **52** |
| 301 | **42** |
| 000 | **41** |
| 601 | **24** |
| 605 | **16** |
| 001 | **12** |
| 003 | **4** |

---

# Exclusion Check

| 检查项 | count |
|--------|-------|
| already_in_c_class included | **0** |
| phase2_smoke included | **0** |
| phase2_failure included | **0** |
| delisted included | **0** |
| 退 / 退市 / *ST included | **0** |
| BSE included | **0** |
| hold included | **0** |
| identity_conflict included | **0** |
| manual_review included | **0** |
| duplicate company_code | **0** |

---

# Expected Future Harvest Size

**500 companies × 7 live source calls = 3500 planned cases**

Security source remains observe-only.

---

# Gate

**`phase3_batch_500_001_universe_selection_gate = PASS`**

---

# Execution Status

Harvest not started.

Snapshot not started.

---

# 产物

- [batch YAML](../../lab/eval_companies_c_class_phase3_batch_500_001.yaml)
- [selection matrix](cninfo_c_class_phase3_batch_500_001_selection_matrix.csv)

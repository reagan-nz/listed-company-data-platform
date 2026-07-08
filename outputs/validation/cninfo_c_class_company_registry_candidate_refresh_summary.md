# CNINFO C-Class Company Registry Candidate Refresh Summary

_生成时间：2026-07-08_

> 离线 registry candidate refresh 摘要。**validation artifact only** · **无 CNINFO** · **无 merge**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Input Counts

| 输入 | count |
|------|-------|
| candidate_draft_count | **6124** |
| reconciliation_result_count | **6124** |
| identity_decision_count | **267** |

---

# Refresh Counts

## classification counts

| classification | count |
|----------------|-------|
| matched_active | **4647** |
| already_in_c_class | **863** |
| matched_hold | **26** |
| matched_bse_supported_candidate | **320** |
| matched_bse_legacy_hold | **242** |
| identity_conflict | **10** |
| needs_manual_review | **16** |
| not_found_in_cninfo | **0** |

## refresh_action counts

| refresh_action | count |
|----------------|-------|
| bse_supported_candidate | **320** |
| conflict_review_required | **10** |
| full_market_active_candidate | **4647** |
| manual_review_required | **16** |
| preserve_high_confidence | **863** |
| preserve_hold | **26** |
| preserve_legacy_hold | **242** |

## refresh_confidence counts

| refresh_confidence | count |
|--------------------|-------|
| high | **863** |
| low | **4647** |
| medium | **588** |
| review | **26** |

## manual_review_required

| 指标 | count |
|------|-------|
| requires_manual_review=true | **26** |

---

# Safety

| 项 | 值 |
|----|-----|
| CNINFO called | **false** |
| merge executed | **false** |
| registry implemented | **false** |

---

# Gate

**`registry_candidate_refresh_dryrun_gate = PASS_WITH_CAVEAT`**

**C-class 状态保持：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# 产物

- [refreshed candidate](cninfo_c_class_company_registry_candidate_refreshed.csv) · **6124** 行
- refreshed CSV 为 **validation artifact only** · registry implementation **deferred**

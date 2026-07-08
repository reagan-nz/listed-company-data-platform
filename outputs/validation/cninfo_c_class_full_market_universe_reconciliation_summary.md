# CNINFO C-Class Full Market Universe Reconciliation Summary

_生成时间：2026-07-08_

> 离线 universe 对账 dry-run 摘要。**仅分类** · **不合并** · **无 CNINFO**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Universe Counts

| Universe | Count |
|----------|-------|
| Era B baseline | **6124** |
| Era C active | **863** |
| Hold | **26** |
| BSE supported（classification） | **320** |
| BSE legacy（classification） | **242** |

---

# Matching Results

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

---

# Identity Risk

| 指标 | count |
|------|-------|
| identity_conflict | **10** |
| needs_manual_review | **16** |

---

# Important Caveat

Era B 6124 and Era C 863 belong to different lineage sources.

Reconciliation result is classification only.

It does not create registry rows.

It does not trigger harvest expansion.

---

# Gate

**`universe_reconciliation_dryrun_gate = PASS_WITH_CAVEAT`**

---

# 产物

- [reconciliation result](cninfo_c_class_full_market_universe_reconciliation_result.csv) · **6124** 行
- [reconciliation plan](../../plans/cninfo_c_class_full_market_universe_reconciliation_plan.md)

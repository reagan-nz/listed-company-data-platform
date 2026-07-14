# CNINFO C 类 Era D — Status-fix-8 Apply Next-Step Recommendation

_生成时间：2026-07-10_

---

## Completed

- **8/8** proposed rows **appended** to production `company_harvest_status.csv`
- Backup: `company_harvest_status.csv.bak_erad_status_fix_8_20260710T080910Z`
- Post-verify: **8/8** `harvest_status=complete` · `post_verify_ok=yes`

---

## Primary Next C-Class Task

### Offline human-review packet for 6 partial-source companies

**Scope（validation-only · no auto-fix · no live unless gaps proven）：**

| company_code | normalized_sources |
|--------------|-------------------|
| 002267 | 6/10 |
| 002710 | 6/10 |
| 301333 | 6/10 |
| 301583 | 6/10 |
| 601206 | 6/10 |
| 688688 | 6/10 |

**Deliverables（未来切片）：**

- `outputs/validation/cninfo_c_class_erad_needs_review_6_human_review_packet.csv`
- Summary + recommended_action per company
- **live_needed = no** unless disk proves missing normalized artifacts

**Do NOT:** auto-append status rows for these 6 without separate triage + approval.

---

## Optional Follow-ups（非必须）

| 项 | 说明 |
|----|------|
| Re-run harvest resume audit | 863_primary needs_review may drop from 58 → 50（ledger 对齐后） |
| C-line retention/index doc | 491+863 snapshot gitignore 纪律 |
| Slice-C-EraD-03b | 仅当单独请求 |

---

## Explicitly NOT Recommended

- Live harvest / resume for 8 or 6
- Snapshot rebuild（Option A HOLD）
- Holdout promotion

---

## Gate

```
c_class_erad_status_fix_8_apply_gate = PASS_WITH_CAVEAT
```

---

## Red Lines

No CNINFO · no live · no unapproved writes · no commit/push

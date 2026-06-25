# Financial audit fix #30 summary

_Generated: 2026-06-25 | docs-only consolidation for #30a–#30g_

## Scope and boundary

This document consolidates the **#30 financial follow-up series**:

- `#30a` broker `not_found_missed` audit tightening
- `#30b` ratio/table audit calibration + `major_subsidiaries` gate
- `#30c` bank ratio extraction helper
- `#30d` broker income / margin recall
- `#30e` financial table plausibility audit hardening
- `#30f` insurer low-n audit hardening
- `#30g` subtype/tag diagnosis only

**Boundary / anti-claims:**

- no full financial rollout
- no full CNINFO rerun
- no SQLite import
- no YAML tag changes
- no non-fin `9.43/11` headline change
- financial extraction is **not** fully signed off
- financial metrics remain **separate** from the non-financial headline

## #30a–#30g changelog

| Step | Theme | Type | Main result | Rollout status |
|---|---|---|---|---|
| `#30a` | broker `not_found_missed` tightening | audit-only | reduced broker over-calls; improved frozen agreement `202/325 -> 226/325` | committed |
| `#30b` | ratio/table calibration + `major_subsidiaries` gate | audit-only | joined agreement `226/325 -> 233/325` | committed |
| `#30c` | bank ratio helper | extraction + targeted sample apply | `6/6` bank-ratio `MISSED` recovered; `0/11` WRONG controls became usable | wider rollout deferred |
| `#30d` | broker income / margin recall | extraction + targeted sample apply | `4/4` confirmed broker `MISSED` recovered; `0/23` negative controls usable | wider rollout deferred |
| `#30e` | table plausibility hardening | audit-only | `18/18` manual-WRONG table targets strict wrong; harness artifact cleaned up | no sample apply |
| `#30f` | insurer low-n semantic hardening | audit-only | `8/8` insurer negatives non-usable; `10/10` positives preserved | no sample apply |
| `#30g` | subtype/tag review | diagnosis-only | reviewed `000402` / `600816` / `600318`; no YAML change | deferred |

## What changed by category

### Audit-only fixes

- `#30a`: broker-specific `not_found_missed` PDF gates reduced false recall hints.
- `#30b`: tightened ratio semantics, table semantics, and improved `major_subsidiaries` treatment.
- `#30e`: tightened financial table plausibility for `loan_structure`, `deposit_structure`, `regional_distribution`, `revenue_by_region`, and `revenue_by_segment`.
- `#30f`: added narrow insurer-only semantic guards for `combined_ratio`, `claims_expense`, `investment_income`, `solvency_ratio`, insurer segment tables/snippets, and insurer business-line snippets.

### Extraction helpers

- `#30c`: bank-only ratio extraction helper for the targeted ratio recall failures.
- `#30d`: broker-only helpers for:
  - segment income extraction
  - deep investment-banking notes fallback
  - margin balance extraction

### Diagnosis-only subtype review

- `#30g`: read-only subtype/tag review for:
  - `000402` 金融街: likely not broker; probably not financial at all
  - `600816` 建元信托: trust-like, not bank
  - `600318` 新力金融: diversified financial holding, not bank
- No YAML or schema tags were changed in `#30g`.

## Validation summary

| Step | Validation result |
|---|---|
| `#30a` | broker `not_found_missed` reduced; frozen joined agreement `202/325 -> 226/325` |
| `#30b` | joined agreement `226/325 -> 233/325` |
| `#30c` | `6/6` bank-ratio `MISSED` recovered; `0/11` WRONG controls became usable; wider rollout deferred |
| `#30d` | `4/4` broker `MISSED` recovered; `0/23` negative controls usable; wider rollout deferred |
| `#30e` | `18/18` manual-WRONG table targets strict wrong; `0/26` controls newly downgraded after harness cleanup |
| `#30f` | `8/8` insurer negative targets non-usable; `10/10` positive controls preserved |
| `#30g` | subtype diagnosis only for `000402` / `600816` / `600318`; no YAML change |

## Metric caveat

`#30` used the frozen `#29` manual calibration sample as a validation anchor.

That means **agreement can decrease even when extraction improves**:

- if a row is manually labeled `MISSED`
- and the new extraction correctly recovers it as `usable`
- the frozen manual-vs-auto agreement metric can go down because the manual label stays `MISSED`

This happened in sample applies such as `#30c` and `#30d`. It should be read as a **frozen-label metric caveat**, not automatically as a regression.

## Deferred work mapped to follow-up issues

| Issue | Topic | Routed work |
|---|---|---|
| `#31` | Financial under-tagging scan / 金融公司漏标扫描 | under-tagging scan; controlled retagging follow-up for `000402` / `600816` / `600318` |
| `#32` | Revenue + rnd residual fixes / 收入与研发字段残留问题 | residual revenue/rnd wrong cells and related scoped fixes |
| `#33` | Multiyear expansion decision / 多年份扩展决策 | 2025 / 2023 / 2022 scope, run naming, and expansion posture |

If subtype retagging is approved later, it should be tracked under **`#31`** or a tightly scoped child task of `#31`.

## Closure posture

`#30` is ready to close as a **financial follow-up tranche**, with the following explicit framing:

- audit hardening delivered
- targeted extraction helpers delivered where low-risk and validated
- subtype/tag caveats diagnosed but **not** auto-changed
- wider financial rollout remains deferred

## Safe-to-commit list

- `outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md`
- `CURRENT_STATUS.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `docs/financial_company_schema.md`
- `docs/evaluation_method.md`
- `outputs/generalization/full_market_2024/stage3_quality_followup_summary.md` (cross-link only)

## Do-not-commit list

- any `company_profile.json`
- any `eval_results.json`
- `financial_audit_sample.csv`
- `financial_audit_population.csv`
- `financial_audit_summary.md`
- any YAML tag changes
- PDFs / `.cache`
- `outputs/db/*.db`

## Related artifacts

- [financial_audit_fix_30a_summary.md](financial_audit_fix_30a_summary.md)
- [financial_audit_fix_30b_summary.md](financial_audit_fix_30b_summary.md)
- [financial_audit_fix_30c_apply_summary.md](financial_audit_fix_30c_apply_summary.md)
- [financial_audit_fix_30d_apply_summary.md](financial_audit_fix_30d_apply_summary.md)
- [financial_audit_fix_30e_dryrun_summary.md](financial_audit_fix_30e_dryrun_summary.md)
- [financial_audit_fix_30f_dryrun_summary.md](financial_audit_fix_30f_dryrun_summary.md)
- [financial_subtype_review_30g.md](financial_subtype_review_30g.md)

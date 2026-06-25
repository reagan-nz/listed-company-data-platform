# Financial audit fix #30f dry-run — insurer field semantic review

_Generated: 2026-06-25 | insurer-only audit dry-run over cached PDFs / current profiles_

## Verdict: **PASS**

| Gate | Result |
|---|---|
| Negative insurer targets are not usable | **PASS** |
| `601336/601628 combined_ratio` become wrong/not usable | **PASS** |
| `601336/601628 claims_expense` become wrong/not usable | **PASS** |
| Positive insurer controls remain usable/partial | **PASS** |
| `601628 revenue_by_segment` is not wrong | **PASS** |
| `601628 major_subsidiaries` is not wrong | **PASS** |
| `601628 main_business_segments` is not wrong | **PASS** |
| No forbidden files modified | **PASS** |

## Files changed

- `lab/strict_audit_financial_full_market.py`
- `lab/financial_audit_fix_30f_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30f_dryrun_summary.md`

## Exact code changes

1. Added insurer-only numeric semantic guards in `lab/strict_audit_financial_full_market.py` for `combined_ratio`, `claims_expense`, `investment_income`, and `solvency_ratio`.
2. Added insurer-only snippet/table semantics for `main_business_segments` and `revenue_by_segment` to reject EV/sensitivity pages and preserve true line-of-business disclosures.
3. Kept the pass audit-only; no extraction helper or field-schema changes were needed.

## Mode

**Audit-only.** No extraction changes were made in `#30f`.

## Insurer negative target table

| Code | Field | Manual | Before strict | After strict | After reason | Fresh strict |
|---|---|---|---|---|---|---|
| 601336 | `investment_income` | WRONG | wrong | **wrong** | insurer investment field only has year/tiny fragment values | wrong |
| 601336 | `claims_expense` | WRONG | wrong | **wrong** | insurer claims field hit surrender/dividend/reserve/product context | wrong |
| 601336 | `combined_ratio` | WRONG | usable | **wrong** | insurer sensitivity/EV page, not combined ratio | wrong |
| 601336 | `revenue_by_segment` | WRONG | wrong | **wrong** | insurer segment field hit EV/sensitivity page | wrong |
| 601336 | `major_subsidiaries` | WRONG | wrong | **wrong** | subsidiary field hit employee/qualifications section | wrong |
| 601336 | `main_business_segments` | WRONG | usable | **wrong** | insurer main-business field hit EV/sensitivity section | wrong |
| 601628 | `claims_expense` | WRONG | partial | **wrong** | insurer claims field hit surrender/dividend/reserve/product context | wrong |
| 601628 | `combined_ratio` | WRONG | usable | **wrong** | insurer sensitivity/EV page, not combined ratio | wrong |

## Insurer positive/control table

| Code | Field | Manual | Before strict | After strict | After reason | Fresh strict |
|---|---|---|---|---|---|---|
| 601336 | `premium_income` | CORRECT | usable | usable | amount label '原保险保费收入' value=170,511 | usable |
| 601336 | `solvency_ratio` | CORRECT | usable | usable | insurer solvency ratio from context value=217.55% | usable |
| 601336 | `embedded_value` | CORRECT | usable | usable | amount label '内含价值' value=2024 | usable |
| 601628 | `premium_income` | PARTIAL | partial | partial | status=partial | partial |
| 601628 | `investment_income` | CORRECT | usable | usable | insurer investment label '投资收益' value=308,251 | usable |
| 601628 | `solvency_ratio` | CORRECT | usable | usable | insurer solvency label '偿付能力充足率' value=207.76% | usable |
| 601628 | `embedded_value` | CORRECT | usable | usable | amount label '内含价值' value=1,401,146 | usable |
| 601628 | `revenue_by_segment` | CORRECT | wrong | partial | insurer line-of-business snippet | partial |
| 601628 | `major_subsidiaries` | CORRECT | usable | usable | subsidiary table/snippet substantive (out-of-region ok, len=278) | usable |
| 601628 | `main_business_segments` | CORRECT | usable | usable | insurer business-line snippet substantive (len=291) | usable |

## Downgraded controls

No positive/control rows were downgraded to `wrong` or another not-usable state.

## n=2 caveat

- Insurer cohort size is only **2** (`601336`, `601628`), so all rules in `#30f` were kept narrow and schema-specific.
- `investment_income` remains somewhat noisy for `601336`; current fix only hardens audit semantics and preserves the confirmed `601628` positive.
- `embedded_value` and `premium_income` were intentionally left extraction-unchanged to avoid low-n overfitting.

## Sample apply recommendation

**No sample apply recommended yet.** `#30f` is audit-only hardening for the insurer low-n cohort; no population rollout should be attempted from this pass alone.

## Safe-to-commit list

- `lab/strict_audit_financial_full_market.py`
- `lab/financial_audit_fix_30f_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30f_dryrun_summary.md`

## Do-not-commit list

- any `company_profile.json`
- `financial_audit_population.csv`
- `financial_audit_summary.md`
- `financial_audit_sample.csv`
- any `eval_results.json`

## Deferred items

- `601336 investment_income`: likely needs insurer-only extraction cleanup if you want the field to become truly usable rather than just non-usable.
- `embedded_value` extraction noise on `601336`: currently tolerated because manual calibration says CORRECT and audit-only tightening would be risky.
- Whether insurer line-of-business premium tables should always count as `revenue_by_segment` remains a low-n schema interpretation choice and should not be generalized beyond the insurer cohort.

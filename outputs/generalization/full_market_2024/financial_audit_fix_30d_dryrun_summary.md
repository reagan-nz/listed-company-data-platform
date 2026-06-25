# Financial audit fix #30d dry-run — broker income / margin recall

_Generated: 2026-06-25 | code-only dry-run on cached PDFs only_

## Verdict: **PASS**

| Gate | Result |
|---|---|
| 4/4 confirmed MISSED positives become strict usable | **PASS** |
| 0/23 ABSENT-OK controls become strict usable | **PASS** |
| 600030 margin_lending_balance remains not usable | **PASS** |
| 601108 IB/AM/proprietary narrative rows remain not usable | **PASS** |
| No profile/eval/population/sample CSV writes | **PASS** |

## Files changed

- `lab/extract_annual_report.py`
- `lab/field_schema.py`
- `lab/financial_audit_fix_30d_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30d_dryrun_summary.md`

## Exact code changes

1. Added broker-only `extract_broker_segment_income()` for `investment_banking_income` and `asset_management_income` with whitespace-tolerant labels, segment-table context checks, comma-amount requirement, and narrative rejects.
2. Added `extract_broker_deep_ib_income()` notes fallback for `investment_banking_income` only, gated by `手续费及佣金` page context and amount ≥ ¥1B.
3. Added `extract_broker_margin_balance()` for MD&A-only `融出资金` asset-composition rows; rejects 利息/净增加/减值/现金流 noise and does not search notes.
4. Wired these broker branches in `extract_field()` before generic numeric extraction.
5. Added narrow secondary anchors in `field_schema.py` for IB/AM net-income labels.

## Positive recovery table

| Code | Field | Before strict | After strict | After page | Value | Pass |
|---|---|---|---|---:|---|---|
| 601878 | `investment_banking_income` | not_found_missed | **usable** | 50 | 投资银行业务=677,073,421.90 | **PASS** |
| 601878 | `asset_management_income` | not_found_missed | **usable** | 51 | 资产管理业务=530,211,137.63 | **PASS** |
| 601878 | `margin_lending_balance` | not_found_missed | **usable** | 53 | 融出资金=24,224,341,732.66 | **PASS** |
| 600030 | `investment_banking_income` | not_found_missed | **usable** | 300 | 投资银行业务净收入=4,159,191,856.95 | **PASS** |

## Negative-control table

| Code | Field | Before strict | After strict | After status | Pass |
|---|---|---|---|---|---|
| 601377 | `brokerage_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601377 | `margin_lending_balance` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601878 | `brokerage_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601878 | `proprietary_trading_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601878 | `risk_control_indicators` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 600369 | `proprietary_trading_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 600369 | `risk_control_indicators` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601990 | `brokerage_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601990 | `asset_management_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601990 | `risk_control_indicators` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601696 | `asset_management_income` | not_found_missed | not_found_missed | not_found | **PASS** |
| 601696 | `margin_lending_balance` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 600030 | `margin_lending_balance` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 600030 | `risk_control_indicators` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601108 | `investment_banking_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601108 | `asset_management_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601108 | `proprietary_trading_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 000783 | `brokerage_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 000783 | `investment_banking_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 000783 | `margin_lending_balance` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601059 | `risk_control_indicators` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601136 | `proprietary_trading_income` | not_found_unverified | not_found_unverified | not_found | **PASS** |
| 601136 | `margin_lending_balance` | not_found_unverified | not_found_unverified | not_found | **PASS** |

## Risk caveats

- Deep IB notes fallback is medium risk on other mega-brokers, but is constrained to fee-note pages and `投资银行业务净收入`/`投行业务净收入` labels with amount ≥ ¥1B.
- Margin parsing intentionally excludes notes, so large consolidated `融出资金` balances in notes remain unavailable by design.
- `brokerage_income` and generic `投资收益` logic were not widened.

## Sample-company apply recommendation: **Yes**

Proceed to a tightly scoped sample-company apply only if you want to persist the 4 broker positive recoveries into profile files.

## Safe-to-commit list

- `lab/extract_annual_report.py`
- `lab/field_schema.py`
- `lab/financial_audit_fix_30d_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30d_dryrun_summary.md`

## Do-not-commit list

- any `company_profile.json`
- `financial_audit_population.csv`
- `financial_audit_summary.md`
- any `eval_results.json`
- PDFs / `.cache` / SQLite

# Financial subtype review #30g

## Scope and guardrails

- Scope: read-only subtype/tag review for `000402`, `600816`, `600318`.
- Inputs inspected: YAML financial flag, stored `company_profile.json`, sampled/population audit rows, `field_schema.py`, profile resolution logic, and annual-report PDF business descriptions.
- No YAML, code, profile, eval, extraction, apply, or population changes were made.
- Recommendations below are diagnostic only and should not be auto-applied without a separate approved task.

## Current schema vs recommendation

| Code | Name | Board | YAML financial | Current schema | Recommended direction | Confidence |
|---|---|---|---|---|---|---|
| `000402` | 金融街 | `szse_main` | `true` | `broker` | likely remove broker tagging; either `industrial` / `financial:false`, or at most defer to human review before any reclass | medium-high |
| `600816` | 建元信托 | `sse_main` | `true` | `bank` | keep financial, move away from `bank`; near-term target should be `other_financial`, longer-term consider `trust_profile` | high |
| `600318` | 新力金融 | `sse_main` | `true` | `bank` | keep financial, move away from `bank`; near-term target should be `other_financial`, longer-term consider `holding/diversified_financial_profile` | high |

## Per-company evidence summary

### `000402` 金融街

- YAML currently marks the company `financial: true`; stored `schema_profile` is `broker`.
- Stored profile evidence is strongly real-estate oriented:
  - PDF page 5 states the company's main business changed in 2000 to `房地产开发和经营`.
  - Industry discussion on page 9 is explicitly `房地产行业形势分析`.
  - `major_subsidiaries` shows subsidiaries such as `廊坊市融方房地产开发有限公司`.
  - `main_business_segments` contains `房产开发`, `物业出租`, `物业经营`, `其他收入`.
- Broker-fit is poor:
  - `brokerage_income`, `investment_banking_income`, `asset_management_income`, `risk_control_indicators`, `revenue_by_segment` are all `not_found`.
  - `margin_lending_balance` is a false hit on shareholder credit-trading account text, not broker balance disclosure.
  - `proprietary_trading_income` is only a weak `投资收益` hit tied to asset disposal/investment loss, not broker self-operation disclosure.
- Conclusion: current `broker` schema does not fit the company's disclosed identity.

### `600816` 建元信托

- YAML currently marks the company `financial: true`; stored `schema_profile` is `bank`.
- Business identity is clearly trust-company oriented:
  - MD&A says `信托行业作为国家金融体系的关键一环`.
  - Industry discussion says 2024 is the first full year after the trust-industry `三分类新规`.
  - The report repeatedly discusses `信托公司`, `信托本源`, family-service trust, risk-disposal service trust, and structured entities.
- Bank-fit is mixed and unstable:
  - Some generic financial fields are valid: `mda`, `industry_discussion`, `risk_factors`.
  - Some amount fields can still surface from statements: `net_interest_income`, `non_interest_income`.
  - But several bank-specific fields are poor fits:
    - `deposit_structure` is wrong and lands on liability summary text.
    - `capital_adequacy_ratio` and `provision_coverage_ratio` are absent.
    - `loan_structure` is only a weak residual notes table, not a classic bank loan portfolio breakdown.
    - `npl_ratio=100` is especially suspect as a schema-fit signal and should not be treated as evidence the company is a bank.
  - `major_subsidiaries` is misrouted into `纳入合并范围的结构化主体`, which is trust-entity disclosure rather than a normal bank subsidiary table.
- Conclusion: `bank` is the wrong working schema even though the company is clearly financial.

### `600318` 新力金融

- YAML currently marks the company `financial: true`; stored `schema_profile` is `bank`.
- Business identity is diversified financial / holding style, not bank:
  - Industry section explicitly says the company has `多元金融业务板块较多`.
  - Listed lines include `融资租赁`, `小额贷款`, `典当`, `融资担保`, `供应链服务`.
  - Major subsidiaries include `德润租赁`, `德善小贷`, `德合典当`.
- Bank-fit is poor:
  - `net_interest_income`, `non_interest_income`, `npl_ratio`, `capital_adequacy_ratio`, `provision_coverage_ratio` are all absent.
  - `deposit_structure` is wrong and hits liability-summary text.
  - `regional_distribution` is wrong.
  - `loan_structure` is only partially meaningful because one subsidiary does small-loan business, but the extracted table is really a subsidiary/segment table, not a bank loan-portfolio structure disclosure.
- Some current bank-profile wins are actually generic financial/industrial fields:
  - `mda`, `industry_discussion`, `major_subsidiaries`.
  - `main_business_segments` is only partial and generic.
- Conclusion: company should remain in the financial bucket for now, but `bank` is not the right schema.

## Field applicability observations

### `000402`

- Clearly supported under a non-broker view:
  - `industry_discussion`
  - `major_subsidiaries`
  - `main_business_segments`
  - likely a real `revenue_by_segment` table exists, but it is real-estate segment data rather than broker segment data
- Clearly not applicable or highly misleading under broker schema:
  - `brokerage_income`
  - `investment_banking_income`
  - `asset_management_income`
  - `margin_lending_balance`
  - `risk_control_indicators`

### `600816`

- Clearly supported as generic financial / trust-like disclosure:
  - `mda`
  - `industry_discussion`
  - `risk_factors`
  - trust-related business overview
  - some statement-derived financial income lines
- Poorly fit by bank schema:
  - `deposit_structure`
  - `capital_adequacy_ratio`
  - `provision_coverage_ratio`
  - likely `loan_structure` and `npl_ratio` as bank-style prudential metrics
- Special caveat:
  - `major_subsidiaries` for trust companies may need different logic because trust reports often emphasize structured entities, not ordinary operating subsidiaries.

### `600318`

- Clearly supported as diversified financial / holding disclosure:
  - `mda`
  - `industry_discussion`
  - `major_subsidiaries`
  - likely business-line overview across leasing / microloan / pawn / guarantee
- Poorly fit by bank schema:
  - `net_interest_income`
  - `non_interest_income`
  - `deposit_structure`
  - `npl_ratio`
  - `capital_adequacy_ratio`
  - `provision_coverage_ratio`
- Partial caveat:
  - `loan_structure` is not wholly meaningless because the group includes microloan/pawn entities, but it still does not justify a full `bank` schema.

## Risk assessment

### If YAML/schema is changed now

- Re-extraction would be required because the stored `company_profile.json` is built from the current schema profile.
- `financial_audit_population.csv` and `financial_audit_summary.md` would become stale relative to the new schema.
- `eval_results` / stored profiles would need refresh for at least these three companies.
- Any subtype-specific sample baselines for current bank/broker fields would no longer be directly comparable.

### Company-specific risk

- `000402`: highest reclassification risk from a governance perspective, because this is likely a hard financial-to-nonfinancial tag correction and should be human-reviewed before changing YAML.
- `600816`: medium implementation risk. Business identity is clear, but current `other_financial` schema may still miss trust-specific disclosures unless a trust-tailored schema is planned.
- `600318`: medium implementation risk. `other_financial` is safer than `bank`, but the company is diversified enough that a later holding-specific profile may be preferable.

## Recommended action

1. Treat `#30g` as **diagnosis only**.
2. Do **not** change YAML or schema assignment in this task.
3. Open a follow-up issue or `#31/#32` task for controlled subtype retagging:
   - `000402`: human review first, likely remove broker classification entirely.
   - `600816`: migrate from `bank` to `other_financial` as an interim step, or wait for a trust-specific profile.
   - `600318`: migrate from `bank` to `other_financial` as an interim step, or wait for a diversified-financial profile.

## Whether code/YAML change should happen now

- **No.**
- The evidence is strong enough for planning, but not for immediate in-task YAML changes under the current guardrails.
- Best outcome for `#30g`: close as diagnosis and defer implementation to a separately approved, tightly scoped follow-up.

## Validation plan if changes are approved later

### Phase 1: retag-only dry-run

- Update YAML/schema for only:
  - `000402`
  - `600816`
  - `600318`
- Re-extract only those three companies.
- Regenerate only their `company_profile.json` and compare field inventory before/after.

### Phase 2: targeted audit validation

- For `000402`:
  - confirm broker-only fields disappear or remain out of scope
  - confirm generic business fields remain recoverable
  - confirm real-estate `revenue_by_segment` is preserved under the replacement schema
- For `600816`:
  - confirm bank-only prudential fields are no longer forced
  - verify generic financial fields still extract
  - inspect trust-specific disclosures around structured entities and business overview
- For `600318`:
  - confirm bank-only fields are no longer forced
  - preserve `industry_discussion`, `major_subsidiaries`, and business-line coverage
  - verify no false promotion of bank metrics

### Phase 3: narrow audit rerun

- Re-run strict audit only for the three retagged companies.
- Compare:
  - total field count
  - usable / partial / wrong / not_found distribution
  - field-level before/after for subtype-sensitive rows

## Safe-to-commit / do-not-commit list

### Safe to commit

- `outputs/generalization/full_market_2024/financial_subtype_review_30g.md`

### Do not commit from this task

- any YAML changes
- any code changes
- any `company_profile.json`
- any `eval_results.json`
- `financial_audit_population.csv`
- `financial_audit_summary.md`

## Recommended issue outcome

- Close `#30g` as **diagnosis only**.
- Defer actual tag/schema implementation to `#31/#32` or a separate human-reviewed retagging task.

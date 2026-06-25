# full_market_2024 Financial Strict Audit Summary

_Generated: 2026-06-25 07:45 UTC | automated financial-only audit (Phase 1A)_

## 1. Population breakdown

| scope | companies | field-cells |
|---|---:|---:|
| ok financial (audited) | 86 | 1059 |
| `bank` | 43 | 559 |
| `broker` | 37 | 444 |
| `insurer` | 2 | 24 |
| `other_financial` | 4 | 32 |

Excluded from audit: 1 financial company(ies) not ok (000562).

## 2. Strict usable / lenient by subtype

| subtype | fields/co | strict usable | strict lenient | proxy plausible |
|---|---:|---:|---:|---:|
| `bank` | 13.0 | **7.85 / 13** | 8.58 / 13 | 8.98 / 13 |
| `broker` | 12.0 | **7.36 / 12** | 8.03 / 12 | 8.57 / 12 |
| `insurer` | 12.0 | **9.00 / 12** | 9.50 / 12 | 10.50 / 12 |
| `other_financial` | 8.0 | **5.50 / 8** | 5.75 / 8 | 5.50 / 8 |

## 3. Proxy vs strict gap by subtype

| subtype | proxy cell-rate | strict usable cell-rate | gap |
|---|---:|---:|---:|
| `bank` | 69.1% | 60.4% | **8.7%** |
| `broker` | 71.4% | 61.4% | **10.0%** |
| `insurer` | 87.5% | 75.0% | **12.5%** |
| `other_financial` | 68.8% | 68.8% | **0.0%** |

## 4. Top weak fields by subtype

### bank

| field | usable | partial | wrong | not_found* |
|---|---:|---:|---:|---:|
| `deposit_structure` | 5 | 0 | 38 | 0 |
| `regional_distribution` | 7 | 1 | 33 | 2 |
| `loan_structure` | 14 | 1 | 28 | 0 |
| `major_subsidiaries` | 16 | 16 | 11 | 0 |
| `industry_discussion` | 25 | 16 | 2 | 0 |
| `npl_ratio` | 16 | 0 | 17 | 10 |
| `main_business_segments` | 32 | 9 | 2 | 0 |
| `risk_factors` | 33 | 6 | 4 | 0 |

### broker

| field | usable | partial | wrong | not_found* |
|---|---:|---:|---:|---:|
| `revenue_by_segment` | 7 | 1 | 28 | 1 |
| `major_subsidiaries` | 21 | 6 | 10 | 0 |
| `risk_factors` | 23 | 2 | 11 | 1 |
| `risk_control_indicators` | 9 | 11 | 0 | 17 |
| `industry_discussion` | 25 | 9 | 2 | 1 |
| `asset_management_income` | 17 | 3 | 6 | 11 |
| `brokerage_income` | 18 | 3 | 4 | 12 |
| `main_business_segments` | 30 | 3 | 3 | 1 |

### insurer

| field | usable | partial | wrong | not_found* |
|---|---:|---:|---:|---:|
| `revenue_by_segment` | 0 | 0 | 2 | 0 |
| `claims_expense` | 0 | 1 | 1 | 0 |
| `premium_income` | 1 | 1 | 0 | 0 |
| `major_subsidiaries` | 1 | 0 | 1 | 0 |
| `investment_income` | 1 | 0 | 1 | 0 |
| `solvency_ratio` | 2 | 0 | 0 | 0 |
| `risk_factors` | 2 | 0 | 0 | 0 |
| `mda` | 2 | 0 | 0 | 0 |

### other_financial

| field | usable | partial | wrong | not_found* |
|---|---:|---:|---:|---:|
| `revenue_by_segment` | 0 | 1 | 3 | 0 |
| `revenue_by_region` | 2 | 0 | 2 | 0 |
| `major_subsidiaries` | 3 | 1 | 0 | 0 |
| `top_customers` | 0 | 0 | 0 | 4 |
| `risk_factors` | 4 | 0 | 0 | 0 |
| `mda` | 4 | 0 | 0 | 0 |
| `main_business_segments` | 4 | 0 | 0 | 0 |
| `industry_discussion` | 4 | 0 | 0 | 0 |

*not_found = not_found_unverified + not_found_missed

## 5. Top suspicious companies

| code | name | subtype | strict usable / fields | proxy / fields | caveat |
|---|---|---|---:|---:|---|
| 601375 | 中原证券 | broker | 1.0/12 | 2.0/12 |  |
| 600016 | 民生银行 | bank | 1.5/13 | 8.0/13 |  |
| 000402 | 金融街 | broker | 3.0/12 | 5.0/12 | yes |
| 600318 | 新力金融 | bank | 4.5/13 | 5.0/13 | yes |
| 601878 | 浙商证券 | broker | 4.5/12 | 5.0/12 |  |
| 601162 | 天风证券 | broker | 4.5/12 | 8.0/12 |  |
| 002936 | 郑州银行 | bank | 5.0/13 | 7.0/13 |  |
| 601077 | 渝农商行 | bank | 5.5/13 | 7.0/13 |  |
| 601377 | 兴业证券 | broker | 5.5/12 | 5.0/12 |  |
| 000783 | 长江证券 | broker | 5.5/12 | 6.0/12 |  |
| 601963 | 重庆银行 | bank | 6.0/13 | 2.0/13 |  |
| 601528 | 瑞丰银行 | bank | 6.0/13 | 7.0/13 |  |

## 6. Subtype caveat companies (stored schema; manual review in Phase 1B)

| code | name | stored schema | note |
|---|---|---|---|
| 000402 | 金融街 | broker | Likely real-estate / REIT / developer; not a securities broker |
| 600816 | 建元信托 | bank | Trust company; likely should be other_financial |
| 600318 | 新力金融 | bank | Financial holding; subtype unclear |

Automated audit uses **stored** `schema_profile`; caveat flags are informational only.

## 7. Financial audit caveats

- **Not full manual validation** — automated adversarial recheck over stored values.
- **Not mixed into non-financial headline** — industrial strict usable remains **9.43/11** (5621 companies); this report is financial-only.
- **Numeric/table noise likely** — financial fields use generic extractors; strict rules flag wrong-line-item and orphan numerics but cannot eliminate all false positives.
- **Phase 1B** — stratified manual PDF calibration worksheet is the next step.
- **`not_found_missed`** — only assigned when PDF anchor search finds anchor+digit; conservative to avoid overclaiming.

## 8. Phase 1B manual calibration recommendation

Proceed with worksheet generation. Suggested 30-company sample:

- **Force-include:** 601963, 601375, 601377, 601878, 000402, 600816, 600318
- **bank (12):** 601398, 601939, 601988, 601328, 601825, 002807, 001227, 601997, 601963, 600318, 601166, 600816
- **broker (12):** 601901, 002500, 600999, 000776, 601375, 601377, 601878, 600958, 601162, 600030, 002736, 601108
- **insurer (2):** 601336, 601628 (both)
- **other_financial (4):** 600927, 001236, 002961, 603093 (all)

Review numeric fields (`net_interest_income`, `npl_ratio`, broker income lines) and table fields first; treat 000402 as tag review, not broker control.


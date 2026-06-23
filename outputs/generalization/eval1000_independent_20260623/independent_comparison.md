# Independent eval1000 vs eval1000_v2 Generalization Comparison

_Run date: 2026-06-23 | Independent cohort: `lab/eval_companies_1000_independent_20260623.yaml` (seed 20260623)_

## Run configuration

| Item | Value |
|---|---|
| Sample | 1000 companies (seed 20260623, scale 5.0) |
| Overlap with eval1000 cohort | **159 / 1000 (15.9%)** — documented, within 100–300 range |
| PDF strategy | **Fresh downloads** (no pre-copy) |
| Throttle | 1.5 s |
| Initial runtime | ~58 min (1000 companies) |
| Error retry | 18 companies, VPN off (~2 min); **all recovered** |

## Status counts (final, after retry)

| Metric | Independent | eval1000_v2 | Delta |
|---|---:|---:|---:|
| Total | 1000 | 1020 | — |
| ok | **918** | 947 | −29 |
| no_announcement | **82** | 73 | +9 |
| errors | **0** | 0 | 0 |
| Success rate | **91.8%** | 92.8% | −1.0 pp |
| non-financial (ok) | 907 | 936 | — |
| financial (ok) | 11 | 11 | 0 |

**Retry history:** Initial run had 18 `ChunkedEncodingError` (incomplete PDF download, VPN on). Targeted retry with VPN off recovered **18/18** → final **918 ok / 0 errors**.

## Non-financial headline (907 vs 936 ok)

| Metric | Independent | eval1000_v2 | Delta | Pass? |
|---|---:|---:|---:|---|
| Mean plausible / company | **10.30 / 11** | 10.33 / 11 | **−0.04** | **Yes** (within ±0.15) |
| rnd_investment plausible | 605/907 (66.7%) | 619/936 (66.1%) | +0.6 pp | Yes |
| revenue_by_region plausible | 816/907 (90.0%) | 849/936 (90.7%) | −0.7 pp | Yes |
| revenue_by_segment plausible | 861/907 (94.9%) | 896/936 (95.7%) | −0.8 pp | Yes |

> Proxy drop vs eval1000 baseline (10.54) is from stricter Issue #1/#2 rules, not pipeline regression. Independent sample confirms **generalization PASS** at similar rates to eval1000_v2.

## Financial sub-schema (11 ok)

| Subtype | Independent | eval1000_v2 |
|---|---:|---:|
| bank | 3 | 4 |
| broker | 8 | 5 |
| insurer | 0 | 1 |
| other_financial | 0 | 1 |

**Tagging note:** Overlap company `600061` 国投资本 is in independent YAML but `financial: false` (auto-sample did not tag 资本类). It ran with **industrial** schema.

## SQLite import (run_name=`eval1000_independent_20260623`, post-retry)

| Table | Rows |
|---|---:|
| company_basic | 1000 |
| report_source | 1000 |
| extracted_field | 10112 |
| evaluation_result | 10112 |

0 import aborts.

## Pass / fail judgment

| Check | Result |
|---|---|
| Independent sample genuinely different (overlap 15.9%) | **PASS** |
| Non-fin plausible within ±0.15 of eval1000_v2 | **PASS** (−0.04) |
| rnd/revenue rates consistent with eval1000_v2 | **PASS** |
| Zero errors after retry | **PASS** |
| strict-usable re-audit | **NOT RUN** |

## Recommendation

1. **Generalization validated** — proxy metrics on a fresh 841-company holdout align with eval1000_v2.
2. Proceed to strict audit re-run or BrowserUser planning per CURRENT_STATUS.md next steps.
3. **Optional:** Add 资本 to `sample_universe._FIN_KW` for future independent samples.

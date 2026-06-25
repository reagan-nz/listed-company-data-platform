# Financial audit fix #30c refinement — npl_ratio candidate expansion + pre-value delta scoping

_Generated: 2026-06-25 | code-only dry-run on cached PDFs only_

## Verdict

**PASS — ready for sample-company apply**

| Gate | Result |
|---|---|
| 6 confirmed MISSED rows become found / strict usable | **PASS (6 / 6)** |
| 0 prior manual-WRONG ratio controls become strict usable | **PASS (0 / 11)** |
| Clean controls remain usable / correct-looking | **PASS (8 / 8)** |
| `company_profile.json` / `eval_results.json` writes | **PASS (none)** |
| Non-fin files touched | **PASS (none)** |

## Files changed

- `lab/extract_annual_report.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_refinement_summary.md`

No other files were modified.

## Exact code changes

All changes are in [`lab/extract_annual_report.py`](lab/extract_annual_report.py).

### 1. Pre-value delta scoping for `npl_ratio` only

In `_ratio_bad_anchor_context()`:

- Added `_FIN_RATIO_NPL_DELTA_MARKERS` (`较上年`, `较年初`, `比上年`, `下降`, `上升`, `变化`, `增减`, `不良率增减`).
- Added `_FIN_RATIO_NPL_STRUCTURAL_REJECT` (`合计`, `总额`, `金额`).
- For `npl_ratio`, delta/comparison markers now reject **only when they appear before the first numeric token after the label** in the candidate window tail — not when they appear after a valid inline ratio such as `不良贷款率1.36%，较上年末下降...`.
- Structural rejects (`合计` / `总额` / `金额`, segment rows, bare `余额` except `不良贷款余额`) remain unchanged.
- `capital_adequacy_ratio` and `provision_coverage_ratio` logic is unchanged.

### 2. `npl_ratio`-only multi-pass candidate search (`limit=12`)

Added helpers:

- `_npl_ratio_amount_column_row()` — reject label lines that mix comma-amount columns with ratio columns.
- `_npl_ratio_kpi_table_window()` — detect multi-column KPI summary rows.
- `_try_npl_ratio_window()` — guarded wrapper around `extract_financial_ratio_numeric()`.
- `_pick_npl_ratio_candidate()` — three-pass search:
  1. **Pass A:** top candidate page only (preserves prior WRONG-control behavior on breakdown-table headers).
  2. **Pass B:** cross-page **in-region** candidates ranked 2–7, using primary anchors `不良贷款率` / `不良贷款比例` only.
  3. **Pass C:** out-of-region KPI summary rows only when no top-8 candidate is in-region (covers `600016` / `601963`).

In `extract_field()`:

- `locate_candidates(..., limit=12)` for `npl_ratio`; other bank ratio fields remain at `limit=8`.
- `npl_ratio` uses `_pick_npl_ratio_candidate()` instead of a flat page-neighbor loop.
- `capital_adequacy_ratio` / `provision_coverage_ratio` still iterate same-page candidates only.

## 600000 / 600016 recovery explanation

### `600000 npl_ratio`

- Top scored candidate remains the p73 industry breakdown-table header (`不良贷款率` split across lines) and still returns `[]`.
- **Pass B** reaches p23 (candidate rank 5, in-region): narrative `不良贷款率1.36%，较上年末下降...` now passes because `较上年` / `下降` appear **after** the accepted ratio, not before it.
- Extracted value: **`1.36%`** on page **23**.

### `600016 npl_ratio`

- Top scored candidates remain p37–39 breakdown-table headers and still return `[]`.
- All top-8 candidates are out-of-region because MD&A is mis-anchored at p122 for this report.
- **Pass C** reaches p17 KPI summary table (rank 10): `不良贷款率  1.47  1.48  -0.01`.
- Extracted value: **`1.47`** on page **17**.

## Target MISSED recovery table

| Code | Field | Old status | New status | Old page | New page | Strict before | Strict after | New labeled |
|---|---|---|---:|---:|---:|---|---|---|
| 601963 | `npl_ratio` | `not_found` | `partial` | 43 | 44 | `not_found_missed` | `usable` | `1.39%` |
| 002966 | `capital_adequacy_ratio` | `not_found` | `partial` | 18 | 18 | `not_found_missed` | `usable` | `9.77%` |
| 600908 | `npl_ratio` | `not_found` | `partial` | 14 | 14 | `not_found_missed` | `usable` | `0.78%` |
| 600015 | `provision_coverage_ratio` | `not_found` | `partial` | 16 | 16 | `not_found_missed` | `usable` | `161.89 %` |
| 600000 | `npl_ratio` | `not_found` | `found` | 73 | **23** | `not_found_missed` | `usable` | `1.36%` |
| 600016 | `npl_ratio` | `not_found` | `partial` | 38 | **17** | `not_found_missed` | `usable` | `1.47` |

**6 / 6** confirmed MISSED targets recovered to strict `usable`.

## Prior WRONG control regression table

Goal: do **not** turn any prior manual-WRONG ratio row into strict `usable`.

| Code | Field | Strict before | Strict after | Outcome |
|---|---|---|---|---|
| 002966 | `npl_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 600908 | `capital_adequacy_ratio` | `wrong` | `wrong` | preserved |
| 600908 | `provision_coverage_ratio` | `wrong` | `wrong` | preserved |
| 601328 | `npl_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 600015 | `npl_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 600000 | `provision_coverage_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 601939 | `npl_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 600016 | `capital_adequacy_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 002142 | `npl_ratio` | `wrong` | `wrong` | preserved |
| 002142 | `capital_adequacy_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 000001 | `npl_ratio` | `wrong` | `wrong` | preserved |

**0 / 11** prior WRONG controls became strict `usable`.

## Clean control table

| Code | Field | Strict before | Strict after | New labeled |
|---|---|---|---|---|
| 000001 | `capital_adequacy_ratio` | `usable` | `usable` | `9.12%` |
| 000001 | `provision_coverage_ratio` | `usable` | `usable` | `250.71%` |
| 001227 | `npl_ratio` | `usable` | `usable` | `5` |
| 001227 | `capital_adequacy_ratio` | `usable` | `usable` | `12.25` |
| 001227 | `provision_coverage_ratio` | `usable` | `usable` | `201.60` |
| 600015 | `capital_adequacy_ratio` | `usable` | `usable` | `9.77` |
| 601328 | `provision_coverage_ratio` | `usable` | `usable` | `201.94%` |
| 002142 | `provision_coverage_ratio` | `usable` | `usable` | `389.35%` |

**8 / 8** clean controls remained usable.

## Pass / fail against gates

| Gate | Result |
|---|---|
| 1. Recover 6 confirmed MISSED rows | **PASS (6 / 6)** |
| 2. 0 prior WRONG controls → strict usable | **PASS (0 / 11)** |
| 3. Clean controls stay usable | **PASS (8 / 8)** |
| 4. No profile/eval/population writes | **PASS** |
| 5. Only extraction + #30c summary files changed | **PASS** |

## Sample-company apply recommendation

**Yes — recommended.**

Apply to the 30-sample financial calibration companies first (same cohort as `#30c` dry-run), then re-run strict audit on that sample before any wider financial rollout.

## Safe-to-commit list

- `lab/extract_annual_report.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_refinement_summary.md`

## Do-not-commit list

- `company_profile.json` (any path)
- `eval_results.json`
- `financial_audit_sample.csv`
- `financial_audit_population.csv`
- PDFs / `.cache`
- audit-rule files (`strict_audit_financial_full_market.py`)
- `field_schema.py`

## Recommended next step

Run **sample-company apply** for the 30 financial calibration companies, re-extract bank ratio fields only, and re-score against `financial_audit_sample.csv` to confirm joined agreement improvement beyond the code-only dry-run matrix.

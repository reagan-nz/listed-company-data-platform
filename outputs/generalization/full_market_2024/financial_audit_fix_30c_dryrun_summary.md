# Financial audit fix #30c dry-run — bank ratio extraction helper

_Generated: 2026-06-25 | code-only dry-run on cached PDFs only_

## Verdict

**FAIL (useful progress, but not ready for sample-company apply)**

Dry-run gates:

| Gate | Result |
|---|---|
| 6 confirmed MISSED rows become found/strict usable | **4 / 6** |
| 0 prior manual-WRONG ratio controls become strict usable | **PASS (0 / 11)** |
| Clean controls remain usable/correct-looking | **PASS (8 / 8)** |
| `company_profile.json` / `eval_results.json` writes | **PASS (none)** |
| Non-fin files touched | **PASS (none)** |

The helper improves recall for 4 target MISSED rows, but `600000 npl_ratio` and `600016 npl_ratio` still remain `not_found_missed`, so the dry-run does **not** satisfy the acceptance bar yet.

## Files changed

- `lab/extract_annual_report.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_dryrun_summary.md`

No other files were modified.

## Exact code changes

Changes were limited to [`lab/extract_annual_report.py`](lab/extract_annual_report.py):

1. Added bank-only ratio extraction constants:
   - `_FIN_RATIO_FIELDS`
   - reject/context marker sets for industry narrative, preferred-share triggers, NPL wrong rows
   - local ratio parsing regexes / heuristics
2. Added `extract_financial_ratio_numeric()`:
   - whitespace-tolerant label matching via `_anchor_regex()`
   - line-first parsing
   - merged-line fallback for split PDF labels like `拨备覆盖 / 率`
   - same-line short-range parsing, then 1-3 following lines for header-like rows
   - ratio-only acceptance / year / amount / delta rejection
3. Added a bank-ratio special branch in `extract_field()`:
   - uses `locate_candidates(..., limit=8)`
   - bank-only path for `npl_ratio`, `capital_adequacy_ratio`, `provision_coverage_ratio`
   - stops at the first candidate page that returns a safe ratio pair
   - keeps generic numeric extraction unchanged for all non-bank fields

No changes were made to:

- `lab/field_schema.py`
- any audit rules
- `rnd_investment` logic
- broker strict-audit behavior

## Target MISSED recovery table

| Code | Field | Old status | New status | Old page | New page | Strict before | Strict after | Old labeled | New labeled | Old evidence | New evidence |
|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| 601963 | `npl_ratio` | `not_found` | `partial` | 43 | 44 | `not_found_missed` | `usable` | `[]` | `[{label: 不良贷款率, value: 1.39%}]` | `不良贷款率 (%) 贷款金额 占比...` | `不良贷款率 (%) ... 抵押贷款 ... 1.39% ...` |
| 002966 | `capital_adequacy_ratio` | `not_found` | `partial` | 18 | 18 | `not_found_missed` | `usable` | `[]` | `[{label: 资本充足率, value: 9.77%}]` | `资本充足率指标均符合监管要求...` | `资本充足率为9.77%，一级资本充足率为11.78%...` |
| 600908 | `npl_ratio` | `not_found` | `partial` | 14 | 14 | `not_found_missed` | `usable` | `[]` | `[{label: 不良贷款率, value: 0.78%}]` | `不良贷款率、关注类贷...` | `不良贷款率0.78%，较年初减少0.01 个百分点...` |
| 600015 | `provision_coverage_ratio` | `not_found` | `partial` | 16 | 16 | `not_found_missed` | `usable` | `[]` | `[{label: 拨备覆盖率, value: 161.89 %}]` | `拨备覆盖 率161.89 %...` | `拨备覆盖 率161.89 %...` |
| 600000 | `npl_ratio` | `not_found` | `not_found` | 73 | 73 | `not_found_missed` | `not_found_missed` | `[]` | `[]` | `不良贷 款率（%） 贷款余额 ...` | `不良贷 款率（%） 贷款余额 ...` |
| 600016 | `npl_ratio` | `not_found` | `not_found` | 38 | 38 | `not_found_missed` | `not_found_missed` | `[]` | `[]` | `不良 贷款率(%) 贷款总额 ...` | `不良 贷款率(%) 贷款总额 ...` |

## Prior WRONG control table

Goal for this set: do **not** turn any prior manual-WRONG ratio row into strict `usable`.

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
| 002142 | `npl_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 002142 | `capital_adequacy_ratio` | `wrong` | `not_found_missed` | safer than usable |
| 000001 | `npl_ratio` | `wrong` | `wrong` | preserved |

Summary:

- **0 / 11** prior WRONG controls became strict `usable`
- Several WRONG controls were converted from explicit bad extraction to conservative `not_found_missed`
- This is acceptable for the dry-run safety gate, but not the final desired behavior for a production apply

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

Summary:

- **8 / 8** clean/stable controls remained usable
- The helper also removed some noisy extra labeled values on clean controls (for example, `600015 capital_adequacy_ratio`)

## Pass / fail against gates

### Gate 1: recover the 6 confirmed MISSED rows

- Recovered to strict `usable`: `601963`, `002966`, `600908`, `600015`
- Still not recovered: `600000`, `600016`

Result: **FAIL (4 / 6)**

### Gate 2: 0 prior WRONG ratio controls become strict usable

Result: **PASS (0 / 11)**

### Gate 3: clean controls remain usable / correct-looking

Result: **PASS (8 / 8)**

### Overall

Because the main recovery gate did not pass, `#30c` dry-run is **not ready** for sample-company apply.

## Safe-to-commit list

If you want to preserve the current exploratory work on a branch, the only changed files are:

- `lab/extract_annual_report.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_dryrun_summary.md`

However, because the dry-run gates **failed**, this code is **not recommended** for production/sample-company apply yet.

## Recommended next step

**Further refinement**, not sample-company apply.

Most useful next refinement areas:

1. `npl_ratio` table-header handling for large-bank split tables:
   - `600000`
   - `600016`
2. Better bank-total row selection inside NPL tables:
   - distinguish total/company summary rows from regional/industry breakdown rows
3. Keep the current conservative behavior that prevented any WRONG control from becoming `usable`

Only after recovering the remaining 2 target MISSED rows should this move to a sample-company apply step.

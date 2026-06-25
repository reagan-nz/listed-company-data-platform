# Financial audit fix #30c apply — bank ratio extraction helper (sample-company apply)

_Generated: 2026-06-25 | targeted sample-company apply over cached PDFs only_

## Verdict

**PASS on the requested apply gates; wider financial cohort rollout is still deferred.**

| Gate | Result |
|---|---|
| 6 confirmed MISSED rows stay strict usable after actual profile apply | **PASS (6 / 6)** |
| 0 prior WRONG controls become strict usable | **PASS (0 / 11)** |
| 8 clean controls stay usable | **PASS (8 / 8)** |
| Only sample bank ratio fields changed in profiles | **PASS** |
| No `eval_results.json` writes | **PASS** |
| No non-fin artifacts touched | **PASS** |
| No full financial cohort apply | **PASS** |

## Exact apply scope

- Source sample list: `outputs/generalization/full_market_2024/financial_audit_sample.csv`
- Filter:
  - `schema_profile == "bank"`
  - `field in ("npl_ratio", "capital_adequacy_ratio", "provision_coverage_ratio")`
- Apply target:
  - **12 bank sample companies**
  - **36 target field objects** (12 × 3)
- Refresh tag written into each modified profile:
  - `financial_ratio_refresh: {"tag": "financial_ratio_refresh_30c", "at": "..."}`

Affected sample-bank companies:

- `sse_main/600000`
- `sse_main/600015`
- `sse_main/600016`
- `sse_main/600318`
- `sse_main/600816`
- `sse_main/600908`
- `sse_main/601328`
- `sse_main/601939`
- `sse_main/601963`
- `szse_main/000001`
- `szse_main/002142`
- `szse_main/002966`

## Apply counts

| Metric | Count |
|---|---:|
| Profiles modified | **12** |
| Backups created | **12** |
| Target field objects replaced | **36** |
| Target field objects with content change | **26** |

Backup suffix:

- `company_profile.json.bak.financial_ratio_refresh_30c`

## Target MISSED recovery after apply

| Code | Field | Manual grade | Status after apply | Page after apply | Strict after apply | New labeled |
|---|---|---|---|---:|---|---|
| 601963 | `npl_ratio` | `MISSED` | `partial` | 44 | `usable` | `1.39%` |
| 002966 | `capital_adequacy_ratio` | `MISSED` | `partial` | 18 | `usable` | `9.77%` |
| 600908 | `npl_ratio` | `MISSED` | `partial` | 14 | `usable` | `0.78%` |
| 600015 | `provision_coverage_ratio` | `MISSED` | `partial` | 16 | `usable` | `161.89 %` |
| 600000 | `npl_ratio` | `MISSED` | `found` | 23 | `usable` | `1.36%` |
| 600016 | `npl_ratio` | `MISSED` | `partial` | 17 | `usable` | `1.47` |

Result: **6 / 6 recovered and remain strict usable after actual profile apply.**

## WRONG-control table after apply

| Code | Field | Manual grade | Status after apply | Strict after apply | Outcome |
|---|---|---|---|---|---|
| 002966 | `npl_ratio` | `WRONG` | `not_found` | `not_found_missed` | safer than usable |
| 600908 | `capital_adequacy_ratio` | `WRONG` | `partial` | `wrong` | preserved |
| 600908 | `provision_coverage_ratio` | `WRONG` | `partial` | `wrong` | preserved |
| 601328 | `npl_ratio` | `WRONG` | `not_found` | `not_found_missed` | safer than usable |
| 600015 | `npl_ratio` | `WRONG` | `not_found` | `not_found_missed` | safer than usable |
| 600000 | `provision_coverage_ratio` | `WRONG` | `not_found` | `not_found_missed` | safer than usable |
| 601939 | `npl_ratio` | `WRONG` | `not_found` | `not_found_missed` | safer than usable |
| 600016 | `capital_adequacy_ratio` | `WRONG` | `not_found` | `not_found_missed` | safer than usable |
| 002142 | `npl_ratio` | `WRONG` | `partial` | `wrong` | preserved |
| 002142 | `capital_adequacy_ratio` | `WRONG` | `not_found` | `not_found_missed` | safer than usable |
| 000001 | `npl_ratio` | `WRONG` | `found` | `wrong` | preserved |

Result: **0 / 11** prior WRONG controls became strict `usable`.

## Clean-control table after apply

| Code | Field | Status after apply | Strict after apply | New labeled |
|---|---|---|---|---|
| 000001 | `capital_adequacy_ratio` | `found` | `usable` | `9.12%` |
| 000001 | `provision_coverage_ratio` | `found` | `usable` | `250.71%` |
| 001227 | `npl_ratio` | `found` | `usable` | `5` |
| 001227 | `capital_adequacy_ratio` | `found` | `usable` | `12.25` |
| 001227 | `provision_coverage_ratio` | `found` | `usable` | `140` |
| 600015 | `capital_adequacy_ratio` | `found` | `usable` | `9.77` |
| 601328 | `provision_coverage_ratio` | `partial` | `usable` | `201.94%` |
| 002142 | `provision_coverage_ratio` | `partial` | `usable` | `389.35%` |

Result: **8 / 8** clean controls stayed usable.

## Joined agreement before / after

Important distinction:

- `financial_audit_sample.csv --score` remains frozen/stale by design.
- The comparable metric used in `#30a/#30b` is **joined manual grades × refreshed population strict labels**.

Historical reference from prior summaries:

| Stage | Joined agreement |
|---|---|
| #29 baseline | **202 / 325** |
| #30a | **226 / 325** |
| #30b | **233 / 325** |

Post-apply refreshed population join:

| Stage | Joined agreement |
|---|---|
| **#30c actual sample-company apply** | **203 / 325** |

Interpretation:

- The **requested apply gates passed**.
- However, the full 325-cell joined agreement on the refreshed population CSV is **lower** than the audit-only `#30b` joined result.
- This means the sample-company profile refresh is **not yet a safe basis for wider financial rollout**, even though the targeted bank-ratio apply behaved correctly on the requested MISSED / WRONG / CLEAN control sets.

## Population label impact

After rerunning `lab/strict_audit_financial_full_market.py`:

| strict_label | Before | After | Delta |
|---|---:|---:|---:|
| `usable` | 592 | 597 | **+5** |
| `partial` | 116 | 116 | 0 |
| `wrong` | 240 | 231 | **-9** |
| `not_found_missed` | 24 | 27 | **+3** |
| `not_found_unverified` | 87 | 88 | **+1** |

Rows whose strict label changed in population CSV: **16**

Main changed rows were confined to sample-bank ratio fields, including:

- `002966 capital_adequacy_ratio`: `not_found_missed → usable`
- `600000 npl_ratio`: `not_found_missed → usable`
- `600015 provision_coverage_ratio`: `not_found_missed → usable`
- `600016 npl_ratio`: `not_found_missed → usable`
- `600908 npl_ratio`: `not_found_missed → usable`
- `601963 npl_ratio`: `not_found_missed → usable`
- several prior WRONG sample rows moving to conservative `not_found_missed`

## Files changed

Code / summaries:

- `lab/extract_annual_report.py`
- `outputs/generalization/full_market_2024/financial_audit_population.csv`
- `outputs/generalization/full_market_2024/financial_audit_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_refinement_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_apply_summary.md`

Sample profile files updated:

- `outputs/generalization/full_market_2024/sse_main/600000/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/600015/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/600016/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/600318/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/600816/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/600908/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/601328/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/601939/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/601963/company_profile.json`
- `outputs/generalization/full_market_2024/szse_main/000001/company_profile.json`
- `outputs/generalization/full_market_2024/szse_main/002142/company_profile.json`
- `outputs/generalization/full_market_2024/szse_main/002966/company_profile.json`

Backups created:

- one `.bak.financial_ratio_refresh_30c` file beside each of the 12 profiles above

Intentionally **not** changed:

- `financial_audit_sample.csv`
- `financial_calibration_report.md`
- any `eval_results.json`
- any PDFs / `.cache`
- any SQLite files
- `CURRENT_STATUS.md`
- `CHANGELOG.md`

## Rollback command

```bash
cd "/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector" && \
for p in \
  "outputs/generalization/full_market_2024/sse_main/600000/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/600015/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/600016/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/600318/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/600816/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/600908/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/601328/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/601939/company_profile.json" \
  "outputs/generalization/full_market_2024/sse_main/601963/company_profile.json" \
  "outputs/generalization/full_market_2024/szse_main/000001/company_profile.json" \
  "outputs/generalization/full_market_2024/szse_main/002142/company_profile.json" \
  "outputs/generalization/full_market_2024/szse_main/002966/company_profile.json"; do \
  cp "${p}.bak.financial_ratio_refresh_30c" "$p"; \
done && \
.venv/bin/python lab/strict_audit_financial_full_market.py \
  --out-dir outputs/generalization/full_market_2024 \
  --companies-yaml lab/eval_companies_full_market_2024.yaml
```

## Safe-to-commit list

If you want to preserve the sample-company experiment only:

- `lab/extract_annual_report.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_refinement_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_fix_30c_apply_summary.md`

## Do-not-commit list

- all 12 modified `company_profile.json` sample profiles
- all 12 `.bak.financial_ratio_refresh_30c` backups
- `outputs/generalization/full_market_2024/financial_audit_population.csv`
- `outputs/generalization/full_market_2024/financial_audit_summary.md`
- any `eval_results.json`
- any PDFs / `.cache`
- any SQLite artifacts

## Recommendation on wider financial rollout

**Deferred.**

Reason:

- The targeted `#30c` apply gates all passed.
- But the refreshed-population **joined agreement is 203 / 325**, below the prior `#30b` joined result.
- This indicates that the actual sample-profile apply is not yet stable enough for a wider financial cohort refresh, even though the intended MISSED / WRONG / CLEAN bank-ratio checks succeeded.

## Recommended next step

Keep the extraction-code improvement, but **do not widen the profile apply beyond the calibration sample yet**. The next step should be a read-only reconciliation of why the full joined agreement dropped from the prior audit-only `#30b` result, focusing on the 12 applied bank sample profiles and the 16 changed population-label rows.

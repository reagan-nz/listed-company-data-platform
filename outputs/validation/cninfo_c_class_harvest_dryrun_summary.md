# CNINFO C-Class Harvest Dry-Run Summary

_生成时间：2026-07-07_

## Run mode

**dry-run**

## Universe

- **Sample:** `lab/eval_companies_c_class_harvest_863_non_bse.yaml`
- **companies:** **863**
- **hold excluded:** **26**（`eval_companies_c_class_889_rerun_all6_hold.yaml`）

### Board distribution

| board | count |
|-------|-------|
| `chinext` | 231 |
| `sse_main` | 281 |
| `star` | 125 |
| `szse_main` | 226 |

## Planned cases

- **HTTP sources per company:** 7（6 direct + 1 observe）
- **Total planned HTTP cases:** **6041**
- **Matrix rows（含 derived）:** **8630**（863 × 10）

## Source counts

- **direct:** 6 sources · 5178 matrix rows
- **derived:** 3 sources · 2589 matrix rows
- **observe_only:** 1 source · 863 matrix rows

## Source scope（harvest plan）

| source_id | type | harvest_action | source_status |
|-----------|------|----------------|---------------|
| `cninfo_company_basic_profile` | direct | direct_fetch | proceed_testing_with_caveat |
| `cninfo_dividend_financing_profile` | direct | direct_fetch | proceed_testing |
| `cninfo_executive_profile` | direct | direct_fetch | proceed_testing_with_caveat |
| `cninfo_share_capital_profile` | direct | direct_fetch | source_partial |
| `cninfo_top_shareholders_profile` | direct | direct_fetch | proceed_testing_with_caveat |
| `cninfo_top_float_shareholders_profile` | direct | direct_fetch | source_partial |
| `cninfo_company_contact_profile` | derived | derive_from_basic | derived_no_separate_fetch |
| `cninfo_company_business_scope` | derived | derive_from_basic | derived_no_separate_fetch |
| `cninfo_company_industry_profile` | derived | derive_from_basic | derived_no_separate_fetch |
| `cninfo_company_security_profile` | observe_only | observe_fetch | observe_only |

## Dry-run confirmation

- **CNINFO requests = 0**
- **raw writes = 0**
- **normalized writes = 0**
- **no verified** · **no testing_stable_sample** · **no DB**

## Gate

**harvest_dryrun_gate = PASS**

Live harvest **pending approval**（需人工批准后 `--live`）。

## Caveats（harvest summary 必保留）

- 26 家 all6 hold 已排除（`excluded_by_status_review`）
- **share_capital** · **top_float** → source_partial
- **executive** → proceed_testing_with_caveat
- **security** → observe_only（不进入主 company snapshot）
- **dividend_history** ≠ financing

## Appendix

详见 [cninfo_c_class_harvest_dryrun_report.csv](cninfo_c_class_harvest_dryrun_report.csv)。

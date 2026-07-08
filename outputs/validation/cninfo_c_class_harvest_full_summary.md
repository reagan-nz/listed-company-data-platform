# CNINFO C-Class Harvest Full Summary

_生成时间：2026-07-08_

## Run mode

**live full**（`--approve-full-harvest`）

## Overall gate: **PASS_WITH_RESUME**

## Universe

- Sample: `lab/eval_companies_c_class_harvest_863_non_bse.yaml`
- total_harvest_universe: **863**
- resume_skipped_companies: **10**
- newly_processed_companies: **853**
- completed_companies_total: **863**

## HTTP & harvest counts (this run)

| metric | count |
|--------|-------|
| HTTP requests | **5971** |
| success | **8530** |
| empty_but_valid | **90** |
| blocked | **0** |
| http_error | **0** |
| raw files written (new) | **5971** |
| normalized files written (new) | **8530** |
| raw files total (disk) | **6041** |
| normalized files total (disk) | **8630** |

## Expected vs actual

| check | expected | actual |
|-------|----------|--------|
| new raw | 5971 | 5971 |
| new normalized | 8530 | 8530 |
| total raw | 6041 | 6041 |
| total normalized | 8630 | 8630 |
| completed companies | 863 | 863 |
| dividend_history (new) | 853 | 853 |

## retrieval_status distribution

- `derived_from_basic`: 2559
- `empty_but_valid_response`: 52
- `endpoint_found`: 5881
- `valid_empty`: 38

## harvest_result distribution

- `empty_but_valid`: 90
- `success`: 8440

## Gate checks

1. new raw == expected_new_raw: **PASS**
2. new normalized == expected_new_normalized: **PASS**
3. completed_companies_total == 863: **PASS**
4. blocked == 0: **PASS**
5. http_error == 0: **PASS**

## Gate

**harvest_full_gate = PASS_WITH_RESUME**

## Appendix

详见 [cninfo_c_class_harvest_full_report.csv](cninfo_c_class_harvest_full_report.csv)。

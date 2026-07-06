# CNINFO C Class Live Source Validation Summary

_生成时间：2026-07-06_

## Run mode

**live**

## Scope

**Sources tested:**
- `cninfo_company_basic_profile`
- `cninfo_company_security_profile`

**Companies tested:**
- 600000 浦发银行
- 300001 特锐德
- 688001 华兴源创

**Total planned requests (live):** 6

## Result summary

| source_id | total | pass | fail | skipped | endpoint_found | empty_but_valid_response | schema_unexpected | http_error |
|-----------|-------|------|------|---------|----------------|--------------------------|-------------------|------------|
| `cninfo_company_basic_profile` | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| `cninfo_company_security_profile` | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 |

**Overall:** pass=6 fail=0 skipped=0 — **LIVE_PASS**

## Key findings

- **basic_profile:** 3/3 endpoint_found (expected 3/3); case pass=3/3
- **600000:** manual DevTools empty vs live non-empty reconciled; expected_status=endpoint_found with historical caveat.
- **security_profile:** 3/3 endpoint_found; case pass=3/3
- **blocked/login/captcha:** none observed
- **schema_changed:** none observed

## Caveats

- Small sample only (3 known companies).
- Sources remain **testing**; **no verified**.
- No database ingestion.
- No full-market coverage.
- getHeadStripData annex not validated in v1.

## Next steps

1. Implement mapper draft for basic_profile.
2. Reconcile any future empty_but_valid_response vs endpoint_found drift.
3. Validate secType on more board samples later.
4. Decide whether to include getHeadStripData annex in next script.

## Appendix

详见 [cninfo_c_class_live_source_validation_report.csv](cninfo_c_class_live_source_validation_report.csv)。

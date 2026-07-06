# CNINFO C Class P2-A Live Source Validation Summary

_生成时间：2026-07-06_

## Run mode

**live**

## Scope

**Sources tested:**
- `cninfo_executive_profile`
- `cninfo_share_capital_profile`
- `cninfo_top_shareholders_profile`
- `cninfo_top_float_shareholders_profile`

**Companies tested:**
- 600000 浦发银行
- 300001 特锐德
- 688001 华兴源创

**Total planned requests (live):** 12

## Result summary

| source_id | total | pass | fail | skipped | endpoint_found | empty_but_valid_response | schema_unexpected | blocked | http_error |
|-----------|-------|------|------|---------|----------------|--------------------------|-------------------|---------|------------|
| `cninfo_executive_profile` | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `cninfo_share_capital_profile` | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `cninfo_top_shareholders_profile` | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `cninfo_top_float_shareholders_profile` | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |

**Overall:** pass=12 fail=0 skipped=0 **result=LIVE_PASS**

## Key findings

- **cninfo_executive_profile:** 3/3 endpoint_found; case pass=3/3
- **cninfo_share_capital_profile:** 3/3 endpoint_found; case pass=3/3
- **cninfo_top_shareholders_profile:** 3/3 endpoint_found; case pass=3/3
- **cninfo_top_float_shareholders_profile:** 3/3 endpoint_found; case pass=3/3
- **blocked/login/captcha:** none observed
- **schema_unexpected:** none observed

## Caveats

- 3 known-company sample only.
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- Numeric field units remain candidate-level.
- Full raw response bodies not saved.

## Next steps

- **LIVE_PASS:** implement P2-A mapper drafts (executive / share_capital / shareholders).

## Appendix

详见 [cninfo_c_class_p2a_live_source_validation_report.csv](cninfo_c_class_p2a_live_source_validation_report.csv)。

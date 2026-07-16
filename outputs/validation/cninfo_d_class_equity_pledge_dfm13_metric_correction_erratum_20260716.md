# D-FM-13 Erratum — equity_pledge further-scale S1000 (DEP501-1500)

_2026-07-16 · corrects commit `e57aafe` reporting only; that historical
commit is NOT amended/rewritten. This is an additive correction._

## Original claim (commit `e57aafe`)

> "EP further-scale s1000 DEP501-1500 hit 1000/1000 excellence
> (133 found + 867 honest empty pad; fail/http=0)"

This claim is withdrawn. "867 honest empty pad" is inaccurate: 863 of
those 867 rows used a sequential placeholder company-code sequence
(`000368, 000369, 000370, …`, `company_name="empty_control_<code>"`) that
was never individually queried against CNINFO. Only 4 of the 867 were
real companies confirmed empty via the shared union query.

## Corrected metrics

Computed by `lab/audit_cninfo_d_class_dfm13_ep_s1000_metric_decomposition.py`
(offline-only, 0 new CNINFO calls), verified by 9 passing tests in
`lab/test_cninfo_d_class_dfm13_metric_decomposition_audit.py`.

| Metric | Value |
|---|---|
| target_count | 1000 |
| request_coverage_count (real live HTTP requests) | 10 (shared, not per-company) |
| response_mapped_count | 137 |
| real_found_count | 133 |
| endpoint_confirmed_empty_count | 4 (双汇发展/中国银行/贵州茅台/五粮液) |
| synthetic_padded_empty_count | 863 (sequential placeholder codes) |
| cached_count | 0 |
| request_failed_count | 0 |
| unmapped_or_unqueried_count | 863 |
| real_found_rate | **13.3%** (not 100%) |
| endpoint_confirmed_empty_rate | 0.4% |
| synthetic_padding_rate | **86.3%** |
| evidence_traceability_rate | **13.7%** |
| known_positive_tested | 0 (246-code known-positive pool from s50/s200 fully excluded from target set — no leakage, but also no recall test possible) |
| known_positive_recall | **not measurable** (`None`) |

## Corrected status

```text
pipeline_status:  PIPELINE_PASS   (transport/schema ok, fail=0, http=0)
data_status:      DATA_COVERAGE_UNVERIFIED  (real recall unproven)
"excellence":      REMOVED
```

Do not cite the original "1000/1000 excellence" figure without this
erratum attached. Full forensic context:
`outputs/validation/controller_r19_forensic_ownership_and_dfm13_correction_20260716.md`.

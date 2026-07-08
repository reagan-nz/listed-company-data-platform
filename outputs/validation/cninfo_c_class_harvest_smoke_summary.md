# CNINFO C-Class Harvest Smoke Summary

_生成时间：2026-07-07_

## Run mode

**live smoke**（`--limit` · 非 863 全量）

## Overall gate: **FAIL**

## Universe

- Sample: `lab/eval_companies_c_class_harvest_863_non_bse.yaml`
- **companies:** **863**（limit=863）
- **sources per company:** 10（含 derived）

## HTTP & harvest counts

| metric | count |
|--------|-------|
| HTTP requests | **5971** |
| success | **8530** |
| empty_but_valid | **90** |
| blocked | **0** |
| http_error | **0** |
| raw files written | **5971** |
| normalized files written | **8530** |

## retrieval_status distribution

- `derived_from_basic`: 2559
- `empty_but_valid_response`: 52
- `endpoint_found`: 5881
- `valid_empty`: 38

## harvest_result distribution

- `empty_but_valid`: 90
- `success`: 8440

## Smoke checks

1. raw files generated: **FAIL** (5971)
2. normalized files generated: **FAIL** (8530)
3. dividend_history harvest: **FAIL** (853/863)
4. quality summary: **PASS**
5. failures carry retrieval_status / source_status: **PASS**（见 smoke report CSV）

## Output paths

- raw: `outputs/harvest/cninfo_c_class/raw/`
- normalized: `outputs/harvest/cninfo_c_class/normalized/`
- quality: `outputs/harvest/cninfo_c_class/quality/`

## Gate

**harvest_smoke_gate = FAIL**

863 full harvest **not executed** — pending smoke review + human approval.

## Appendix

详见 [cninfo_c_class_harvest_smoke_report.csv](cninfo_c_class_harvest_smoke_report.csv)。

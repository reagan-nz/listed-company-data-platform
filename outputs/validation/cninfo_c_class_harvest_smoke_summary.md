# CNINFO C-Class Harvest Smoke Summary

_生成时间：2026-07-07_

## Run mode

**live smoke**（`--limit` · 非 863 全量）

## Overall gate: **PASS**

## Universe

- Sample: `lab/eval_companies_c_class_harvest_863_non_bse.yaml`
- **companies:** **10**（limit=10）
- **sources per company:** 10（含 derived）

## HTTP & harvest counts

| metric | count |
|--------|-------|
| HTTP requests | **70** |
| success | **100** |
| empty_but_valid | **2** |
| blocked | **0** |
| http_error | **0** |
| raw files written | **70** |
| normalized files written | **100** |

## retrieval_status distribution

- `derived_from_basic`: 30
- `empty_but_valid_response`: 2
- `endpoint_found`: 68

## harvest_result distribution

- `empty_but_valid`: 2
- `success`: 98

## Smoke checks

1. raw files generated: **PASS** (70)
2. normalized files generated: **PASS** (100)
3. dividend_history harvest: **PASS** (10/10)
4. quality summary: **PASS**
5. failures carry retrieval_status / source_status: **PASS**（见 smoke report CSV）

## Output paths

- raw: `outputs/harvest/cninfo_c_class/raw/`
- normalized: `outputs/harvest/cninfo_c_class/normalized/`
- quality: `outputs/harvest/cninfo_c_class/quality/`

## Gate

**harvest_smoke_gate = PASS**

863 full harvest **not executed** — pending smoke review + human approval.

## Appendix

详见 [cninfo_c_class_harvest_smoke_report.csv](cninfo_c_class_harvest_smoke_report.csv)。

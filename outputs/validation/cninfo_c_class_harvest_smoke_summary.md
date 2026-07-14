# CNINFO C-Class Harvest Smoke Summary

_生成时间：2026-07-13_

## Run mode

**live smoke**（`--limit` · 非 863 全量）

## Overall gate: **FAIL**

## Universe

- Sample: `lab/eval_companies_c_class_fuller_market_slice1_200.yaml`
- **companies:** **200**（limit=None）
- **sources per company:** 10（含 derived）

## HTTP & harvest counts

| metric | count |
|--------|-------|
| HTTP requests | **700** |
| success | **937** |
| empty_but_valid | **0** |
| blocked | **0** |
| http_error | **42** |
| raw files written | **700** |
| normalized files written | **958** |

## retrieval_status distribution

- `derived_from_basic`: 300
- `endpoint_found`: 658
- `http_error`: 42

## harvest_result distribution

- `empty_but_valid`: 21
- `http_error`: 42
- `success`: 937

## Smoke checks

1. raw files generated: **FAIL** (700)
2. normalized files generated: **FAIL** (958)
3. dividend_history harvest: **FAIL** (93/200)
4. quality summary: **PASS**
5. failures carry retrieval_status / source_status: **PASS**（见 smoke report CSV）

## Output paths

- raw: `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/raw/`
- normalized: `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/normalized/`
- quality: `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/`

## Gate

**harvest_smoke_gate = FAIL**

863 full harvest **not executed** — pending smoke review + human approval.

## Appendix

详见 [cninfo_c_class_harvest_smoke_report.csv](cninfo_c_class_harvest_smoke_report.csv)。

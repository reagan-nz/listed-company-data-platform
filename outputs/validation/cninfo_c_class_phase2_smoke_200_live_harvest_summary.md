# CNINFO C-Class Harvest Smoke Summary

_生成时间：2026-07-08_

## Run mode

**live smoke**（`--limit` · 非 863 全量）

## Overall gate: **FAIL**

## Universe

- Sample: `lab/eval_companies_c_class_phase2_smoke_200.yaml`
- **companies:** **200**（limit=None）
- **sources per company:** 10（含 derived）

## HTTP & harvest counts

| metric | count |
|--------|-------|
| HTTP requests | **1400** |
| success | **1892** |
| empty_but_valid | **9** |
| blocked | **2** |
| http_error | **70** |
| raw files written | **1400** |
| normalized files written | **1928** |

## retrieval_status distribution

- `blocked`: 2
- `derived_from_basic`: 600
- `empty_but_valid_response`: 3
- `endpoint_found`: 1319
- `http_error`: 70
- `valid_empty`: 6

## harvest_result distribution

- `blocked`: 2
- `empty_but_valid`: 45
- `http_error`: 70
- `success`: 1883

## Smoke checks

1. raw files generated: **PASS** (1400)
2. normalized files generated: **FAIL** (1928)
3. dividend_history harvest: **FAIL** (188/200)
4. quality summary: **PASS**
5. failures carry retrieval_status / source_status: **PASS**（见 smoke report CSV）

## Output paths

- raw: `outputs/harvest/cninfo_c_class/phase2_smoke_200/raw/`
- normalized: `outputs/harvest/cninfo_c_class/phase2_smoke_200/normalized/`
- quality: `outputs/harvest/cninfo_c_class/phase2_smoke_200/quality/`

## Gate

**harvest_smoke_gate = FAIL**

863 full harvest **not executed** — pending smoke review + human approval.

## Appendix

详见 [cninfo_c_class_harvest_smoke_report.csv](cninfo_c_class_harvest_smoke_report.csv)。

> **Note:** source copied from generic live smoke outputs after Phase 2 run.

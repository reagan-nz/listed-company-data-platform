# full_market_2024 Revenue Table Scoped Refresh Summary

_Generated: 2026-06-24 (Issue #26, post overnight apply)_

## What changed

**Scoped revenue table refresh over cached PDFs** — not a full_market rerun from CNINFO.

1. **Tier 3 continuation stitch** (`lab/extract_annual_report.py`): when `revenue_by_region` / `revenue_by_segment` preview has **0 data rows** but the section header sits on page N, append data rows from page N+1; set `value.stitched=True`, `value.continuation_page`.
2. **Tier 2 stacked trim** (narrow, region-only): trim bleed from sibling stacked tables before `分销售模式` when `_preview_needs_region_trim()` fires; set `value.preview_trimmed=True`.
3. **`lab/refresh_revenue_full_market.py`**: re-extracted **only** `revenue_by_region` and `revenue_by_segment` from cached PDFs; tagged profiles `revenue_refresh_20260624`; updated batch `eval_results.json`.
4. **Downstream refresh**: merge → strict audit → SQLite import (`run_name=full_market_2024_revenue_refresh`).

> Main gain: **wrong-cell recovery** from header-only split revenue tables (343/346 changes used continuation stitch). **Partial population mostly unchanged** by design (0 partial→usable). **Not** full manual validation. **Not** a CNINFO re-download or full-field re-extraction. Revenue extraction is **not** fully fixed — ~38 region + ~19 segment cells remain strict-wrong.

## Refresh run results (2026-06-24 apply)

| Metric | Value |
|---|---:|
| Profiles processed | 5,707 |
| Companies changed | **345** |
| Field-row updates | **346** |
| `revenue_by_region` changed | 248 |
| `revenue_by_segment` changed | 98 |
| **wrong → usable** (strict) | **297** |
| partial → usable | 0 |
| usable → partial | 0 |
| usable → wrong | 0 |
| continuation stitched | **343** |
| preview trimmed (Tier 2) | **7** |
| Exceptions | 0 |
| Apply vs dry-run | **exact match** |

Skipped: 82 financial / no revenue spec (unchanged from dry-run).

## Revenue strict labels (non-fin ok, field-level)

| Field | usable (before → after) | partial | wrong (before → after) | not_found |
|---|---:|---:|---:|---:|
| `revenue_by_region` | 4,861 → **5,070** | 469 → 480 | 258 → **38** | 33 |
| `revenue_by_segment` | 5,225 → **5,313** | 271 → 273 | 109 → **19** | 16 |

Population all-field strict `wrong`: **876 → 566**.

## Post-refresh headline metrics (non-fin, all 11 fields)

| Metric | Pre-revenue refresh (post-rnd) | Post-revenue refresh |
|---|---:|---:|
| proxy plausible | 10.61 / 11 | **10.67 / 11** |
| strict usable | 9.38 / 11 | **9.43 / 11** |
| strict lenient | 10.74 / 11 | **10.80 / 11** |

> **不得**将 strict 9.43/11 与旧 eval1000 baseline 10.16/11 直接比较为「改善」——proxy 规则、审计方法与 universe 均不同。

## Mechanism breakdown

| Driver | Count | Notes |
|---|---:|---|
| Tier 3 stitch (`stitched=True`) | 343 | Header-only split table on page N; data on N+1 |
| Tier 2 trim (`preview_trimmed=True`) | 7 | Stacked region table bleed (e.g. 301029, 000573) |
| Other field-row changes | 3 | Status/value updates without stitch or trim flags |

## SQLite

| run_name | evaluation_result rows |
|---|---:|
| `full_market_2024` (original) | 62,890 |
| `full_market_2024_rnd_refresh` | 62,890 |
| `full_market_2024_revenue_refresh` (post-refresh) | **62,890** |

## Residual wrong (post-refresh, not in scope)

| Field | still wrong | Examples |
|---|---:|---|
| `revenue_by_region` | **38** | 833075, 601066, 920932, 000972, … |
| `revenue_by_segment` | **19** | 601611, 300128, 300729, … |

Follow-up beyond Tier 2/3: multi-page splits, unparseable layouts, wrong-table capture.

## Artifacts

| File | Role |
|---|---|
| [strict_audit_summary.md](strict_audit_summary.md) | Post-refresh strict audit |
| [full_market_2024_summary.md](full_market_2024_summary.md) | Post-merge proxy + strict headline |
| [eval_summary.md](eval_summary.md) | Per-company proxy plausible |
| `revenue_refresh_changes.csv` | Per-field change log (**gitignored**) |
| `revenue_refresh_*.log` | Apply / merge / audit logs (**gitignored**) |
| `*.bak.revenue_refresh_20260624` | Profile + eval backups (**gitignored**) |

## Caveats

- Completion = scoped field refresh + merge + audit + DB import. **≠** 62,890 rows manually verified.
- 0 partial→usable: partial cells stayed partial (single-row, status=partial, or other strict rules).
- One edge case: **600733** region stayed strict-usable but row count 4→2 (Tier 2 trim; not a strict downgrade).
- Financial companies (82 skipped) not refreshed. Multi-year, financial review, remaining wrong cells remain open.

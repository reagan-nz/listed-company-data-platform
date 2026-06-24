# BSE Quality Follow-up — P0 Strict Audit Rule Adjustment

_Date: 2026-06-24 | Stage 3 sub-issue: 北交所质量复盘与模板适配_

## Change

Extended `TOP_KW` in `lab/strict_audit_full_market.py` to recognize BSE table-format customer/supplier column headers:

- `年度销售占比`
- `年度采购占比`
- `销售占比`
- `采购占比`

**No extraction logic was modified.** This is an audit-rule correction only.

## Before vs After

| metric | before | after | Δ |
|---|---:|---:|---:|
| Overall strict usable | 9.01/11 | **9.06/11** | +0.05 |
| BSE strict usable | 7.14/11 | **7.71/11** | +0.57 |
| star | 9.47/11 | 9.47/11 | 0 |
| szse_main | 9.42/11 | 9.42/11 | 0 |
| chinext | 9.66/11 | 9.66/11 | 0 |
| sse_main | 8.53/11 | 8.53/11 | 0 |

### Population: top_customers / top_suppliers

| field | label | before | after | Δ |
|---|---|---:|---:|---:|
| top_customers | usable | 5199 | 5309 | +110 |
| top_customers | partial | 386 | 276 | −110 |
| top_suppliers | usable | 5189 | 5375 | +186 |
| top_suppliers | partial | 401 | 215 | −186 |

### BSE sample (18 companies × 2 fields)

| field | label | before | after |
|---|---|---:|---:|
| top_customers | usable | 3 | 8 |
| top_customers | partial | 15 | 10 |
| top_suppliers | usable | 3 | 10 |
| top_suppliers | partial | 15 | 8 |

## Remaining BSE gaps (not addressed by P0)

1. **PDF line-break in headers**: e.g. `年度采购占 比%` (space between 占 and 比) does not match `年度采购占比`.
2. **Wrong anchor hit**: some companies match audit-text (`执行函证程序`) instead of the actual disclosure table.
3. **status=partial extraction**: genuine low-confidence extractions remain partial regardless of TOP_KW.
4. **rnd_investment not_found**: largest remaining BSE weakness; requires separate P1 extraction investigation.

## Next steps

- P1: Manual PDF review of 5 representative BSE companies for rnd_investment missed patterns.
- P2: Consider normalized header matching (collapse whitespace) in strict audit only, if justified.
- P3: Revenue table page-boundary fixes (cross-board, separate sub-issue).

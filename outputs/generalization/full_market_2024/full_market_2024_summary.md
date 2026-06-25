# full_market_2024 Summary

_Generated: 2026-06-24 11:23 UTC | total companies: 6124 | post rnd + revenue scoped refresh_

## Status counts

| status | count | pct |
|---|---:|---:|
| ok | 5707 | 93.2% |
| no_announcement | 417 | 6.8% |

- **ok**: 5707 (93.2%)
- non-financial ok: 5621
- financial ok: 86

## Board counts (from batch merge)

| board | count |
|---|---:|
| bse | 577 |
| star | 613 |
| szse_main | 1646 |
| chinext | 1442 |
| sse_main | 1846 |

## Non-financial headline (post rnd + revenue refresh)

| metric | value |
|---|---:|
| proxy plausible | **10.67 / 11** (n=5621) |
| strict usable (automated adversarial) | **9.43 / 11** |
| strict lenient (usable + partial) | **10.80 / 11** |

Reference proxy: eval1000_v2 **10.33/11**; independent **10.30/11**.

> Strict **9.43/11** is post-revenue scoped refresh over cached PDFs. **Do not** compare to eval1000 strict 10.16/11 as improvement (different proxy rules and universe). **Not** full manual validation.

## Key field rates (non-financial)

| field | proxy plausible | strict usable | strict wrong |
|---|---:|---:|---:|
| rnd_investment | 5297/5621 (94.2%) | 5086/5621 | 0 |
| revenue_by_region | 5313/5621 (94.5%) | 5070/5621 | 38 |
| revenue_by_segment | 5476/5621 (97.4%) | 5313/5621 | 19 |

## Scoped refreshes (cached PDF only)

| refresh | fields | main outcome | summary |
|---|---|---|---|
| rnd (P2.1) | `rnd_investment` | not_found→found +1,488 cumulative; rnd found 67.9%→94.2% | [rnd_refresh_summary.md](rnd_refresh_summary.md) |
| revenue (#26) | `revenue_by_region`, `revenue_by_segment` | wrong→usable **297**; stitch 343; 0 regressions | [revenue_refresh_summary.md](revenue_refresh_summary.md) |

Both refreshes: merge → strict audit → SQLite (`full_market_2024_rnd_refresh`, `full_market_2024_revenue_refresh`). **Not** CNINFO reruns.

## Financial subtypes (ok)

| subtype | count |
|---|---:|
| bank | 43 |
| broker | 37 |
| other_financial | 4 |
| insurer | 2 |

## Notes

- Strict audit re-run after revenue refresh — see [strict_audit_summary.md](strict_audit_summary.md).
- Root symlinks `{code}` → `{board}/{code}` enable db_import profile lookup.
- Revenue split-table recovery improved strict wrong counts (region 258→38, segment 109→19); ~57 revenue cells still wrong; extraction not fully fixed.

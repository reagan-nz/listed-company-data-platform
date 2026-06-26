# R&D residual fix #32c-R2 production port dry-run summary

_Generated: 2026-06-26 | R2 production extract_field() vs stored profiles; no profile writes_

## Verdict: **PASS**

| Gate | Result |
|---|---|
| Rows evaluated | **207** |
| Target improved (fresh R2 vs stored) | **117** |
| Target regressed | **0** |
| P0 improved | **32** |
| Mandatory improved | **7/8** |
| Control regressions | **0** |
| Fresh R2 matches R1 selected_final | **207/207** |
| Some P0 improvement | **PASS** |
| No control downgrade | **PASS** |
| No target regression | **PASS** |
| No profile/eval/audit writes | **PASS** |

## Files changed

- `lab/extract_annual_report.py` (R2 situation-table helper + production guard)
- `lab/rnd_residual_fix_32c_dryrun.py` (R2 validation mode)
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r2_summary.md` (this file)

## Helper design

- **`extract_rnd_situation_table_numeric()`** — Pass 1 scans MD&A in-region pages for `研发投入情况表`; Pass 2 walks anchor candidates. Parses 费用化/资本化/合计 with 元/万元/百万元/亿元 unit scaling. Rejects P&L-only windows and cumulative narrative without table labels.
- **`extract_rnd_investment_baseline()`** — prior anchor+candidate path unchanged.

## Production guard design

- **`merge_rnd_investment_with_guard(baseline, situation)`** — strict-rank max with tie-break favoring baseline.
- Situation eligible only when `sit_rank >= baseline_rank` and not cumulative narrative.
- Blocks usable→partial regressions (e.g. 002415 situation=partial, baseline=usable → fresh=usable).

## Mandatory examples

| Code | Name | Stored | Baseline | Situation | Fresh R2 | R1 selected |
|---|---|---|---|---|---|---|
| 600011 | 华能国际 | partial | partial | usable | **usable** | usable |
| 600020 | 中原高速 | partial | partial | usable | **usable** | usable |
| 301221 | 光庭信息 | partial | partial | usable | **usable** | usable |
| 000333 | 美的集团 | partial | partial | partial | **partial** | partial |
| 688081 | 兴图新科 | not_found_unverified | not_found_unverified | usable | **usable** | usable |
| 600029 | 南方航空 | not_found_unverified | not_found_unverified | usable | **usable** | usable |
| 600115 | 中国东航 | not_found_unverified | not_found_unverified | usable | **usable** | usable |
| 600844 | 金煤科技 | not_found_unverified | not_found_unverified | usable | **usable** | usable |

## Controls

| Code | Stored | Baseline | Situation | Fresh R2 | Regressed? |
|---|---|---|---|---|---|
| 002415 | usable | usable | partial | **usable** | no |
| 300750 | usable | usable | not_found | **usable** | no |
| 600519 | usable | usable | usable | **usable** | no |
| 601012 | usable | usable | usable | **usable** | no |
| 688111 | usable | usable | usable | **usable** | no |

**002415**: stored=usable, situation=partial, fresh R2=**usable** — guard kept baseline.

**000333**: fresh R2=**partial** (not forced usable; cumulative narrative blocked).

## Regressed rows

_None_

## Recommended next step

1. **Scoped rnd_investment apply** on P0 residual list (dry-run refresh CSV first).
2. Human review for 000333 narrative partial.
3. Full-market apply only after P0 scoped apply + strict audit re-check.

## Safe to commit

- `lab/extract_annual_report.py`
- `lab/rnd_residual_fix_32c_dryrun.py`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r2_summary.md`

## Do not commit

- Profiles, eval_results, audit summaries, refresh CSVs, SQLite, YAML


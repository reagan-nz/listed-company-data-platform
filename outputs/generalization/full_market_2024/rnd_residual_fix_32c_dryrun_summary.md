# R&D residual fix #32c-R1 dry-run summary

_Generated: 2026-06-26 | R1 control-safe guard over cached PDFs; no profile writes_

## Verdict: **PASS**

| Gate | Result |
|---|---|
| Rows evaluated (targets + controls) | **207** |
| Target rows improved (selected_final vs stored) | **117** |
| Target rows regressed (selected_final) | **0** |
| P0 rows improved | **32** |
| Mandatory examples improved | **7/8** |
| Control regressions (selected_final) | **0** (R0: 1) |
| Experimental-only regressions blocked by guard | **1** |
| Some P0 rows show improved selection | **PASS** |
| No control downgrade | **PASS** |
| No target regression | **PASS** |
| No profile/eval/audit writes | **PASS** |

## Files changed

- `lab/rnd_residual_fix_32c_dryrun.py` (R1 guard refinement)
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_dryrun_summary.md` (this file)

## Guard design (R1)

Added `selected_final = max(production, experimental)` with strict rank:

| Label | Rank |
|---|---:|
| usable | 4 |
| partial | 3 |
| wrong | 2 |
| not_found_missed / not_found_unverified / not_found | 1 |

- **Production baseline** = best of stored profile and fresh `extract_field()`.
- **Experimental** is eligible only if `exp_rank >= prod_rank` and evidence is not cumulative narrative.
- **Tie-break** at same rank: stored > fresh > experimental (prefer production).
- **Improvement/regression** metrics use `selected_final`, not raw experimental.

## Why R0 failed on 002415

- **002415** 海康威视: stored/fresh strict=**usable**, raw experimental=**partial** (status=partial).
- Selected final=**usable** via `stored` — guard kept production.
- Root cause: situation-table pass on MD&A picked a weaker partial table candidate instead of the production anchor hit.

## Scope

- Same universe as R0: P0/P1 R&D residuals + mandatory examples + clean controls
- Compares stored / fresh / raw experimental / **selected_final** (dry-run only)

## Mandatory examples

| Code | Name | Stored | Fresh | Raw Exp | Selected | Source |
|---|---|---|---|---|---|---|
| 600011 | 华能国际 | partial | partial | usable | **usable** | experimental |
| 600020 | 中原高速 | partial | partial | usable | **usable** | experimental |
| 301221 | 光庭信息 | partial | partial | usable | **usable** | experimental |
| 000333 | 美的集团 | partial | partial | partial | **partial** | stored |
| 688081 | 兴图新科 | not_found_unverified | not_found_unverified | usable | **usable** | experimental |
| 600029 | 南方航空 | not_found_unverified | not_found_unverified | usable | **usable** | experimental |
| 600115 | 中国东航 | not_found_unverified | not_found_unverified | usable | **usable** | experimental |
| 600844 | 金煤科技 | not_found_unverified | not_found_unverified | usable | **usable** | experimental |

## Controls (before/after guard)

| Code | Stored | Fresh | Raw Exp | Selected (R1) | Regressed? |
|---|---|---|---|---|---|
| 002415 | usable | usable | partial | **usable** | no |
| 300750 | usable | usable | usable | **usable** | no |
| 600519 | usable | usable | usable | **usable** | no |
| 601012 | usable | usable | usable | **usable** | no |
| 688111 | usable | usable | usable | **usable** | no |

R0: `002415` raw experimental=partial → regressed. R1: selected_final=usable via stored/fresh.

## Improved targets (selected_final)

| Code | Name | P | Stored → Selected | Preview change |
|---|---|---|---|---|
| 301221 | 光庭信息 | P2 | partial → **usable** | 研发投入合计=7,021.75 万元 → 研发投入合计=70,217,500 |
| 600011 | 华能国际 | P0 | partial → **usable** | 研发费用=1,658,380,654 → 研发投入合计=1,696,000,000 |
| 600019 | 宝钢股份 | P1 | partial → **usable** | 研发投入合计=25,044; 费用化研发投入=3,779 → 研发投入合计=25,044,000,000 |
| 600020 | 中原高速 | P0 | partial → **usable** | 研发费用=500,000.00 → 研发投入合计=6,407,300 |
| 600026 | 中远海能 | P1 | partial → **usable** | 研发投入合计=5,405.70; 费用化研发投入=5,200.59 → 研发投入合计=54,057,000 |
| 600029 | 南方航空 | P0 | not_found_unverified → **usable** | 研发投入合计 545 研发投入总额占营业收入比例（%） 0.31 研发投入资本化的比重（%） 0.1 → 研发投入合计=545,000,000 |
| 600057 | 厦门象屿 | P0 | partial → **usable** | 费用化研发投入=9,622.42 → 研发投入合计=116,710,200 |
| 600058 | 五矿发展 | P1 | partial → **usable** | 研发投入合计=4,800.92; 费用化研发投入=1,372.21 → 研发投入合计=48,009,200 |
| 600064 | 南京高科 | P1 | partial → **usable** | 研发投入合计=4,121.08 → 研发投入合计=41,210,800 |
| 600097 | 开创国际 | P0 | not_found_unverified → **usable** | 研发投入总额占营业收入比例（%） 0.05 研发投入资本化的比重（%） (2).研发人员情况表 □适 → 研发投入合计=1,228,000 |
| 600113 | 浙江东日 | P0 | not_found_unverified → **usable** | 研发投入， 加快培育和发展科技创新能力，切实推进公司业务向产业链上下游延伸，较好地完成了年度的各 项 → 研发投入合计=9,036,200 |
| 600115 | 中国东航 | P0 | not_found_unverified → **usable** | 研发投入合计 350 研发投入总额占营业收入比例（%） 0.26 研发投入资本化的比重（%） 2.0 → 研发投入合计=350,000,000 |
| 600125 | 铁龙物流 | P0 | not_found_unverified → **usable** | 研发投入合计 28.25 研发投入总额占营业收入比例（%） 0.002 研发投入资本化的比重（%）  → 研发投入合计=282,500 |
| 600135 | 乐凯胶片 | P1 | partial → **usable** | 研发投入合计=10,159.19 → 研发投入合计=101,591,900 |
| 600221 | 海航控股 | P1 | partial → **usable** | 研发投入合计=36,483 → 研发投入合计=36,483,000 |
| 600236 | 桂冠电力 | P1 | partial → **usable** | 研发投入合计=25,095.67 → 研发投入合计=250,956,700 |
| 600293 | 三峡新材 | P1 | partial → **usable** | 研发投入合计=7,111.90 → 研发投入合计=71,119,000 |
| 600323 | 瀚蓝环境 | P1 | partial → **usable** | 研发投入合计=14,204.34; 费用化研发投入=7,366.91 → 研发投入合计=142,043,400 |
| 600343 | 航天动力 | P1 | partial → **usable** | 研发投入合计=5,541.76; 费用化研发投入=4,933.12 → 研发投入合计=55,417,600 |
| 600346 | 恒力石化 | P0 | partial → **usable** | 研发费用=170,288.42 → 研发投入合计=1,703,000,000 |
| 600354 | 敦煌种业 | P0 | partial → **usable** | 费用化研发投入=20,312,119.73 → 研发投入合计=26,459,835 |
| 600362 | 江西铜业 | P0 | not_found_unverified → **usable** | 研发投入合计 60.12 研发投入总额占营业收入比例（%） 1.15 研发投入资本化的比重（%） 8 → 研发投入合计=6,012,000,000 |
| 600415 | 小商品城 | P1 | partial → **usable** | 研发投入合计=5,218.95; 费用化研发投入=2,322.14 → 研发投入合计=52,189,500 |
| 600425 | 青松建化 | P1 | partial → **usable** | 研发投入合计=10,382.19 → 研发投入合计=103,821,900 |
| 600487 | 亨通光电 | P0 | partial → **usable** | 费用化研发投入=1,741,785,134.75 → 研发投入合计=1,894,602,593 |
| 600488 | 津药药业 | P1 | partial → **usable** | 研发投入合计=24,763.65; 费用化研发投入=20,449.20 → 研发投入合计=247,636,500 |
| 600525 | ST长园 | P1 | partial → **usable** | 研发投入合计=87,271.59; 费用化研发投入=86,991.96 → 研发投入合计=872,715,900 |
| 600548 | 深高速 | P1 | partial → **usable** | 研发投入合计=32,931 → 研发投入合计=32,931,000 |
| 600565 | ST迪马 | P0 | partial → **usable** | 费用化研发投入=46,326,410.65 → 研发投入合计=51,565,213 |
| 600613 | 神奇制药 | P1 | partial → **usable** | 研发投入合计=3,288.51 → 研发投入合计=32,885,100 |
| 600668 | 尖峰集团 | P1 | partial → **usable** | 研发投入合计=12,633.60; 费用化研发投入=10,589.79 → 研发投入合计=126,336,000 |
| 600710 | 苏美达 | P1 | partial → **usable** | 研发投入合计=47,630.93; 费用化研发投入=38,287.13 → 研发投入合计=476,309,300 |
| 600733 | 北汽蓝谷 | P0 | partial → **usable** | 费用化研发投入=94,380,985.37 → 研发投入合计=3,191,257,789 |
| 600737 | 中粮糖业 | P1 | partial → **usable** | 研发投入合计=5,654.04 → 研发投入合计=56,540,400 |
| 600750 | 华润江中 | P1 | partial → **usable** | 研发投入合计=21,357.87; 费用化研发投入=10,774.09 → 研发投入合计=213,578,700 |
| 600798 | 宁波海运 | P0 | not_found_unverified → **usable** | 研发投入合计 18.82 研发投入总额占营业收入比例（%） 0.01% 研发投入资本化的比重（%）  → 研发投入合计=188,200 |
| 600808 | 马钢股份 | P0 | partial → **usable** | 研发费用=1,103,101,885 → 研发投入合计=3,646,000,000 |
| 600826 | 兰生股份 | P0 | not_found_unverified → **usable** | 研发投入总额占营业收入比例（%） 0.11 研发投入资本化的比重（%） - (2).研发人员情况表  → 研发投入合计=1,848,800 |
| 600844 | 金煤科技 | P0 | not_found_unverified → **usable** | 研发费用减少，主要原因系报告期对纳入口径进行合规性调减所致。 经营活动产生的现金流量净额变动原因说明 → 研发投入合计=2,161,600 |
| 600855 | 航天长峰 | P1 | partial → **usable** | 研发投入合计=9,204.70; 费用化研发投入=8,845.67 → 研发投入合计=92,047,000 |
| … | (77 more) | | | |

## Regressed targets

_None_

## Experimental-only downgrades blocked by guard

- 002415 海康威视: exp=partial < prod → kept `stored` (usable)

## Failure / not-solved

- **000333** 美的集团: selected=partial — narrative_or_mixed_unit_partial

## Recommended next step

1. **Implement production helper** in `extract_annual_report.py` with the same guard (situation-table-first + max(prod, exp)).
2. Run scoped P0 dry-run refresh harness before any `--apply`.
3. Defer narrative partial (`000333`) to manual review.

## Safe to commit

- `lab/rnd_residual_fix_32c_dryrun.py`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_dryrun_summary.md`

## Do not commit

- Profiles, eval_results, audit summaries, refresh CSVs, SQLite, YAML


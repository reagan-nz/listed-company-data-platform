# R&D residual fix #32c-R3 scoped P0 refresh dry-run summary

_Generated: 2026-06-26 | Read-only dry-run; no profile/eval writes_

## Verdict: **PASS**

## Apply recommendation: **approve scoped P0 apply**

| Gate | Result |
|---|---|
| P0 pool field-rows (CSV) | **104** |
| P0 companies evaluated | **104** |
| P0 improved (strict) | **32** |
| P0 regressed | **0** |
| Mandatory improved | **7/8** |
| Mandatory gates passed | **8/8** |
| Control regressions | **0** |
| No target regression | **PASS** |
| No profile/eval writes | **PASS** |

## Files changed

- `lab/rnd_residual_fix_32c_r3_dryrun.py` (new)
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_dryrun_changes.csv`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_summary.md` (this file)

## Commands run

```bash
python lab/rnd_residual_fix_32c_r3_dryrun.py
```
```bash
python lab/refresh_rnd_full_market.py --dry-run --codes 000039,000420,000516,000546,000619,000626,000838,000862,000885,000888,000892,000982,001266,001376,002003,002016,002040,002183,002274,002285,002306,002366,002380,002423,002505,002569,002645,002656,002679,002731,002742,002769,002879,002891,002892,002896,300251,300280,300518,300810,301382,600011,600020,600029,600057,600082,600088,600097,600113,600115,600125,600185,600234,600238,600310,600346,600354,600362,600487,600508,600512,600565,600694,600696,600705,600706,600715,600733,600758,600798,600808,600826,600844,600846,600900,601021,601099,601186,601238,601330,601686,601727,601778,601865,601898,603000,603031,603259,603277,603309,603355,603558,603668,603682,603687,603698,603776,605090,605133,605199,605303,688081,688429,688571 --changes-csv outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_dryrun_changes.csv  # cross-validated: 104 targets, 32 status changes, 0 errors
```

## Target pool

- **Companies:** 104 (deduplicated)
- **Field-rows:** 104 (one rnd_investment row per company)
  - `profit_statement_研发费用_not_rnd_table`: 62
  - `expensed_vs_total_anchor_collision`: 27
  - `not_found_but_table_evidence`: 15

## Strict transition table (P0 pool)

| Transition | Count |
|---|---:|
| not_found_unverified -> usable | 14 |
| partial -> usable | 18 |
| partial -> partial | 71 |
| not_found_unverified -> not_found_unverified | 1 |
| **regressions (strict rank down)** | **0** |

## Mandatory examples

| Code | Name | In P0 pool | Before | After | Changed |
|---|---|---|---|---|---|
| 600011 | 华能国际 | yes | partial | **usable** | improved |
| 600020 | 中原高速 | yes | partial | **usable** | improved |
| 301221 | 光庭信息 | no (validation only) | partial | **usable** | improved |
| 000333 | 美的集团 | no (validation only) | partial | **partial** | same |
| 688081 | 兴图新科 | yes | not_found_unverified | **usable** | improved |
| 600029 | 南方航空 | yes | not_found_unverified | **usable** | improved |
| 600115 | 中国东航 | yes | not_found_unverified | **usable** | improved |
| 600844 | 金煤科技 | yes | not_found_unverified | **usable** | improved |

## Controls (spot-check, not in P0 apply pool)

| Code | Before | After | Regressed? |
|---|---|---|---|
| 002415 | usable | usable | no |
| 300750 | usable | usable | no |
| 600519 | usable | usable | no |
| 601012 | usable | usable | no |
| 688111 | usable | usable | no |

## Top improved (P0)

| Code | Name | Transition | After preview |
|---|---|---|---|
| 600029 | 南方航空 | not_found_unverified → **usable** | 研发投入合计=545,000,000 |
| 600097 | 开创国际 | not_found_unverified → **usable** | 研发投入合计=1,228,000 |
| 600113 | 浙江东日 | not_found_unverified → **usable** | 研发投入合计=9,036,200 |
| 600115 | 中国东航 | not_found_unverified → **usable** | 研发投入合计=350,000,000 |
| 600125 | 铁龙物流 | not_found_unverified → **usable** | 研发投入合计=282,500 |
| 600362 | 江西铜业 | not_found_unverified → **usable** | 研发投入合计=6,012,000,000 |
| 600798 | 宁波海运 | not_found_unverified → **usable** | 研发投入合计=188,200 |
| 600826 | 兰生股份 | not_found_unverified → **usable** | 研发投入合计=1,848,800 |
| 600844 | 金煤科技 | not_found_unverified → **usable** | 研发投入合计=2,161,600 |
| 601727 | 上海电气 | not_found_unverified → **usable** | 研发投入合计=5,694,000,000 |
| 601865 | 福莱特 | not_found_unverified → **usable** | 研发投入合计=604,790,000 |
| 601898 | 中煤能源 | not_found_unverified → **usable** | 研发投入合计=4,237,000,000 |
| 688081 | 兴图新科 | not_found_unverified → **usable** | 研发投入合计=40,751,382 |
| 688429 | 时创能源 | not_found_unverified → **usable** | 研发投入合计=231,489,952 |
| 600011 | 华能国际 | partial → **usable** | 研发投入合计=1,696,000,000 |
| 600020 | 中原高速 | partial → **usable** | 研发投入合计=6,407,300 |
| 600057 | 厦门象屿 | partial → **usable** | 研发投入合计=116,710,200 |
| 600346 | 恒力石化 | partial → **usable** | 研发投入合计=1,703,000,000 |
| 600354 | 敦煌种业 | partial → **usable** | 研发投入合计=26,459,835 |
| 600487 | 亨通光电 | partial → **usable** | 研发投入合计=1,894,602,593 |

## Unresolved (still partial/not_found after dry-run)

- **000039** 中集集团: partial — profit_statement_研发费用_not_rnd_table
- **000420** 吉林化纤: partial — profit_statement_研发费用_not_rnd_table
- **000516** 国际医学: partial — profit_statement_研发费用_not_rnd_table
- **000546** 金圆股份: partial — profit_statement_研发费用_not_rnd_table
- **000619** 海螺新材: partial — profit_statement_研发费用_not_rnd_table
- **000626** 远大控股: partial — profit_statement_研发费用_not_rnd_table
- **000838** *ST发展: partial — profit_statement_研发费用_not_rnd_table
- **000862** 银星能源: partial — profit_statement_研发费用_not_rnd_table
- **000885** 城发环境: partial — profit_statement_研发费用_not_rnd_table
- **000888** 峨眉山A: partial — profit_statement_研发费用_not_rnd_table
- **000892** 欢瑞世纪: partial — profit_statement_研发费用_not_rnd_table
- **000982** 中银绒业: partial — profit_statement_研发费用_not_rnd_table
- **001266** 宏英智能: partial — profit_statement_研发费用_not_rnd_table
- **001376** 百通能源: partial — profit_statement_研发费用_not_rnd_table
- **002003** 伟星股份: partial — profit_statement_研发费用_not_rnd_table
- … and 57 more

## Regressions

_None_

## Apply command (do not run until approved)

```bash
cd listed_company_data_collector
python lab/refresh_rnd_full_market.py --apply --codes 000039,000420,000516,000546,000619,000626,000838,000862,000885,000888,000892,000982,001266,001376,002003,002016,002040,002183,002274,002285,002306,002366,002380,002423,002505,002569,002645,002656,002679,002731,002742,002769,002879,002891,002892,002896,300251,300280,300518,300810,301382,600011,600020,600029,600057,600082,600088,600097,600113,600115,600125,600185,600234,600238,600310,600346,600354,600362,600487,600508,600512,600565,600694,600696,600705,600706,600715,600733,600758,600798,600808,600826,600844,600846,600900,601021,601099,601186,601238,601330,601686,601727,601778,601865,601898,603000,603031,603259,603277,603309,603355,603558,603668,603682,603687,603698,603776,605090,605133,605199,605303,688081,688429,688571 --changes-csv outputs/generalization/full_market_2024/rnd_refresh_changes_32c_apply.csv
```

## Rollback plan

- Profiles: restore `company_profile.json.bak.rnd_refresh_20260624` per company
- Eval: restore `eval_results.json.bak.rnd_refresh_20260624` per board
- Re-run strict audit on restored profiles to confirm baseline

## Safe to commit

- `lab/rnd_residual_fix_32c_r3_dryrun.py`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_dryrun_changes.csv`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_summary.md`

## Do not commit

- company_profile.json, eval_results.json, rnd_refresh_changes.csv (production), strict_audit_summary.md, YAML


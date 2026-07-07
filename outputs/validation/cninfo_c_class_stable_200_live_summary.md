# CNINFO C Class Stable 200 Non-BSE (Live) Summary

_生成时间：2026-07-07_

## Run mode

**live**

## Scope

- **Sample:** `lab/eval_companies_c_class_stable_200_non_bse.yaml` (200 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

## Stable sample design

- **Parent:** `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` (889 companies)
- **Eligible pool after cleaning:** 863
- **Excluded from pool:** 26

### Exclusion rules

- exclude six_fail_hold (26)
- exclude abnormal_review explicit
- exclude name 退市 / suffix 退 / delisted / terminated
- exclude board bse
- exclude suspicious_duplicate_orgid 000765; keep 001267
- *ST not auto-excluded unless in six_fail_hold or abnormal_review
- stratified sample by board toward 889 non-BSE distribution

### Excluded by reason

| reason | count |
|--------|-------|
| `six_fail_hold` | 26 |

### Board targets vs actual

| board | target | actual |
|-------|--------|--------|
| `chinext` | 52 | 52 |
| `sse_main` | 66 | 66 |
| `star` | 28 | 28 |
| `szse_main` | 54 | 54 |

### Source policy（[source status decision](../plans/cninfo_c_class_source_status_decision.md)）

- **主判定 source（6）：** basic · dividend · executive · share_capital · top_shareholders · top_float
- **observe_only：** security（不绑定主 gate）
- **derived_no_separate_fetch：** contact · business_scope · industry
- **source_partial 提醒：** share_capital · top_float（reachable ≠ non_empty）

## Active-only 样本分层

| board | count |
|-------|-------|
| `chinext` | 52 |
| `sse_main` | 66 |
| `star` | 28 |
| `szse_main` | 54 |

**pass / fail / blocked / 429:** 1200 / 0 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 1400

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 200/200 | 100.0% | 200 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 200 | 0 |
| `cninfo_dividend_financing_profile` | 200/200 | 100.0% | 198 | 99.0% | 2 | 0 | 0 | 0 | 0.0% | 200 | 0 |
| `cninfo_executive_profile` | 200/200 | 100.0% | 200 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 200 | 0 |
| `cninfo_share_capital_profile` | 200/200 | 100.0% | 200 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 200 | 0 |
| `cninfo_top_shareholders_profile` | 200/200 | 100.0% | 200 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 200 | 0 |
| `cninfo_top_float_shareholders_profile` | 200/200 | 100.0% | 200 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 200 | 0 |
| `cninfo_company_security_profile` | 200/200 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

## Basic key field fill_rate (endpoint_found only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 100.0% |
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F015V` | 100.0% |
| `F016V` | 100.0% |
| `F032V` | 100.0% |
| `MARKET` | 100.0% |

## Dividend field fill_rate (non-empty records only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 96.0% |
| `F007V` | 100.0% |
| `F018D` | 100.0% |
| `F020D` | 98.5% |
| `F023D` | 92.4% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `endpoint_found` | 198 |
| `valid_empty` | 2 |

## empty_but_valid 股东源案例

- 无

## Shareholder empty_but_valid policy

- **empty_but_valid_count（股东源）:** 0
- HTTP 200 · json/resultCode 正常 · `data.records` 为空 list → `empty_but_valid_response`
- **不计** http_error / blocked / schema_unexpected；**计入** endpoint reachable
- 主 gate **case_result=pass**（非接口失败）；**non_empty_rate** 仍下降
- top_float / top_shareholders 标记 **source_partial**（reachable ≠ non_empty）

## Derived sources (from basic basicInformation)

### `cninfo_company_contact_profile`

| field | fill_rate% |
|-------|------------|
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F006V` | 100.0% |
| `F011V` | 99.0% |
| `F012V` | 100.0% |
| `F013V` | 100.0% |
| `F014V` | 100.0% |
| `F018V` | 100.0% |

### `cninfo_company_business_scope`

| field | fill_rate% |
|-------|------------|
| `F015V` | 100.0% |
| `F016V` | 100.0% |
| `F017V` | 100.0% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 100.0% |
| `F044V` | 96.0% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `chinext` | `cninfo_company_basic_profile` | 52 | 52 | 100.0% | 100.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 52 | 52 | 100.0% | 100.0% |
| `chinext` | `cninfo_executive_profile` | 52 | 52 | 100.0% | 100.0% |
| `chinext` | `cninfo_share_capital_profile` | 52 | 52 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_shareholders_profile` | 52 | 52 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 52 | 52 | 100.0% | 100.0% |
| `sse_main` | `cninfo_company_basic_profile` | 66 | 66 | 100.0% | 100.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 66 | 66 | 100.0% | 100.0% |
| `sse_main` | `cninfo_executive_profile` | 66 | 66 | 100.0% | 100.0% |
| `sse_main` | `cninfo_share_capital_profile` | 66 | 66 | 100.0% | 100.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 66 | 66 | 100.0% | 100.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 66 | 66 | 100.0% | 100.0% |
| `star` | `cninfo_company_basic_profile` | 28 | 28 | 100.0% | 100.0% |
| `star` | `cninfo_dividend_financing_profile` | 28 | 28 | 100.0% | 100.0% |
| `star` | `cninfo_executive_profile` | 28 | 28 | 100.0% | 100.0% |
| `star` | `cninfo_share_capital_profile` | 28 | 28 | 100.0% | 100.0% |
| `star` | `cninfo_top_shareholders_profile` | 28 | 28 | 100.0% | 100.0% |
| `star` | `cninfo_top_float_shareholders_profile` | 28 | 28 | 100.0% | 100.0% |
| `szse_main` | `cninfo_company_basic_profile` | 54 | 54 | 100.0% | 100.0% |
| `szse_main` | `cninfo_dividend_financing_profile` | 54 | 54 | 100.0% | 100.0% |
| `szse_main` | `cninfo_executive_profile` | 54 | 54 | 100.0% | 100.0% |
| `szse_main` | `cninfo_share_capital_profile` | 54 | 54 | 100.0% | 100.0% |
| `szse_main` | `cninfo_top_shareholders_profile` | 54 | 54 | 100.0% | 100.0% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 54 | 54 | 100.0% | 100.0% |

**Overall:** pass=1200 fail=0 skipped=0 **result=LIVE_PASS**

## Gate: dividend YAML backfill

**Decision: GO**

dividend reachability=100.0% error_rate=0.0% valid_empty=2. 建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。

## Gate: stable 200 non-BSE

**stable_gate = LIVE_COMPLETED_DIAGNOSIS_REQUIRED**

Cleaned stable sample **200** 家；live **已完成**（见 Overall result）；post-live 诊断 required。

## Caveats

- **stable 200 non-BSE live**；非 889 全量；非 verified / testing_stable_sample。
- **testing** status only; **no verified**.
- **No testing_stable_sample**（文件名 stable 仅为设计语义）。
- No database ingestion.
- observe_only / derived_no_separate_fetch / source_partial 口径见 [source status decision](../plans/cninfo_c_class_source_status_decision.md)。

## Appendix

详见 [cninfo_c_class_stable_200_live_summary.csv](cninfo_c_class_stable_200_live_summary.csv)。

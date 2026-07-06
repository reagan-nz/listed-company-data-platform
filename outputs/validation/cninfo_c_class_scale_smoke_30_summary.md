# CNINFO C Class 30-Company Scale Smoke Summary

_生成时间：2026-07-06_

## Run mode

**live**

## Scope

- **Sample:** `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/lab/eval_companies_c_class_smoke_30.yaml` (30 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

**Planned live requests per company:** 7
**Total planned (live):** 210

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 27/30 | 90.0% | 27 | 90.0% | 0 | 0 | 0 | 3 | 10.0% | 27 | 3 |
| `cninfo_dividend_financing_profile` | 27/30 | 90.0% | 25 | 83.3% | 2 | 0 | 0 | 3 | 10.0% | 27 | 3 |
| `cninfo_executive_profile` | 27/30 | 90.0% | 27 | 90.0% | 0 | 0 | 0 | 3 | 10.0% | 27 | 3 |
| `cninfo_share_capital_profile` | 27/30 | 90.0% | 27 | 90.0% | 0 | 0 | 0 | 3 | 10.0% | 27 | 3 |
| `cninfo_top_shareholders_profile` | 26/30 | 86.7% | 26 | 86.7% | 0 | 0 | 0 | 3 | 10.0% | 26 | 4 |
| `cninfo_top_float_shareholders_profile` | 25/30 | 83.3% | 25 | 83.3% | 0 | 0 | 0 | 3 | 10.0% | 25 | 5 |
| `cninfo_company_security_profile` | 30/30 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

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
| `F001V` | 100.0% |
| `F007V` | 100.0% |
| `F018D` | 84.0% |
| `F020D` | 84.0% |
| `F023D` | 84.0% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `endpoint_found` | 25 |
| `http_error` | 3 |
| `valid_empty` | 2 |

## Derived sources (from basic basicInformation)

### `cninfo_company_contact_profile`

| field | fill_rate% |
|-------|------------|
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F006V` | 100.0% |
| `F011V` | 100.0% |
| `F012V` | 100.0% |
| `F013V` | 100.0% |
| `F014V` | 100.0% |
| `F018V` | 100.0% |

### `cninfo_company_business_scope`

| field | fill_rate% |
|-------|------------|
| `F015V` | 100.0% |
| `F016V` | 100.0% |
| `F017V` | 88.9% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 100.0% |
| `F044V` | 92.6% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `bse` | `cninfo_company_basic_profile` | 4 | 4 | 100.0% | 100.0% |
| `bse` | `cninfo_dividend_financing_profile` | 4 | 4 | 100.0% | 100.0% |
| `bse` | `cninfo_executive_profile` | 4 | 4 | 100.0% | 100.0% |
| `bse` | `cninfo_share_capital_profile` | 4 | 4 | 100.0% | 100.0% |
| `bse` | `cninfo_top_shareholders_profile` | 4 | 4 | 100.0% | 100.0% |
| `bse` | `cninfo_top_float_shareholders_profile` | 3 | 4 | 75.0% | 75.0% |
| `chinext` | `cninfo_company_basic_profile` | 6 | 6 | 100.0% | 100.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 6 | 6 | 100.0% | 100.0% |
| `chinext` | `cninfo_executive_profile` | 6 | 6 | 100.0% | 100.0% |
| `chinext` | `cninfo_share_capital_profile` | 6 | 6 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_shareholders_profile` | 6 | 6 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 6 | 6 | 100.0% | 100.0% |
| `sse_main` | `cninfo_company_basic_profile` | 6 | 8 | 75.0% | 75.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 6 | 8 | 75.0% | 75.0% |
| `sse_main` | `cninfo_executive_profile` | 6 | 8 | 75.0% | 75.0% |
| `sse_main` | `cninfo_share_capital_profile` | 6 | 8 | 75.0% | 75.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 6 | 8 | 75.0% | 75.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 6 | 8 | 75.0% | 75.0% |
| `star` | `cninfo_company_basic_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_dividend_financing_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_executive_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_share_capital_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_top_shareholders_profile` | 5 | 6 | 83.3% | 83.3% |
| `star` | `cninfo_top_float_shareholders_profile` | 5 | 6 | 83.3% | 83.3% |
| `szse_main` | `cninfo_company_basic_profile` | 5 | 6 | 83.3% | 83.3% |
| `szse_main` | `cninfo_dividend_financing_profile` | 5 | 6 | 83.3% | 83.3% |
| `szse_main` | `cninfo_executive_profile` | 5 | 6 | 83.3% | 83.3% |
| `szse_main` | `cninfo_share_capital_profile` | 5 | 6 | 83.3% | 83.3% |
| `szse_main` | `cninfo_top_shareholders_profile` | 5 | 6 | 83.3% | 83.3% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 5 | 6 | 83.3% | 83.3% |

**Overall:** pass=159 fail=21 skipped=0 **result=LIVE_PARTIAL**

## Gate: dividend YAML backfill

**Decision: NO-GO**

dividend reachability=90.0% error_rate=10.0% — 未达门槛 (reach>=95% & error<5%).

## Gate: expand to 200 companies

**Decision: CONDITIONAL**

扩至 200 家前需修复：cninfo_company_basic_profile: reachability 90.0%; cninfo_company_basic_profile: error_rate 10.0%; cninfo_dividend_financing_profile: reachability 90.0%; cninfo_dividend_financing_profile: error_rate 10.0%; cninfo_executive_profile: reachability 90.0%; cninfo_executive_profile: error_rate 10.0%; cninfo_share_capital_profile: reachability 90.0%; cninfo_share_capital_profile: error_rate 10.0%; cninfo_top_shareholders_profile: reachability 86.7%; cninfo_top_shareholders_profile: error_rate 10.0%; cninfo_top_float_shareholders_profile: reachability 83.3%; cninfo_top_float_shareholders_profile: error_rate 10.0%; board bse / cninfo_top_float_shareholders_profile: pass 75.0%; board sse_main / cninfo_company_basic_profile: pass 75.0%; board sse_main / cninfo_dividend_financing_profile: pass 75.0%; board sse_main / cninfo_executive_profile: pass 75.0%; board sse_main / cninfo_share_capital_profile: pass 75.0%; board sse_main / cninfo_top_shareholders_profile: pass 75.0%; board sse_main / cninfo_top_float_shareholders_profile: pass 75.0%

## Caveats

- 30-company stratified sample only; not full-market.
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security uses hardcoded `secType=szshe`; cross-board risk observed separately.

## Appendix

详见 [cninfo_c_class_scale_smoke_30_report.csv](cninfo_c_class_scale_smoke_30_report.csv)。

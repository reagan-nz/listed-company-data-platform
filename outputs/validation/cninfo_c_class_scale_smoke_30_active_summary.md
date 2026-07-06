# CNINFO C Class 30-Company Scale Smoke Summary (Active-Only)

_生成时间：2026-07-06_

## Run mode

**live**

## Scope

- **Sample:** `lab/eval_companies_c_class_smoke_30_active.yaml` (30 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

## Active-only 样本分层

| board | count |
|-------|-------|
| `bse` | 4 |
| `chinext` | 6 |
| `sse_main` | 8 |
| `star` | 6 |
| `szse_main` | 6 |

**pass / fail / blocked / 429:** 177 / 3 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 210

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 30/30 | 100.0% | 30 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 30 | 0 |
| `cninfo_dividend_financing_profile` | 30/30 | 100.0% | 28 | 93.3% | 2 | 0 | 0 | 0 | 0.0% | 30 | 0 |
| `cninfo_executive_profile` | 30/30 | 100.0% | 30 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 30 | 0 |
| `cninfo_share_capital_profile` | 30/30 | 100.0% | 30 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 30 | 0 |
| `cninfo_top_shareholders_profile` | 29/30 | 96.7% | 29 | 96.7% | 0 | 0 | 0 | 0 | 0.0% | 29 | 1 |
| `cninfo_top_float_shareholders_profile` | 28/30 | 93.3% | 28 | 93.3% | 0 | 0 | 0 | 0 | 0.0% | 28 | 2 |
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
| `F018D` | 85.7% |
| `F020D` | 85.7% |
| `F023D` | 85.7% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `endpoint_found` | 28 |
| `valid_empty` | 2 |

## empty_but_valid 股东源案例

| company_code | company_name | board | source_id | record_count |
|--------------|--------------|-------|-----------|--------------|
| `688797` | 臻宝科技 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `920186` | 中科仪 | `bse` | `cninfo_top_float_shareholders_profile` | 0 |

## 与上一轮含退市样本对比

**上一轮：** 含退市样本（上一轮） · pass=159 fail=21
**本轮 active-only：** pass=177 fail=3

| source_id | 上一轮 reachability% | 本轮 reachability% | Δ fail |
|-----------|---------------------|-------------------|--------|
| `cninfo_company_basic_profile` | 90.0% | 100.0% | -3 |
| `cninfo_dividend_financing_profile` | 90.0% | 100.0% | -3 |
| `cninfo_executive_profile` | 90.0% | 100.0% | -3 |
| `cninfo_share_capital_profile` | 90.0% | 100.0% | -3 |
| `cninfo_top_shareholders_profile` | 86.7% | 96.7% | -3 |
| `cninfo_top_float_shareholders_profile` | 83.3% | 93.3% | -3 |
| `cninfo_company_security_profile` | 100.0% | 100.0% | 0 |

**解读：** 上一轮 3 家退市标的（600647 / 600002 / 002473）各拖累 6 条主判定 fail；剔除后 fail 应显著下降，reachability 应升至 ~100%。


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
| `F017V` | 90.0% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 100.0% |
| `F044V` | 93.3% |
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
| `sse_main` | `cninfo_company_basic_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_executive_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_share_capital_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 8 | 8 | 100.0% | 100.0% |
| `star` | `cninfo_company_basic_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_dividend_financing_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_executive_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_share_capital_profile` | 6 | 6 | 100.0% | 100.0% |
| `star` | `cninfo_top_shareholders_profile` | 5 | 6 | 83.3% | 83.3% |
| `star` | `cninfo_top_float_shareholders_profile` | 5 | 6 | 83.3% | 83.3% |
| `szse_main` | `cninfo_company_basic_profile` | 6 | 6 | 100.0% | 100.0% |
| `szse_main` | `cninfo_dividend_financing_profile` | 6 | 6 | 100.0% | 100.0% |
| `szse_main` | `cninfo_executive_profile` | 6 | 6 | 100.0% | 100.0% |
| `szse_main` | `cninfo_share_capital_profile` | 6 | 6 | 100.0% | 100.0% |
| `szse_main` | `cninfo_top_shareholders_profile` | 6 | 6 | 100.0% | 100.0% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 6 | 6 | 100.0% | 100.0% |

**Overall:** pass=177 fail=3 skipped=0 **result=LIVE_PARTIAL**

## Gate: dividend YAML backfill

**Decision: GO**

dividend reachability=100.0% error_rate=0.0% valid_empty=2. 建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。

## Gate: expand to 200 companies

**enter_200 = CONDITIONAL**

active-only 样本扩至 200 家前需修复：board bse / cninfo_top_float_shareholders_profile: pass 75.0%

## Caveats

- 30-company stratified sample only; not full-market.
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security uses hardcoded `secType=szshe`; cross-board risk observed separately.
- active 样本以 YAML 名称 heuristics 剔除退市，未联网校验 *ST 等上市状态。

## Appendix

详见 [cninfo_c_class_scale_smoke_30_active_summary.csv](cninfo_c_class_scale_smoke_30_active_summary.csv)。

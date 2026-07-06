# CNINFO C Class 195-Company Scale Smoke Summary (Active-Only)

_生成时间：2026-07-06_

## Run mode

**dry-run**

## Scope

- **Sample:** `lab/eval_companies_c_class_smoke_200_active.yaml` (195 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

## Active-only 样本分层

| board | count |
|-------|-------|
| `bse` | 20 |
| `chinext` | 45 |
| `sse_main` | 57 |
| `star` | 25 |
| `szse_main` | 48 |

**pass / fail / blocked / 429:** 0 / 0 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 1365

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 0/195 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_dividend_financing_profile` | 0/195 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_executive_profile` | 0/195 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_share_capital_profile` | 0/195 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_top_shareholders_profile` | 0/195 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_top_float_shareholders_profile` | 0/195 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_company_security_profile` | 0/195 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

## Basic key field fill_rate (endpoint_found only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 0.0% |
| `F004V` | 0.0% |
| `F005V` | 0.0% |
| `F015V` | 0.0% |
| `F016V` | 0.0% |
| `F032V` | 0.0% |
| `MARKET` | 0.0% |

## Dividend field fill_rate (non-empty records only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 0.0% |
| `F007V` | 0.0% |
| `F018D` | 0.0% |
| `F020D` | 0.0% |
| `F023D` | 0.0% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `` | 195 |

## empty_but_valid 股东源案例

- 无

## 与上一轮含退市样本对比

**上一轮：** 含退市样本（上一轮） · pass=159 fail=21
**本轮 active-only：** pass=0 fail=0

| source_id | 上一轮 reachability% | 本轮 reachability% | Δ fail |
|-----------|---------------------|-------------------|--------|
| `cninfo_company_basic_profile` | 90.0% | 0.0% | -3 |
| `cninfo_dividend_financing_profile` | 90.0% | 0.0% | -3 |
| `cninfo_executive_profile` | 90.0% | 0.0% | -3 |
| `cninfo_share_capital_profile` | 90.0% | 0.0% | -3 |
| `cninfo_top_shareholders_profile` | 86.7% | 0.0% | -4 |
| `cninfo_top_float_shareholders_profile` | 83.3% | 0.0% | -5 |
| `cninfo_company_security_profile` | 100.0% | 0.0% | 0 |

**解读：** 上一轮 3 家退市标的（600647 / 600002 / 002473）各拖累 6 条主判定 fail；剔除后 fail 应显著下降，reachability 应升至 ~100%。


## Derived sources (from basic basicInformation)

### `cninfo_company_contact_profile`

| field | fill_rate% |
|-------|------------|
| `F004V` | 0.0% |
| `F005V` | 0.0% |
| `F006V` | 0.0% |
| `F011V` | 0.0% |
| `F012V` | 0.0% |
| `F013V` | 0.0% |
| `F014V` | 0.0% |
| `F018V` | 0.0% |

### `cninfo_company_business_scope`

| field | fill_rate% |
|-------|------------|
| `F015V` | 0.0% |
| `F016V` | 0.0% |
| `F017V` | 0.0% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 0.0% |
| `F044V` | 0.0% |
| `MARKET` | 0.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `bse` | `cninfo_company_basic_profile` | 0 | 20 | 0.0% | 0.0% |
| `bse` | `cninfo_dividend_financing_profile` | 0 | 20 | 0.0% | 0.0% |
| `bse` | `cninfo_executive_profile` | 0 | 20 | 0.0% | 0.0% |
| `bse` | `cninfo_share_capital_profile` | 0 | 20 | 0.0% | 0.0% |
| `bse` | `cninfo_top_shareholders_profile` | 0 | 20 | 0.0% | 0.0% |
| `bse` | `cninfo_top_float_shareholders_profile` | 0 | 20 | 0.0% | 0.0% |
| `chinext` | `cninfo_company_basic_profile` | 0 | 45 | 0.0% | 0.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 0 | 45 | 0.0% | 0.0% |
| `chinext` | `cninfo_executive_profile` | 0 | 45 | 0.0% | 0.0% |
| `chinext` | `cninfo_share_capital_profile` | 0 | 45 | 0.0% | 0.0% |
| `chinext` | `cninfo_top_shareholders_profile` | 0 | 45 | 0.0% | 0.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 0 | 45 | 0.0% | 0.0% |
| `sse_main` | `cninfo_company_basic_profile` | 0 | 57 | 0.0% | 0.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 0 | 57 | 0.0% | 0.0% |
| `sse_main` | `cninfo_executive_profile` | 0 | 57 | 0.0% | 0.0% |
| `sse_main` | `cninfo_share_capital_profile` | 0 | 57 | 0.0% | 0.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 0 | 57 | 0.0% | 0.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 0 | 57 | 0.0% | 0.0% |
| `star` | `cninfo_company_basic_profile` | 0 | 25 | 0.0% | 0.0% |
| `star` | `cninfo_dividend_financing_profile` | 0 | 25 | 0.0% | 0.0% |
| `star` | `cninfo_executive_profile` | 0 | 25 | 0.0% | 0.0% |
| `star` | `cninfo_share_capital_profile` | 0 | 25 | 0.0% | 0.0% |
| `star` | `cninfo_top_shareholders_profile` | 0 | 25 | 0.0% | 0.0% |
| `star` | `cninfo_top_float_shareholders_profile` | 0 | 25 | 0.0% | 0.0% |
| `szse_main` | `cninfo_company_basic_profile` | 0 | 48 | 0.0% | 0.0% |
| `szse_main` | `cninfo_dividend_financing_profile` | 0 | 48 | 0.0% | 0.0% |
| `szse_main` | `cninfo_executive_profile` | 0 | 48 | 0.0% | 0.0% |
| `szse_main` | `cninfo_share_capital_profile` | 0 | 48 | 0.0% | 0.0% |
| `szse_main` | `cninfo_top_shareholders_profile` | 0 | 48 | 0.0% | 0.0% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 0 | 48 | 0.0% | 0.0% |

**Overall:** pass=0 fail=0 skipped=1365 **result=DRY_RUN_ONLY**

## Dry-run confirmation

- **No CNINFO requests executed**（all cases skipped）
- **Company count:** 195
- **Cases:** 1365 = 195 × 7 sources
- **Planned live requests:** 1365
- **主判定 source:** basic · dividend · P2-A 四源（executive / share_capital / top_shareholders / top_float）
- **security_profile:** observe-only（不绑定主判定 gate）
- **derived 三源:** contact / business_scope / industry — 无单独 HTTP 请求，仅 live 时随 basic fill_rate 统计

## Gate: dividend YAML backfill

**Decision: NO-GO**

dividend reachability=0.0% error_rate=0.0% — 未达门槛 (reach>=95% & error<5%).

## Gate: expand to 200 companies

**enter_200 = CONDITIONAL**

active-only 样本扩至 200 家前需修复：basic reachability 0.0%; basic non_empty 0.0%; dividend reachability 0.0%; board bse / cninfo_company_basic_profile: pass 0.0%; board bse / cninfo_dividend_financing_profile: pass 0.0%; board bse / cninfo_executive_profile: pass 0.0%; board bse / cninfo_share_capital_profile: pass 0.0%; board bse / cninfo_top_shareholders_profile: pass 0.0%; board bse / cninfo_top_float_shareholders_profile: pass 0.0%; board chinext / cninfo_company_basic_profile: pass 0.0%; board chinext / cninfo_dividend_financing_profile: pass 0.0%; board chinext / cninfo_executive_profile: pass 0.0%; board chinext / cninfo_share_capital_profile: pass 0.0%; board chinext / cninfo_top_shareholders_profile: pass 0.0%; board chinext / cninfo_top_float_shareholders_profile: pass 0.0%; board sse_main / cninfo_company_basic_profile: pass 0.0%; board sse_main / cninfo_dividend_financing_profile: pass 0.0%; board sse_main / cninfo_executive_profile: pass 0.0%; board sse_main / cninfo_share_capital_profile: pass 0.0%; board sse_main / cninfo_top_shareholders_profile: pass 0.0%; board sse_main / cninfo_top_float_shareholders_profile: pass 0.0%; board star / cninfo_company_basic_profile: pass 0.0%; board star / cninfo_dividend_financing_profile: pass 0.0%; board star / cninfo_executive_profile: pass 0.0%; board star / cninfo_share_capital_profile: pass 0.0%; board star / cninfo_top_shareholders_profile: pass 0.0%; board star / cninfo_top_float_shareholders_profile: pass 0.0%; board szse_main / cninfo_company_basic_profile: pass 0.0%; board szse_main / cninfo_dividend_financing_profile: pass 0.0%; board szse_main / cninfo_executive_profile: pass 0.0%; board szse_main / cninfo_share_capital_profile: pass 0.0%; board szse_main / cninfo_top_shareholders_profile: pass 0.0%; board szse_main / cninfo_top_float_shareholders_profile: pass 0.0%

## Caveats

- 30-company stratified sample only; not full-market.
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security uses hardcoded `secType=szshe`; cross-board risk observed separately.
- active 样本以 YAML 名称 heuristics 剔除退市，未联网校验 *ST 等上市状态。

## Appendix

详见 [cninfo_c_class_scale_smoke_200_active_summary.csv](cninfo_c_class_scale_smoke_200_active_summary.csv)。

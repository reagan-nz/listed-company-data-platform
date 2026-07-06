# CNINFO C Class 195-Company Scale Smoke Summary (Active-Only)

_生成时间：2026-07-06_

## Run mode

**live**

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

**pass / fail / blocked / 429:** 1101 / 69 / 4 / 0

**Planned live requests per company:** 7
**Total planned (live):** 1365

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 184/195 | 94.4% | 184 | 94.4% | 0 | 0 | 0 | 11 | 5.6% | 184 | 11 |
| `cninfo_dividend_financing_profile` | 184/195 | 94.4% | 181 | 92.8% | 3 | 0 | 0 | 11 | 5.6% | 184 | 11 |
| `cninfo_executive_profile` | 184/195 | 94.4% | 184 | 94.4% | 0 | 2 | 0 | 9 | 5.6% | 184 | 11 |
| `cninfo_share_capital_profile` | 184/195 | 94.4% | 184 | 94.4% | 0 | 0 | 0 | 11 | 5.6% | 184 | 11 |
| `cninfo_top_shareholders_profile` | 183/195 | 93.8% | 183 | 93.8% | 0 | 1 | 0 | 10 | 5.6% | 183 | 12 |
| `cninfo_top_float_shareholders_profile` | 182/195 | 93.3% | 182 | 93.3% | 0 | 1 | 0 | 10 | 5.6% | 182 | 13 |
| `cninfo_company_security_profile` | 195/195 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

## Basic key field fill_rate (endpoint_found only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 100.0% |
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F015V` | 100.0% |
| `F016V` | 99.5% |
| `F032V` | 100.0% |
| `MARKET` | 100.0% |

## Dividend field fill_rate (non-empty records only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 98.3% |
| `F007V` | 100.0% |
| `F018D` | 93.4% |
| `F020D` | 92.8% |
| `F023D` | 86.7% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `endpoint_found` | 181 |
| `http_error` | 11 |
| `valid_empty` | 3 |

## empty_but_valid 股东源案例

| company_code | company_name | board | source_id | record_count |
|--------------|--------------|-------|-----------|--------------|
| `688797` | 臻宝科技 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `920186` | 中科仪 | `bse` | `cninfo_top_float_shareholders_profile` | 0 |

## 与上一轮含退市样本对比（historical reference only）

> **注意：** 本节对比的是 **30-company 含退市样本** vs **195-company active live**，样本规模与宇宙不同，**不作为本轮 200 live gate 依据**。详见 [BSE diagnosis](cninfo_c_class_scale_smoke_200_bse_diagnosis.md)。

**上一轮（30 家含退市）：** pass=159 fail=21
**本轮（195 active live）：** pass=1101 fail=69

| source_id | 上一轮 reachability% (n=30) | 本轮 reachability% (n=195) | 备注 |
|-----------|----------------------------|------------------------------|------|
| `cninfo_company_basic_profile` | 90.0% | 94.4% | 不可直接对比 Δ fail |
| `cninfo_dividend_financing_profile` | 90.0% | 94.4% | 不可直接对比 Δ fail |
| `cninfo_executive_profile` | 90.0% | 94.4% | 不可直接对比 Δ fail |
| `cninfo_share_capital_profile` | 90.0% | 94.4% | 不可直接对比 Δ fail |
| `cninfo_top_shareholders_profile` | 86.7% | 93.8% | 不可直接对比 Δ fail |
| `cninfo_top_float_shareholders_profile` | 83.3% | 93.3% | 不可直接对比 Δ fail |
| `cninfo_company_security_profile` | 100.0% | 100.0% | observe-only |

**历史解读：** 30 家轮次中 3 家退市标的（600647 / 600002 / 002473）各拖累 6 条主判定 fail；与 200 轮 BSE 旧代码 / ST 异常失败模式不同。


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
| `F014V` | 98.9% |
| `F018V` | 99.5% |

### `cninfo_company_business_scope`

| field | fill_rate% |
|-------|------------|
| `F015V` | 100.0% |
| `F016V` | 99.5% |
| `F017V` | 93.5% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 100.0% |
| `F044V` | 95.1% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `bse` | `cninfo_company_basic_profile` | 12 | 20 | 60.0% | 60.0% |
| `bse` | `cninfo_dividend_financing_profile` | 12 | 20 | 60.0% | 60.0% |
| `bse` | `cninfo_executive_profile` | 12 | 20 | 60.0% | 60.0% |
| `bse` | `cninfo_share_capital_profile` | 12 | 20 | 60.0% | 60.0% |
| `bse` | `cninfo_top_shareholders_profile` | 12 | 20 | 60.0% | 60.0% |
| `bse` | `cninfo_top_float_shareholders_profile` | 11 | 20 | 55.0% | 55.0% |
| `chinext` | `cninfo_company_basic_profile` | 45 | 45 | 100.0% | 100.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 45 | 45 | 100.0% | 100.0% |
| `chinext` | `cninfo_executive_profile` | 45 | 45 | 100.0% | 100.0% |
| `chinext` | `cninfo_share_capital_profile` | 45 | 45 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_shareholders_profile` | 45 | 45 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 45 | 45 | 100.0% | 100.0% |
| `sse_main` | `cninfo_company_basic_profile` | 55 | 57 | 96.5% | 96.5% |
| `sse_main` | `cninfo_dividend_financing_profile` | 55 | 57 | 96.5% | 96.5% |
| `sse_main` | `cninfo_executive_profile` | 55 | 57 | 96.5% | 96.5% |
| `sse_main` | `cninfo_share_capital_profile` | 55 | 57 | 96.5% | 96.5% |
| `sse_main` | `cninfo_top_shareholders_profile` | 55 | 57 | 96.5% | 96.5% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 55 | 57 | 96.5% | 96.5% |
| `star` | `cninfo_company_basic_profile` | 25 | 25 | 100.0% | 100.0% |
| `star` | `cninfo_dividend_financing_profile` | 25 | 25 | 100.0% | 100.0% |
| `star` | `cninfo_executive_profile` | 25 | 25 | 100.0% | 100.0% |
| `star` | `cninfo_share_capital_profile` | 25 | 25 | 100.0% | 100.0% |
| `star` | `cninfo_top_shareholders_profile` | 24 | 25 | 96.0% | 96.0% |
| `star` | `cninfo_top_float_shareholders_profile` | 24 | 25 | 96.0% | 96.0% |
| `szse_main` | `cninfo_company_basic_profile` | 47 | 48 | 97.9% | 97.9% |
| `szse_main` | `cninfo_dividend_financing_profile` | 47 | 48 | 97.9% | 97.9% |
| `szse_main` | `cninfo_executive_profile` | 47 | 48 | 97.9% | 97.9% |
| `szse_main` | `cninfo_share_capital_profile` | 47 | 48 | 97.9% | 97.9% |
| `szse_main` | `cninfo_top_shareholders_profile` | 47 | 48 | 97.9% | 97.9% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 47 | 48 | 97.9% | 97.9% |

**Overall:** pass=1101 fail=69 skipped=0 **result=LIVE_PARTIAL**

## Gate: dividend YAML backfill

**Decision: NO-GO**

dividend reachability=94.4% error_rate=5.6% — 未达门槛 (reach>=95% & error<5%).

## Gate: expand to 200 companies

**enter_200 = CONDITIONAL**

active-only 样本扩至 200 家前需修复：blocked=4 rate_limited_429=0; basic reachability 94.4%; dividend reachability 94.4%; cninfo_company_basic_profile: error_rate 5.6%; cninfo_dividend_financing_profile: error_rate 5.6%; cninfo_executive_profile: error_rate 5.6%; cninfo_share_capital_profile: error_rate 5.6%; cninfo_top_shareholders_profile: error_rate 5.6%; cninfo_top_float_shareholders_profile: error_rate 5.6%; board bse / cninfo_company_basic_profile: pass 60.0%; board bse / cninfo_dividend_financing_profile: pass 60.0%; board bse / cninfo_executive_profile: pass 60.0%; board bse / cninfo_share_capital_profile: pass 60.0%; board bse / cninfo_top_shareholders_profile: pass 60.0%; board bse / cninfo_top_float_shareholders_profile: pass 55.0%

## Caveats

- **195-company active sample**（母本 200 剔除 5 退市名）；非全市场。
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security uses hardcoded `secType=szshe`; cross-board risk observed separately（observe-only，不绑定主 gate）。
- active 样本以 YAML 名称 heuristics 剔除退市，未联网校验 *ST 等上市状态；BSE 旧代码（83/87）与 920 层行为分裂见 [BSE diagnosis](cninfo_c_class_scale_smoke_200_bse_diagnosis.md)。

## Appendix

详见 [cninfo_c_class_scale_smoke_200_active_summary.csv](cninfo_c_class_scale_smoke_200_active_summary.csv)。

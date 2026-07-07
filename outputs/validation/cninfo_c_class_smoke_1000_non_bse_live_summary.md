# CNINFO C Class 889-Company Non-BSE 1000-like Live Summary

_生成时间：2026-07-06_

## Run mode

**live**

## Scope

- **Sample:** `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` (889 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

## Active-only 样本分层

| board | count |
|-------|-------|
| `chinext` | 233 |
| `sse_main` | 292 |
| `star` | 125 |
| `szse_main` | 239 |

**pass / fail / blocked / 429:** 5064 / 270 / 14 / 0

**Planned live requests per company:** 7
**Total planned (live):** 6223

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 840/889 | 94.5% | 840 | 94.5% | 0 | 3 | 0 | 23 | 2.9% | 840 | 49 |
| `cninfo_dividend_financing_profile` | 860/889 | 96.7% | 826 | 92.9% | 34 | 2 | 0 | 24 | 2.9% | 860 | 29 |
| `cninfo_executive_profile` | 841/889 | 94.6% | 841 | 94.6% | 0 | 3 | 0 | 23 | 2.9% | 841 | 48 |
| `cninfo_share_capital_profile` | 845/889 | 95.1% | 845 | 95.1% | 0 | 1 | 0 | 25 | 2.9% | 845 | 44 |
| `cninfo_top_shareholders_profile` | 847/889 | 95.3% | 847 | 95.3% | 0 | 2 | 0 | 24 | 2.9% | 847 | 42 |
| `cninfo_top_float_shareholders_profile` | 831/889 | 93.5% | 831 | 93.5% | 0 | 3 | 0 | 23 | 2.9% | 831 | 58 |
| `cninfo_company_security_profile` | 889/889 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

## Basic key field fill_rate (endpoint_found only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 100.0% |
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F015V` | 100.0% |
| `F016V` | 99.6% |
| `F032V` | 99.6% |
| `MARKET` | 100.0% |

## Dividend field fill_rate (non-empty records only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 98.5% |
| `F007V` | 100.0% |
| `F018D` | 100.0% |
| `F020D` | 99.2% |
| `F023D` | 95.3% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `blocked` | 2 |
| `endpoint_found` | 826 |
| `http_error` | 24 |
| `schema_unexpected` | 3 |
| `valid_empty` | 34 |

## empty_but_valid 股东源案例

| company_code | company_name | board | source_id | record_count |
|--------------|--------------|-------|-----------|--------------|
| `688048` | 长光华芯 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688244` | 永信至诚 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688168` | 安博通 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688235` | 百济神州 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688235` | 百济神州 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688187` | 时代电气 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688096` | 京源环保 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688096` | 京源环保 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688035` | 德邦科技 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688081` | 兴图新科 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688081` | 兴图新科 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688087` | 英科再生 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `603897` | 长城科技 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `600662` | 外服控股 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `603889` | 新澳股份 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `600375` | 汉马科技 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601113` | 华鼎股份 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601668` | 中国建筑 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `605028` | 世茂能源 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601939` | 建设银行 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688363` | 华熙生物 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688082` | 盛美上海 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688291` | 金橙子 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_shareholders_profile` | 0 |
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `301578` | 辰奕智能 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301123` | 奕东电子 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300472` | *ST新元 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301669` | 高特电子 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301669` | 高特电子 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |

## Derived sources (from basic basicInformation)

### `cninfo_company_contact_profile`

| field | fill_rate% |
|-------|------------|
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F006V` | 100.0% |
| `F011V` | 99.6% |
| `F012V` | 100.0% |
| `F013V` | 100.0% |
| `F014V` | 98.9% |
| `F018V` | 99.9% |

### `cninfo_company_business_scope`

| field | fill_rate% |
|-------|------------|
| `F015V` | 100.0% |
| `F016V` | 99.6% |
| `F017V` | 100.0% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 99.6% |
| `F044V` | 95.5% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `chinext` | `cninfo_company_basic_profile` | 227 | 233 | 97.4% | 97.4% |
| `chinext` | `cninfo_dividend_financing_profile` | 231 | 233 | 99.1% | 99.1% |
| `chinext` | `cninfo_executive_profile` | 231 | 233 | 99.1% | 99.1% |
| `chinext` | `cninfo_share_capital_profile` | 230 | 233 | 98.7% | 98.7% |
| `chinext` | `cninfo_top_shareholders_profile` | 228 | 233 | 97.9% | 97.9% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 227 | 233 | 97.4% | 97.4% |
| `sse_main` | `cninfo_company_basic_profile` | 273 | 292 | 93.5% | 93.5% |
| `sse_main` | `cninfo_dividend_financing_profile` | 279 | 292 | 95.5% | 95.5% |
| `sse_main` | `cninfo_executive_profile` | 266 | 292 | 91.1% | 91.1% |
| `sse_main` | `cninfo_share_capital_profile` | 271 | 292 | 92.8% | 92.8% |
| `sse_main` | `cninfo_top_shareholders_profile` | 275 | 292 | 94.2% | 94.2% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 267 | 292 | 91.4% | 91.4% |
| `star` | `cninfo_company_basic_profile` | 114 | 125 | 91.2% | 91.2% |
| `star` | `cninfo_dividend_financing_profile` | 124 | 125 | 99.2% | 99.2% |
| `star` | `cninfo_executive_profile` | 119 | 125 | 95.2% | 95.2% |
| `star` | `cninfo_share_capital_profile` | 119 | 125 | 95.2% | 95.2% |
| `star` | `cninfo_top_shareholders_profile` | 119 | 125 | 95.2% | 95.2% |
| `star` | `cninfo_top_float_shareholders_profile` | 112 | 125 | 89.6% | 89.6% |
| `szse_main` | `cninfo_company_basic_profile` | 226 | 239 | 94.6% | 94.6% |
| `szse_main` | `cninfo_dividend_financing_profile` | 226 | 239 | 94.6% | 94.6% |
| `szse_main` | `cninfo_executive_profile` | 225 | 239 | 94.1% | 94.1% |
| `szse_main` | `cninfo_share_capital_profile` | 225 | 239 | 94.1% | 94.1% |
| `szse_main` | `cninfo_top_shareholders_profile` | 225 | 239 | 94.1% | 94.1% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 225 | 239 | 94.1% | 94.1% |

**Overall:** pass=5064 fail=270 skipped=0 **result=LIVE_PARTIAL**

## Gate: dividend YAML backfill

**Decision: GO**

dividend reachability=96.7% error_rate=2.9% valid_empty=34. 建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。

## Gate: post-889 scale / next planning

**next_gate = DIAGNOSIS_DONE**

889-company non-BSE live 已完成（**LIVE_PARTIAL** · pass=5064 fail=270）。下一步：见 [post-889 diagnosis](cninfo_c_class_smoke_1000_non_bse_diagnosis.md) — 样本清洗补强 · failed-company targeted retry · full-market non-BSE planning（**非 enter_200 门槛**）。

## Caveats

- **889-company non-BSE 1000-like live sample**；非 full-market verified。
- Live 输出命名已修正：`cninfo_c_class_smoke_1000_non_bse_live_report.csv` / `_live_summary.md`（旧 `dryrun` 文件为历史误命名副本）。
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security uses hardcoded `secType=szshe`; cross-board risk observed separately（**observe-only · 889/889 observe_pass**）。
- 股东源 `empty_but_valid_response` 当前 runner 仍计 fail；解读见 [diagnosis](cninfo_c_class_smoke_1000_non_bse_diagnosis.md)。

## Appendix

详见 [cninfo_c_class_smoke_1000_non_bse_live_report.csv](cninfo_c_class_smoke_1000_non_bse_live_report.csv)。

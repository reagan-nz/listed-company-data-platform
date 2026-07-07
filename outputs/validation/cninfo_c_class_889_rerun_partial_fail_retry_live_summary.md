# CNINFO C Class 889 Rerun Partial-Fail Retry (Live) — 41 companies

_生成时间：2026-07-07_

## Run mode

**live**

## Scope

- **Sample:** `lab/eval_companies_c_class_889_rerun_partial_fail_retry.yaml` (41 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

## Active-only 样本分层

| board | count |
|-------|-------|
| `chinext` | 36 |
| `sse_main` | 1 |
| `star` | 2 |
| `szse_main` | 2 |

**pass / fail / blocked / 429:** 237 / 9 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 287

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 41/41 | 100.0% | 41 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 41 | 0 |
| `cninfo_dividend_financing_profile` | 41/41 | 100.0% | 36 | 87.8% | 5 | 0 | 0 | 0 | 0.0% | 41 | 0 |
| `cninfo_executive_profile` | 40/41 | 97.6% | 40 | 97.6% | 0 | 0 | 0 | 0 | 0.0% | 40 | 1 |
| `cninfo_share_capital_profile` | 33/41 | 80.5% | 33 | 80.5% | 0 | 0 | 0 | 0 | 0.0% | 33 | 8 |
| `cninfo_top_shareholders_profile` | 41/41 | 100.0% | 36 | 87.8% | 0 | 0 | 0 | 0 | 0.0% | 41 | 0 |
| `cninfo_top_float_shareholders_profile` | 41/41 | 100.0% | 32 | 78.0% | 0 | 0 | 0 | 0 | 0.0% | 41 | 0 |
| `cninfo_company_security_profile` | 41/41 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

## Basic key field fill_rate (endpoint_found only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 100.0% |
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F015V` | 100.0% |
| `F016V` | 100.0% |
| `F032V` | 92.7% |
| `MARKET` | 100.0% |

## Dividend field fill_rate (non-empty records only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 100.0% |
| `F007V` | 100.0% |
| `F018D` | 100.0% |
| `F020D` | 100.0% |
| `F023D` | 100.0% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `endpoint_found` | 36 |
| `valid_empty` | 5 |

## empty_but_valid 股东源案例

| company_code | company_name | board | source_id | record_count |
|--------------|--------------|-------|-----------|--------------|
| `688750` | 金天钛业 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `300261` | 雅本化学 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300460` | ST惠伦 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301198` | 喜悦智行 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301198` | 喜悦智行 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_shareholders_profile` | 0 |
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `300884` | 狄耐克 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_float_shareholders_profile` | 0 |

## Shareholder empty_but_valid policy

- **empty_but_valid_count（股东源）:** 14
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
| `F017V` | 100.0% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 92.7% |
| `F044V` | 85.4% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `chinext` | `cninfo_company_basic_profile` | 36 | 36 | 100.0% | 100.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 36 | 36 | 100.0% | 100.0% |
| `chinext` | `cninfo_executive_profile` | 35 | 36 | 97.2% | 97.2% |
| `chinext` | `cninfo_share_capital_profile` | 31 | 36 | 86.1% | 86.1% |
| `chinext` | `cninfo_top_shareholders_profile` | 36 | 36 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 36 | 36 | 100.0% | 100.0% |
| `sse_main` | `cninfo_company_basic_profile` | 1 | 1 | 100.0% | 100.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 1 | 1 | 100.0% | 100.0% |
| `sse_main` | `cninfo_executive_profile` | 1 | 1 | 100.0% | 100.0% |
| `sse_main` | `cninfo_share_capital_profile` | 0 | 1 | 0.0% | 0.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 1 | 1 | 100.0% | 100.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 1 | 1 | 100.0% | 100.0% |
| `star` | `cninfo_company_basic_profile` | 2 | 2 | 100.0% | 100.0% |
| `star` | `cninfo_dividend_financing_profile` | 2 | 2 | 100.0% | 100.0% |
| `star` | `cninfo_executive_profile` | 2 | 2 | 100.0% | 100.0% |
| `star` | `cninfo_share_capital_profile` | 1 | 2 | 50.0% | 50.0% |
| `star` | `cninfo_top_shareholders_profile` | 2 | 2 | 100.0% | 100.0% |
| `star` | `cninfo_top_float_shareholders_profile` | 2 | 2 | 100.0% | 100.0% |
| `szse_main` | `cninfo_company_basic_profile` | 2 | 2 | 100.0% | 100.0% |
| `szse_main` | `cninfo_dividend_financing_profile` | 2 | 2 | 100.0% | 100.0% |
| `szse_main` | `cninfo_executive_profile` | 2 | 2 | 100.0% | 100.0% |
| `szse_main` | `cninfo_share_capital_profile` | 1 | 2 | 50.0% | 50.0% |
| `szse_main` | `cninfo_top_shareholders_profile` | 2 | 2 | 100.0% | 100.0% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 2 | 2 | 100.0% | 100.0% |

**Overall:** pass=237 fail=9 skipped=0 **result=LIVE_PARTIAL**

## Gate: dividend YAML backfill

**Decision: GO**

dividend reachability=100.0% error_rate=0.0% valid_empty=5. 建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。

## Gate: 889 rerun partial-fail targeted retry

**retry_gate = LIVE_COMPLETED_POST_DECISION**

Partial-fail targeted retry **已完成**（**41** 家 · **287** cases · pass=**237** fail=**9** · **LIVE_PARTIAL**）。
26 家 all6 hold 见 `eval_companies_c_class_889_rerun_all6_hold.yaml`（hold_no_retry · 不变）。
残留 **9** fail 均为 `empty_but_valid_response`（share_capital **8** · executive **1**）— **source-level residual**，非 runner/pacing。
**post-retry 决策：** [cninfo_c_class_889_post_retry_decision.md](../../plans/cninfo_c_class_889_post_retry_decision.md)
**harvest：** 可进入 **planning**（summary 须保留 26 hold + share_capital caveat）；**不写 verified** · **不升级 testing_stable_sample**。
**889 全量：** **不立即重跑**。

## Caveats

- **889 rerun partial-fail targeted retry live 已完成**；非 889 全量重跑。
- 26 家 all6 hold 见 `eval_companies_c_class_889_rerun_all6_hold.yaml`（hold_no_retry）。
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- **share_capital** 继续 **source_partial**；**executive** 继续 **caveat**。
- **dividend_history YAML** → **GO（决策 only）** · **不执行** backfill。
- **C-class harvest** 可进入 planning；须保留 26 hold 与 share_capital residual caveat。

## Appendix

详见 [cninfo_c_class_889_rerun_partial_fail_retry_live_summary.csv](cninfo_c_class_889_rerun_partial_fail_retry_live_summary.csv)。

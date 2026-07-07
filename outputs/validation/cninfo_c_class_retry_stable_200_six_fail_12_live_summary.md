# CNINFO C Class Stable 200 Six-Fail 12 Retry (Live) Summary

_生成时间：2026-07-07_

## Run mode

**live**

## Scope

- **Sample:** `lab/eval_companies_c_class_retry_stable_200_six_fail_12.yaml` (12 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

## Active-only 样本分层

| board | count |
|-------|-------|
| `chinext` | 4 |
| `sse_main` | 8 |

**pass / fail / blocked / 429:** 72 / 0 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 84

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 12/12 | 100.0% | 12 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 12 | 0 |
| `cninfo_dividend_financing_profile` | 12/12 | 100.0% | 12 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 12 | 0 |
| `cninfo_executive_profile` | 12/12 | 100.0% | 12 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 12 | 0 |
| `cninfo_share_capital_profile` | 12/12 | 100.0% | 12 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 12 | 0 |
| `cninfo_top_shareholders_profile` | 12/12 | 100.0% | 12 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 12 | 0 |
| `cninfo_top_float_shareholders_profile` | 12/12 | 100.0% | 12 | 100.0% | 0 | 0 | 0 | 0 | 0.0% | 12 | 0 |
| `cninfo_company_security_profile` | 12/12 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

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
| `F018D` | 100.0% |
| `F020D` | 100.0% |
| `F023D` | 91.7% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `endpoint_found` | 12 |

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
| `F032V` | 100.0% |
| `F044V` | 100.0% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `chinext` | `cninfo_company_basic_profile` | 4 | 4 | 100.0% | 100.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 4 | 4 | 100.0% | 100.0% |
| `chinext` | `cninfo_executive_profile` | 4 | 4 | 100.0% | 100.0% |
| `chinext` | `cninfo_share_capital_profile` | 4 | 4 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_shareholders_profile` | 4 | 4 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 4 | 4 | 100.0% | 100.0% |
| `sse_main` | `cninfo_company_basic_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_executive_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_share_capital_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 8 | 8 | 100.0% | 100.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 8 | 8 | 100.0% | 100.0% |

**Overall:** pass=72 fail=0 skipped=0 **result=LIVE_PASS**

## Gate: dividend YAML backfill

**Decision: GO**

dividend reachability=100.0% error_rate=0.0% valid_empty=0. 建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。

## Gate: stable 200 six-fail 12 retry

**retry_gate = LIVE_PENDING_APPROVAL**

Targeted retry **12** 家；planned live **84** cases。
backoff patch + orgId fallback 已加入 runner；**等待人工批准**后 `--live`。

## Caveats

- 30-company stratified sample only; not full-market.
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security uses hardcoded `secType=szshe`; cross-board risk observed separately.

## Appendix

详见 [cninfo_c_class_retry_stable_200_six_fail_12_live_summary.csv](cninfo_c_class_retry_stable_200_six_fail_12_live_summary.csv)。

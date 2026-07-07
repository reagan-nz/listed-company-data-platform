# CNINFO C Class 889 Retry — Partial Fail Targeted (Live) — 62 companies

_生成时间：2026-07-07_

## Run mode

**live**

## Scope

- **Sample:** `lab/eval_companies_c_class_retry_889_partial_fail_retry.yaml` (62 companies)
- **主判定 source:** basic · dividend · P2-A 四源
- **观察维度:** security（不绑定主判定）
- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）

## Active-only 样本分层

| board | count |
|-------|-------|
| `chinext` | 7 |
| `sse_main` | 33 |
| `star` | 20 |
| `szse_main` | 2 |

**pass / fail / blocked / 429:** 300 / 72 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 434

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 41/62 | 66.1% | 41 | 66.1% | 0 | 0 | 0 | 0 | 0.0% | 41 | 21 |
| `cninfo_dividend_financing_profile` | 60/62 | 96.8% | 33 | 53.2% | 27 | 0 | 0 | 0 | 0.0% | 60 | 2 |
| `cninfo_executive_profile` | 42/62 | 67.7% | 42 | 67.7% | 0 | 0 | 0 | 0 | 0.0% | 42 | 20 |
| `cninfo_share_capital_profile` | 37/62 | 59.7% | 37 | 59.7% | 0 | 0 | 0 | 0 | 0.0% | 37 | 25 |
| `cninfo_top_shareholders_profile` | 60/62 | 96.8% | 35 | 56.5% | 0 | 0 | 0 | 0 | 0.0% | 60 | 2 |
| `cninfo_top_float_shareholders_profile` | 60/62 | 96.8% | 37 | 59.7% | 0 | 0 | 0 | 0 | 0.0% | 60 | 2 |
| `cninfo_company_security_profile` | 62/62 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

## Basic key field fill_rate (endpoint_found only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 100.0% |
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F015V` | 100.0% |
| `F016V` | 97.6% |
| `F032V` | 97.6% |
| `MARKET` | 100.0% |

## Dividend field fill_rate (non-empty records only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 93.9% |
| `F007V` | 100.0% |
| `F018D` | 100.0% |
| `F020D` | 100.0% |
| `F023D` | 87.9% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `endpoint_found` | 33 |
| `schema_unexpected` | 2 |
| `valid_empty` | 27 |

## empty_but_valid 股东源案例

| company_code | company_name | board | source_id | record_count |
|--------------|--------------|-------|-----------|--------------|
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_shareholders_profile` | 0 |
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `300472` | *ST新元 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301123` | 奕东电子 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301123` | 奕东电子 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301295` | 美硕科技 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301507` | 民生健康 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301507` | 民生健康 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301578` | 辰奕智能 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301669` | 高特电子 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301669` | 高特电子 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `600007` | 中国国贸 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `600117` | 西宁特钢 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `600117` | 西宁特钢 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `600187` | *ST国中 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `600187` | *ST国中 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `600302` | ST标准 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `600882` | 妙可蓝多 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `600882` | 妙可蓝多 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `600958` | 东方证券 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `600958` | 东方证券 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601113` | 华鼎股份 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601113` | 华鼎股份 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601328` | 交通银行 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601328` | 交通银行 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601368` | 绿城水务 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601368` | 绿城水务 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601566` | 九牧王 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601566` | 九牧王 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601668` | 中国建筑 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601668` | 中国建筑 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `601939` | 建设银行 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601939` | 建设银行 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `603107` | 上海汽配 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `603107` | 上海汽配 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `603408` | 建霖家居 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `603408` | 建霖家居 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `603698` | 航天工程 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `603839` | 安正时尚 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `603889` | 新澳股份 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_float_shareholders_profile` | 0 |

## Shareholder empty_but_valid policy

- **empty_but_valid_count（股东源）:** 48
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
| `F018V` | 97.6% |

### `cninfo_company_business_scope`

| field | fill_rate% |
|-------|------------|
| `F015V` | 100.0% |
| `F016V` | 97.6% |
| `F017V` | 97.6% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 97.6% |
| `F044V` | 92.7% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `chinext` | `cninfo_company_basic_profile` | 4 | 7 | 57.1% | 57.1% |
| `chinext` | `cninfo_dividend_financing_profile` | 7 | 7 | 100.0% | 100.0% |
| `chinext` | `cninfo_executive_profile` | 1 | 7 | 14.3% | 14.3% |
| `chinext` | `cninfo_share_capital_profile` | 2 | 7 | 28.6% | 28.6% |
| `chinext` | `cninfo_top_shareholders_profile` | 7 | 7 | 100.0% | 100.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 7 | 7 | 100.0% | 100.0% |
| `sse_main` | `cninfo_company_basic_profile` | 18 | 33 | 54.5% | 54.5% |
| `sse_main` | `cninfo_dividend_financing_profile` | 32 | 33 | 97.0% | 97.0% |
| `sse_main` | `cninfo_executive_profile` | 23 | 33 | 69.7% | 69.7% |
| `sse_main` | `cninfo_share_capital_profile` | 18 | 33 | 54.5% | 54.5% |
| `sse_main` | `cninfo_top_shareholders_profile` | 32 | 33 | 97.0% | 97.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 32 | 33 | 97.0% | 97.0% |
| `star` | `cninfo_company_basic_profile` | 19 | 20 | 95.0% | 95.0% |
| `star` | `cninfo_dividend_financing_profile` | 19 | 20 | 95.0% | 95.0% |
| `star` | `cninfo_executive_profile` | 18 | 20 | 90.0% | 90.0% |
| `star` | `cninfo_share_capital_profile` | 17 | 20 | 85.0% | 85.0% |
| `star` | `cninfo_top_shareholders_profile` | 19 | 20 | 95.0% | 95.0% |
| `star` | `cninfo_top_float_shareholders_profile` | 19 | 20 | 95.0% | 95.0% |
| `szse_main` | `cninfo_company_basic_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_dividend_financing_profile` | 2 | 2 | 100.0% | 100.0% |
| `szse_main` | `cninfo_executive_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_share_capital_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_top_shareholders_profile` | 2 | 2 | 100.0% | 100.0% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 2 | 2 | 100.0% | 100.0% |

**Overall:** pass=300 fail=72 skipped=0 **result=LIVE_PARTIAL**

## Gate: dividend YAML backfill

**Decision: GO**

dividend reachability=96.8% error_rate=0.0% valid_empty=27. 建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。

## Gate: targeted retry

**retry_gate = LIVE_PENDING_REVIEW**

Partial-fail subset **62** 家；planned live **434** requests。
26 家 6/6 全失败已 hold，不在此样本。
**等待人工批准**后跑 `--live`。

## Caveats

- **889 partial-fail targeted retry live**；非 889 全量重跑。
- 26 家 6/6 全失败见 `eval_companies_c_class_retry_889_six_fail_hold.yaml`（hold）。
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- 股东 empty_but_valid 口径已修正（见 Shareholder empty_but_valid policy）。

## Appendix

详见 [cninfo_c_class_retry_889_partial_fail_live_summary.csv](cninfo_c_class_retry_889_partial_fail_live_summary.csv)。

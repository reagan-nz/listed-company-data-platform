# CNINFO C Class 889-Company Non-BSE 1000-like Dry-Run Summary

_生成时间：2026-07-07_

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

**pass / fail / blocked / 429:** 5119 / 215 / 20 / 0

**Planned live requests per company:** 7
**Total planned (live):** 6223

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 862/889 | 97.0% | 862 | 97.0% | 0 | 4 | 0 | 23 | 3.0% | 862 | 27 |
| `cninfo_dividend_financing_profile` | 862/889 | 97.0% | 807 | 90.8% | 55 | 3 | 0 | 23 | 2.9% | 862 | 27 |
| `cninfo_executive_profile` | 834/889 | 93.8% | 834 | 93.8% | 0 | 4 | 0 | 24 | 3.1% | 834 | 55 |
| `cninfo_share_capital_profile` | 837/889 | 94.2% | 837 | 94.2% | 0 | 2 | 0 | 25 | 3.0% | 837 | 52 |
| `cninfo_top_shareholders_profile` | 862/889 | 97.0% | 824 | 92.7% | 0 | 3 | 0 | 24 | 3.0% | 862 | 27 |
| `cninfo_top_float_shareholders_profile` | 862/889 | 97.0% | 822 | 92.5% | 0 | 4 | 0 | 23 | 3.0% | 862 | 27 |
| `cninfo_company_security_profile` | 889/889 | 100.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

## Basic key field fill_rate (endpoint_found only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 100.0% |
| `F004V` | 100.0% |
| `F005V` | 100.0% |
| `F015V` | 100.0% |
| `F016V` | 99.7% |
| `F032V` | 99.7% |
| `MARKET` | 100.0% |

## Dividend field fill_rate (non-empty records only)

| field | fill_rate% |
|-------|------------|
| `F001V` | 98.5% |
| `F007V` | 100.0% |
| `F018D` | 100.0% |
| `F020D` | 99.1% |
| `F023D` | 95.0% |

## Dividend empty distribution

| status | count |
|--------|-------|
| `blocked` | 3 |
| `cninfo_throttled_business_code` | 1 |
| `endpoint_found` | 807 |
| `http_error` | 23 |
| `valid_empty` | 55 |

## empty_but_valid 股东源案例

| company_code | company_name | board | source_id | record_count |
|--------------|--------------|-------|-----------|--------------|
| `600029` | 南方航空 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688797` | 臻宝科技 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `600556` | 天下秀 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_shareholders_profile` | 0 |
| `601206` | 海尔施 | `sse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_shareholders_profile` | 0 |
| `688688` | 蚂蚁集团 | `star` | `cninfo_top_float_shareholders_profile` | 0 |
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_shareholders_profile` | 0 |
| `002710` | 慈铭体检 | `szse_main` | `cninfo_top_float_shareholders_profile` | 0 |
| `300329` | 海伦钢琴 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300329` | 海伦钢琴 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300383` | 光环新网 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300383` | 光环新网 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301687` | 新广益 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301687` | 新广益 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301338` | 凯格精机 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301338` | 凯格精机 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301025` | 读客文化 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300039` | 上海凯宝 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300039` | 上海凯宝 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301055` | 张小泉 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301055` | 张小泉 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300414` | 中光防雷 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300414` | 中光防雷 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300123` | ST亚光 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300644` | 南京聚隆 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300644` | 南京聚隆 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300891` | 惠云钛业 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300891` | 惠云钛业 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300738` | 奥飞数据 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300406` | 九强生物 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300406` | 九强生物 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300993` | 玉马科技 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301583` | 托伦斯 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300460` | ST惠伦 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300460` | ST惠伦 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301336` | 趣睡科技 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301345` | 涛涛车业 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301345` | 涛涛车业 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300479` | 神思电子 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300171` | 东富龙 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300171` | 东富龙 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300528` | 幸福蓝海 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300444` | 双杰电气 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301066` | 万事利 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301066` | 万事利 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300762` | 上海瀚讯 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300884` | 狄耐克 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300884` | 狄耐克 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300858` | 科拓生物 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301669` | 高特电子 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301669` | 高特电子 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301157` | 华塑科技 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300107` | 建新股份 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300107` | 建新股份 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301538` | 骏鼎达 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301665` | 泰禾股份 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300288` | 朗玛信息 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300288` | 朗玛信息 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301198` | 喜悦智行 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301198` | 喜悦智行 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301077` | 星华新材 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301077` | 星华新材 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301021` | 英诺激光 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301021` | 英诺激光 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300261` | 雅本化学 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300261` | 雅本化学 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300623` | 捷捷微电 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300623` | 捷捷微电 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300627` | 华测导航 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300627` | 华测导航 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300224` | 正海磁材 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `300224` | 正海磁材 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `301011` | 华立科技 | `chinext` | `cninfo_top_shareholders_profile` | 0 |
| `301011` | 华立科技 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |
| `300162` | 雷曼光电 | `chinext` | `cninfo_top_float_shareholders_profile` | 0 |

## Shareholder empty_but_valid policy

- **empty_but_valid_count（股东源）:** 78
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
| `F011V` | 99.5% |
| `F012V` | 100.0% |
| `F013V` | 100.0% |
| `F014V` | 99.0% |
| `F018V` | 99.9% |

### `cninfo_company_business_scope`

| field | fill_rate% |
|-------|------------|
| `F015V` | 100.0% |
| `F016V` | 99.7% |
| `F017V` | 99.9% |

### `cninfo_company_industry_profile`

| field | fill_rate% |
|-------|------------|
| `F032V` | 99.7% |
| `F044V` | 95.5% |
| `MARKET` | 100.0% |

## Board-group pass rate (main judgment sources)

| board | source_id | pass | total | pass% | reachability% |
|-------|-----------|------|-------|-------|---------------|
| `chinext` | `cninfo_company_basic_profile` | 230 | 233 | 98.7% | 98.7% |
| `chinext` | `cninfo_dividend_financing_profile` | 230 | 233 | 98.7% | 98.7% |
| `chinext` | `cninfo_executive_profile` | 204 | 233 | 87.6% | 87.6% |
| `chinext` | `cninfo_share_capital_profile` | 209 | 233 | 89.7% | 89.7% |
| `chinext` | `cninfo_top_shareholders_profile` | 231 | 233 | 99.1% | 99.1% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 231 | 233 | 99.1% | 99.1% |
| `sse_main` | `cninfo_company_basic_profile` | 281 | 292 | 96.2% | 96.2% |
| `sse_main` | `cninfo_dividend_financing_profile` | 281 | 292 | 96.2% | 96.2% |
| `sse_main` | `cninfo_executive_profile` | 281 | 292 | 96.2% | 96.2% |
| `sse_main` | `cninfo_share_capital_profile` | 280 | 292 | 95.9% | 95.9% |
| `sse_main` | `cninfo_top_shareholders_profile` | 281 | 292 | 96.2% | 96.2% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 281 | 292 | 96.2% | 96.2% |
| `star` | `cninfo_company_basic_profile` | 125 | 125 | 100.0% | 100.0% |
| `star` | `cninfo_dividend_financing_profile` | 125 | 125 | 100.0% | 100.0% |
| `star` | `cninfo_executive_profile` | 124 | 125 | 99.2% | 99.2% |
| `star` | `cninfo_share_capital_profile` | 123 | 125 | 98.4% | 98.4% |
| `star` | `cninfo_top_shareholders_profile` | 124 | 125 | 99.2% | 99.2% |
| `star` | `cninfo_top_float_shareholders_profile` | 124 | 125 | 99.2% | 99.2% |
| `szse_main` | `cninfo_company_basic_profile` | 226 | 239 | 94.6% | 94.6% |
| `szse_main` | `cninfo_dividend_financing_profile` | 226 | 239 | 94.6% | 94.6% |
| `szse_main` | `cninfo_executive_profile` | 225 | 239 | 94.1% | 94.1% |
| `szse_main` | `cninfo_share_capital_profile` | 225 | 239 | 94.1% | 94.1% |
| `szse_main` | `cninfo_top_shareholders_profile` | 226 | 239 | 94.6% | 94.6% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 226 | 239 | 94.6% | 94.6% |

**Overall:** pass=5119 fail=215 skipped=0 **result=LIVE_PARTIAL**

## Gate: dividend YAML backfill

**Decision: GO**

dividend reachability=97.0% error_rate=2.9% valid_empty=55. 建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。

## Gate: post-889 scale / next planning

**next_gate = SEE_DIAGNOSIS**

889-company non-BSE 1000-like；下一门槛为 post-889 diagnosis / full-market non-BSE planning（非 enter_200）。

## Caveats

- **889-company non-BSE 1000-like live sample**；非 full-market verified。
- Live 输出：`cninfo_c_class_smoke_1000_non_bse_live_report.csv` / `_live_summary.md`。
- Next gate: post-889 diagnosis / possible 1000 or full-market non-BSE planning.
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security observe-only；不绑定主 gate。

## Appendix

详见 [cninfo_c_class_889_non_bse_rerun_live_summary.csv](cninfo_c_class_889_non_bse_rerun_live_summary.csv)。

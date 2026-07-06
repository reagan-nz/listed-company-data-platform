# CNINFO C Class 889-Company Non-BSE 1000-like Dry-Run Summary

_生成时间：2026-07-06_

## Universe derivation（离线派生）

| 项 | 值 |
|----|-----|
| 母本 | `lab/eval_companies_1000.yaml` |
| 母本数量 | **1020** |
| 清洗后 non-BSE candidate | **889** |
| 剔除合计 | **131** |
| suspicious duplicate notes | **2**（`000765`/`001267` 同 orgid） |

### 剔除规则与数量

| exclusion_reason | count |
|------------------|-------|
| `board_bse` | 106 |
| `name_suffix_tui` | 15 |
| `name_delisted_cn` | 7 |
| `abnormal_review_explicit` | 3 |

规则与 [universe split plan](../plans/cninfo_c_class_universe_split_and_sample_cleaning_plan.md) 一致：排除 BSE · 退市/heuristic · 已知 abnormal（600065 / 600978 / 000405）；*ST 不自动剔除；**无联网补数**。

### 候选样本

`lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`

## Run mode

**dry-run**

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

**pass / fail / blocked / 429:** 0 / 0 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 6223

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 0/889 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_dividend_financing_profile` | 0/889 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_executive_profile` | 0/889 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_share_capital_profile` | 0/889 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_top_shareholders_profile` | 0/889 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_top_float_shareholders_profile` | 0/889 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_company_security_profile` | 0/889 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

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
| `` | 889 |

## empty_but_valid 股东源案例

- 无

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
| `chinext` | `cninfo_company_basic_profile` | 0 | 233 | 0.0% | 0.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 0 | 233 | 0.0% | 0.0% |
| `chinext` | `cninfo_executive_profile` | 0 | 233 | 0.0% | 0.0% |
| `chinext` | `cninfo_share_capital_profile` | 0 | 233 | 0.0% | 0.0% |
| `chinext` | `cninfo_top_shareholders_profile` | 0 | 233 | 0.0% | 0.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 0 | 233 | 0.0% | 0.0% |
| `sse_main` | `cninfo_company_basic_profile` | 0 | 292 | 0.0% | 0.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 0 | 292 | 0.0% | 0.0% |
| `sse_main` | `cninfo_executive_profile` | 0 | 292 | 0.0% | 0.0% |
| `sse_main` | `cninfo_share_capital_profile` | 0 | 292 | 0.0% | 0.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 0 | 292 | 0.0% | 0.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 0 | 292 | 0.0% | 0.0% |
| `star` | `cninfo_company_basic_profile` | 0 | 125 | 0.0% | 0.0% |
| `star` | `cninfo_dividend_financing_profile` | 0 | 125 | 0.0% | 0.0% |
| `star` | `cninfo_executive_profile` | 0 | 125 | 0.0% | 0.0% |
| `star` | `cninfo_share_capital_profile` | 0 | 125 | 0.0% | 0.0% |
| `star` | `cninfo_top_shareholders_profile` | 0 | 125 | 0.0% | 0.0% |
| `star` | `cninfo_top_float_shareholders_profile` | 0 | 125 | 0.0% | 0.0% |
| `szse_main` | `cninfo_company_basic_profile` | 0 | 239 | 0.0% | 0.0% |
| `szse_main` | `cninfo_dividend_financing_profile` | 0 | 239 | 0.0% | 0.0% |
| `szse_main` | `cninfo_executive_profile` | 0 | 239 | 0.0% | 0.0% |
| `szse_main` | `cninfo_share_capital_profile` | 0 | 239 | 0.0% | 0.0% |
| `szse_main` | `cninfo_top_shareholders_profile` | 0 | 239 | 0.0% | 0.0% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 0 | 239 | 0.0% | 0.0% |

**Overall:** pass=0 fail=0 skipped=6223 **result=DRY_RUN_ONLY**

## Dry-run confirmation

- **No CNINFO requests executed**（all cases skipped）
- **Company count:** 889
- **Cases:** 6223 = 889 × 7 sources
- **Planned live requests:** 6223
- **主判定 source:** basic · dividend · P2-A 四源（executive / share_capital / top_shareholders / top_float）
- **security_profile:** observe-only（不绑定主判定 gate）
- **derived 三源:** contact / business_scope / industry — 无单独 HTTP 请求，仅 live 时随 basic fill_rate 统计

### Live 批准建议

- **本轮仅 dry-run** — **0 CNINFO 请求** · **无 live** · **无 DB** · **无 YAML backfill**
- **建议等待人工批准后**再跑 non-BSE 1000-like `--live`（planned **6223** requests ≈ 889 × 7 sources）

## Gate: dividend YAML backfill

**Decision: NO-GO**

dividend reachability=0.0% error_rate=0.0% — 未达门槛 (reach>=95% & error<5%).

## Gate: expand to 200 companies

**enter_200 = CONDITIONAL**

当前样本扩至 200 家前需修复：basic reachability 0.0%; basic non_empty 0.0%; dividend reachability 0.0%; board chinext / cninfo_company_basic_profile: pass 0.0%; board chinext / cninfo_dividend_financing_profile: pass 0.0%; board chinext / cninfo_executive_profile: pass 0.0%; board chinext / cninfo_share_capital_profile: pass 0.0%; board chinext / cninfo_top_shareholders_profile: pass 0.0%; board chinext / cninfo_top_float_shareholders_profile: pass 0.0%; board sse_main / cninfo_company_basic_profile: pass 0.0%; board sse_main / cninfo_dividend_financing_profile: pass 0.0%; board sse_main / cninfo_executive_profile: pass 0.0%; board sse_main / cninfo_share_capital_profile: pass 0.0%; board sse_main / cninfo_top_shareholders_profile: pass 0.0%; board sse_main / cninfo_top_float_shareholders_profile: pass 0.0%; board star / cninfo_company_basic_profile: pass 0.0%; board star / cninfo_dividend_financing_profile: pass 0.0%; board star / cninfo_executive_profile: pass 0.0%; board star / cninfo_share_capital_profile: pass 0.0%; board star / cninfo_top_shareholders_profile: pass 0.0%; board star / cninfo_top_float_shareholders_profile: pass 0.0%; board szse_main / cninfo_company_basic_profile: pass 0.0%; board szse_main / cninfo_dividend_financing_profile: pass 0.0%; board szse_main / cninfo_executive_profile: pass 0.0%; board szse_main / cninfo_share_capital_profile: pass 0.0%; board szse_main / cninfo_top_shareholders_profile: pass 0.0%; board szse_main / cninfo_top_float_shareholders_profile: pass 0.0%

## Caveats

- non-BSE 1000-like **offline candidate**；非 full-market verified。
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- security uses hardcoded `secType=szshe`; cross-board risk observed separately.
- dividend / enter_200 gate 指标在 dry-run 下为占位 0%；**不以本节 gate 结论作为 live 决策**。

## Appendix

详见 [cninfo_c_class_smoke_1000_non_bse_dryrun_report.csv](cninfo_c_class_smoke_1000_non_bse_dryrun_report.csv)。

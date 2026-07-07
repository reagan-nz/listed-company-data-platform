# CNINFO C Class 889 Rerun Partial-Fail Retry (Dry-Run) — 41 companies

_生成时间：2026-07-07_

## Run mode

**dry-run**

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

**pass / fail / blocked / 429:** 0 / 0 / 0 / 0

**Planned live requests per company:** 7
**Total planned (live):** 287

## Per-source reachability

| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | blocked | 429 | http_error | error% | pass | fail |
|-----------|-----------|---------------|-----------|------------|-------------|---------|-----|------------|--------|------|------|
| `cninfo_company_basic_profile` | 0/41 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_dividend_financing_profile` | 0/41 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_executive_profile` | 0/41 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_share_capital_profile` | 0/41 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_top_shareholders_profile` | 0/41 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_top_float_shareholders_profile` | 0/41 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |
| `cninfo_company_security_profile` | 0/41 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0 | 0.0% | 0 | 0 |

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
| `` | 41 |

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
| `chinext` | `cninfo_company_basic_profile` | 0 | 36 | 0.0% | 0.0% |
| `chinext` | `cninfo_dividend_financing_profile` | 0 | 36 | 0.0% | 0.0% |
| `chinext` | `cninfo_executive_profile` | 0 | 36 | 0.0% | 0.0% |
| `chinext` | `cninfo_share_capital_profile` | 0 | 36 | 0.0% | 0.0% |
| `chinext` | `cninfo_top_shareholders_profile` | 0 | 36 | 0.0% | 0.0% |
| `chinext` | `cninfo_top_float_shareholders_profile` | 0 | 36 | 0.0% | 0.0% |
| `sse_main` | `cninfo_company_basic_profile` | 0 | 1 | 0.0% | 0.0% |
| `sse_main` | `cninfo_dividend_financing_profile` | 0 | 1 | 0.0% | 0.0% |
| `sse_main` | `cninfo_executive_profile` | 0 | 1 | 0.0% | 0.0% |
| `sse_main` | `cninfo_share_capital_profile` | 0 | 1 | 0.0% | 0.0% |
| `sse_main` | `cninfo_top_shareholders_profile` | 0 | 1 | 0.0% | 0.0% |
| `sse_main` | `cninfo_top_float_shareholders_profile` | 0 | 1 | 0.0% | 0.0% |
| `star` | `cninfo_company_basic_profile` | 0 | 2 | 0.0% | 0.0% |
| `star` | `cninfo_dividend_financing_profile` | 0 | 2 | 0.0% | 0.0% |
| `star` | `cninfo_executive_profile` | 0 | 2 | 0.0% | 0.0% |
| `star` | `cninfo_share_capital_profile` | 0 | 2 | 0.0% | 0.0% |
| `star` | `cninfo_top_shareholders_profile` | 0 | 2 | 0.0% | 0.0% |
| `star` | `cninfo_top_float_shareholders_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_company_basic_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_dividend_financing_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_executive_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_share_capital_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_top_shareholders_profile` | 0 | 2 | 0.0% | 0.0% |
| `szse_main` | `cninfo_top_float_shareholders_profile` | 0 | 2 | 0.0% | 0.0% |

**Overall:** pass=0 fail=0 skipped=287 **result=DRY_RUN_ONLY**

## Dry-run confirmation

- **No CNINFO requests executed**（all cases skipped）
- **Company count:** 41
- **Cases:** 287 = 41 × 7 sources
- **Planned live requests:** 287
- **主判定 source:** basic · dividend · P2-A 四源（executive / share_capital / top_shareholders / top_float）
- **security_profile:** observe-only（不绑定主判定 gate）
- **derived 三源:** contact / business_scope / industry — 无单独 HTTP 请求，仅 live 时随 basic fill_rate 统计

## 889 rerun partial-fail retry scope

- **来源：** 889 rerun diagnosis partial-fail 子集
- **排除：** 26 家 all6 hold（`eval_companies_c_class_889_rerun_all6_hold.yaml`）
- **retry_priority：** high=4 · medium=37 · low=0
- **不重跑 889 全量** · **harvest 暂停**
- **runner pacing 暂不调**
- **no verified** · **no testing_stable_sample** · **no DB**

## Gate: dividend YAML backfill

**Decision: NO-GO**

dividend reachability=0.0% error_rate=0.0% — 未达门槛 (reach>=95% & error<5%).

## Gate: 889 rerun partial-fail targeted retry

**retry_gate = DRY_RUN_READY**

Partial-fail subset **41** 家；planned live **287** cases。
26 家 all6 hold 见 `eval_companies_c_class_889_rerun_all6_hold.yaml`（hold_no_retry）。
targeted retry 后再决定是否进入 C-class harvest。
**等待人工批准**后跑 `--live`。

## Caveats

- **889 rerun partial-fail targeted retry dry-run**；planned live only；**无 CNINFO**。
- 26 家 all6 hold 已剔除；见 `eval_companies_c_class_889_rerun_all6_hold.yaml`。
- **testing** status only; **no verified**.
- **No testing_stable_sample**.
- No database ingestion.
- **harvest 暂停**；targeted retry 后再评估 harvest gate。

## Appendix

详见 [cninfo_c_class_889_rerun_partial_fail_retry_dryrun_summary.csv](cninfo_c_class_889_rerun_partial_fail_retry_dryrun_summary.csv)。

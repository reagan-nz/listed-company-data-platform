# full_market_2024 Summary

_Generated: 2026-06-24 | Milestone: extraction + merge + SQLite import + hybrid strict audit + scoped rnd refresh **complete**_

_Post-rnd refresh merge + strict audit: 2026-06-24_

> **Caveat**：本 milestone 表示管道执行、数据库导入、混合 strict 审计与 scoped rnd refresh 均已完成。**不等于** 62,890 条 SQLite 记录已全量人工验证。strict **9.38/11** 为自动化 adversarial 全 population 估计，经 15 家公司 PDF deep-read 小样本校准。

---

## Final status counts

| status | count | pct | 说明 |
|---|---:|---:|---|
| **total** | **6124** | 100% | full_market_2024 universe 全部 A 股公司数 |
| **ok** | **5707** | 93.2% | 成功找到年报并完成抽取（≠ 每字段正确） |
| no_announcement | 417 | 6.8% | CNINFO 当前规则下未找到可用 2024 年报 |
| **error** | **0** | 0% | 技术失败（688267 中触媒经重试恢复） |

- non-financial ok: **5621**
- financial ok: **86**（使用金融子 schema，**不纳入**非金融 11 字段 headline）

## Board counts (universe YAML)

| board | 中文 | count |
|---|---|---:|
| bse | 北交所 | 577 |
| star | 科创板 | 613 |
| szse_main | 深市主板 | 1646 |
| chinext | 创业板 | 1442 |
| sse_main | 沪市主板 | 1846 |

## Non-financial proxy (headline, post-rnd refresh)

| metric | value |
|---|---:|
| Mean proxy plausible | **10.61 / 11** (n=5621) |
| Pre-rnd refresh proxy | 10.35 / 11 |

### Comparison vs controlled eval runs

| run | universe | ok | no_ann | error | non-fin proxy |
|---|---:|---:|---:|---:|---:|
| eval1000_v2 | 1020 | 947 | 73 | 0 | **10.33/11** |
| independent eval1000 | 1000 | 918 | 82 | 0 | **10.30/11** |
| **full_market_2024** | **6124** | **5707** | **417** | **0** | **10.61/11** |

> 全市场规模 proxy 与 v2/independent 一致，说明管道规模泛化良好。

## Key field plausible rates (non-financial)

| field | plausible | rate | pre-rnd refresh |
|---|---:|---:|---:|
| rnd_investment | 5269/5621 | **93.7%** | 67.9% |
| revenue_by_region | 5093/5621 | 90.6% | — |
| revenue_by_segment | 5386/5621 | 95.8% | — |

## Strict audit (post-rnd refresh, non-fin)

| metric | pre-rnd | post-rnd |
|---|---:|---:|
| strict usable | 9.06 / 11 | **9.38 / 11** |
| strict lenient | 10.47 / 11 | **10.73 / 11** |
| gap (proxy − strict usable) | 1.29 | **1.23** |

### Board-level strict usable (post-rnd refresh)

| board | 中文 | n (ok) | strict usable /11 |
|---|---|---:|---:|
| bse | 北交所 | 513 | **8.71** |
| sse_main | 沪市主板 | 1652 | **9.25** |
| szse_main | 深市主板 | 1487 | 9.41 |
| star | 科创板 | 584 | **9.56** |
| chinext | 创业板 | 1385 | 9.65 |

> **不得**将 9.38/11 与旧 eval1000 strict 10.16/11 比较为「改善」或「下降」——universe 与 proxy 规则均不同。

See [strict_audit_summary.md](strict_audit_summary.md) and [rnd_refresh_summary.md](rnd_refresh_summary.md).

## Financial subtypes (ok, n=86)

| subtype | count |
|---|---:|
| bank | 43 |
| broker | 37 |
| other_financial | 4 |
| insurer | 2 |

> 金融字段质量需单独 review；未纳入 strict headline。

## SQLite import

| run_name | evaluation_result rows |
|---|---:|
| `full_market_2024` (original) | 62,890 |
| `full_market_2024_rnd_refresh` (post-rnd) | 62,890 |

- **Scoped rnd refresh** (2026-06-24): re-extracted rnd_investment only from cached PDFs; better recall of existing R&D disclosures; not a full_market CNINFO rerun. See [rnd_refresh_summary.md](rnd_refresh_summary.md).
- Root symlinks `{code}` → `{board}/{code}` enable db_import profile lookup.
- Re-run merge after batch re-runs or eval reconciliation.

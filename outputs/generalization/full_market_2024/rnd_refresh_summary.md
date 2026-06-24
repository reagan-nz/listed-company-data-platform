# full_market_2024 rnd_investment Scoped Refresh Summary

_Generated: 2026-06-24 (post P2.1 candidate-fallback)_

## What changed

**Scoped rnd_investment refresh over cached PDFs** — not a full_market rerun from CNINFO.

1. **P1 code fix** (`lab/field_schema.py`, `lab/extract_annual_report.py`): added BSE 研发支出 anchors; reordered summary-total labels above project-table column headers.
2. **`lab/refresh_rnd_full_market.py`**: re-extracted **only** `rnd_investment` from cached PDFs; updated `company_profile.json` and batch `eval_results.json` rnd field.
3. **P2.1 candidate-fallback** (`lab/extract_annual_report.py`): when top-priority anchor window yields no parseable amount, try next-best anchor candidates; skip fallback when primary 研发投入 disclosure is explicitly 不适用.
4. **Downstream refresh**: merge → strict audit → SQLite import (`run_name=full_market_2024_rnd_refresh`).

> Better recall of **existing** R&D disclosures (especially BSE 研发支出 template and 研发投入合计 summary tables). **Not** full manual validation. **Not** a CNINFO re-download or full-field re-extraction.

## Refresh run results (latest P2.1 apply)

| Metric | Value |
|---|---|
| Profiles processed (non-fin ok) | 5,621 |
| Changed (this P2.1 run) | 155 |
| not_found → found (this run) | **+28** |
| found → not_found / partial (this run) | **0** |
| Errors | 0 (non-fin) |

Cumulative since original baseline: not_found→found **+1,488**; original 15 regressions **resolved** (13→found, 2→partial).

## rnd_investment found rate

| Scope | Before (original) | After (post P2.1) | Δ |
|---|---:|---:|---:|
| Non-fin rnd found | 3,817 / 5,621 (**67.9%**) | **5,297 / 5,621 (94.2%)** | +26.3 pp |
| BSE rnd found | 117 / 513 (**22.8%**) | **509 / 513 (99.2%)** | +76.4 pp |

## Post-refresh headline metrics (non-fin)

| Metric | Pre-rnd refresh | Post P2.1 |
|---|---:|---:|
| proxy plausible | 10.35 / 11 | **10.61 / 11** |
| strict usable | 9.06 / 11 | **9.38 / 11** |
| strict lenient | 10.47 / 11 | **10.74 / 11** |
| rnd strict usable (field) | 3,332 / 5,621 | **5,086 / 5,621** |
| rnd not_found_unverified | 1,791 | **280** |

### Board strict usable (post P2.1)

| board | 中文 | before | after |
|---|---|---:|---:|
| bse | 北交所 | 7.71 | **8.71** |
| sse_main | 沪市主板 | 8.53 | **9.25** |
| szse_main | 深市主板 | 9.42 | 9.41 |
| star | 科创板 | 9.47 | **9.56** |
| chinext | 创业板 | 9.66 | 9.65 |

> **不得**将 strict 9.38/11 与旧 eval1000 baseline 10.16/11 直接比较为「改善」——proxy 规则与 universe 均不同。

## SQLite

| run_name | evaluation_result rows |
|---|---:|
| `full_market_2024` (original) | 62,890 |
| `full_market_2024_rnd_refresh` (post-refresh) | 62,890 |

## P2.1 regression resolution (15 companies)

All 15 original regressions resolved by candidate-fallback (no guard relaxation):

| code | name | status after P2.1 | anchor |
|---|---|---|---|
| 600011 | 华能国际 | found | 研发费用 |
| 600020 | 中原高速 | found | 研发费用 |
| 600033 | 福建高速 | found | 研发投入 |
| 600346 | 恒力石化 | found | 研发费用 |
| 600808 | 马钢股份 | found | 研发费用 |
| 601778 | 晶科科技 | found | 研发费用 |
| 603776 | 永安行 | found | 研发费用 |
| 301221 | 光庭信息 | partial | 研发投入合计 |
| 000063 | 中兴通讯 | found | 研发投入金额 |
| 000333 | 美的集团 | partial | 研发投入合计 |
| 002296 | 辉煌科技 | found | 研发投入金额 |
| 000517 | 荣安地产 | found | 研发投入金额 |
| 001300 | 三柏硕 | found | 研发投入金额 |
| 002907 | 华森制药 | found | 研发投入金额 |
| 300445 | 康斯特 | found | 研发投入金额 |

**Residuals (documented, not blockers):** 000333/301221 remain `partial` (narrative cumulative figures). 600011/600020/etc. recover full-yuan 费用化/研发费用 baseline values, not 亿元-table 合计 (P2.2 unit-aware parsing follow-up).

## Artifacts

| File | Role |
|---|---|
| [strict_audit_summary.md](strict_audit_summary.md) | Post-refresh strict audit |
| [full_market_2024_summary.md](full_market_2024_summary.md) | Post-merge proxy summary |
| `rnd_refresh_changes.csv` | Per-company change log (**gitignored**) |

## Caveats

- Completion = scoped field refresh + merge + audit + DB import. **≠** 62,890 rows manually verified.
- Revenue table slicing, financial review, multi-year remain open (Stage 3).

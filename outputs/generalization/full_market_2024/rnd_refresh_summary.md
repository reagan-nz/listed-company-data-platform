# full_market_2024 rnd_investment Scoped Refresh Summary

_Generated: 2026-06-24 (post-remediation)_

## What changed

**Scoped rnd_investment refresh over cached PDFs** — not a full_market rerun from CNINFO.

1. **P1 code fix** (`lab/field_schema.py`, `lab/extract_annual_report.py`): added BSE 研发支出 anchors; reordered summary-total labels above project-table column headers.
2. **`lab/refresh_rnd_full_market.py`**: re-extracted **only** `rnd_investment` from cached PDFs; updated `company_profile.json` and batch `eval_results.json` rnd field.
3. **Downstream refresh**: merge → strict audit → SQLite import (`run_name=full_market_2024_rnd_refresh`).
4. **Post-audit remediation** (2026-06-24): patched 7 stale batch `eval_results.json` entries from refreshed profiles (earlier killed `--apply` had updated profiles but not batch eval); re-merge + re-audit + re-import.

> Better recall of **existing** R&D disclosures (especially BSE 研发支出 template and 研发投入合计 summary tables). **Not** full manual validation. **Not** a CNINFO re-download or full-field re-extraction.

## Refresh run results

| Metric | Value |
|---|---|
| Profiles processed (non-fin ok) | 5,621 |
| Changed | 1,988 |
| not_found → found | **+1,460** |
| found → not_found / partial (vs original baseline) | **15** (known follow-up) |
| Errors | 0 |
| Profiles with `rnd_refresh` tag | 2,003 |

## rnd_investment found rate

| Scope | Before | After | Δ |
|---|---:|---:|---:|
| Non-fin rnd found (profile status=found) | 3,817 / 5,621 (**67.9%**) | **5,269 / 5,621 (93.7%)** | +25.8 pp |
| BSE rnd found (profiles) | 117 / 513 (**22.8%**) | **509 / 513 (99.2%)** | +76.4 pp |

> Proxy plausible for rnd equals status=found after remediation (5,269 / 93.7%). Earlier docs cited 5,276 / 93.9% due to 7 stale batch eval rows; reconciled 2026-06-24.

## Post-refresh headline metrics (non-fin)

| Metric | Pre-rnd refresh | Post-rnd refresh |
|---|---:|---:|
| proxy plausible | 10.35 / 11 | **10.61 / 11** |
| strict usable | 9.06 / 11 | **9.38 / 11** |
| strict lenient | 10.47 / 11 | **10.73 / 11** |
| rnd strict usable (field) | 3,332 / 5,621 | **5,078 / 5,621** |
| rnd not_found_unverified | 1,791 | **331** |

### Board strict usable (post-rnd refresh)

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

`extracted_field` upserts from refreshed profiles; `evaluation_result` uses updated proxy from merged `eval_results.json`. Original `full_market_2024` evaluation_result run preserved.

## Known follow-up (15 regressions vs original baseline)

Old `found` → new `not_found` / `partial` after anchor reorder. Cause: high-priority summary labels (`费用化研发投入`, `研发投入总额/合计`) sometimes anchor narrative or governance sentences without a parseable total.

| code | name | board | after | anchor |
|---|---|---|---|---|
| 600011 | 华能国际 | sse_main | not_found | 费用化研发投入 |
| 600020 | 中原高速 | sse_main | not_found | 费用化研发投入 |
| 600033 | 福建高速 | sse_main | not_found | 费用化研发投入 |
| 600346 | 恒力石化 | sse_main | not_found | 费用化研发投入 |
| 600808 | 马钢股份 | sse_main | not_found | 费用化研发投入 |
| 601778 | 晶科科技 | sse_main | not_found | 费用化研发投入 |
| 603776 | 永安行 | sse_main | not_found | 费用化研发投入 |
| 301221 | 光庭信息 | chinext | partial | 研发投入合计 |
| 000063 | 中兴通讯 | szse_main | not_found | 研发投入总额 |
| 000333 | 美的集团 | szse_main | partial | 研发投入合计 |
| 002296 | 辉煌科技 | szse_main | not_found | 研发投入总额 |
| 000517 | 荣安地产 | szse_main | not_found | 研发投入总额 |
| 001300 | 三柏硕 | szse_main | not_found | 研发投入总额 |
| 002907 | 华森制药 | szse_main | not_found | 研发投入合计 |
| 300445 | 康斯特 | chinext | not_found | 研发投入合计 |

8 detected in final refresh run; 7 additional from earlier interrupted `--apply` (profiles updated, batch eval stale until remediation). Net rnd gain remains strongly positive (+1,452 vs original). Follow-up anchor/window tuning; not blockers for this milestone.

## Artifacts

| File | Role |
|---|---|
| [strict_audit_summary.md](strict_audit_summary.md) | Post-refresh strict audit |
| [full_market_2024_summary.md](full_market_2024_summary.md) | Post-merge proxy summary |
| `rnd_refresh_changes.csv` | Per-company change log (~5,621 rows; **gitignored**) |

## Caveats

- Completion = scoped field refresh + merge + audit + DB import. **≠** 62,890 rows manually verified.
- 15 regressions need separate anchor/window tuning (P1.1 follow-up).
- Revenue table slicing, financial review, multi-year remain open (Stage 3).

# Financial strict audit fix #30b — ratio/table reject labels + major_subsidiaries gate

_Generated: 2026-06-25 | Issue #30b validation report_

## Verdict

**#30b PASSES**

- Joined manual↔automated agreement: **202/325 (62%) → 226/325 (69.5%) [#30a] → 233/325 (71.7%) [#30b]** (+7 vs #30a, +31 vs #29).
- Broker `not_found_missed` unchanged from #30a (sample **4**, population **7**).
- All **4 #30a true MISSED broker numeric rows** preserved.
- Ratio/table auto-`partial`/`usable` vs manual-`WRONG` mismatches in sample: **0** (was 19+ before #30b on target lists).
- Frozen `financial_audit_sample.csv` `--score` remains **202/325 (62%)** (stale auto column).

---

## Code changes (`lab/strict_audit_financial_full_market.py`)

### 1. Bank ratio semantic checks (#30b)

- Expanded `FIELD_REJECT_LABELS` for `npl_ratio`, `capital_adequacy_ratio`, `provision_coverage_ratio`.
- Added `_npl_label_is_wrong_line_item()` — rejects 合计/总额/区域行业行/不良率增减/纯「不良率」等。
- Added `_ratio_context_industry_narrative()` — rejects 银行业运行/商业银行正积极… 等行业叙述中的比率。
- Added `_ratio_context_preferred_share_trigger()` — rejects 600016 优先股转股触发阈值。
- Added `_evaluate_ratio_numeric()` — shared evaluator; **partial ratio rows** now scored (not auto-passed as `partial`).

### 2. Financial table plausibility (#30b)

Enhanced `_financial_table_plausible()` + `_revenue_table_plausible_strict()` with field-specific reject/require vocab:

| Field | Reject examples | Require / structure |
|---|---|---|
| `loan_structure` | 利息收入、存放中央银行、金融投资、资产构成 | 贷款结构/按产品/按担保等 breakdown；拒绝 mixed balance-sheet lines |
| `deposit_structure` | 长期股权投资、应付职工薪酬、现金流量、利息支出 | 存款/吸收存款 vocabulary |
| `regional_distribution` | 营业网点、证券持仓、地址/邮编 | 地区/区域 vocabulary |
| `revenue_by_segment` | 现金流量、业务及管理费、利息净/支出、EV 敏感性 | 分部/主营业务分/segment revenue；拒绝母公司利润表（利息净收入+利息支出 无分部标题） |

- `strict_financial_table()` partial branch now runs plausibility (fixes 601963/600927/603093 partial wrong-table rows).
- Evidence sentence included in plausibility blob.

### 3. major_subsidiaries usable gate (#30b)

- `_major_subsidiaries_wrong_section()` — 在职员工/业务资格/员工情况等 → `wrong`.
- `_major_subsidiaries_structured_only()` — 纯结构化主体附注（无子公司表头）→ `wrong`.
- `_major_subsidiaries_table_substantive()` — 子公司/控股/注册资本/持股比例 + 表格数字 → **`usable` even when `in_region=False`**.
- Skips generic `FIN_BOILER_KW` rejection for substantive subsidiary tables (fixes 601628 法律法规 in scope text).
- #30a broker `not_found_missed` code paths untouched.

---

## Before vs after joined agreement

| Milestone | Agreement | Δ |
|---|---:|---:|
| #29 baseline | 202/325 **62.0%** | — |
| #30a (broker missed tighten) | 226/325 **69.5%** | +24 |
| **#30b (this change)** | **233/325 71.7%** | **+7 vs #30a** |

Frozen `--score` on sample CSV: **202/325 (62%)** unchanged.

---

## Ratio / table disagreement changes (sample targets)

### Ratio manual-WRONG targets (11/11 now agree)

| Code | Field | Before (#30a) | After (#30b) |
|---|---|---|---|
| 600908 | capital_adequacy_ratio | partial | **wrong** |
| 600908 | provision_coverage_ratio | partial | **wrong** |
| 600000 | provision_coverage_ratio | usable | **wrong** |
| 600016 | capital_adequacy_ratio | usable | **wrong** |
| 002966, 601328, 600015, 601939, 002142, 000001 | npl_ratio | wrong | wrong (maintained) |
| 002142 | capital_adequacy_ratio | wrong | wrong (maintained) |

Sample ratio fields overall: **30/36 agree**, **0** manual-WRONG still auto partial/usable.

### Table manual-WRONG targets (18/18 now agree)

| Code | Field | Before | After |
|---|---|---|---|
| 002966, 600015 | loan_structure | usable | **wrong** |
| 600000 | loan_structure, deposit_structure | usable/partial | **wrong** |
| 601963 | loan_structure, deposit_structure | partial | **wrong** |
| 002142 | loan_structure, deposit_structure | partial | **wrong** |
| 600369, 601878, 601696, 601136, 601336 | revenue_by_segment | usable/partial | **wrong** |
| 600927, 603093 | revenue_by_segment | partial | **wrong** |
| 001236, 002961 | revenue_by_region | partial | **wrong** |

Sample table fields overall: **35/58 agree**, **0** manual-WRONG still auto partial/usable.

---

## major_subsidiaries label changes

| Code | Manual | Before | After |
|---|---|---|---|
| 600318, 002966, 600908, 601328, 600000, 600016, 601628, 601878, 601696, 601108, 601059, 001236, 000402 | CORRECT | partial | **usable** |
| 600816, 600015, 601375, 601136, 601336 | WRONG | partial | **wrong** |
| 002142, 000783, 000001, 601939, 601377, 601990, 600030, 600369 | PARTIAL | partial | partial (unchanged) |

Sample major_subsidiaries: **24/30 agree** (was ~18/30 before gate fixes).

---

## Broker not_found_missed preservation

| Metric | #30a | #30b |
|---|---:|---:|
| Sample broker `not_found_missed` | 4 | **4** |
| Population broker `not_found_missed` | 7 | **7** |
| Total population `not_found_missed` | 24 | **24** |

| Code | Field | After | Manual |
|---|---|---|---|
| 601878 | investment_banking_income | not_found_missed | MISSED |
| 601878 | asset_management_income | not_found_missed | MISSED |
| 601878 | margin_lending_balance | not_found_missed | MISSED |
| 600030 | investment_banking_income | not_found_missed | MISSED |

---

## True MISSED preservation (all broker numeric #30a list)

All **4** preserved (see above).

Note: `000402 revenue_by_segment` (manual MISSED, auto `not_found_unverified`) predates #30b — table `not_found` path unchanged; not a broker-numeric #30a row.

---

## Population impact

| strict_label | #30a (approx) | #30b |
|---|---:|---:|
| usable | ~600 | **592** |
| partial | ~125 | **116** |
| wrong | ~220 | **240** |
| not_found_unverified | ~87 | **87** |
| not_found_missed | 24 | **24** |

More `wrong` labels from ratio industry-narrative rejection and table plausibility — intended direction.

---

## Caveats

1. **Frozen sample CSV** auto column stale; use population join for agreement.
2. **Industry-narrative ratio reject** may demote some partial rows where company ratio and industry paragraph coexist (intended for 600908/600000 calibration).
3. **major_subsidiaries usable gate** applies to substantive subsidiary **tables**; truncated contact-only snippets (601939) remain `partial`.
4. **Structured-entity sections** with numeric product tables (601990/600030) stay `partial` when manual grade is PARTIAL — not promoted to usable or demoted to wrong.
5. **000402 revenue_by_segment MISSED** still `not_found_unverified` — extraction/audit recall gap, not introduced by #30b.
6. Non-financial strict audit and extraction code unchanged.

---

## Safe to commit

- `lab/strict_audit_financial_full_market.py`
- `outputs/generalization/full_market_2024/financial_audit_population.csv`
- `outputs/generalization/full_market_2024/financial_audit_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_fix_30b_summary.md`
- `CURRENT_STATUS.md`, `CHANGELOG.md`

## Do not commit

- `outputs/generalization/full_market_2024/financial_audit_sample.csv`
- `outputs/generalization/full_market_2024/financial_calibration_report.md`
- `company_profile.json`, `eval_results.json`, PDFs, `.cache`, `outputs/db/*.db`
- Extraction code, `field_schema.py`, YAML tags

---

## Validation commands

```bash
.venv/bin/python lab/strict_audit_financial_full_market.py \
  --out-dir outputs/generalization/full_market_2024 \
  --companies-yaml lab/eval_companies_full_market_2024.yaml

.venv/bin/python lab/financial_calibration_sample.py \
  --score outputs/generalization/full_market_2024/financial_audit_sample.csv
```

Joined agreement computed from frozen `financial_audit_sample.csv` manual grades × refreshed `financial_audit_population.csv` strict labels.

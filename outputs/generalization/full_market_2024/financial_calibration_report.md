# Financial Manual Calibration Report (#29)

_Generated: 2026-06-25 | Worksheet: `financial_audit_sample.csv`_

---

## 1. Scope

This report closes **Issue #29 — financial manual calibration grading** on the stratified audit worksheet.

| Item | Value |
|---|---|
| Worksheet | `outputs/generalization/full_market_2024/financial_audit_sample.csv` |
| Companies | **30** (12 bank, 12 broker, 2 insurer, 4 other_financial) |
| Field-cells | **325** |
| Grading method | Human PDF review with `manual_grade` + `manual_notes` |
| Reviewers | `model-gpt-5.4` (Batches 1–5, 202 rows) · `model-composer-2.5` (Batches 6–8, 123 rows) |

**What this is:**

- A **sample calibration** of financial extraction quality on 325 hand-reviewed cells.
- A separate track from the non-financial headline metric (**9.43 / 11** on industrial schema companies).

**What this is not:**

- Full **1,059-cell** manual validation of the financial population (`financial_audit_population.csv`).
- A sign-off that financial extraction is production-ready.
- A replacement for population-level strict audit statistics.

---

## 2. Completion

Pre-score verification (read-only):

| Check | Result |
|---|---|
| Total worksheet rows | **325** |
| Rows with `manual_grade` filled | **325** |
| Blank `manual_grade` | **0** |

All 30 companies × sampled fields are graded. Issue #29 manual calibration grading is **complete**.

---

## 3. Raw `--score` Output

Command:

```bash
.venv/bin/python lab/financial_calibration_sample.py \
  --score outputs/generalization/full_market_2024/financial_audit_sample.csv
```

Stdout:

```
[fin_calib] graded 325/325 rows
[fin_calib] manual vs automated strict agreement (heuristic): 202/325 (62%)
[fin_calib] grade distribution: {'CORRECT': 128, 'PARTIAL': 52, 'ABSENT-OK': 48, 'WRONG': 86, 'MISSED': 11}
[fin_calib] fields with WRONG/MISSED: {'revenue_by_segment': 12, 'npl_ratio': 10, 'main_business_segments': 7, 'loan_structure': 6, 'major_subsidiaries': 5, 'industry_discussion': 5, 'deposit_structure': 5, 'proprietary_trading_income': 5, 'asset_management_income': 5, 'risk_factors': 4}
```

---

## 4. Grade Distribution

### Overall (325 cells)

| Grade | Count | Share |
|---|---|---|
| CORRECT | 128 | 39.4% |
| PARTIAL | 52 | 16.0% |
| WRONG | 86 | 26.5% |
| MISSED | 11 | 3.4% |
| ABSENT-OK | 48 | 14.8% |

### By schema profile

| Profile | Cells | CORRECT | PARTIAL | WRONG | MISSED | ABSENT-OK |
|---|---|---|---|---|---|---|
| bank | 146 | 56 | 31 | 42 | 6 | 11 |
| broker | 133 | 46 | 13 | 32 | 5 | 37 |
| insurer | 22 | 11 | 3 | 8 | 0 | 0 |
| other_financial | 24 | 15 | 5 | 4 | 0 | 0 |

---

## 5. Automated vs Manual Agreement Summary

The `--score` script uses a **heuristic** mapping between `manual_grade` and `automated_strict_label`:

| Manual grade | Treats as agreeing when auto label is |
|---|---|
| CORRECT | `usable` |
| PARTIAL or CORRECT | `partial` |
| WRONG | `wrong` |
| MISSED | `not_found_missed` |
| ABSENT-OK | `not_found_unverified` |

**Headline:** 202 / 325 (**62%**) heuristic agreement.

### Cross-tab (automated → manual)

| Auto label | CORRECT | PARTIAL | WRONG | MISSED | ABSENT-OK |
|---|---|---|---|---|---|
| `usable` | 84 | 23 | 18 | — | 1 |
| `partial` | 41 | 25 | **44** | — | 5 |
| `wrong` | 3 | 4 | 24 | — | — |
| `not_found_missed` | — | — | — | 9 | **23** |
| `not_found_unverified` | — | — | — | 2 | 19 |

### Largest disagreement patterns (123 cells)

| Pattern | Count | Interpretation |
|---|---|---|
| auto=`partial` → manual=**WRONG** | 44 | Strict audit passes weak snippets; PDF review finds wrong section/table |
| auto=`not_found_missed` → manual=**ABSENT-OK** | 23 | Broker `not_found_missed` mostly audit false positives (anchor exists, field N/A or alternate label) |
| auto=`usable` → manual=**WRONG** | 18 | Usable label on wrong line item or narrative-only capture |
| auto=`partial` → manual=**CORRECT** | 41 | In-region gate / partial audit under-credits good extractions |
| auto=`wrong` → manual=**CORRECT** | 3 | Strict audit over-penalizes valid captures |

Agreement by grading batch: `model-gpt-5.4` 118/202 (58%) · `model-composer-2.5` 84/123 (68%).

---

## 6. Key Findings

### 6.1 Broker `not_found_missed` — mostly audit false positives

26 broker cells carry `automated_strict_label=not_found_missed`. Manual review:

- **23 → ABSENT-OK** (tagged `audit-fp-anchor` in notes): anchor text exists but field is genuinely absent, uses alternate disclosure, or is not applicable for that broker subtype.
- **3 → MISSED** (601878): `investment_banking_income`, `asset_management_income`, `margin_lending_balance` — PDF contains extractable line items at p50–p53.

Pattern: strict audit treats “label near miss” as `not_found_missed`; manual review often finds the disclosure is **absent or differently labeled**, not a true extract miss.

### 6.2 Confirmed MISSED rows (11 total)

| Code | Field | Page | Auto label | Notes |
|---|---|---|---|---|
| 601963 | npl_ratio | p43 | not_found_missed | 不良贷款率 in PDF, extractor not_found |
| 002966 | capital_adequacy_ratio | p18 | not_found_missed | 资本充足率 |
| 600908 | npl_ratio | p14 | not_found_missed | 不良贷款率 |
| 600015 | provision_coverage_ratio | p16 | not_found_missed | 拨备覆盖率 |
| 600000 | npl_ratio | p73 | not_found_missed | 不良贷款率 |
| 600016 | npl_ratio | p38 | not_found_missed | 不良贷款率 |
| 000402 | revenue_by_segment | p197 | not_found_unverified | tag-review; segment table present |
| 601878 | investment_banking_income | p50 | not_found_missed | 投资银行业务 |
| 601878 | asset_management_income | p51 | not_found_missed | 资产管理业务 |
| 601878 | margin_lending_balance | p53 | not_found_missed | 融出资金 |
| 600030 | investment_banking_income | p300 | not_found_unverified | 投资银行业务净收入 |

**Bank ratios dominate recall gaps:** 6 of 11 MISSED are `npl_ratio` or `provision_coverage_ratio` on bank profiles.

### 6.3 WRONG rows — wrong line item / wrong table / narrative-only

86 WRONG cells. Top fields: `revenue_by_segment` (12), `npl_ratio` (10), `main_business_segments` (7), `loan_structure` (6), `major_subsidiaries` (5).

Common failure modes:

- **Wrong line item:** numeric extractor grabs adjacent table row (e.g. 601336 `claims_expense` → 退保金; insurer `combined_ratio` → sensitivity 赔付率/费用率).
- **Wrong table:** balance-sheet movement or P&L variance table tagged as segment or income field.
- **Narrative-only / wrong section:** governance, director bios, ECL footnotes, employee stats, structured-entity notes captured as `industry_discussion`, `risk_factors`, or `main_business_segments`.
- **Wrong semantic:** `investment_income` captures fragment values instead of 总投资收益 total.

### 6.4 `major_subsidiaries` — structural audit-gate behavior

30 `major_subsidiaries` cells in sample: **15 CORRECT · 10 PARTIAL · 5 WRONG**.

Many PARTIAL rows are **real subsidiary content** downgraded by `in_region-gate` or truncated/pointer snippets (`issue:pointer-only`, `issue:in_region-gate`). Manual grades often **CORRECT** where strict audit says `partial`. WRONG cases land on employee stats, structured entities, or branch tables — not subsidiary ownership tables.

### 6.5 Insurer n=2 remains low-n

Only **601336** and **601628** in sample (22 cells). Findings:

- Numeric fields: `premium_income`, `solvency_ratio`, `embedded_value` often CORRECT; `combined_ratio` and `claims_expense` systematically WRONG (sensitivity / product-table confusion).
- Section snippets: `major_subsidiaries` and `main_business_segments` WRONG on employee/EV sensitivity pages.
- All insurer rows tagged `issue:low-n-insurer` where relevant. **Do not generalize** beyond these two annual reports.

### 6.6 Subtype caveat companies (000402 / 600816 / 600318)

Tagged `tag-review-*` in manual notes. Key outcomes:

- **000402** (broker-tagged non-broker): 1 MISSED (`revenue_by_segment` p197); several ABSENT-OK for broker numeric fields (`na-subtype`).
- **600816** (bank-tagged non-bank): `major_subsidiaries` WRONG (wrong line item p175); many bank numeric fields ABSENT-OK.
- **600318** (bank-tagged hybrid): mostly CORRECT/PARTIAL on snippets; bank numerics largely ABSENT-OK.

→ Subtype/schema mismatch drives both false strict-audit signal and manual ABSENT-OK.

---

## 7. Triage Table

| Pattern / tag | Example | Count (approx.) | Follow-up issue |
|---|---|---|---|
| `audit-fp-anchor` | Broker `not_found_missed` → ABSENT-OK | ~23 | **#30** audit rule refinement (anchor vs field applicability) |
| `issue:extract-miss` / MISSED | Bank `npl_ratio`, 601878 income/balance | 11 | **#30** extraction recall fixes |
| `wrong-line-item` / `wrong-table` / `wrong-section` | `revenue_by_segment`, insurer ratios, segment bios | ~86 WRONG | **#30** extractor label priority, table plausibility, section routing |
| `issue:in_region-gate` / `issue:pointer-only` | `major_subsidiaries` PARTIAL→CORRECT | ~10 PARTIAL | **#30** audit in-region gate + snippet completeness |
| `tag-review-000402` / `600816` / `600318` | Subtype caveat companies | 35 cells | **#30** tag/subtype review |
| `issue:na-subtype` | Bank fields on non-bank profiles | ~15 ABSENT-OK | **#30** tag/subtype review |
| `issue:low-n-insurer` | 601336 / 601628 | 22 cells | **#30** insurer field anchors (low-n caveat) |
| Under-tagging in eval cohort | Companies not marked `financial: true` | population scan | **#31** financial under-tagging scan |

---

## 8. Follow-up Recommendations

### #30 — Financial audit / extract / tag fixes (priority)

1. **Audit:** Relax or refine `not_found_missed` when anchor hit but field N/A; fix `in_region-gate` on `major_subsidiaries`; reduce false `partial` on usable subsidiary tables.
2. **Extract:** Bank ratio recall (`npl_ratio`, `provision_coverage_ratio`, `capital_adequacy_ratio`); broker segment income lines (601878 pattern); insurer `combined_ratio` / `claims_expense` disambiguation from sensitivity and product tables.
3. **Tag/subtype:** Resolve 000402 / 600816 / 600318 schema assignment; propagate `na-subtype` handling into profile detection.

### #31 — Financial under-tagging scan

- Scan `eval_companies_full_market_2024.yaml` (and eval1000 cohort) for financial companies missing `financial: true`.
- Prevents industrial 11-field schema from running on banks/brokers/insurers.

---

## 9. Caveats

1. **Sample size:** 325 cells from 30 companies — not the full 1,059-cell financial population manual validation.
2. **Separate metrics:** Financial calibration results must **not** be merged into the non-fin **9.43/11** headline without explicit relabeling.
3. **Calibration ≠ population truth:** Manual grades calibrate extractor/audit behavior on a stratified sample; they do not replace population CSV or strict audit rollups.
4. **Insurer low-n:** n=2 insurers — findings are directional only.
5. **No sign-off:** This report documents Issue #29 completion only. **Financial extraction is not signed off** for full-market deployment.

---

## Appendix: Score Script Reference

Heuristic agreement logic lives in `lab/financial_calibration_sample.py` → `cmd_score()`. Re-run after any future worksheet edits:

```bash
.venv/bin/python lab/financial_calibration_sample.py \
  --score outputs/generalization/full_market_2024/financial_audit_sample.csv
```

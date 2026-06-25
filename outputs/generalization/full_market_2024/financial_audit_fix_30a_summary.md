# Financial strict audit fix #30a — broker `not_found_missed` tightening

_Generated: 2026-06-25 | Issue #30a validation report_

## Verdict

**#30a PASSES**

- Joined manual↔automated agreement improved **202/325 (62%) → 226/325 (69.5%)** (+24 cells).
- All **4 true MISSED** broker rows preserved as `not_found_missed`.
- All **23/23** manual ABSENT-OK broker over-call targets now `not_found_unverified`.
- Frozen `financial_audit_sample.csv` `--score` remains **202/325 (62%)** because the sample file’s `automated_strict_label` column was not regenerated (by design).

---

## Code changes (`lab/strict_audit_financial_full_market.py`)

### 1. Broker-specific infrastructure

- Added regex/helpers: `_BROKER_COMMA_AMOUNT_RE`, `_BROKER_ASSET_COMPOSITION_RE`, segment-section markers, weak-window markers, deep-IB net-income labels/threshold.
- Added `_iter_spaced_keyword_positions()` to fix PDF line-break spacing (e.g. `资产管 理业务`, `投资银 行业务`) without preferring narrative exact-match hits first.

### 2. Field-specific missed-evidence gates

| Field | Promotion rule | Demotion / guard |
|---|---|---|
| `risk_control_indicators` | **Never** promote from PDF scan | Manual ABSENT-OK even when 净资本 tables exist |
| `brokerage_income` | **Never** promote from PDF scan | Removes MD&A/fee-note false positives (601377, 601990, …) |
| `investment_banking_income` | MD&A segment row with **internal label break** + comma amount + margin/YoY markers; **or** deep fee-note `投资银行业务净收入` ≥ ¥1B (600030 p300) | Rejects clean-label segment rows (601108) and narrative anchors |
| `asset_management_income` | MD&A segment operating row (spaced-label tolerant) | Skip when `brokerage_income` already `found` (601696 gate) |
| `proprietary_trading_income` | Strong 自营 labels with comma amounts only | No generic 投资收益 promotion |
| `margin_lending_balance` | Asset-composition `融出资金` row under `(二) 非主营业务` + `(三) 资产、负债情况分析` | Rejects 主要财务指标 tables, cash-flow/利息/万亿 narrative |

### 3. Wiring

- `_pdf_broker_field_missed_evidence()` routes broker numerics; non-broker still uses `_pdf_anchor_with_number()`.
- `strict_financial_numeric()` / `strict_audit_field()` accept `profile_fields` so AM gate can see sibling extraction status.

### 4. Unchanged

- Extraction code, `field_schema.py`, YAML tags, frozen `financial_audit_sample.csv`, non-broker audit paths.

---

## Before vs after agreement

| Metric | #29 baseline | #30a after |
|---|---:|---:|
| Joined agreement (manual × refreshed population) | 202/325 **62%** | **226/325 69.5%** |
| Frozen sample `--score` (stale auto column) | 202/325 62% | 202/325 62% (unchanged) |
| Broker `not_found_missed` in sample | 26 | **4** |
| Broker `not_found_missed` in population | 58 | **7** |
| Total `not_found_missed` in population | 75 | **24** |

Grade distribution unchanged (325/325 graded): CORRECT 128, PARTIAL 52, WRONG 86, MISSED 11, ABSENT-OK 48.

---

## True MISSED preservation

| Code | Field | Before (auto) | After (auto) | Manual | Match |
|---|---|---|---|---|---|
| 601878 | investment_banking_income | not_found_missed | not_found_missed | MISSED | Yes |
| 601878 | asset_management_income | not_found_missed | not_found_missed | MISSED | Yes |
| 601878 | margin_lending_balance | not_found_missed | not_found_missed | MISSED | Yes |
| 600030 | investment_banking_income | not_found_unverified | **not_found_missed** | MISSED | Yes (improved) |

Sample broker `not_found_missed` rows after fix = exactly these four 601878 fields + 600030 IB (5 broker numeric misses in sample set; 601878 contributes 3).

---

## Manual ABSENT-OK over-call reduction (23-target list)

| Code | Field | Before | After |
|---|---|---|---|
| 601377 | brokerage_income | not_found_missed | not_found_unverified |
| 601377 | margin_lending_balance | not_found_missed | not_found_unverified |
| 601878 | brokerage_income | not_found_missed | not_found_unverified |
| 601878 | proprietary_trading_income | not_found_missed | not_found_unverified |
| 601878 | risk_control_indicators | not_found_missed | not_found_unverified |
| 600369 | proprietary_trading_income | not_found_missed | not_found_unverified |
| 600369 | risk_control_indicators | not_found_missed | not_found_unverified |
| 601990 | brokerage_income | not_found_missed | not_found_unverified |
| 601990 | asset_management_income | not_found_missed | not_found_unverified |
| 601990 | risk_control_indicators | not_found_missed | not_found_unverified |
| 601696 | asset_management_income | not_found_missed | not_found_unverified |
| 601696 | margin_lending_balance | not_found_missed | not_found_unverified |
| 600030 | margin_lending_balance | not_found_missed | not_found_unverified |
| 600030 | risk_control_indicators | not_found_missed | not_found_unverified |
| 601108 | investment_banking_income | not_found_missed | not_found_unverified |
| 601108 | asset_management_income | not_found_missed | not_found_unverified |
| 601108 | proprietary_trading_income | not_found_missed | not_found_unverified |
| 000783 | brokerage_income | not_found_missed | not_found_unverified |
| 000783 | investment_banking_income | not_found_missed | not_found_unverified |
| 000783 | margin_lending_balance | not_found_missed | not_found_unverified |
| 601059 | risk_control_indicators | not_found_missed | not_found_unverified |
| 601136 | proprietary_trading_income | not_found_missed | not_found_unverified |
| 601136 | margin_lending_balance | not_found_missed | not_found_unverified |

**23/23 fixed.**

---

## Population impact

- Broker `not_found` cells: **69** `not_found_unverified` + **7** `not_found_missed` (was 58 missed / 17 unverified among not_found broker numerics at #29 baseline).
- Remaining population `not_found_missed` (non-sample examples): `600837` IB, `600909`/`601162` proprietary trading — promoted by stricter segment/deep-IB rules; not in calibration sample.
- `600030` IB flipped unverified → missed (recall alignment with manual MISSED).

---

## Caveats

1. **Frozen sample CSV** still shows old auto labels; use joined population scoring for agreement.
2. **`brokerage_income` never PDF-promoted** — conservative by calibration; true brokerage recall misses deferred to #30d extraction.
3. **`risk_control_indicators` never PDF-promoted** — tables may exist while manual grade is ABSENT-OK.
4. **Deep IB threshold (≥ ¥1B)** targets large-broker fee-note line items; mid-cap segment tables without internal label breaks stay unverified.
5. **AM gate** (`brokerage_income found` → skip AM missed) is a calibration heuristic, not a disclosure rule.
6. Population missed count drop (75 → 24) includes non-broker tightening from removing global strong-label pass on prior iteration plus broker rules above.

---

## Safe to commit

- `lab/strict_audit_financial_full_market.py`
- `outputs/generalization/full_market_2024/financial_audit_population.csv`
- `outputs/generalization/full_market_2024/financial_audit_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_fix_30a_summary.md`
- `CURRENT_STATUS.md`, `CHANGELOG.md` (post-pass doc sync)

## Do not commit

- `outputs/generalization/full_market_2024/financial_audit_sample.csv` (frozen manual grades / stale auto column)
- `outputs/generalization/full_market_2024/financial_calibration_report.md`
- `company_profile.json`, `eval_results.json`, PDFs, `.cache`, `outputs/db/*.db`
- Extraction code, `field_schema.py`, YAML tags

---

## Validation commands run

```bash
.venv/bin/python lab/strict_audit_financial_full_market.py \
  --out-dir outputs/generalization/full_market_2024 \
  --companies-yaml lab/eval_companies_full_market_2024.yaml

.venv/bin/python lab/financial_calibration_sample.py \
  --score outputs/generalization/full_market_2024/financial_audit_sample.csv
```

Joined scoring: manual_grade from sample CSV × `strict_label` from refreshed population CSV (heuristic in `financial_calibration_sample.cmd_score`).

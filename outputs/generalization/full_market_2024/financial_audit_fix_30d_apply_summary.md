# Financial audit fix #30d apply — sample-only broker recall refresh

_Generated: 2026-06-25 | targeted sample-company apply over cached PDFs only_

## Verdict

**PASS on the requested sample-only apply gates; wider broker rollout remains deferred.**

| Gate | Result |
|---|---|
| 4/4 target rows are strict usable | **PASS (4 / 4)** |
| 0/23 ABSENT-OK controls become strict usable | **PASS (0 / 23)** |
| `600030 margin_lending_balance` remains not usable | **PASS** |
| `601108` IB / AM / proprietary narrative rows remain not usable | **PASS** |
| Only 2 profiles modified | **PASS** |
| Only 4 target field objects changed, plus refresh marker | **PASS** |
| No `eval_results.json` writes | **PASS** |
| No `financial_audit_sample.csv` writes | **PASS** |
| No non-fin artifacts touched by apply step | **PASS** |

## Exact apply scope

- Source validation basis:
  - `outputs/generalization/full_market_2024/financial_audit_fix_30d_dryrun_summary.md`
  - current cached PDFs and current `company_profile.json`
- Apply target:
  - **2 broker sample companies**
  - **4 target field objects**
- Profiles touched:
  - `outputs/generalization/full_market_2024/sse_main/601878/company_profile.json`
  - `outputs/generalization/full_market_2024/sse_main/600030/company_profile.json`
- Backup suffix:
  - `company_profile.json.bak.broker_recall_30d`
- Refresh marker written into each modified profile:
  - `broker_recall_refresh: {"tag": "broker_recall_30d", "at": "..."}`

## Apply counts

| Metric | Count |
|---|---:|
| Profiles modified | **2** |
| Backups created | **2** |
| Target field objects replaced | **4** |
| Non-target field objects replaced | **0** |

## 4-positive recovery table

| Code | Field | Manual grade | Status after apply | Page after apply | Strict after apply | New labeled |
|---|---|---|---|---:|---|---|
| 601878 | `investment_banking_income` | `MISSED` | `found` | 50 | `usable` | `投资银行业务=677,073,421.90` |
| 601878 | `asset_management_income` | `MISSED` | `found` | 51 | `usable` | `资产管理业务=530,211,137.63` |
| 601878 | `margin_lending_balance` | `MISSED` | `found` | 53 | `usable` | `融出资金=24,224,341,732.66` |
| 600030 | `investment_banking_income` | `MISSED` | `found` | 300 | `usable` | `投资银行业务净收入=4,159,191,856.95` |

Result: **4 / 4** confirmed MISSED broker rows recovered and strict usable after actual profile apply.

## 23-negative-control table

| Code | Field | Manual grade | Status after apply | Strict after apply | Outcome |
|---|---|---|---|---|---|
| 601377 | `brokerage_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601377 | `margin_lending_balance` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601878 | `brokerage_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601878 | `proprietary_trading_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601878 | `risk_control_indicators` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 600369 | `proprietary_trading_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 600369 | `risk_control_indicators` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601990 | `brokerage_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601990 | `asset_management_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601990 | `risk_control_indicators` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601696 | `asset_management_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601696 | `margin_lending_balance` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 600030 | `margin_lending_balance` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 600030 | `risk_control_indicators` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601108 | `investment_banking_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601108 | `asset_management_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601108 | `proprietary_trading_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 000783 | `brokerage_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 000783 | `investment_banking_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 000783 | `margin_lending_balance` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601059 | `risk_control_indicators` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601136 | `proprietary_trading_income` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |
| 601136 | `margin_lending_balance` | `ABSENT-OK` | `not_found` | `not_found_unverified` | preserved |

Result: **0 / 23** ABSENT-OK controls became strict `usable`.

## Specific safety checks

### `600030 margin_lending_balance`

- Status after apply: `not_found`
- Strict after apply: `not_found_unverified`
- Evidence remains the narrative `融资融券利息收入减少...`

Result: **PASS** — the notes-region consolidated `融出资金` balances were still not accepted.

### `601108` narrative-row checks

| Field | Status after apply | Strict after apply |
|---|---|---|
| `investment_banking_income` | `not_found` | `not_found_unverified` |
| `asset_management_income` | `not_found` | `not_found_unverified` |
| `proprietary_trading_income` | `not_found` | `not_found_unverified` |

Result: **PASS** — narrative-only anchors remained not usable.

## Joined agreement before / after

Important distinction:

- `financial_audit_sample.csv` stayed frozen and unchanged.
- Comparable calibration metric remains **manual grades × refreshed population strict labels**.

| Stage | Joined agreement |
|---|---|
| Before #30d sample apply | **233 / 325** |
| After #30d sample apply | **229 / 325** |

Interpretation:

- The 4 target rows were all manual `MISSED`, so moving them from `not_found_missed` to `usable` **improves extraction** but **reduces joined agreement by 4** under the current calibration mapping.
- This is expected and should be interpreted the same way as the #30c MISSED-recovery tradeoff, not as a new extraction regression.

## Population label impact

After rerunning `lab/strict_audit_financial_full_market.py`:

| strict_label | Before | After | Delta |
|---|---:|---:|---:|
| `usable` | 592 | 596 | **+4** |
| `partial` | 116 | 116 | 0 |
| `wrong` | 240 | 240 | 0 |
| `not_found_unverified` | 87 | 87 | 0 |
| `not_found_missed` | 24 | 20 | **-4** |

Rows whose strict label changed in population CSV: **4**

- `600030 investment_banking_income`: `not_found_missed → usable`
- `601878 investment_banking_income`: `not_found_missed → usable`
- `601878 asset_management_income`: `not_found_missed → usable`
- `601878 margin_lending_balance`: `not_found_missed → usable`

## Caveats

- The calibration joined-agreement metric decreased **233 → 229** purely because 4 manual `MISSED` rows became correctly extracted `usable`.
- `601696 asset_management_income` remained **not usable** (`not_found_unverified`) after apply. This is an audit-recall caveat, not an apply failure.
- Wider broker rollout is still **not** recommended from this sample apply alone; this confirms the 4 targeted recoveries only.

## Files changed

Code / harness / summaries:

- `lab/extract_annual_report.py`
- `lab/field_schema.py`
- `lab/financial_audit_fix_30d_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30d_dryrun_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_fix_30d_apply_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_population.csv`
- `outputs/generalization/full_market_2024/financial_audit_summary.md`
- `CURRENT_STATUS.md`
- `CHANGELOG.md`

Sample profile files updated:

- `outputs/generalization/full_market_2024/sse_main/601878/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/600030/company_profile.json`

Backups created:

- `outputs/generalization/full_market_2024/sse_main/601878/company_profile.json.bak.broker_recall_30d`
- `outputs/generalization/full_market_2024/sse_main/600030/company_profile.json.bak.broker_recall_30d`

Intentionally **not** changed:

- `financial_audit_sample.csv`
- `financial_calibration_report.md`
- any `eval_results.json`
- any PDFs / `.cache`
- any SQLite files
- any YAML tags
- non-fin strict audit code

## Rollback command

```bash
cd "/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector" && \
cp "outputs/generalization/full_market_2024/sse_main/601878/company_profile.json.bak.broker_recall_30d" \
   "outputs/generalization/full_market_2024/sse_main/601878/company_profile.json" && \
cp "outputs/generalization/full_market_2024/sse_main/600030/company_profile.json.bak.broker_recall_30d" \
   "outputs/generalization/full_market_2024/sse_main/600030/company_profile.json" && \
.venv/bin/python lab/strict_audit_financial_full_market.py \
  --out-dir outputs/generalization/full_market_2024 \
  --companies-yaml lab/eval_companies_full_market_2024.yaml
```

## Safe-to-commit list

- `lab/extract_annual_report.py`
- `lab/field_schema.py`
- `lab/financial_audit_fix_30d_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30d_dryrun_summary.md`
- `outputs/generalization/full_market_2024/financial_audit_fix_30d_apply_summary.md`
- `CURRENT_STATUS.md`
- `CHANGELOG.md`

## Do-not-commit list

- `outputs/generalization/full_market_2024/sse_main/601878/company_profile.json`
- `outputs/generalization/full_market_2024/sse_main/600030/company_profile.json`
- both `.bak.broker_recall_30d` backup files
- `outputs/generalization/full_market_2024/financial_audit_population.csv`
- `outputs/generalization/full_market_2024/financial_audit_summary.md`
- any `eval_results.json`
- any PDFs / `.cache`
- any SQLite artifacts

## Recommendation on wider rollout

**Deferred.**

Reason:

- The 4 confirmed MISSED broker rows were recovered cleanly.
- The 23 ABSENT-OK controls stayed protected.
- But this apply is still a **sample-only validation**, not a sufficient basis for wider broker or wider financial profile refresh.

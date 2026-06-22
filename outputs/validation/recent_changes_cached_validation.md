# Recent Changes — Cached Validation Report

_Generated: 2026-06-22_

**Scope:** Cached-only validation on existing eval1000 outputs. No PDF download, no network fetch, no full eval pipeline rerun.

**Verdict:** **PASS** — SQLite full import succeeds; Issue #1 / Issue #2 proxy changes behave as intended on cached data; no regression on other fields' plausible logic. Safe to proceed to financial schema implementation or BrowserUser planning, with known limitations documented below.

---

## Commands run

```bash
cd listed_company_data_collector

# 1. SQLite full import
.venv/bin/python lab/db_init.py
.venv/bin/python lab/db_import.py --limit 0
.venv/bin/python lab/db_import.py --limit 0   # idempotency re-run

sqlite3 outputs/db/listed_companies_v1.db \
  "SELECT 'company_basic', COUNT(*) FROM company_basic UNION ALL
   SELECT 'report_source', COUNT(*) FROM report_source UNION ALL
   SELECT 'extracted_field', COUNT(*) FROM extracted_field UNION ALL
   SELECT 'evaluation_result', COUNT(*) FROM evaluation_result;"

git check-ignore -v outputs/db/listed_companies_v1.db

# 2–4. Cached proxy impact (eval_results.json + company_profile.json)
.venv/bin/python -c "..."   # recomputed field_plausible on 10417 merged ok-field records
```

**Data sources:** `outputs/generalization/eval1000/eval_results.json` (1020 companies) + `*/company_profile.json` (947 profiles for status=ok companies).

---

## 1. SQLite full cached import

| Table | Row count |
|---|---|
| `company_basic` | **1020** |
| `report_source` | **1020** |
| `extracted_field` | **10417** |
| `evaluation_result` | **10417** |

| Check | Result |
|---|---|
| Import abort | **None** — exit code 0 both runs |
| `profile_errors` | **0** |
| Idempotency (2× `--limit 0`) | Counts unchanged |
| `.db` gitignored | **Yes** — `.gitignore:49:outputs/db/*.db` |
| Audit metadata | `in_region` populated 10417; `anchor_matched` non-empty 10343 |
| FK enforcement | `PRAGMA foreign_keys` returns 0 in sqlite3 CLI session (connection default); import uses `connect_db()` with FK ON |

**Note:** 1020 companies in eval list; 947 have cached `company_profile.json` (946 status=ok + partial cache). Import reads `eval_results.json` for all 1020 and profiles where present.

---

## 2. rnd_investment cached impact (Issue #1)

Applied **new** `rnd_investment_plausible` vs **old** generic numeric plausible on cached stored values (no re-extraction).

| Metric | Count |
|---|---|
| Total cells (status=ok companies) | 947 |
| `status=found` | 745 |
| Stored plausible (eval run, old rule) | 745 |
| Old rule pass | 745 |
| **New rule pass** | **644** |
| **Rejected by stricter rule** | **101** (13.6% of found) |

### Rejection breakdown

| Reason | Count |
|---|---|
| list-marker (1 / 2 / 3) | 39 |
| no-substantive-amount | 28 |
| ratio-only | 28 |
| 0.00-only | 6 |

### Representative rejected examples

| Type | Code | Stored value snippet |
|---|---|---|
| list-marker | 603199 | `研发投入: 1`, `2` — from `(1).研发投入情况表` section numbering |
| list-marker | 605169 | `研发费用: 2` — adjacent cash-flow table line |
| ratio-only | 688282 | `27.68%` only — no substantive amount |
| ratio-only | 002237 | `2.84%`, `0.00%` — ratio table row |
| 0.00-only | 300093 | `0`, `0` — capitalized amount row only |
| no-substantive-amount | 600029 | `545`, `0.31`, `0.18` — small bare numbers from 研发投入合计 row |

### Representative accepted examples

| Type | Code | Stored value snippet |
|---|---|---|
| 元 amount | 688293 | `34,187,414.01` |
| 万元 amount | 839680 | `1,012.10 万元`, `1,045.30 万元` |
| 亿元-scale comma amount | 600063 | `439,129,134.82` |
| multiline table | 600176 | `528,291,814.11` with label `研发投入` from MD&A table |

---

## 3. revenue table cached impact (Issue #2)

Applied **new** `revenue_table_plausible` vs **old** generic table plausible (`rows` + `match_hits≥1`).

### revenue_by_region

| Metric | Count |
|---|---|
| Total cells | 947 |
| `status=found` | 902 |
| Stored plausible (old) | 902 |
| **New rule pass** | **851** |
| **Rejected** | **51** (5.7% of found) |

Rejection reasons: title-only 33, header-only 16, empty-label-with-data 2.

### revenue_by_segment

| Metric | Count |
|---|---|
| Total cells | 947 |
| `status=found` | 922 |
| Stored plausible (old) | 922 |
| **New rule pass** | **898** |
| **Rejected** | **24** (2.6% of found) |

Rejection reasons: title-only 10, header-only 12, empty-label-with-data 2.

### Representative rejected examples

| Type | Code | Pattern |
|---|---|---|
| header-only | 000981 | Rows: `分地区`, `分销售模式` — no numeric data |
| title-only | 600377 | `主营业务分地区情况` + header row + `-` placeholders |
| empty preview | 601065 | Single title row only |
| section/title-only | 600488 | `主营业务分产品情况` + column headers, no data rows in preview |

### Representative accepted examples

| Type | Code | Pattern |
|---|---|---|
| 分地区 + amounts | 000559 | `国内销售` + `11,030,604,426.10` … |
| 分地区 + amounts | 603701 | `国内` + `692,398,474.92` … |
| 分行业 table | 603359 | `分行业` header + data rows with revenue/cost |
| 分产品 table | 603589 | `分行业`/`分产品` structure with numeric cells |

### Known limitation: empty-label rows

| Code | Fields affected | Issue |
|---|---|---|
| **603132** | region + segment | pdfplumber lost row label (first cell empty); preview has real amounts e.g. `695,831,436.81` |
| **605090** | region + segment | Same pattern — 4 cells total across both fields |

These are **false negatives** (~4 fields, 2 companies, <0.2% of revenue table found cells). Tables contain valid data; proxy rejects because `_table_row_is_data_row` requires a non-empty non-header label in the first column.

---

## 4. Regression check

| Check | Result |
|---|---|
| Non-rnd / non-revenue fields: old generic vs current `field_plausible` | **0 mismatches** across 8,927 found cells |
| `revenue_table_plausible` applied only to revenue fields | Confirmed in `field_plausible` branch |
| `rnd_investment_plausible` applied only to rnd | Confirmed |
| Stored plausible delta (expected — rules changed) | rnd −101 cells; revenue −75 cells |

### Updated headline estimate (recomputed proxy, not full eval rerun)

| Cohort | Stored plausible (eval run) | Recomputed with new rules |
|---|---|---|
| Non-financial (936 ok) | **10.54 / 11** | **10.36 / 11** (−0.18) |
| Financial (11 ok) | varies | −2 cells total across 11 companies |

> **Do not treat recomputed proxy as final eval1000 headline.** Full pipeline rerun would also re-extract (Issue #1 affects extraction, not just proxy). Strict-usable audit has not been rerun.

---

## 5. Pass / fail judgment

| Area | Judgment |
|---|---|
| SQLite import hardening | **PASS** |
| rnd_investment proxy tightening | **PASS** — rejects intended noise; retains substantive amounts |
| revenue_table_plausible | **PASS with known limitation** — empty-label false negatives documented |
| Regression on other fields | **PASS** |
| Overall | **PASS** |

---

## 6. Known limitations

1. **Not a full eval rerun** — extraction + eval summary + strict audit numbers remain stale.
2. **Empty-label revenue rows** — 603132, 605090 (4 field instances).
3. **`strict_audit_result` loader** — DB column exists; not populated from audit.
4. **947 / 946 profile cache** — 73 no_announcement + 1 ok company may lack local profile; import still succeeds from eval_results.

---

## 7. Proceed recommendation

**Safe to proceed** to either:

- **Financial schema implementation (Issue #4)** — industrial proxy validation stable; financial companies already excluded from non-financial headline.
- **BrowserUser planning** — no blocker from this validation.

**Recommended before claiming new headline metrics:** optional controlled re-extraction on a 50–100 company subset for rnd/revenue fields, or full eval rerun when compute budget allows.

---

## Artifacts

| File | Purpose |
|---|---|
| `outputs/validation/recent_changes_cached_validation.md` | This report |
| `outputs/validation/_summary.json` | Machine-readable counts and examples |
| `outputs/db/listed_companies_v1.db` | Full import DB (gitignored) |

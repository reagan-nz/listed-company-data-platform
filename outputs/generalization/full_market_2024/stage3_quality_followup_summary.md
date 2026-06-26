# full_market_2024 Stage 3a Quality Follow-up Summary

_Generated: 2026-06-25 | Issue #28 — Stage 3a closure documentation_

## 1. Scope and completion statement

This document consolidates **Stage 3a quality follow-up** for the full_market_2024 2024 annual-report baseline (#24–#28).

**In scope (completed):**

- #24 BSE strict audit-rule correction (TOP_KW)
- #25 rnd_investment extraction fixes + scoped cached-PDF refresh
- #26 revenue page-boundary extraction fixes + scoped cached-PDF refresh
- #27 financial-only audit framework (inventory + automated strict + calibration worksheet)
- #28 this summary and doc sync

**Out of scope (explicitly not done):**

- Full CNINFO re-download or full-field re-extraction
- Full manual validation of 62,890 SQLite rows
- Financial extraction/tag sign-off (worksheet grading pending)
- Multiyear expansion (2025 / 2023 / 2022)
- Mixing financial metrics into the non-financial 9.43/11 headline

**Method posture:** automated strict audit + **targeted scoped refreshes over cached PDFs** + sampled / manual calibration **support** — not population-wide human review.

**Closure decision:** **full_market_2024 Stage 3a quality follow-up PASS.** Residual issues are documented and deferred; they do **not** block baseline closure. **Full Stage 3** (ROADMAP) remains open for residuals, financial grading, and multiyear planning (Stage 3b).

---

## 2. Final non-fin quality snapshot

Latest SQLite `run_name`: **`full_market_2024_revenue_refresh`**

| Metric | Value |
|---|---:|
| Universe total | 6,124 |
| ok | 5,707 |
| no_announcement | 417 |
| error | **0** |
| Non-fin ok companies | **5,621** |
| Audit population | 5,621 × 11 = **61,831 cells** |
| **Proxy plausible** | **10.67 / 11** |
| **Strict usable** | **9.43 / 11** |
| **Strict lenient** | **10.80 / 11** |
| All-field strict **wrong** | **566** (was 876 pre-#26) |
| rnd_investment **found** | **5,297 / 5,621 (94.2%)** |
| rnd strict usable (field) | **5,086 / 5,621** |
| revenue_by_region strict **wrong** | **38** (was 258 pre-#26) |
| revenue_by_segment strict **wrong** | **19** (was 109 pre-#26) |
| SQLite evaluation_result rows | **62,890** |

**Board strict usable (non-fin, post-revenue):**

| board | strict usable / 11 |
|---|---:|
| bse | **8.82** |
| sse_main | **9.35** |
| szse_main | **9.43** |
| star | **9.61** |
| chinext | **9.67** |

**Calibration support (non-fin):** 55 companies × 7 targeted fields (sample CSV); 15-company PDF deep-read (105 cells). Manual vs automated agreement: 45/105 (43%). **Not full manual validation.**

Detail: [strict_audit_summary.md](strict_audit_summary.md)

---

## 3. Financial audit snapshot (separate headline)

**Do not mix into non-fin 9.43/11.**

| Metric | Value |
|---|---:|
| YAML `financial: true` | **87** tagged / **86 ok** (000562 no_announcement) |
| Subtypes | bank **43** / broker **37** / insurer **2** / other **4** |
| Automated audit cells | **1,059** |
| **bank strict usable** | **9.00 / 13** |
| **broker strict usable** | **7.66 / 12** |
| **insurer strict usable** | **9.25 / 12** (n=2 — illustrative only) |
| **other_financial strict usable** | **5.75 / 8** |
| Calibration worksheet | **30 companies × 325 cells** — **`manual_grade` pending** |
| Population labels | usable 557 / partial 310 / wrong 81 / not_found_missed 75 / not_found_unverified 36 |

**#27 status:** audit **framework complete** — not financial extraction signed off. Worksheet generated; grading not done.

Detail: [financial_audit_summary.md](financial_audit_summary.md)

---

## 4. Strict metric trajectory (full_market_2024 only)

Population-consistent evolution within full_market_2024 after initial hybrid audit:

| Step | Trigger | Non-fin strict usable | Notes |
|---|---|---:|---|
| Initial audit | Post–full_market merge | **9.01 / 11** | Automated adversarial + 15-co PDF sample |
| #24 | BSE TOP_KW audit rule | **9.06 / 11** | Audit-rule only; BSE board **7.14 → 7.71** |
| #25 | rnd scoped refresh | **9.38 / 11** | Extraction + cached-PDF refresh; BSE board **7.71 → 8.71** |
| #26 | revenue scoped refresh | **9.43 / 11** | Extraction + cached-PDF refresh; BSE board **8.71 → 8.82** |

```
9.01  →  9.06  →  9.38  →  9.43
 ^         ^         ^         ^
initial   #24       #25       #26
```

> This trajectory describes **scoped audit/refresh evolution on the same full_market_2024 universe**. **Do not** compare 9.43/11 to eval1000 strict **10.16/11** as improvement — different proxy rules, audit scope, and universe scale.

---

## 5. #24–#27 changelog

### #24 — BSE strict audit-rule correction

- **Change:** Expanded `TOP_KW` in `lab/strict_audit_full_market.py` for BSE customer/supplier table column headers (`年度销售占比`, `年度采购占比`, etc.).
- **Type:** Audit-rule correction only — **no extraction change**.
- **Effect:** BSE strict **7.14 → 7.71**; overall strict **9.01 → 9.06**.
- **Artifact:** [bse_quality_followup.md](bse_quality_followup.md)

### #25 — rnd_investment scoped refresh

- **Change:** BSE 研发支出 anchors + summary-total priority; P2.1 candidate-fallback in extractors; scoped rnd refresh over cached PDFs.
- **Type:** Extraction fix + scoped cached-PDF refresh.
- **Effect:** rnd found **67.9% → 94.2%**; BSE rnd **22.8% → 99.2%**; strict **9.06 → 9.38**; proxy **10.35 → 10.61/11**.
- **Artifact:** [rnd_refresh_summary.md](rnd_refresh_summary.md) | SQLite `run_name=full_market_2024_rnd_refresh`

### #26 — revenue page-boundary scoped refresh

- **Change:** Tier 3 continuation stitch + Tier 2 stacked trim; scoped revenue refresh (`revenue_by_region`, `revenue_by_segment`) over cached PDFs.
- **Type:** Extraction fix + scoped cached-PDF refresh.
- **Effect:** wrong→usable **297**; usable regressions **0**; region wrong **258 → 38**; segment wrong **109 → 19**; strict **9.38 → 9.43**; all-field wrong **876 → 566**.
- **Artifact:** [revenue_refresh_summary.md](revenue_refresh_summary.md) | SQLite `run_name=full_market_2024_revenue_refresh`

### #27 — financial audit framework

- **Change:** Population inventory; automated financial strict audit; 30-company calibration worksheet (`seed=20260627`).
- **Type:** Audit framework + documentation — **not extraction repair**.
- **Effect:** 1,059 cells audited separately; worksheet **325 cells** with blank `manual_grade`.
- **Artifact:** [financial_audit_summary.md](financial_audit_summary.md)

---

## 6. Fix taxonomy

| Issue | Audit-rule correction | Extraction fix | Scoped cached-PDF refresh | Audit framework / docs |
|---|---:|---:|---:|---:|
| #24 | **Yes** | — | — | — |
| #25 | — | **Yes** | **Yes** (rnd only) | — |
| #26 | — | **Yes** | **Yes** (revenue fields) | — |
| #27 | Partial (financial strict rules) | — | — | **Yes** |
| #28 | — | — | — | **Yes** (this summary) |

**Global constraint:** All field refreshes were **targeted scoped refreshes over cached PDFs** — not full CNINFO reruns.

---

## 7. Calibration and validation posture

| Layer | Non-fin | Financial |
|---|---|---|
| Population automated strict | 5,621 × 11 = 61,831 cells | 86 ok × sub-schema = 1,059 cells |
| Sampled support | 55 co × 7 fld CSV; 15 co PDF deep-read (105 cells) | 30 co × 325 cells worksheet |
| Manual grades | Deep-read labels only (not full worksheet) | **`manual_grade` blank — pending** |
| Claim allowed | Automated strict estimate + calibration **support** | Separate automated strict; grading **pending** |
| Claim **not** allowed | Full manual validation of 62,890 rows | Financial quality signed off |

Hybrid method matches [strict_audit_summary.md](strict_audit_summary.md) §1. Financial worksheet grades (`CORRECT | PARTIAL | WRONG | MISSED | ABSENT-OK`) will refine broker `not_found_missed` interpretation after manual review.

---

## 8. Remaining issues

| ID | Issue | Scope | Severity | Deferred to |
|---|---|---|---|---|
| R1 | Revenue strict-wrong residual | region **38** + segment **19** ≈ **57 cells** | Medium | Follow-up: scoped extraction/audit |
| R2 | rnd residual regressions | ~**8 companies** (sse_main 费用化研发投入; e.g. 600011 + 301221 partial) | Low | Small scoped fix |
| R3 | BSE board gap | **8.82/11** vs chinext 9.67 | Medium | Monitor / optional board follow-up |
| R4 | risk_factors strict-wrong | **221 cells** (top false-positive field) | Medium | Audit or extraction triage |
| R5 | major_subsidiaries (non-fin) | **0 usable / 5549 partial** — structural | Low | Audit behavior; do not overread |
| R6 | Financial manual grading | **325 cells**, `manual_grade` blank | **High** | Manual calibration grading |
| R7 | Broker `not_found_missed` | **~58/75** recall hints — **not confirmed truth** | Medium | Refine after manual grade |
| R8 | Financial subtype caveats | **000402 / 600816 / 600318** stored schema | Medium | Tag review |
| R9 | Financial under-tagging | YAML completeness not scanned | Medium | Under-tagging scan |
| R10 | Financial numeric/table noise | broker proxy−strict gap **7.5%** | Medium | Financial plausible rules |
| R11 | Insurer low-n | **n=2** insurers | Info | Expand tagging before trusting means |
| R12 | major_subsidiaries (financial) | **0/86 usable** — industrial in_region gate | Low | Structural partial; not extraction regression |

Revenue extraction is **not fully fixed**. Financial audit framework is complete; **extraction is not signed off**.

---

## 9. Follow-up backlog (post–Stage 3a)

| Priority | Topic | Notes |
|---|---|---|
| 1 | **Financial manual calibration grading** | Fill `financial_audit_sample.csv` → `--score` |
| 2 | **Broker `not_found_missed` refinement** | After grading; tighten audit rules |
| 4 | **rnd residual regressions** | ~~#32c scoped P0 apply verified~~ — 72/104 P0 pool still partial; full R&D rollout deferred |
| 3 | **Remaining revenue strict-wrong** | ~57 cells; scoped cached-PDF refresh only (#32b Tier 4) |
| 5 | **Financial under-tagging scan** | YAML `financial: true` completeness |
| 6 | **Financial extraction/tag fixes** | Numeric plausible, subtype tags (000402 etc.) |
| 7 | **2025 / 2023 / 2022 expansion decision** | Scope, batch strategy, run naming — **no default full CNINFO rerun** |

Optional lower priority: `strict_audit_result` DB loader; BrowserUser pilot (ROADMAP Phase 4).

---

## 10. Stage 3a closure decision

**Verdict: full_market_2024 Stage 3a quality follow-up PASS.**

**Rationale:**

- Non-fin baseline after targeted scoped refreshes: strict **9.43/11**, proxy **10.67/11**, **0** pipeline errors, **0** usable→wrong regressions on #26 revenue refresh.
- BSE board strict **8.82/11** meets ROADMAP threshold (≥8.5).
- Financial audit **framework** delivered with separate headline and documented caveats.
- Residual wrong cells and pending financial grading are **tracked**, not hidden.

**Do not claim:**

- Full Stage 3 (multiyear + all residuals) is complete
- All extraction issues fixed
- Full manual validation
- Financial metrics merged into non-fin headline

**ROADMAP:** Stage **3a** Done (#24–#28); Stage **3b** In Progress (residuals, grading, multiyear planning).

---

## 11. Artifact index

| Artifact | Issue | Description |
|---|---|---|
| [bse_quality_followup.md](bse_quality_followup.md) | #24 | BSE TOP_KW audit-rule before/after |
| [rnd_refresh_summary.md](rnd_refresh_summary.md) | #25 | rnd scoped refresh metrics |
| [revenue_refresh_summary.md](revenue_refresh_summary.md) | #26 | revenue scoped refresh metrics |
| [strict_audit_summary.md](strict_audit_summary.md) | baseline + post-refresh | Non-fin hybrid strict audit |
| [strict_audit_sample.csv](strict_audit_sample.csv) | baseline | 55 co × 7 fld sample |
| [financial_audit_summary.md](financial_audit_summary.md) | #27 | Financial automated strict |
| [financial_audit_population.csv](financial_audit_population.csv) | #27 | 1,059 audit rows |
| [financial_audit_sample.csv](financial_audit_sample.csv) | #27 | 30 co worksheet (grading pending) |
| [financial_population_inventory.csv](financial_population_inventory.csv) | #27 | 87 tagged inventory |
| [full_market_2024_summary.md](full_market_2024_summary.md) | Stage 2 | Full extraction run report |
| **This file** | #28 | Stage 3a consolidation + closure |

Cross-links: [CURRENT_STATUS.md](../../CURRENT_STATUS.md) | [ROADMAP.md](../../ROADMAP.md) | [docs/evaluation_method.md](../../docs/evaluation_method.md)

Stage 3b financial follow-up continued in `#30`; see [financial_audit_fix_30_summary.md](financial_audit_fix_30_summary.md).

**#32c update (2026-06-26):** Scoped P0 R&D apply verification completed — 104 targets, 32 profile updates, post-apply verify PASS; global non-fin headline **9.43/11 unchanged**. See [rnd_residual_fix_32c_post_apply_verify.md](rnd_residual_fix_32c_post_apply_verify.md).

**#32 closure (2026-06-26):** #32 current scope complete (inventory + #32c + #32b dry-run); revenue production fix deferred; non-fin headline **9.43/11 unchanged**. See [revenue_rnd_fix_32_final_summary.md](revenue_rnd_fix_32_final_summary.md).

**#33 decision (2026-06-26):** Multiyear expansion strategy documented — 2025 first, staged rollout; parent #23 ready to close. See [multiyear_expansion_decision_33.md](multiyear_expansion_decision_33.md).

---

## 12. Anti-claims checklist

Use this list when writing issues, reports, or supervisor summaries:

| Claim | Allowed? |
|---|---|
| Stage 3a quality follow-up PASS | **Yes** — with caveats in §10 |
| Full Stage 3 / all roadmap Phase 3 complete | **No** — 3b remains |
| Non-fin strict **9.43/11** as latest headline | **Yes** — separate from financial |
| Financial bank **9.00/13**, broker **7.66/12**, etc. | **Yes** — **separate headline only** |
| Mix financial into 9.43/11 | **No** |
| 9.43/11 improved vs eval1000 **10.16/11** | **No** — unlike baselines |
| Full manual validation of 62,890 rows | **No** |
| All extraction / all fields fixed | **No** — §8 residuals |
| Financial extraction signed off | **No** — grading pending |
| Full CNINFO rerun required for closure | **No** — scoped refresh model |
| Automated strict + scoped refresh + calibration support | **Yes** — correct framing |

---

## 13. Safe-to-commit and do-not-touch guidance

### Safe to commit (explicit paths)

**Stage 3a summary + doc sync (#28):**

```
outputs/generalization/full_market_2024/stage3_quality_followup_summary.md
CURRENT_STATUS.md
CHANGELOG.md
ROADMAP.md
docs/evaluation_method.md
README.md
```

**Prior Stage 3 artifacts (if not yet committed — use explicit `git add`):**

```
outputs/generalization/full_market_2024/bse_quality_followup.md
outputs/generalization/full_market_2024/rnd_refresh_summary.md
outputs/generalization/full_market_2024/revenue_refresh_summary.md
outputs/generalization/full_market_2024/strict_audit_summary.md
outputs/generalization/full_market_2024/strict_audit_sample.csv
outputs/generalization/full_market_2024/financial_audit_summary.md
outputs/generalization/full_market_2024/financial_audit_population.csv
outputs/generalization/full_market_2024/financial_audit_sample.csv
outputs/generalization/full_market_2024/financial_population_inventory.csv
lab/strict_audit_financial_full_market.py
lab/financial_calibration_sample.py
docs/financial_company_schema.md
```

Use `git add <paths>` — not `git add -A`.

### Do not commit / do not modify in doc-only tasks

| Category | Paths |
|---|---|
| Runtime JSON | `eval_results.json`, `company_profile.json`, batch subdirs `[0-9]*/` |
| PDFs / cache | `*.pdf`, `.cache/` |
| SQLite | `outputs/db/*.db` |
| Refresh deltas | `rnd_refresh_changes.csv`, `revenue_refresh_changes.csv`, `revenue_refresh_changes_targeted.csv`, overnight reports |
| Logs / backups | `*.log`, backups |
| Generated batch YAML | `lab/batch_*_2024.yaml` |

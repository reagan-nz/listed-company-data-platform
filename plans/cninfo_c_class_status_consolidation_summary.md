# CNINFO C Class Status Consolidation Summary

_最后更新：2026-07-06_

> **Scope:** All 10 C-class source candidates — P1 + P2-A consolidated view.  
> **Related:** [P2-A mapper completion](cninfo_c_class_p2a_mapper_completion_summary.md) · [P1 YAML backfill decision](cninfo_c_class_p1_yaml_backfill_decision.md) · [P2-A YAML backfill decision](cninfo_c_class_p2a_yaml_backfill_decision.md) · [candidate YAML](../config/cninfo_c_class_source_candidates.yaml)（**not modified this round**）

---

## 1. Summary

C-class currently has **10** source candidates.

| Bucket | Count | Status |
|--------|-------|--------|
| Endpoint populated + `recommended_status=testing` | **6** | basic · security · executive · share_capital · top_shareholders · top_float_shareholders |
| `candidate` — derived / no independent endpoint | **1** | industry |
| `candidate` — P2-B probe needed | **3** | dividend_financing · contact · business_scope |

**Global invariants:**

- All sources remain **`verified=false`**
- No source is **`testing_stable_sample`**
- No database ingestion has been performed
- All mapper work remains **testing / prototype** level on 3 known companies (600000 · 300001 · 688001)

---

## 2. Source status table

| source_id | current_status | endpoint_status | live_validation | mapper_status | fixture_count | schema_validation | notes |
|-----------|----------------|-----------------|-----------------|---------------|---------------|-------------------|-------|
| `cninfo_company_basic_profile` | testing / verified=false | endpoint populated | P1 live PASS, 3/3 endpoint_found | mapper_draft_complete | 2 | 2/2 PASS | 600000 live/probe historical empty caveat; 2 non-empty fixtures only |
| `cninfo_company_security_profile` | testing / verified=false | endpoint populated | P1 live PASS, 3/3 endpoint_found | mapper_draft_complete | 3 | 3/3 PASS | marketOverview; getHeadStripData annex only, not mapped |
| `cninfo_company_industry_profile` | candidate / verified=false | endpoint null | derived field check only / no independent endpoint | not_started | 0 | n/a | derived_from basic_profile via F032V / MARKET / F044V |
| `cninfo_executive_profile` | testing / verified=false | endpoint populated | P2-A live PASS, 3/3 endpoint_found | mapper_draft_complete | 6 | 6/6 PASS | getCompanyExecutives |
| `cninfo_share_capital_profile` | testing / verified=false | endpoint populated | P2-A live PASS, 3/3 endpoint_found | mapper_draft_complete | 6 | 6/6 PASS | getStockStructure |
| `cninfo_top_shareholders_profile` | testing / verified=false | endpoint populated | P2-A live PASS, 3/3 endpoint_found | covered_by_shareholder_mapper | 6 top-scope rows inside 12 total | 12/12 shared shareholder PASS | getTopTenStockholders |
| `cninfo_top_float_shareholders_profile` | testing / verified=false | endpoint populated | P2-A live PASS, 3/3 endpoint_found | covered_by_shareholder_mapper | 6 float-scope rows inside 12 total | 12/12 shared shareholder PASS | getTopTenCirculatingStockholders |
| `cninfo_dividend_financing_profile` | candidate / verified=false | endpoint null | not_started | not_started | 0 | n/a | P2-B candidate |
| `cninfo_company_contact_profile` | candidate / verified=false | endpoint null | not_started | not_started | 0 | n/a | P2-B candidate; some contact fields may already exist in basic_profile raw |
| `cninfo_company_business_scope` | candidate / verified=false | endpoint null | not_started | not_started | 0 | n/a | P2-B candidate; business_scope may already be covered by basic_profile raw/mapped fields |

**Status rollup:** **6 testing** · **4 candidate** · **0 verified** · **0 testing_stable_sample**

---

## 3. Completed validation chain

### P1 — basic + security (+ industry derived check)

| Stage | Status | Reference |
|-------|--------|-----------|
| DevTools probe | 9 P1 probe records | [c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml) |
| YAML backfill decision | Done | [cninfo_c_class_p1_yaml_backfill_decision.md](cninfo_c_class_p1_yaml_backfill_decision.md) |
| Source candidate YAML backfill | basic + security → `testing` | [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) |
| Registry lint | PASS | [registry lint summary](../outputs/validation/cninfo_c_class_registry_lint_summary.md) |
| Live validation v1 | **LIVE_PASS** 6/6 (2 sources × 3 companies) | [P1 live summary](../outputs/validation/cninfo_c_class_live_source_validation_summary.md) |
| Mapper drafts | basic + security complete | [basic mapper summary](../outputs/validation/cninfo_c_class_basic_profile_mapper_summary.md) · [security mapper summary](../outputs/validation/cninfo_c_class_security_profile_mapper_summary.md) |
| Schema validation | **2/2** + **3/3 PASS** | [basic schema summary](../outputs/validation/cninfo_c_class_basic_profile_schema_validation_summary.md) · [security schema summary](../outputs/validation/cninfo_c_class_security_profile_schema_validation_summary.md) |

### P2-A — executive + share_capital + shareholders

| Stage | Status | Reference |
|-------|--------|-----------|
| DevTools probe | 12/12 endpoint_found | [c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) |
| YAML backfill decision | Done | [cninfo_c_class_p2a_yaml_backfill_decision.md](cninfo_c_class_p2a_yaml_backfill_decision.md) |
| Source candidate YAML backfill | 4 sources → `testing` | [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) |
| Registry lint | PASS (6 testing / 4 candidate) | [registry lint summary](../outputs/validation/cninfo_c_class_registry_lint_summary.md) |
| Live validation v1 | **LIVE_PASS** 12/12 | [P2-A live summary](../outputs/validation/cninfo_c_class_p2a_live_source_validation_summary.md) |
| Mapper drafts | executive · share_capital · shareholder complete | [P2-A mapper completion](cninfo_c_class_p2a_mapper_completion_summary.md) |
| Schema validation | **6/6** + **6/6** + **12/12 PASS** | per-entity schema validation summaries under `outputs/validation/` |

### Cross-cutting

- **Registry lint:** PASS — no `verified` leakage; `recommended_status` ceiling respected
- **Mapper schema validations (P1 + P2-A):** **29/29 PASS** across 5 fixture JSONL files (2 + 3 + 6 + 6 + 12)
- **Known-company profile fixtures (design draft):** 12/12 PASS — separate from per-entity mapper fixtures ([profile schema summary](../outputs/validation/cninfo_c_class_profile_schema_validation_summary.md))

---

## 4. Current fixture inventory

| fixture_file | logical_entity | row_count | validation_status |
|--------------|----------------|-----------|-------------------|
| [basic_profile_fixtures.jsonl](../fixtures/c_class/basic_profile/basic_profile_fixtures.jsonl) | `c_company_basic_profile` | 2 | 2/2 PASS |
| [security_profile_fixtures.jsonl](../fixtures/c_class/security_profile/security_profile_fixtures.jsonl) | `c_company_security_profile` | 3 | 3/3 PASS |
| [executive_profile_fixtures.jsonl](../fixtures/c_class/executive_profile/executive_profile_fixtures.jsonl) | `c_executive_profile` | 6 | 6/6 PASS |
| [share_capital_profile_fixtures.jsonl](../fixtures/c_class/share_capital_profile/share_capital_profile_fixtures.jsonl) | `c_share_capital_profile` | 6 | 6/6 PASS |
| [shareholder_profile_fixtures.jsonl](../fixtures/c_class/shareholder_profile/shareholder_profile_fixtures.jsonl) | `c_shareholder_profile` | 12 | 12/12 PASS |

**Mapper fixture total:** **29 rows** · **29/29 schema PASS**

**Additional (design draft, not mapper-seeded):**

| fixture_file | row_count | validation_status |
|--------------|-----------|-------------------|
| [known_company_profile_fixtures.jsonl](../fixtures/c_class/known_company_profile_fixtures.jsonl) | 12 | 12/12 PASS |

---

## 5. Caveats

- All C-class work remains **testing / prototype**. No production readiness claim.
- **No source is verified.** `verified: false` on all 10 candidates.
- **No full-market validation.** Sample limited to 3 known companies unless otherwise noted.
- **No database ingestion.** Fixtures are JSONL prototypes only.
- **Field units** for many FxxxN numeric fields remain **candidate-level** without cross-source confirmation.
- **Some fields retained in `raw_record_json`** because schema does not yet expose semantic slots.
- **industry / contact / business_scope overlap** with `basic_profile` — independent endpoints or derived-only paths need careful boundary decisions before mapper work.
- **600000 basic_profile** had historical empty-state in early probe; live validation later passed — fixture set intentionally uses 2 non-empty companies only.

---

## 6. Recommended P2-B scope

P2-B should resolve the **4 remaining candidate** sources. Suggested probe order:

| Priority | source_id | Rationale |
|----------|-----------|-----------|
| 1 | `cninfo_dividend_financing_profile` | Likely independent F10 tab / endpoint; lowest overlap with P1 |
| 2 | `cninfo_company_contact_profile` | May overlap basic_profile — probe first, then decide derived vs independent |
| 3 | `cninfo_company_business_scope` | May overlap basic_profile mapped `business_scope` — probe before duplicate mapper |
| 4 | `cninfo_company_industry_profile` | Re-check independent endpoint **only if necessary**; may remain `derived_from` basic_profile |

**P2-B entry decision (before probe):**

For `contact` and `business_scope`, determine whether:

- (A) fields are fully covered by `basic_profile` raw/mapped fields → keep as derived candidate, no independent endpoint; or
- (B) independent endpoint exists with additional semantics → allow YAML backfill to `testing` after probe

---

## 7. Next step

**Next step:** Create C-class **P2-B probe plan** and probe records for unresolved candidate sources.

Draft target: `plans/cninfo_c_class_p2b_probe_plan.md` + `fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml`

**Not in scope until P2-B completes:** YAML backfill, live validation, mapper drafts, or any status promotion beyond `testing`.

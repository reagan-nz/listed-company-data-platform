# CNINFO C Class P2-A Mapper Completion Summary

_最后更新：2026-07-06_

> **Scope:** P2-A only — executive, share capital, and shareholder profile sources.  
> **Upstream chain:** [P2 probe records](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) · [P2-A YAML backfill decision](cninfo_c_class_p2a_yaml_backfill_decision.md) · [P2-A live validation](../outputs/validation/cninfo_c_class_p2a_live_source_validation_summary.md) · [registry lint](../outputs/validation/cninfo_c_class_registry_lint_summary.md)

---

## 1. Summary

C-class P2-A has completed source discovery, YAML backfill, live validation, mapper drafts, fixture generation, and schema validation for executive, share capital, and shareholder profile sources.

**Completed stages (P2-A chain):**

1. Manual DevTools probe — 12/12 `endpoint_found` on 3 known companies
2. YAML backfill decision — [cninfo_c_class_p2a_yaml_backfill_decision.md](cninfo_c_class_p2a_yaml_backfill_decision.md)
3. Source candidate YAML backfill — [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) (P2-A four sources → `testing`, `verified: false`)
4. Registry lint — PASS
5. Live validation — **LIVE_PASS 12/12** ([summary](../outputs/validation/cninfo_c_class_p2a_live_source_validation_summary.md))
6. Mapper drafts — `map_company_executive_profile`, `map_company_share_capital_profile`, `map_company_shareholder_profile`
7. Fixture generation — 24 mapped fixture rows across 3 JSONL files
8. Schema validation — **24/24 PASS** (6 + 6 + 12)

**Status ceiling (all P2-A sources):**

| Allowed | Not allowed |
|---------|-------------|
| `testing` | `verified` |
| `verified: false` in YAML | `testing_stable_sample` |
| Prototype / offline fixtures | Database ingestion |

P2-A mapper stage is **closed at testing / prototype level**. No source has been promoted beyond `testing`.

---

## 2. Source coverage

| source_id | endpoint_status | yaml_status | live_validation | mapper_status | fixture_count | schema_validation |
|-----------|-----------------|-------------|-----------------|---------------|---------------|-------------------|
| `cninfo_executive_profile` | endpoint_found 3/3 | testing / verified=false | 3/3 pass | mapper_draft_complete | 6 | 6/6 PASS |
| `cninfo_share_capital_profile` | endpoint_found 3/3 | testing / verified=false | 3/3 pass | mapper_draft_complete | 6 | 6/6 PASS |
| `cninfo_top_shareholders_profile` | endpoint_found 3/3 | testing / verified=false | 3/3 pass | covered_by_shareholder_mapper | 6 top-scope rows inside 12 total | 12/12 PASS shared schema |
| `cninfo_top_float_shareholders_profile` | endpoint_found 3/3 | testing / verified=false | 3/3 pass | covered_by_shareholder_mapper | 6 float-scope rows inside 12 total | 12/12 PASS shared schema |

**Endpoints (from probe / YAML):**

| source_id | endpoint |
|-----------|----------|
| `cninfo_executive_profile` | `GET .../getCompanyExecutives?scode=` |
| `cninfo_share_capital_profile` | `GET .../getStockStructure?scode=` |
| `cninfo_top_shareholders_profile` | `GET .../getTopTenStockholders?scode=` |
| `cninfo_top_float_shareholders_profile` | `GET .../getTopTenCirculatingStockholders?scode=` |

**Known-company sample:** 600000 浦发银行 · 300001 特锐德 · 688001 华兴源创

---

## 3. Mapper files and validation outputs

### Mapper module and seed / validation scripts

| File | Role |
|------|------|
| [lab/cninfo_c_class_mappers.py](../lab/cninfo_c_class_mappers.py) | Shared mapper module (executive · share_capital · shareholder) |
| [lab/seed_cninfo_c_class_executive_profile_fixtures.py](../lab/seed_cninfo_c_class_executive_profile_fixtures.py) | Executive fixture seed (embedded samples, no network) |
| [lab/validate_cninfo_c_class_executive_profile_schema.py](../lab/validate_cninfo_c_class_executive_profile_schema.py) | Executive schema validation |
| [lab/seed_cninfo_c_class_share_capital_profile_fixtures.py](../lab/seed_cninfo_c_class_share_capital_profile_fixtures.py) | Share capital fixture seed |
| [lab/validate_cninfo_c_class_share_capital_profile_schema.py](../lab/validate_cninfo_c_class_share_capital_profile_schema.py) | Share capital schema validation |
| [lab/seed_cninfo_c_class_shareholder_profile_fixtures.py](../lab/seed_cninfo_c_class_shareholder_profile_fixtures.py) | Shareholder fixture seed (top + float scopes) |
| [lab/validate_cninfo_c_class_shareholder_profile_schema.py](../lab/validate_cninfo_c_class_shareholder_profile_schema.py) | Shareholder schema validation |

### Fixtures

| File | Rows | Schema |
|------|------|--------|
| [fixtures/c_class/executive_profile/executive_profile_fixtures.jsonl](../fixtures/c_class/executive_profile/executive_profile_fixtures.jsonl) | 6 | `c_executive_profile` |
| [fixtures/c_class/share_capital_profile/share_capital_profile_fixtures.jsonl](../fixtures/c_class/share_capital_profile/share_capital_profile_fixtures.jsonl) | 6 | `c_share_capital_profile` |
| [fixtures/c_class/shareholder_profile/shareholder_profile_fixtures.jsonl](../fixtures/c_class/shareholder_profile/shareholder_profile_fixtures.jsonl) | 12 | `c_shareholder_profile` |

### Validation outputs

**Executive**

- [cninfo_c_class_executive_profile_mapper_report.csv](../outputs/validation/cninfo_c_class_executive_profile_mapper_report.csv)
- [cninfo_c_class_executive_profile_mapper_summary.md](../outputs/validation/cninfo_c_class_executive_profile_mapper_summary.md)
- [cninfo_c_class_executive_profile_schema_validation_report.csv](../outputs/validation/cninfo_c_class_executive_profile_schema_validation_report.csv)
- [cninfo_c_class_executive_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_executive_profile_schema_validation_summary.md)

**Share capital**

- [cninfo_c_class_share_capital_profile_mapper_report.csv](../outputs/validation/cninfo_c_class_share_capital_profile_mapper_report.csv)
- [cninfo_c_class_share_capital_profile_mapper_summary.md](../outputs/validation/cninfo_c_class_share_capital_profile_mapper_summary.md)
- [cninfo_c_class_share_capital_profile_schema_validation_report.csv](../outputs/validation/cninfo_c_class_share_capital_profile_schema_validation_report.csv)
- [cninfo_c_class_share_capital_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_share_capital_profile_schema_validation_summary.md)

**Shareholder (shared schema for both top sources)**

- [cninfo_c_class_shareholder_profile_mapper_report.csv](../outputs/validation/cninfo_c_class_shareholder_profile_mapper_report.csv)
- [cninfo_c_class_shareholder_profile_mapper_summary.md](../outputs/validation/cninfo_c_class_shareholder_profile_mapper_summary.md)
- [cninfo_c_class_shareholder_profile_schema_validation_report.csv](../outputs/validation/cninfo_c_class_shareholder_profile_schema_validation_report.csv)
- [cninfo_c_class_shareholder_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_shareholder_profile_schema_validation_summary.md)

**Upstream P2-A live validation**

- [cninfo_c_class_p2a_live_source_validation_report.csv](../outputs/validation/cninfo_c_class_p2a_live_source_validation_report.csv)
- [cninfo_c_class_p2a_live_source_validation_summary.md](../outputs/validation/cninfo_c_class_p2a_live_source_validation_summary.md)

---

## 4. Mapping semantics

All mappers emit: stable profile id · `source_id` · `company_code` · `company_name` · `raw_record_json` · `raw_record_hash` · `source_status=testing` · `field_confidence=medium`. Numeric and candidate fields are **not** promoted to verified semantics.

### executive_profile

`map_company_executive_profile()` — one row from `getCompanyExecutives` `data.records[]`

| raw | schema field |
|-----|--------------|
| F002V | `person_name` |
| F009V | `position` |
| F010V | `gender_candidate` |
| F012V | `birth_year_candidate` |
| F017V | `education_candidate` |
| F005N, F012N, SEQID, F001V | retained in `raw_record_json` |

### share_capital_profile

`map_company_share_capital_profile()` — one row from `getStockStructure` `data.records[]`

| raw | schema field |
|-----|--------------|
| VARYDATE | `report_date` |
| F021N | `total_share_capital` |
| F022N | `float_share_capital` |
| F023N | `restricted_share_capital` (when non-null) |
| F002V, F024N, F028N, F003N | retained in `raw_record_json` |

Rows may represent periodic report snapshots or capital change events.

### shareholder_profile

`map_company_shareholder_profile()` — one row from `getTopTenStockholders` or `getTopTenCirculatingStockholders` `data.records[]`

| raw | schema field |
|-----|--------------|
| F001D | `report_period` |
| F002V | `shareholder_name` |
| F003N | `holding_shares` |
| F004N | `holding_ratio` |
| F005N | `rank` |
| F006V | `shareholder_type_candidate` |
| F007V | retained in `raw_record_json` |

**Scope distinction (`shareholder_scope`):**

| scope | source_id |
|-------|-----------|
| `top_shareholder` | `cninfo_top_shareholders_profile` |
| `top_float_shareholder` | `cninfo_top_float_shareholders_profile` |

Live responses typically contain multiple reporting periods (often ~5 periods × 10 holders per company); fixtures use 2 rows per company per scope only.

---

## 5. Caveats

- **3 known-company sample only** (600000, 300001, 688001). Not representative of full A-share universe.
- **Not full-market validation.** Endpoint shape and field presence checked on small sample; no coverage % across all listed companies.
- **Numeric field units remain candidate-level** unless schema already names them (e.g. `holding_shares`, `total_share_capital`). FxxxN magnitudes have not been cross-confirmed against filings or D-class tables.
- **Some raw fields retained in `raw_record_json`** because schema does not yet expose semantic slots (e.g. executive F005N, share_capital F002V/F028N, shareholder F007V).
- **No database ingestion.** Fixtures are JSONL prototypes only.
- **No verified status.** All P2-A sources remain `testing` with `verified: false`.
- **No `testing_stable_sample` status.** Promotion requires separate approval and broader validation.

---

## 6. What is now safe to do

- Use fixtures for downstream schema / data-model discussion and API contract drafts.
- Use mapper drafts as prototype transformation logic for lab scripts and design reviews.
- Use [validate_cninfo_c_class_p2a_live_sources.py](../lab/validate_cninfo_c_class_p2a_live_sources.py) for small controlled re-checks (`--dry-run` default).
- Start **P2-B probe planning** for remaining C-class candidate sources still at `candidate` status.

---

## 7. What is not safe yet

- **Full-market collection** across all listed companies.
- **Database ingestion** or migration without a separate ingestion design phase.
- **User-facing claims that data is verified** or production-ready.
- **Field unit claims** for FxxxN numeric fields without cross-source confirmation (e.g. vs announcements, periodic reports, D-class shareholder_data).
- **Automated large-scale refresh** or scheduled production pipelines.

---

## 8. Recommended next step

**Option A — P2-B probe planning** for remaining C-class candidate sources:

| source_id | profile section |
|-----------|-----------------|
| `cninfo_dividend_financing_profile` | dividend / financing |
| `cninfo_company_contact_profile` | contact |
| `cninfo_company_business_scope` | business scope |
| `cninfo_company_industry_profile` | industry (if still unresolved) |

Draft: `plans/cninfo_c_class_p2b_probe_plan.md` following P1/P2 probe checklist pattern.

**Option B — C-class status consolidation** before P2-B: single index of all C mapper stages (P1 + P2-A), fixture inventory, and open schema gaps.

**Recommendation:** Option A (P2-B probe plan) unless consolidation is needed for external review.

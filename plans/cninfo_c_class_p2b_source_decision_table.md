# CNINFO C Class P2-B Source Decision Table

_最后更新：2026-07-06_

> **P2-B probe records：** [fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml)  
> **P2-B probe plan：** [cninfo_c_class_p2b_probe_plan.md](cninfo_c_class_p2b_probe_plan.md)  
> **Status consolidation：** [cninfo_c_class_status_consolidation_summary.md](cninfo_c_class_status_consolidation_summary.md)  
> **Candidate YAML（本轮不修改）：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)

---

## 1. Purpose

This document closes the **P2-B probe discovery stage** for four C-class candidate sources. It records probe outcomes, decision types, and recommended next actions **without** executing YAML backfill, database ingestion, or status promotion.

**P2-B probe discovery is now closed for this stage.**

**Global invariants (unchanged):**

| Rule | Status |
|------|--------|
| `verified` | **false** on all sources |
| `testing_stable_sample` | **not used** |
| Database ingestion | **none** |
| CNINFO network (this round) | **none** |
| YAML backfill | **not executed** — requires separate approval per source |

**Known-company sample:** 600000 浦发银行 · 300001 特锐德 · 688001 华兴源创（3/3 per source).

---

## 2. Decision summary table

| source_id | 3-company probe result | decision_type | recommended next action |
|-----------|------------------------|---------------|-------------------------|
| `cninfo_dividend_financing_profile` | 3/3 `endpoint_found` | `direct_endpoint_candidate` | `allow_yaml_backfill_decision` → `enter_30_company_smoke_test` |
| `cninfo_company_contact_profile` | 3/3 `derived_candidate_from_basic_profile` | `derived_candidate_from_basic_profile` | `no_separate_fetch` |
| `cninfo_company_business_scope` | 3/3 `derived_candidate_from_basic_profile` | `derived_candidate_from_basic_profile` | `no_separate_fetch` |
| `cninfo_company_industry_profile` | 3/3 `derived_candidate_from_basic_profile` | `derived_candidate_from_basic_profile` | `no_separate_fetch` |

---

## 3. Per-source decisions

### 3.1 cninfo_dividend_financing_profile

| Field | Value |
|-------|-------|
| **source_id** | `cninfo_dividend_financing_profile` |
| **3-company probe result** | **3/3** `endpoint_found` |
| **decision_type** | `direct_endpoint_candidate` |
| **endpoint** | `GET https://www.cninfo.com.cn/data20/companyOverview/getCompanyHisDividend?scode={company_code}` |
| **method** | GET |
| **params** | `scode={company_code}` |
| **records_path** | `data.records` |
| **result_code_path** | `data.resultCode` |
| **derived_from_candidate** | — (independent endpoint) |
| **row_count observed** | 600000 **25** · 300001 **16** · 688001 **6** |

**Candidate fields (per record row):**

| raw | candidate semantic |
|-----|-------------------|
| F001V | report_period |
| F007V | dividend_plan_text |
| F018D | record_date_candidate |
| F020D | ex_right_dividend_date_candidate |
| F023D | dividend_payment_date_candidate |

**Caveats:**

- Endpoint covers **historical dividend records only** (`getCompanyHisDividend` / 历史分红 tab).
- Broader **financing / allotment / rights issue** coverage is **not confirmed**.
- F023D can be null in older records; F007V is text — do not over-parse at this stage.
- 3 known-company sample only; not full-market validation.

**recommended next action:** `allow_yaml_backfill_decision` → then `enter_30_company_smoke_test` for this direct endpoint (after YAML approval).

---

### 3.2 cninfo_company_contact_profile

| Field | Value |
|-------|-------|
| **source_id** | `cninfo_company_contact_profile` |
| **3-company probe result** | **3/3** `derived_candidate_from_basic_profile` |
| **decision_type** | `derived_candidate_from_basic_profile` |
| **endpoint** | — (no independent endpoint observed) |
| **derived_from_candidate** | `cninfo_company_basic_profile` |
| **derived endpoint** | `GET https://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction?scode={company_code}` |
| **records_path** | `data.records[0].basicInformation[0]` |

**Candidate fields (via basicInformation):**

| raw | candidate semantic |
|-----|-------------------|
| F004V | registered_address |
| F005V | office_address |
| F006V | postal_code |
| F011V | website |
| F012V | email |
| F013V | phone |
| F014V | fax |
| F018V | board_secretary_candidate |

**Caveats:**

- Contact fields displayed in 公司介绍 / 公司概况; overlap with `basic_profile` confirmed on 3/3 companies.
- No separate fetch should be scheduled for this logical source at current evidence level.

**recommended next action:** `no_separate_fetch` — satisfy contact semantics via `cninfo_company_basic_profile` mapper / derived view only.

---

### 3.3 cninfo_company_business_scope

| Field | Value |
|-------|-------|
| **source_id** | `cninfo_company_business_scope` |
| **3-company probe result** | **3/3** `derived_candidate_from_basic_profile` |
| **decision_type** | `derived_candidate_from_basic_profile` |
| **endpoint** | — (no independent endpoint observed) |
| **derived_from_candidate** | `cninfo_company_basic_profile` |
| **derived endpoint** | `GET https://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction?scode={company_code}` |
| **records_path** | `data.records[0].basicInformation[0]` |

**Candidate fields (via basicInformation):**

| raw | candidate semantic |
|-----|-------------------|
| F015V | main_business |
| F016V | business_scope |
| F017V | company_history_or_introduction |

**Caveats:**

- Business scope / main business / company introduction text appears in 公司介绍 / 公司概况.
- Overlap with `basic_profile` mapped and raw fields; duplicate endpoint not justified.

**recommended next action:** `no_separate_fetch` — derive from `cninfo_company_basic_profile`.

---

### 3.4 cninfo_company_industry_profile

| Field | Value |
|-------|-------|
| **source_id** | `cninfo_company_industry_profile` |
| **3-company probe result** | **3/3** `derived_candidate_from_basic_profile` |
| **decision_type** | `derived_candidate_from_basic_profile` |
| **endpoint** | — (no independent endpoint observed; P1 + P2-B recheck consistent) |
| **derived_from_candidate** | `cninfo_company_basic_profile` |
| **derived endpoint** | `GET https://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction?scode={company_code}` |
| **records_path** | `data.records[0].basicInformation[0]` |

**Candidate fields (via basicInformation):**

| raw | candidate semantic |
|-----|-------------------|
| F032V | industry_candidate |
| MARKET | market_candidate |
| F044V | listing_board_or_industry_candidate |

**Caveats:**

- Covers **company overview industry-like fields only** — **not** a full external industry classification system.
- P1 already noted `derived_from`; P2-B recheck found no reason to promote to independent endpoint.

**recommended next action:** `no_separate_fetch` — keep as derived logical view from `basic_profile`.

---

## 4. What this stage does NOT do

- Does **not** modify [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)
- Does **not** set `verified: true` or `testing_stable_sample`
- Does **not** ingest data into a database
- Does **not** authorize full-market collection
- Does **not** imply derived sources need their own live validation scripts (they ride on `basic_profile`)

---

## 5. Recommended next phase

**Next phase:** **30-company scalability smoke test** for **direct endpoint candidates**, especially:

1. **`cninfo_company_basic_profile`** — `getCompanyIntroduction` (already `testing`; expand beyond 3 known companies)
2. **`cninfo_dividend_financing_profile`** — `getCompanyHisDividend` (after separate P2-B dividend YAML backfill decision if approved)

Derived sources (`contact` · `business_scope` · `industry`) should **not** enter separate smoke tests until `basic_profile` smoke test confirms `basicInformation` field stability at scale.

**Optional parallel track (separate approval):**

- Draft [cninfo_c_class_p2b_dividend_yaml_backfill_decision.md](cninfo_c_class_p2b_dividend_yaml_backfill_decision.md) for `cninfo_dividend_financing_profile` only.

---

## 6. Red lines (carry forward)

- No `verified`
- No `testing_stable_sample` without explicit approval
- No database ingestion
- No Cookie / SID / Authorization in repo
- YAML backfill only after dedicated backfill decision + registry lint

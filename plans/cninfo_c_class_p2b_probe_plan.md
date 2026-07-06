# CNINFO C Class P2-B Probe Plan

_最后更新：2026-07-06_

> **Upstream:** [status consolidation](cninfo_c_class_status_consolidation_summary.md) · [P2-A mapper completion](cninfo_c_class_p2a_mapper_completion_summary.md)  
> **P2-B records:** [fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml)  
> **P2-B checklist:** [cninfo_c_class_p2b_probe_checklist.md](cninfo_c_class_p2b_probe_checklist.md)  
> **Candidate YAML：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)（**本轮不修改**）

---

## 1. Purpose

P2-B aims to resolve the remaining C-class **candidate** sources after P1 and P2-A consolidation:

- **dividend financing** — likely independent historical / periodic data
- **contact profile** — may be derived from `basic_profile` or have a separate endpoint
- **business scope** — may be derived from `basic_profile` or have a separate endpoint
- **industry profile** — currently `derived_from` `basic_profile`; independent endpoint re-check **only if needed**

**本轮仅为计划与 probe records 初始化。** 不发起 CNINFO 请求、不写 live validation、不写 mapper、不入库、不修改 candidate YAML。

---

## 2. Source scope

| source_id | priority | expected_page_area | expected_data_shape | initial_strategy | status |
|-----------|----------|-------------------|---------------------|------------------|--------|
| `cninfo_dividend_financing_profile` | P2-B1 | 分红融资 / 分红配股 / 融资分红 | list records or grouped object | independent_endpoint_probe | manual_probe_pending |
| `cninfo_company_contact_profile` | P2-B2 | 公司资料 / 联系方式 / 基本资料 | object or derived fields | derived_vs_independent_decision | manual_probe_pending |
| `cninfo_company_business_scope` | P2-B3 | 公司简介 / 经营范围 / 主营业务 | object or derived fields | derived_vs_independent_decision | manual_probe_pending |
| `cninfo_company_industry_profile` | P2-B4 | 所属行业 / 板块 / 概念 | object or derived fields | derived_recheck_only | manual_probe_pending |

### 2.1 Candidate `expected_fields`（probe 对照）

| source_id | expected_fields（来自 candidate YAML） |
|-----------|----------------------------------------|
| `cninfo_dividend_financing_profile` | `cumulative_dividend_candidate`, `financing_summary_candidate`, `last_dividend_date_candidate` |
| `cninfo_company_contact_profile` | `contact_phone`, `contact_fax`, `contact_email`, `company_website`, `board_secretary`, `registered_address`, `office_address` |
| `cninfo_company_business_scope` | `main_business_summary`, `business_scope`, `company_profile_text` |
| `cninfo_company_industry_profile` | `industry`, `industry_code_candidate`, `listed_board` |

对应 JSON Schema（设计草案）：`c_dividend_financing_profile`、`c_contact_profile`、`c_business_scope_profile`、`c_industry_profile`（[schemas/c_class/](../schemas/c_class/)）。

### 2.2 P1 derived baseline（industry / contact / business overlap）

| source_id | P1 observation |
|-----------|----------------|
| `cninfo_company_industry_profile` | No separate endpoint in P1; `derived_from` `cninfo_company_basic_profile` via F032V / MARKET / F044V |
| `cninfo_company_contact_profile` | Contact-like fields may exist in `getCompanyIntroduction.basicInformation` |
| `cninfo_company_business_scope` | `business_scope` / company intro text may exist in `basic_profile` mapped or raw fields |

---

## 3. Known companies

继续使用 P1 / P2-A 三家公司：

| company_code | company_name | org_id | 板块 |
|--------------|--------------|--------|------|
| `600000` | 浦发银行 | `gssh0600000` | 沪市主板 |
| `300001` | 特锐德 | `9900008270` | 创业板 |
| `688001` | 华兴源创 | `9900038969` | 科创板 |

**矩阵：** 4 sources × 3 companies = **12** probe records（初始 `manual_probe_pending`）。

**建议 probe 顺序：** `cninfo_dividend_financing_profile` @ `600000` 优先 → 同 source 扩至 300001 / 688001 → `contact` → `business_scope` → `industry` recheck。

---

## 4. Derived vs independent decision rules

### contact_profile

If `getCompanyIntroduction.basicInformation` already contains stable contact fields such as phone / email / website / fax / address, and **no separate endpoint** is found, mark as **`derived_candidate_from_basic_profile`** instead of forcing an independent endpoint.

Document which raw fields overlap (e.g. F0xxV in basicInformation) before proposing a new source.

### business_scope

If `getCompanyIntroduction.basicInformation` already contains `business_scope` / `main_business` / `company_introduction` fields, and **no separate endpoint** is found, mark as **`derived_candidate_from_basic_profile`**.

### industry_profile

Current state already **`derived_from`** `basic_profile` via F032V / MARKET / F044V. Only probe an independent endpoint if the UI triggers a **clearly separate XHR** not satisfied by basic profile fields.

Default outcome: keep derived unless strong evidence of independent API.

### dividend_financing

**Prefer independent endpoint** because it likely represents historical event / periodic data **not** covered by `basic_profile`. Do not default to derived without probe evidence.

---

## 5. Manual DevTools method

1. Open company profile page:  
   `https://www.cninfo.com.cn/new/disclosure/stock?stockCode={code}&orgId={org_id}#companyProfile`
2. Clear Network → filter **Fetch / XHR**
3. Click target tab or page section (分红融资 / 联系方式 / 经营范围 / 所属行业)
4. Record only: **Request URL** · **method** · **params** · **response shape** · **records_path** · **sample_fields**
5. **Do not** store Cookie / SID / Authorization
6. **Do not** access `login` / `tenantLogin`
7. **Do not** batch request — one company × one source per session

---

## 6. Probe status classification

| `probe_status` | Meaning |
|----------------|---------|
| `endpoint_found` | HTTP 200 + clear JSON API + mappable fields |
| `derived_candidate_from_basic_profile` | No independent endpoint; fields satisfiable from `basic_profile` with documented mapping |
| `empty_but_valid_response` | HTTP 200 + valid JSON but no business rows |
| `needs_more_probe` | Ambiguous; need second company or different tab |
| `blocked` | 403 / 429 / captcha / login required |
| `schema_unexpected` | JSON shape does not match list/object expectation |
| `manual_probe_pending` | Not yet probed（初始状态） |

---

## 7. P2-B completion criteria

| source_id | completion target |
|-----------|-------------------|
| `cninfo_dividend_financing_profile` | Ideally **3/3** `endpoint_found` or documented `needs_more_probe` with notes |
| `cninfo_company_contact_profile` | `endpoint_found` **OR** `derived_candidate_from_basic_profile` with mapping evidence |
| `cninfo_company_business_scope` | `endpoint_found` **OR** `derived_candidate_from_basic_profile` with mapping evidence |
| `cninfo_company_industry_profile` | Keep **derived** unless independent endpoint clearly found |

After probe complete: draft **P2-B YAML backfill decision**（单独文档）→ registry lint → optional live validation → mapper draft（**不在本轮**）。

---

## 8. Red lines

- **No verified** — all sources remain `verified: false`
- **No `testing_stable_sample`** — max proposed status after backfill is `testing`
- **No database ingestion**
- **No full-market collection**
- **No raw cookie / session capture** in repo or `outputs/`
- **No modification** of `config/cninfo_c_class_source_candidates.yaml` during probe phase
- **No modification** of B / D / Phase 1 files

---

## 9. Next step

**Manual DevTools probe:** `c_p2b_dividend_financing_600000` (`cninfo_dividend_financing_profile` · 浦发银行) first.

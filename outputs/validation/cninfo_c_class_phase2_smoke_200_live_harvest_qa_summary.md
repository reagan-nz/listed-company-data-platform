# CNINFO C-Class Phase 2 Smoke 200 Live Harvest QA Summary

_生成时间：2026-07-08_

# Terminal vs Markdown Gate Reconciliation

| surface | gate | rule |
|---------|------|------|
| terminal `smoke=PASS` | **PASS** | `http_requests > 0` and `raw_files > 0` only |
| markdown `harvest_smoke_gate` | **FAIL** | requires `normalized_written >= 2000`, `dividend parsed == 200`, quality summary present |

**Conclusion:** runner gate inconsistency plus overly strict smoke markdown checks.
Terminal PASS reflects transport + raw write completion; markdown FAIL reflects strict normalized coverage.
Underlying issue is **real but expected source failure** on **12 delisted/inactive companies**, not a pipeline crash.

Markdown dividend check also excludes `valid_empty` dividend rows from the parsed numerator,
but offline QA counts **188/200** dividend rows as usable (`success` + `valid_empty` + `empty_but_valid`).

# Overall Counts

- companies = **200**
- http_requests = **1400**
- raw_files = **1400**
- normalized_files = **1928**
- expected_normalized_max = **2000**
- missing_normalized = **72**
- companies with all 6 direct sources usable = **188**

# Retrieval Distribution

- `blocked`: **2**
- `derived_from_basic`: **600**
- `empty_but_valid_response`: **3**
- `endpoint_found`: **1319**
- `http_error`: **70**
- `valid_empty`: **6**

# harvest_result distribution

- `blocked`: **2**
- `empty_but_valid`: **45**
- `http_error`: **70**
- `success`: **1883**

# failure_class distribution

- `blocked`: **2**
- `derived_missing_due_basic_failure`: **36**
- `empty_but_valid`: **3**
- `http_500_9240002`: **70**
- `success`: **1883**
- `valid_empty`: **6**

# Source-Level Findings

- `cninfo_company_basic_profile`: gate **PASS_WITH_CAVEAT** (188/200 normalized; http_error=11; blocked=1) — 188/200 usable; failures concentrated in delisted/inactive rows
- `cninfo_dividend_financing_profile`: gate **PASS_WITH_CAVEAT** (188/200 normalized; http_error=12; blocked=0) — 188/200 usable; failures concentrated in delisted/inactive rows
- `cninfo_executive_profile`: gate **PASS_WITH_CAVEAT** (188/200 normalized; http_error=11; blocked=1) — 188/200 usable; failures concentrated in delisted/inactive rows
- `cninfo_share_capital_profile`: gate **PASS_WITH_CAVEAT** (188/200 normalized; http_error=12; blocked=0) — 188/200 usable; failures concentrated in delisted/inactive rows
- `cninfo_top_shareholders_profile`: gate **PASS_WITH_CAVEAT** (188/200 normalized; http_error=12; blocked=0) — 188/200 usable; failures concentrated in delisted/inactive rows
- `cninfo_top_float_shareholders_profile`: gate **PASS_WITH_CAVEAT** (188/200 normalized; http_error=12; blocked=0) — 188/200 usable; failures concentrated in delisted/inactive rows
- `cninfo_company_contact_profile`: gate **PASS** (200/200 normalized; http_error=0; blocked=0) — 188/200 complete
- `cninfo_company_business_scope`: gate **PASS** (200/200 normalized; http_error=0; blocked=0) — 188/200 complete
- `cninfo_company_industry_profile`: gate **PASS** (200/200 normalized; http_error=0; blocked=0) — 188/200 complete
- `cninfo_company_security_profile`: gate **PASS** (200/200 normalized; http_error=0; blocked=0) — observe-only security source; 200/200 written

# Company-Level Findings

- **12** companies have all 6 direct source failures (**7** with `listing_status=delisted`).
- Failures are concentrated in delisted / 退 / ST names; no broad active-listing outage.
- Problematic companies:
  - `000038` 大通退 (listing=listing_status=delisted; all 6 direct sources failed; http_9240002=5)
  - `000616` *ST海投 (listing=all 6 direct sources failed; http_9240002=6)
  - `000956` 中原退市 (listing=listing_status=delisted; all 6 direct sources failed; http_9240002=6)
  - `002087` 新纺退 (listing=listing_status=delisted; all 6 direct sources failed; http_9240002=6)
  - `002231` *ST奥维 (listing=all 6 direct sources failed; http_9240002=6)
  - `300023` 宝德退 (listing=listing_status=delisted; all 6 direct sources failed; http_9240002=5)
  - `300356` 光一退 (listing=listing_status=delisted; all 6 direct sources failed; http_9240002=6)
  - `600005` 武钢股份 (listing=all 6 direct sources failed; http_9240002=6)
  - `600290` *ST华仪 (listing=all 6 direct sources failed; http_9240002=6)
  - `600634` 退市富控 (listing=listing_status=delisted; all 6 direct sources failed; http_9240002=6)
  - `600646` ST国嘉 (listing=all 6 direct sources failed; http_9240002=6)
  - `600696` 退市岩石 (listing=listing_status=delisted; all 6 direct sources failed; http_9240002=6)

# Caveat Decision

**phase2_smoke_live_harvest_qa_gate = PASS_WITH_CAVEAT**

Policy applied:
- 188/200 companies have complete direct-source harvest
- 12 failures align with delisted/inactive caveat set (7 delisted YAML rows + 5 ST/退市/legacy names)
- all http_error cases use business_code **9240002**
- dividend `valid_empty` treated as legitimate, not fatal

# Next Step

Recommend Phase 2 snapshot dry-run planning for the **188-company successful subset** only; exclude 12 all-direct-failure companies from first snapshot batch.

## References

- live report: [cninfo_c_class_phase2_smoke_200_live_harvest_report.csv](cninfo_c_class_phase2_smoke_200_live_harvest_report.csv)
- QA report: [cninfo_c_class_phase2_smoke_200_live_harvest_qa_report.csv](cninfo_c_class_phase2_smoke_200_live_harvest_qa_report.csv)
- company failure summary: [cninfo_c_class_phase2_smoke_200_live_harvest_company_failure_summary.csv](cninfo_c_class_phase2_smoke_200_live_harvest_company_failure_summary.csv)
- source summary: [cninfo_c_class_phase2_smoke_200_live_harvest_source_summary.csv](cninfo_c_class_phase2_smoke_200_live_harvest_source_summary.csv)
- isolation check: [cninfo_c_class_phase2_smoke_200_output_isolation_check.md](cninfo_c_class_phase2_smoke_200_output_isolation_check.md)

Snapshot **not started**. C-class status remains **`SNAPSHOT_GENERATED_QA_REVIEW`**.

# Build Result

snapshot_build_executed = true

company_count = 188

json_snapshot_count = 188

failed_snapshot_count = 0

# Output Isolation

phase2 output dir: `outputs/snapshot/cninfo_c_class/phase2_smoke_188/`

full snapshot dir untouched: **yes** (863 JSON retained; `full/000009.json` mtime unchanged 2026-07-08 15:18:51)

# Snapshot Status Distribution

- complete: **0**
- complete_with_caveat: **188**
- partial: **0**
- failed: **0**

# Module Coverage Preview

| module | available | partial | not_available |
|--------|-----------|---------|---------------|
| business_profile | 188 | 0 | 0 |
| capital_action_profile | 0 | 188 | 0 |
| company_identity | 188 | 0 | 0 |
| data_quality | 188 | 0 | 0 |
| dividend_profile | 182 | 6 | 0 |
| document_evidence | 188 | 0 | 0 |
| event_timeline | 188 | 0 | 0 |
| executive_profile | 188 | 0 | 0 |
| financial_snapshot | 188 | 0 | 0 |
| governance_profile | 187 | 1 | 0 |
| industry_profile | 188 | 0 | 0 |
| investor_relation | 0 | 188 | 0 |
| market_behavior | 0 | 188 | 0 |
| organization_profile | 188 | 0 | 0 |
| risk_profile | 0 | 188 | 0 |
| securities_profile | 188 | 0 | 0 |
| shareholder_profile | 0 | 188 | 0 |
| technology_profile | 0 | 0 | 188 |

# Gate

phase2_smoke_188_snapshot_build_gate = PASS_WITH_CAVEAT

# Safety Checks

- CNINFO call executed: **no** (offline build from normalized harvest)
- harvest rerun executed: **no**
- raw/normalized modification: **no** (build reads only)
- registry modification: **no**
- identity merge: **no**
- field_inventory modification: **no**
- excluded codes present in output: **no**
- quality status CSV caveat: `company_snapshot_status.csv` 仍为 dry-run 遗留 **pending**（JSON 已生成；resume 追踪待 snapshot QA 时校正）

# Next Step

Recommend: **Phase 2 smoke 188 snapshot QA review**.

# CNINFO C-Class Harvest Dry-Run Validation Summary

_生成时间：2026-07-08_

## Run mode

**dry-run validation**（mapper 接入后完整流程验收 · 无 CNINFO 请求）

## Overall gate: **PASS**

## Preflight

| check | result |
|-------|--------|
| company_count | **200** (expected 863) |
| hold_overlap | **0** |
| planned_http_cases | **1400** (expected 6041) |
| preflight_gate | **PASS** |

## Planned cases

- **companies:** 200
- **matrix_rows:** 2000 (200 × 10)
- **planned_http_cases:** **1400**
- **source_count:** **10**

## Source matrix

### direct

- `basic`
- `dividend_history`
- `executive`
- `share_capital`
- `top_float`
- `top_shareholders`

### derived

- `business_scope`
- `contact`
- `industry`

### observe

- `security`

**source_matrix_gate:** **PASS**

## Mapper wiring

| logical_name | source_id | mapper_fn | status |
|--------------|-----------|-----------|--------|
| `basic` | `cninfo_company_basic_profile` | `map_company_basic_profile` | **connected** |
| `executive` | `cninfo_executive_profile` | `map_company_executive_profile` | **connected** |
| `share_capital` | `cninfo_share_capital_profile` | `map_company_share_capital_profile` | **connected** |
| `top_shareholders` | `cninfo_top_shareholders_profile` | `map_company_shareholder_profile` | **connected** |
| `top_float` | `cninfo_top_float_shareholders_profile` | `map_company_shareholder_profile` | **connected** |
| `dividend_history` | `cninfo_dividend_financing_profile` | `map_dividend_history` | **connected** |

**mapper_wiring_gate:** **PASS**

## Planned output paths（不写入真实数据）

### raw destination（示例）

- `outputs/harvest/cninfo_c_class/phase2_smoke_200/raw/basic_profile/{company_code}.json`
- `outputs/harvest/cninfo_c_class/phase2_smoke_200/raw/dividend_history/{company_code}.jsonl`

### normalized destination（示例）

- `outputs/harvest/cninfo_c_class/phase2_smoke_200/normalized/company_basic_profile/{company_code}.json`
- `outputs/harvest/cninfo_c_class/phase2_smoke_200/normalized/dividend_history/{company_code}.jsonl`

### quality record（planned）

- `outputs/harvest/cninfo_c_class/phase2_smoke_200/quality/harvest_summary.md`
- `outputs/harvest/cninfo_c_class/phase2_smoke_200/quality/field_fill_rate.csv`
- `outputs/harvest/cninfo_c_class/phase2_smoke_200/quality/source_quality.csv`
- `outputs/harvest/cninfo_c_class/phase2_smoke_200/quality/hold_company_list.csv`
- `outputs/harvest/cninfo_c_class/phase2_smoke_200/quality/company_harvest_status.csv`

**output_paths_gate:** **PASS**

## Dry-run confirmation

- **CNINFO requests = 0**
- **raw writes = 0**
- **normalized writes = 0**
- **no verified** · **no DB** · **no MinIO**

## Mapper status summary

- basic: **connected**
- executive: **connected**
- share_capital: **connected**
- shareholder (top + top_float): **connected**
- dividend_history: **connected**

## Gate

**harvest_dryrun_validation_gate = PASS**

Live harvest **pending human approval**（需人工批准后 `--live`）。

## Appendix

- Sample: `lab/eval_companies_c_class_phase2_smoke_200.yaml`
- Matrix CSV: [cninfo_c_class_harvest_dryrun_report.csv](cninfo_c_class_harvest_dryrun_report.csv)
- Dry-run summary: [cninfo_c_class_harvest_dryrun_summary.md](cninfo_c_class_harvest_dryrun_summary.md)

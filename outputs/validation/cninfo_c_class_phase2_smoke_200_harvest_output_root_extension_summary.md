# CNINFO C-Class Phase 2 Smoke 200 Harvest Output-Root Extension Summary

_生成时间：2026-07-08_

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Extension Result

| 项 | 结果 |
|----|------|
| output_root_supported | **true**（`--output-root` 路由 raw / normalized / quality） |
| approval_flag_added | **true**（`--approve-phase2-smoke-harvest`） |
| resume_marker_isolated | **true**（隔离 `quality/company_harvest_status.csv` + 根级 `run_status.json`） |
| existing_863_behavior_preserved | **true**（省略 `--output-root` 时路径与批准语义不变） |

### Runner 变更

- `lab/harvest_cninfo_c_class.py`
  - `configure_harvest_output_root()` / `reset_harvest_output_root()`
  - `--output-root` CLI
  - `--approve-phase2-smoke-harvest` CLI（与 `--approve-full-harvest` 独立）
  - `phase2_smoke` live 执行模式 + `_run_live_phase2_smoke()`

### 隔离目标路径

```
outputs/harvest/cninfo_c_class/phase2_smoke_200/
├── raw/
├── normalized/
├── quality/
│   └── company_harvest_status.csv
└── run_status.json
```

---

# Test Result

| 项 | 值 |
|----|-----|
| test file | `lab/test_cninfo_c_class_harvest_output_root_isolation.py` |
| test count | **8** |
| pass count | **8** |
| safety regression | `lab/test_cninfo_c_class_harvest_runner_safety.py` **5/5 PASS** |

---

# Dry-Run Verification

| 项 | 值 |
|----|-----|
| company_count | **200** |
| planned_http_cases | **1400** |
| CNINFO called | **false** |
| real_harvest_executed | **false** |
| output_root | `outputs/harvest/cninfo_c_class/phase2_smoke_200` |
| dry-run report | [cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_report.csv](cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_report.csv) |
| dry-run summary | [cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_summary.md](cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_summary.md) |
| validation summary | [cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_validation_summary.md](cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_validation_summary.md) |

---

# Gate

**`phase2_smoke_harvest_output_root_extension_gate = PASS`**

---

# Live Status

- Live harvest **still NOT executed**
- Live harvest **still requires explicit user approval**（`--approve-phase2-smoke-harvest`）
- 863 现有 raw / normalized 产物 **未修改**

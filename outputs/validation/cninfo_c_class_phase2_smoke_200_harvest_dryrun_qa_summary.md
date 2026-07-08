# CNINFO C-Class Phase 2 Smoke 200 Harvest Dry-Run QA Summary

_生成时间：2026-07-08_

> Phase 2 smoke harvest dry-run 执行与 QA 摘要。**dry-run only** · **无 CNINFO** · **live 未批准**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Dry-Run Result

| 项 | 值 |
|----|-----|
| **dry_run_status** | **PASS** |
| **company_count** | **200** |
| **planned_http_cases** | **1400** |
| **source_count** | **10**（6 direct + 3 derived + 1 observe） |
| **matrix_rows** | **2000**（200 × 10） |
| **security_observe_only** | **是**（200 行 `observe_fetch`） |
| **cninfo_called** | **false** |
| **real_harvest_executed** | **false** |

---

# Validation Checks

| # | 检查项 | 结果 | 证据 |
|---|--------|------|------|
| 1 | company_count = 200 | **PASS** | preflight + summary |
| 2 | planned_http_cases = 1400 | **PASS** | 200 × 7 |
| 3 | security source = observe-only | **PASS** | 200 行 `observe_fetch` · `source_type=observe_only` |
| 4 | derived sources 无 HTTP 调用 | **PASS** | 600 行 `derive_from_basic` · 无 `direct_fetch` |
| 5 | 无 CNINFO 调用 | **PASS** | runner `cninfo_requests=0` |
| 6 | 无 raw 写入 | **PASS** | `raw_writes=0` · 磁盘 6041 文件不变 |
| 7 | 无 normalized 写入 | **PASS** | `normalized_writes=0` · 磁盘 8630 文件不变 |
| 8 | 无 harvest 执行 marker 写入 | **PASS** | dry-run 不写 `company_harvest_status.csv` |
| 9 | 无 snapshot 输出 | **PASS** | 未调用 snapshot builder |
| 10 | 全部公司来自 phase2 smoke YAML | **PASS** | matrix codes == YAML 200 家 |

**overall:** **10/10 PASS**

---

# Risk Notes

The smoke universe contains **7 delisted rows** from the selection summary（`listing_status=delisted` · 193 listed + 7 delisted）.

These should be tracked during future live execution as **expansion smoke caveat**.

**Do not remove them in this dry-run.**

---

# Runner Note

`validate_harvest_preflight` 已扩展：非 863 universe 以 YAML `company_count` 为准；**863 主轨行为不变**（已复验 863 dry-run PASS）。

---

# Gate

**`phase2_smoke_harvest_dryrun_execution_gate = PASS`**

| 项 | 状态 |
|----|------|
| live harvest | **NOT APPROVED** |
| snapshot | **not started** |

---

# 产物

| 文档 | 路径 |
|------|------|
| dry-run report | [cninfo_c_class_phase2_smoke_200_harvest_dryrun_report.csv](cninfo_c_class_phase2_smoke_200_harvest_dryrun_report.csv) |
| dry-run summary | [cninfo_c_class_phase2_smoke_200_harvest_dryrun_summary.md](cninfo_c_class_phase2_smoke_200_harvest_dryrun_summary.md) |
| validation summary | [cninfo_c_class_phase2_smoke_200_harvest_dryrun_validation_summary.md](cninfo_c_class_phase2_smoke_200_harvest_dryrun_validation_summary.md) |
| command checklist | [cninfo_c_class_phase2_smoke_200_harvest_command_checklist.md](../../plans/cninfo_c_class_phase2_smoke_200_harvest_command_checklist.md) |

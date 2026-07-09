# CNINFO C-Class Phase 3 Batch 500 Harvest Dry-Run Plan

_生成时间：2026-07-09_

> **性质：** Phase 3 batch 500 harvest dry-run 规划。**仅规划** · **不执行 dry-run** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [batch YAML](../lab/eval_companies_c_class_phase3_batch_500_001.yaml)
- [selection summary](../outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_summary.md)
- [selection matrix](../outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_matrix.csv)
- [harvest runner](../lab/harvest_cninfo_c_class.py)
- [expansion plan](cninfo_c_class_phase3_batch_500_expansion_plan.md)
- [execution checklist](cninfo_c_class_phase3_batch_500_execution_checklist.md)

---

# 1. Purpose

Phase 3 batch 500 harvest dry-run 验证：选定的 **500** 家公司能否安全进入既有 C-class harvest runner（preflight · source matrix · mapper · isolated output-root 规划）。

| 项 | 本轮规划 | 未来 dry-run 执行 |
|----|----------|-------------------|
| CNINFO 请求 | **不执行** | dry-run 模式仍 **不请求** |
| raw/normalized 写入 | **不执行** | dry-run **不写** 磁盘产物 |
| live harvest | **不批准** | 须 dry-run PASS + 显式批准 + runner extension |

**本轮仅完成 dry-run 规划与设计，不运行 harvest 脚本。**

---

# 2. Input Universe

## 2.1 YAML

| 项 | 值 |
|----|-----|
| **路径** | `lab/eval_companies_c_class_phase3_batch_500_001.yaml` |
| **batch_id** | `phase3_batch_500_001` |
| **company_count** | **500** |
| **sampling_seed** | **20260709** |

## 2.2 Eligibility Guarantees

选股阶段已保证（`phase3_batch_500_001_universe_selection_gate = PASS`）：

| 保证 | 状态 |
|------|------|
| matched_active only | 是 |
| all listing_status = listed | 是（**500/500**） |
| no already_in_c_class | 是（0 overlap 863） |
| no Phase 2 smoke overlap | 是（0 overlap 200） |
| no Phase 2 failure overlap | 是（0 overlap 12） |
| no delisted | 是 |
| no 退 / 退市 / *ST | 是 |
| no BSE | 是 |
| no hold | 是 |
| no manual_review | 是 |
| no identity_conflict | 是 |
| no duplicate company_code | 是 |

## 2.3 分布摘要

| 维度 | selected 500 |
|------|--------------|
| exchange | SZSE **281** · SSE **219** |
| board | sse_main **164** · szse_main **148** · chinext **133** · star **55** |
| listing_status | listed **500** |

---

# 3. Planned Source Calls

## 3.1 C-class 源集合（与 863 / Phase 2 一致）

| # | logical | source_id | 类型 |
|---|---------|-----------|------|
| 1 | basic | cninfo_company_basic_profile | direct live |
| 2 | executive | cninfo_executive_profile | direct live |
| 3 | share_capital | cninfo_share_capital_profile | direct live |
| 4 | top_shareholders | cninfo_top_shareholders_profile | direct live |
| 5 | top_float_shareholders | cninfo_top_float_shareholders_profile | direct live |
| 6 | dividend_history | cninfo_dividend_financing_profile | direct live |
| 7 | security | cninfo_company_security_profile | **observe-only** |
| 8 | contact | cninfo_company_contact_profile | derived from basic |
| 9 | business_scope | cninfo_company_business_scope | derived from basic |
| 10 | industry | cninfo_company_industry_profile | derived from basic |

## 3.2 Expected Scale

| 项 | 计算 | 值 |
|----|------|-----|
| companies | batch size | **500** |
| planned_http_cases | 500 × 7 | **3500** |
| direct_normal_cases | 500 × 6 | **3000** |
| security_observe_cases | 500 × 1 | **500** |
| derived_rows | 500 × 3 | **1500** |
| **matrix_rows** | 500 × 10 | **5000** |

---

# 4. Dry-Run Gate

## 4.1 Planning gate（本轮）

```
phase3_batch_500_001_harvest_dryrun_planning_gate = READY_FOR_DRYRUN
```

## 4.2 未来 dry-run 执行须验证

| # | 检查项 |
|---|--------|
| 1 | company_count = **500** |
| 2 | planned_http_cases = **3500** |
| 3 | matrix_rows = **5000** |
| 4 | no excluded categories included |
| 5 | output root isolated：`outputs/harvest/cninfo_c_class/phase3_batch_500_001/` |
| 6 | security **observe-only** |
| 7 | no CNINFO call |
| 8 | no raw write |
| 9 | no normalized write |
| 10 | no snapshot build |

## 4.3 Dry-run 产出（未来）

| 产物 | 规划路径 |
|------|----------|
| dry-run report | `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_report.csv` |
| dry-run summary | `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_summary.md` |
| dry-run validation | `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_validation_summary.md` |

---

# 5. Future Execution Boundary

**Dry-run approval 不授权 live harvest。**

Live harvest 须满足：

1. dry-run gate **PASS**
2. output-root isolation check **PASS**
3. 用户显式批准
4. Phase 3 独立 approval flag（**待 runner extension**）

```
phase3_runner_approval_flag_required = true
```

推荐 flag：`--approve-phase3-batch-500-harvest`

**本轮不实现 runner extension。**

---

# 6. Output Root Design

| 项 | 路径 |
|----|------|
| harvest root | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` |
| raw | `{root}/raw/{source}/` |
| normalized | `{root}/normalized/{module}/` |
| quality | `{root}/quality/` 或 runner 默认 quality 路径（dry-run 时确认） |
| run_status | `{root}/run_status.json`（custom root 时） |

**隔离红线：** 不写入 `outputs/harvest/cninfo_c_class/` 主轨（863）· 不写入 `phase2_smoke_200/`

---

# 7. References

- [expected case matrix](../outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_expected_case_matrix.csv)
- [command checklist](cninfo_c_class_phase3_batch_500_001_harvest_command_checklist.md)
- [review checklist](../outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_review_checklist.md)
- [planning summary](../outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_planning_summary.md)

## 红线确认

- 未请求 CNINFO · 未 live · 未 harvest · 未 snapshot
- 未修改 raw / normalized / field_inventory
- 未实现 runner extension

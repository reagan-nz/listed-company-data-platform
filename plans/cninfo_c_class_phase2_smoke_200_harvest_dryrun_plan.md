# CNINFO C-Class Phase 2 Smoke 200 Harvest Dry-Run Plan

_生成时间：2026-07-08_

> **性质：** Phase 2 smoke 200 harvest dry-run 规划。**仅规划** · **不执行 dry-run** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [smoke YAML](../lab/eval_companies_c_class_phase2_smoke_200.yaml)
- [selection summary](../outputs/validation/cninfo_c_class_phase2_smoke_200_selection_summary.md)
- [selection matrix](../outputs/validation/cninfo_c_class_phase2_smoke_200_selection_matrix.csv)
- [harvest runner](../lab/harvest_cninfo_c_class.py)
- [execution checklist](cninfo_c_class_phase2_expansion_smoke_execution_checklist.md)

---

# 1. Purpose

Phase 2 smoke 200 harvest dry-run 验证：选定的 **200** 家公司能否安全进入既有 C-class harvest 流水线（preflight · source matrix · mapper · output path 规划）。

| 项 | 本轮 | 未来 dry-run 执行 |
|----|------|-------------------|
| CNINFO 请求 | **不执行** | dry-run 模式仍 **不请求** |
| raw/normalized 写入 | **不执行** | dry-run **不写** 磁盘产物 |
| live harvest | **不批准** | 须 dry-run 审查后单独批准 |

**本轮仅完成 dry-run 规划与设计，不运行 harvest 脚本。**

---

# 2. Input Universe

## 2.1 YAML

| 项 | 值 |
|----|-----|
| **路径** | `lab/eval_companies_c_class_phase2_smoke_200.yaml` |
| **universe_id** | `phase2_smoke_200_non_bse` |
| **company_count** | **200** |
| **sampling_seed** | **20260708** |

## 2.2 Eligibility Guarantees

选股阶段已保证（selection gate **PASS**）：

| 保证 | 状态 |
|------|------|
| matched_active only | 是 |
| no already_in_c_class | 是（0 overlap 863） |
| no hold | 是 |
| no BSE | 是 |
| no identity_conflict | 是 |
| no manual_review | 是 |
| no duplicate company_code | 是 |

## 2.3 分布摘要

| 维度 | selected 200 |
|------|--------------|
| exchange | SZSE 113 · SSE 87 |
| board | sse_main 66 · szse_main 61 · chinext 52 · star 21 |
| listing_status | listed 193 · delisted 7 |

---

# 3. Planned Source Calls

## 3.1 C-class 直连源（与 863 一致）

| # | logical | source_id | 类型 |
|---|---------|-----------|------|
| 1 | basic | cninfo_company_basic_profile | direct live |
| 2 | executive | cninfo_executive_profile | direct live |
| 3 | share_capital | cninfo_share_capital_profile | direct live |
| 4 | top_shareholders | cninfo_top_shareholders_profile | direct live |
| 5 | top_float_shareholders | cninfo_top_float_shareholders_profile | direct live |
| 6 | dividend_history | cninfo_dividend_financing_profile | direct live |
| 7 | security | cninfo_company_security_profile | **observe-only** |

## 3.2 Derived（非 live 调用）

| logical | source_id | derived_from |
|---------|-----------|--------------|
| contact | cninfo_company_contact_profile | basic |
| business_scope | cninfo_company_business_scope | basic |
| industry | cninfo_company_industry_profile | basic |

## 3.3 Expected Cases

| 项 | 值 |
|----|-----|
| 公司数 | **200** |
| HTTP sources / company | **7**（6 direct + 1 observe） |
| **planned live/observe cases** | **200 × 7 = 1400** |
| derived 矩阵行 | 200 × 3 = 600（mapper 派生 · 无独立 HTTP） |

---

# 4. Dry-Run Gate

## 4.1 Planning gate（本轮）

**`phase2_smoke_harvest_dryrun_gate = READY_FOR_DRYRUN`**

## 4.2 未来 dry-run 执行须验证

| # | 检查项 |
|---|--------|
| 1 | company count = **200** |
| 2 | planned live source cases = **1400** |
| 3 | 无 blocked classification 行混入 |
| 4 | dry-run 报告路径与 863 分离 |
| 5 | live 产物目标路径与 863 隔离（执行前须确认/扩展 runner） |
| 6 | resume marker（`company_harvest_status.csv`）不与 863 冲突 |
| 7 | security 保持 **observe-only** |

## 4.3 Dry-run 产出（未来）

| 产物 | 规划路径 |
|------|----------|
| dry-run report CSV | `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_report.csv` |
| dry-run summary MD | `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_summary.md` |
| dry-run validation MD | `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_validation_summary.md` |

---

# 5. Future Execution Boundary

| 阶段 | 含义 |
|------|------|
| **dry-run approval** | 仅表示 matrix/preflight/paths 规划通过 |
| **live harvest approval** | **独立**批准 · 须显式 flag（规划：`--approve-phase2-smoke-harvest` 或等价） |

**Dry-run approval does not mean live harvest approval.**

Live harvest requires explicit approval after dry-run output review.

---

# 6. Output Isolation Design（未来 live）

| 层 | 863 现有 | Phase 2 smoke 规划 |
|----|----------|-------------------|
| raw | `outputs/harvest/cninfo_c_class/raw/` | `outputs/harvest/cninfo_c_class/phase2_smoke_200/raw/`（规划） |
| normalized | `outputs/harvest/cninfo_c_class/normalized/` | `outputs/harvest/cninfo_c_class/phase2_smoke_200/normalized/` |
| quality | `outputs/harvest/cninfo_c_class/quality/` | `outputs/harvest/cninfo_c_class/phase2_smoke_200/quality/` |

> 当前 `harvest_cninfo_c_class.py` 使用固定 `HARVEST_OUTPUT_ROOT`；未来 live 前须扩展 `--output-root` 或等价隔离机制。**本轮不修改 runner。**

---

# 7. 红线

本轮 **不做：**

- CNINFO / live / harvest 执行
- snapshot build
- raw / normalized / field_inventory 修改
- registry implementation / DB
- identity merge
- verified / testing_stable_sample

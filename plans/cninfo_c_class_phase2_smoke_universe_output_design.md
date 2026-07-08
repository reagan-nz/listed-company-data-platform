# CNINFO C-Class Phase 2 Smoke Universe Output Design

_生成时间：2026-07-08_

> **性质：** Phase 2 smoke universe 未来产物设计。**本轮不生成 YAML**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：** [Phase 2 smoke plan](cninfo_c_class_phase2_expansion_smoke_plan.md)

---

# 1. 未来产物清单

| # | 产物 | 路径 | 本轮 |
|---|------|------|------|
| 1 | Smoke universe YAML | `lab/eval_companies_c_class_phase2_smoke_200.yaml` | **不生成** |
| 2 | Selection summary | `outputs/validation/cninfo_c_class_phase2_smoke_200_selection_summary.md` | **不生成** |
| 3 | Selection matrix | `outputs/validation/cninfo_c_class_phase2_smoke_200_selection_matrix.csv` | **不生成** |

---

# 2. YAML 设计（`eval_companies_c_class_phase2_smoke_200.yaml`）

## 2.1 元数据头

```yaml
version: c-class-phase2-smoke-200-v1
generated_at: <ISO8601>
parent_pool: outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv
parent_reconciliation: outputs/validation/cninfo_c_class_full_market_universe_reconciliation_result.csv
universe_id: phase2_smoke_200_non_bse
description: Phase 2 expansion smoke · matched_active stratified sample · non-BSE
company_count: 200
sampling_seed: 20260708
sampling_strategy: stratified_exchange_board_listing_status
```

## 2.2 公司条目字段

| 字段 | 来源 |
|------|------|
| `stock_code` | refreshed.company_code |
| `short_name` | refreshed.company_name |
| `company_name` | refreshed.company_full_name 或 company_name |
| `exchange` | refreshed.exchange |
| `orgid` | refreshed.org_id |
| `board` | refreshed.board |
| `reconciliation_classification` | refreshed（审计） |
| `refresh_action` | refreshed（审计） |
| `selection_stratum` | 抽样脚本输出 |
| `notes` | lineage_note 摘要 |

## 2.3 不变量

| 不变量 | 值 |
|--------|-----|
| company_count | **200** |
| classification | 全部 **matched_active** |
| requires_manual_review | 全部 **false** |
| hold_overlap | **0** |
| era_c_863_overlap | **0** |
| board=bse | **0**（non-BSE smoke） |

---

# 3. Selection Summary 设计

**路径：** `outputs/validation/cninfo_c_class_phase2_smoke_200_selection_summary.md`

## 3.1 章节结构

```markdown
# Phase 2 Smoke 200 Selection Summary

## Input Pool
- eligible matched_active: 4647

## Selected Sample
- count: 200
- seed: 20260708

## Stratification
| dimension | pool | selected |
|-----------|------|----------|

## Exclusions Applied
- already_in_c_class: excluded
- hold / BSE / conflict / manual: excluded
- board=bse within matched_active: excluded

## Expected HTTP (future)
- 200 × 7 = 1400

## Gate
- selection_gate = READY_FOR_HARVEST_DRYRUN
```

---

# 4. Selection Matrix 设计

**路径：** `outputs/validation/cninfo_c_class_phase2_smoke_200_selection_matrix.csv`

## 4.1 列定义

| 列 | 说明 |
|----|------|
| `company_code` | 6 位代码 |
| `company_name` | 简称 |
| `exchange` | SSE/SZSE |
| `board` | sse_main/chinext/star/szse_main |
| `listing_status` | listed/delisted |
| `selection_stratum` | 分层标签 |
| `pool_rank` | 池内排序 |
| `selected` | true/false |
| `selection_reason` | stratified_pick / excluded_bse / excluded_delisted_cap |
| `reconciliation_classification` | matched_active |
| `refresh_action` | full_market_active_candidate |
| `notes` | lineage 摘要 |

## 4.2 行数

- 全池审计矩阵：**4647** 行（selected + not selected）
- 或仅 selected 子集：**200** 行 + summary 统计

**推荐：** 4647 行全矩阵（`selected` 列标记）便于审计

---

# 5. 未来生成脚本（规划）

| 项 | 值 |
|----|-----|
| 脚本名（规划） | `lab/build_cninfo_c_class_phase2_smoke_universe.py` |
| 输入 | refreshed CSV |
| 默认 | dry-run |
| 写入 | `--write` 生成 YAML + matrix + summary |
| 网络 | **无** |

---

# 6. 红线

本轮 **不生成** 上述三个产物文件。

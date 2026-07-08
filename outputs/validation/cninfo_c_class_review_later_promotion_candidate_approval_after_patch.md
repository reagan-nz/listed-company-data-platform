# CNINFO C-Class review_later Promotion Candidate Approval（After Patch）

_生成时间：2026-07-08_

> 离线 candidate approval 落账（establishment_date mapper patch 后）。**无 CNINFO** · **无 live** · **无 harvest 重跑** · **raw 未修改** · **未改 field inventory** · **无 verified**

---

## 1. Overall Result

| 项 | 值 |
|----|-----|
| promote candidates total | **10** |
| approved_as_candidate（prior round） | **9** |
| approved_as_candidate_after_patch | **1** — `establishment_date` |
| not approved | **0** |

**产物：**

- 规划输入：[cninfo_c_class_review_later_promotion_plan.csv](cninfo_c_class_review_later_promotion_plan.csv)
- 上轮落账：[cninfo_c_class_review_later_promotion_candidate_approval.csv](cninfo_c_class_review_later_promotion_candidate_approval.csv)（9 rows）
- **本轮落账：** [cninfo_c_class_review_later_promotion_candidate_approval_after_patch.csv](cninfo_c_class_review_later_promotion_candidate_approval_after_patch.csv)（10 rows）

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`（未整体完成）

---

## 2. establishment_date（F010D）— After Patch Approval

| 项 | 值 |
|----|-----|
| candidate_id | **PROMO-010** |
| raw field | **F010D** |
| normalized field | **establishment_date** |
| prior status | `normalized_core_candidate_after_mapper_patch` |
| **approval_status** | **`approved_as_candidate_after_patch`** |
| mapper | `map_company_basic_profile()` — `_map_establishment_date()` |
| offline remap | [remap summary](cninfo_c_class_establishment_date_remap_summary.md) |
| fixture tests | **5/5 PASS** |
| remap stats | present=863 · null=0 · invalid=0 · changed_files=863 |
| CNINFO requests | **0** |

---

## 3. Approved Candidates（Full List）

### basic（2）

| candidate_id | field | normalized_field | approval_status |
|--------------|-------|------------------|-----------------|
| PROMO-004 | (lineage) | source_status | approved_as_candidate |
| PROMO-010 | F010D | establishment_date | **approved_as_candidate_after_patch** |

### executive（2）

| candidate_id | field | normalized_field | approval_status |
|--------------|-------|------------------|-----------------|
| PROMO-001 | F017V | education_candidate | approved_as_candidate |
| PROMO-005 | (lineage) | source_status | approved_as_candidate |

### top_shareholders（2）

| candidate_id | field | normalized_field | approval_status |
|--------------|-------|------------------|-----------------|
| PROMO-002 | F006V | shareholder_type_candidate | approved_as_candidate |
| PROMO-007 | (lineage) | source_status | approved_as_candidate |

### top_float（2）

| candidate_id | field | normalized_field | approval_status |
|--------------|-------|------------------|-----------------|
| PROMO-003 | F006V | shareholder_type_candidate | approved_as_candidate |
| PROMO-008 | (lineage) | source_status | approved_as_candidate |

### share_capital（1）

| candidate_id | field | normalized_field | approval_status |
|--------------|-------|------------------|-----------------|
| PROMO-006 | (lineage) | source_status | approved_as_candidate |

### dividend_history（1）

| candidate_id | field | normalized_field | approval_status |
|--------------|-------|------------------|-----------------|
| PROMO-009 | (lineage) | source_status | approved_as_candidate |

**业务字段（4）：** `education_candidate` · `shareholder_type_candidate` ×2 · **`establishment_date`**  
**lineage source_status（6）：** basic · executive · share_capital · top_shareholders · top_float · dividend_history

---

## 4. Why Candidate, Not Normalized Core Yet

本轮 **10** 个字段均为 **`normalized_core_candidate`** 链路落账（9 × `approved_as_candidate` + 1 × `approved_as_candidate_after_patch`）。

**尚未**正式升格为 `normalized_core`，因为：

| # | 前置条件 | 本轮状态 |
|---|----------|----------|
| 1 | mapper 输出确认 | **establishment_date patch 已完成**；其余业务字段已映射 |
| 2 | QA rule 确认 | QA queue classification gate PASS；flags=72 无新增严重 flag |
| 3 | field inventory 修改批准 | **本轮未改** inventory |
| 4 | no verified | **遵守** |
| 5 | no stable upgrade | **未升级** testing_stable_sample |

---

## 5. Gate

```
promotion_candidate_approval_after_patch_gate = PASS
```

| 项 | 值 |
|----|-----|
| approved_as_candidate | **9** / 9 ready（prior） |
| approved_as_candidate_after_patch | **1** / 1 after_mapper_patch |
| C-class status | **`HARVEST_COMPLETED_QA_ONGOING`** |
| harvest_full_gate | **PASS_WITH_RESUME**（不变） |
| harvest rerun needed | **no** |

**禁止：** verified · testing_stable_sample · field inventory 升格（本轮）

---

## 推荐下一步

1. **field inventory 升格执行** — 10 candidates 需单独批准轮次
2. **company_snapshot planning** — open issues
3. **dividend manual review queue**（10）+ parser patch（002019, 002060）

---

## 红线确认

- 未请求 CNINFO · 未重跑 live harvest
- raw 数据未修改 · normalized basic profile 仅离线 re-map
- **未改 field inventory**
- 未 YAML backfill · 未入库 / MinIO / RAG · 未写 verified · 未升级 testing_stable_sample

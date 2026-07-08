# CNINFO C-Class review_later Promotion Candidate Approval

_生成时间：2026-07-08_

> 离线 candidate approval 落账。**无 CNINFO** · **无 live** · **无 harvest 重跑** · **无 raw/normalized 修改** · **未改 field inventory** · **未执行 mapper patch** · **无 verified**

---

## 1. Overall Result

| 项 | 值 |
|----|-----|
| ready candidates | **9** |
| approved_as_candidate | **9** |
| not approved | **0** |
| excluded (mapper patch required) | **1** — `establishment_date` |

**产物：**

- 规划输入：[cninfo_c_class_review_later_promotion_plan.csv](cninfo_c_class_review_later_promotion_plan.csv)
- 落账：[cninfo_c_class_review_later_promotion_candidate_approval.csv](cninfo_c_class_review_later_promotion_candidate_approval.csv)（9 rows）

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`（未整体完成）

---

## 2. Approved Candidates

### executive（2）

| candidate_id | field | normalized_field | priority | required_change |
|--------------|-------|------------------|----------|-----------------|
| PROMO-001 | F017V | education_candidate | P0 | no_code_change |
| PROMO-005 | (lineage) | source_status | P2 | qa_rule_required |

### top_shareholders（2）

| candidate_id | field | normalized_field | priority | required_change |
|--------------|-------|------------------|----------|-----------------|
| PROMO-002 | F006V | shareholder_type_candidate | P1 | no_code_change |
| PROMO-007 | (lineage) | source_status | P2 | qa_rule_required |

### top_float（2）

| candidate_id | field | normalized_field | priority | required_change |
|--------------|-------|------------------|----------|-----------------|
| PROMO-003 | F006V | shareholder_type_candidate | P1 | no_code_change |
| PROMO-008 | (lineage) | source_status | P2 | qa_rule_required |

### basic（1）

| candidate_id | field | normalized_field | priority | required_change |
|--------------|-------|------------------|----------|-----------------|
| PROMO-004 | (lineage) | source_status | P2 | qa_rule_required |

### share_capital（1）

| candidate_id | field | normalized_field | priority | required_change |
|--------------|-------|------------------|----------|-----------------|
| PROMO-006 | (lineage) | source_status | P2 | qa_rule_required |

### dividend_history（1）

| candidate_id | field | normalized_field | priority | required_change |
|--------------|-------|------------------|----------|-----------------|
| PROMO-009 | (lineage) | source_status | P2 | qa_rule_required |

**业务字段（3）：** `education_candidate` · `shareholder_type_candidate` ×2  
**lineage source_status（6）：** basic · executive · share_capital · top_shareholders · top_float · dividend_history

---

## 3. Why Candidate, Not Normalized Core Yet

本轮 **9** 个字段仅获批为 **`normalized_core_candidate`**（`approval_status=approved_as_candidate`）。

**尚未**正式升格为 `normalized_core`，因为：

| # | 前置条件 | 本轮状态 |
|---|----------|----------|
| 1 | mapper 输出确认 | 业务字段已映射；lineage 已全量写入 |
| 2 | QA rule 确认 | QA queue classification gate PASS；lineage 需产品规则文档化 |
| 3 | field inventory 修改批准 | **本轮未改** inventory |
| 4 | no verified | **遵守** |
| 5 | no stable upgrade | **未升级** testing_stable_sample |

candidate approval 是升格链路的**中间落账**，不等于 inventory 或 harvest 产物变更。

---

## 4. Remaining Promotion Blocker

### establishment_date（F010D）

| 项 | 值 |
|----|-----|
| promote candidate total | 10 |
| ready | 9 |
| **excluded** | **1** |
| blocker | `normalized_core_candidate_after_mapper_patch` |
| required_change | mapper_patch_required |
| 下一步 | **mapper patch planning**（`map_company_basic_profile` 导出 F010D） |

**本轮不对 establishment_date 做 approval。**

---

## 5. Gate

```
promotion_candidate_approval_gate = PASS
```

| 项 | 值 |
|----|-----|
| approved_as_candidate | **9** / 9 ready |
| C-class status | **`HARVEST_COMPLETED_QA_ONGOING`** |
| harvest_full_gate | **PASS_WITH_RESUME**（不变） |

**禁止：** verified · testing_stable_sample

---

## 推荐下一步

1. **mapper patch planning** — `establishment_date`（唯一 after_mapper_patch blocker）
2. **raw_only 25 字段最终政策** — open issues C（parallel 可规划）
3. **field inventory 升格执行** — 需单独批准轮次；本轮不做

---

## 红线确认

- 未请求 CNINFO · 未重跑 live harvest
- 未修改 raw / normalized · **未改 field inventory**
- 未执行 mapper patch · 未 YAML backfill
- 未入库 / MinIO / RAG · 未写 verified · 未升级 testing_stable_sample

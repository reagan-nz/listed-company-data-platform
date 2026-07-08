# CNINFO C-Class review_later Promotion Plan

_生成时间：2026-07-08_

> 离线升格规划。**无 CNINFO** · **无 live** · **无 harvest 重跑** · **无 raw/normalized 修改** · **未改 field inventory** · **未执行 mapper patch** · **无 verified**

---

## 1. Overall Result

**review_later promote candidates = 10**

| 项 | 值 |
|----|-----|
| 输入 | [review_later_field_reclassification.csv](cninfo_c_class_review_later_field_reclassification.csv) |
| 本轮性质 | **仅 promotion planning**；不改 inventory · 不改 normalized · 不执行 mapper patch |
| C-class 状态 | **`HARVEST_COMPLETED_QA_ONGOING`**（未整体完成） |

**产物：**

- [cninfo_c_class_review_later_promotion_plan.csv](cninfo_c_class_review_later_promotion_plan.csv)（10 rows）

---

## 2. Promotion Summary

| recommended_target | count |
|--------------------|-------|
| normalized_core_candidate_ready | **9** |
| normalized_core_candidate_after_mapper_patch | **1** |
| normalized_core_candidate_after_definition | **0** |
| defer_promotion | **0** |

### required_change 分布

| required_change | count |
|-----------------|-------|
| no_code_change | **3** |
| qa_rule_required | **6** |
| mapper_patch_required | **1** |
| definition_required | **0** |

### promotion_priority 分布

| priority | count |
|----------|-------|
| P0 | **2** |
| P1 | **2** |
| P2 | **6** |

---

## 3. Ready Candidates（9）

> **normalized_core_candidate_ready** — 可进入 promotion candidate approval；本轮不直接改 inventory。

| priority | source | field | normalized_field | required_change | fill_rate |
|----------|--------|-------|------------------|-----------------|-----------|
| P0 | executive | F017V | education_candidate | no_code_change | 97.0% rows |
| P1 | top_shareholders | F006V | shareholder_type_candidate | no_code_change | 100% rows |
| P1 | top_float | F006V | shareholder_type_candidate | no_code_change | 100% rows |
| P2 | basic | (lineage) | source_status | qa_rule_required | 863/863 |
| P2 | executive | (lineage) | source_status | qa_rule_required | 863/863 |
| P2 | share_capital | (lineage) | source_status | qa_rule_required | 863/863 |
| P2 | top_shareholders | (lineage) | source_status | qa_rule_required | 863/863 |
| P2 | top_float | (lineage) | source_status | qa_rule_required | 863/863 |
| P2 | dividend_history | (lineage) | source_status | qa_rule_required | 863/863 |

---

## 4. Needs Mapper Patch Before Promotion（1）

| priority | source | field | normalized_field | fill_rate | 说明 |
|----------|--------|-------|------------------|-----------|------|
| P0 | basic | F010D | establishment_date | 863/863 (100%) | `map_company_basic_profile()` 未导出；需小 patch + fixture |

**本轮不实施 mapper patch。**

---

## 5. Needs Definition Before Promotion（0）

无。10 个 promote candidates 均已有明确业务语义。

---

## 6. Deferred Promotion（0）

无。本轮未建议 `defer_promotion`。

---

## 7. Risks

| 风险类型 | 涉及字段 | 说明 |
|----------|----------|------|
| mapper 未覆盖 | establishment_date | 唯一需 mapper patch；fill 满、语义稳定，风险 **low** |
| source_partial | top_float shareholder_type · share_capital source_status | P2 source_caveat 已接受；升格 candidate 不触发重 harvest |
| 与已有字段重复 | — | 10 候选均无与 normalized_core 冗余（F003N 等已 downgrade） |
| fill_rate 不足 | — | 最低为 executive education 97% row-level；可接受 |
| 口径不稳 | — | 无 promote candidate 命中；F044V 等已 keep_review_later |
| QA 未关闭项 | lineage source_status ×6 | 需确认 QA queue 已 classification 落账（gate PASS）后 batch approval |

---

## 8. Acceptance Criteria

真正将字段从 `review_later` 升格为 `normalized_core`（inventory 层）前，必须满足：

| # | 条件 |
|---|------|
| 1 | **字段定义清楚** — 业务语义与 raw 字段映射已文档化 |
| 2 | **mapper 输出稳定** — 863 harvest 产物可复现；ready 类 `no_code_change` 或 patch 后 fixture PASS |
| 3 | **field_fill_rate 可接受** — company 级或 row 级 fill 达 reclassification 证据阈值 |
| 4 | **QA 无新增严重 flag** — 升格不产生新 P0；现有 caveat 已 classification |
| 5 | **不写 verified** |
| 6 | **不改 registry stable 状态** — 不升级 testing_stable_sample |

**按字段类型：**

- **education / shareholder_type（ready）**：mapper 已输出 → approval 即可
- **source_status lineage（ready + qa_rule）**：batch 文档化 lineage 语义 → batch approval
- **establishment_date（after_mapper_patch）**：patch + fixture + 可选离线 re-map 规划（本轮不执行）→ 再 approval

---

## 9. Recommendation

### 按 source 汇总

| logical_source | candidates | ready | after_mapper_patch | after_definition | defer |
|----------------|------------|-------|--------------------|------------------|-------|
| basic | 2 | 1 | 1 | 0 | 0 |
| executive | 2 | 2 | 0 | 0 | 0 |
| share_capital | 1 | 1 | 0 | 0 | 0 |
| top_shareholders | 2 | 2 | 0 | 0 | 0 |
| top_float | 2 | 2 | 0 | 0 | 0 |
| dividend_history | 1 | 1 | 0 | 0 | 0 |
| security | 0 | 0 | 0 | 0 | 0 |

### 下一步建议

**ready candidates = 9 > 0** → 建议进入 **promotion candidate approval**（先 P0/P1 业务字段：education · shareholder_type ×2；再 P2 lineage source_status batch）。

**after_mapper_patch = 1** → 并行进入 **mapper patch planning**（仅 `establishment_date` / F010D；本轮不实施 patch）。

**不建议本轮：** 直接改 field inventory · company_snapshot · registry backfill · DB/RAG · harvest 重跑。

---

## 输入

- [cninfo_c_class_review_later_field_reclassification.csv](cninfo_c_class_review_later_field_reclassification.csv)
- [cninfo_c_class_review_later_field_reclassification.md](cninfo_c_class_review_later_field_reclassification.md)
- [cninfo_c_class_field_inventory.csv](cninfo_c_class_field_inventory.csv)
- [field_fill_rate.csv](../harvest/cninfo_c_class/quality/field_fill_rate.csv)
- [cninfo_c_class_full_harvest_qa_review.md](cninfo_c_class_full_harvest_qa_review.md)

## 红线确认

- 未请求 CNINFO · 未重跑 live harvest
- 未修改 raw / normalized · 未改 field inventory
- 未执行 mapper patch · 未 YAML backfill
- 未入库 / MinIO / RAG · 未写 verified · 未升级 testing_stable_sample

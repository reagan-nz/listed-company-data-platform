# CNINFO C-Class review_later 字段复判报告

_生成时间：2026-07-08_

> 离线字段复判与分类。**无 CNINFO** · **无 live** · **无 harvest 重跑** · **无 raw/normalized 修改** · **未改 field inventory** · **无 verified**

---

## 1. Overall Result

**review_later 31 字段复判已完成。**

| 项 | 值 |
|----|-----|
| review_later total | **31**（`include_in_normalized_snapshot=review`） |
| 数据来源 | [field_inventory.csv](cninfo_c_class_field_inventory.csv) · 863 harvest `field_fill_rate` · normalized/raw 离线抽样 |
| 本轮性质 | **仅复判分类**；不改 inventory · 不改 normalized 产物 |

**产物：**

- [cninfo_c_class_review_later_field_reclassification.csv](cninfo_c_class_review_later_field_reclassification.csv)（31 rows）

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`（未整体完成）

---

## 2. Reclassification Summary

| recommended_classification | count |
|----------------------------|-------|
| keep_review_later | **13** |
| promote_to_normalized_core_candidate | **10** |
| needs_mapper_patch | **3** |
| needs_definition | **3** |
| downgrade_to_raw_only | **2** |
| **合计** | **31** |

---

## 3. Promote Candidates（10）

> **仅 candidate**，本轮不直接升级 normalized_core。

| source | field | normalized_field | fill_rate | 理由 |
|--------|-------|------------------|-----------|------|
| basic | F010D | establishment_date | 863/863 | 成立日期语义稳定、fill 满；basic mapper 待补 |
| executive | F017V | education_candidate | 97.0% rows | mapper 已映射、fill 高；inventory 标记滞后 |
| top_shareholders | F006V | shareholder_type_candidate | 100% rows | mapper 已映射、fill 满 |
| top_float | F006V | shareholder_type_candidate | 100% rows | 同上；source_partial caveat 不阻塞 |
| basic | (lineage) | source_status | 863/863 | harvest lineage 已全量写入 |
| executive | (lineage) | source_status | 863/863 | 同上 |
| share_capital | (lineage) | source_status | 863/863 | 同上 |
| top_shareholders | (lineage) | source_status | 863/863 | 同上 |
| top_float | (lineage) | source_status | 863/863 | 同上 |
| dividend_history | (lineage) | source_status | 863/863 | 同上 |

---

## 4. Mapper Patch Needed（3）

| source | field | normalized_field | fill_rate | 缺口 |
|--------|-------|------------------|-----------|------|
| share_capital | F002V | change_reason_or_source | 100% rows | mapper 仅用于 row_key，未导出 |
| executive | F005N | shareholding_quantity_candidate | 91% rows（含 0） | 零值语义待定义 |
| executive | F012N | compensation_candidate | 78.8% rows | 单位/币种未标准化 |

**本轮不实施 mapper patch。**

---

## 5. Keep Review Later（13）

| source | field | normalized_field | 主要原因 |
|--------|-------|------------------|----------|
| basic | F015V | main_business_summary | business_scope derived 已覆盖 |
| basic | F017V | company_profile_text | business_scope derived 已覆盖 |
| basic | F044V | index_or_plate_labels | 与 listed_board 重叠、语义弱 |
| basic (industry) | F044V | index_or_plate_labels | observed-only 行业标签 |
| share_capital | F028N | change_amount_candidate | 65% fill；单位口径待确认 |
| basic | (lineage) | field_confidence | 硬编码 medium |
| executive | (lineage) | field_confidence | 产品规则未定义 |
| share_capital | (lineage) | field_confidence | 同上 |
| top_shareholders | (lineage) | field_confidence | 同上 |
| top_float | (lineage) | field_confidence | 同上 |
| dividend_history | (lineage) | field_confidence | 同上 |
| security | (lineage) | source_status | observe_only 不进主 snapshot |
| security | (lineage) | field_confidence | observe_only + 规则未定义 |

---

## 6. Downgrade to Raw Only（2）

| source | field | normalized_field | 主要原因 |
|--------|-------|------------------|----------|
| share_capital | F024N | unrestricted_share_candidate | fill 仅 3.3% |
| share_capital | F003N | total_capital_candidate | 与 total_share_capital (F021N) 冗余 |

---

## 7. Needs Definition（3）

| source | field | normalized_field | 主要原因 |
|--------|-------|------------------|----------|
| executive | (n/a) | term_start_candidate | CNINFO 源无对应字段 |
| executive | (n/a) | term_end_candidate | CNINFO 源无对应字段 |
| share_capital | (n/a) | share_unit | 源端无显式单位；需业务规则 |

---

## 8. Recommendation

### 按 source 汇总

| logical_source | review_later | promote | keep | downgrade | mapper_patch | needs_def |
|----------------|-------------|---------|------|-----------|--------------|-----------|
| basic | 7 | 2 | 5 | 0 | 0 | 0 |
| executive | 7 | 1 | 1 | 0 | 2 | 2 |
| share_capital | 7 | 1 | 2 | 2 | 1 | 1 |
| top_shareholders | 3 | 2 | 1 | 0 | 0 | 0 |
| top_float | 3 | 2 | 1 | 0 | 0 | 0 |
| dividend_history | 2 | 1 | 1 | 0 | 0 | 0 |
| security | 2 | 0 | 2 | 0 | 0 | 0 |

### 下一步建议

**promote candidates = 10（较多）** → 建议进入 **review_later promotion planning**（升格 candidate 清单与 basic/executive mapper 对齐计划）。

**mapper patch = 3** → 并行准备 **mapper patch planning**（F002V · F005N · F012N；本轮不实施）。

**keep + downgrade = 15（多数）** → 完成后进入 **raw_only 25 字段最终政策**（open issues C）。

**不建议本轮：** company_snapshot 设计 · registry backfill · DB/RAG · harvest 重跑。

---

## 输入

- [cninfo_c_class_field_inventory.md](../../plans/cninfo_c_class_field_inventory.md)
- [cninfo_c_class_field_inventory.csv](cninfo_c_class_field_inventory.csv)
- [field_fill_rate.csv](../harvest/cninfo_c_class/quality/field_fill_rate.csv)
- [cninfo_c_class_full_harvest_qa_review.md](cninfo_c_class_full_harvest_qa_review.md)
- [cninfo_c_class_qa_review_queue_closure_classification.csv](cninfo_c_class_qa_review_queue_closure_classification.csv)
- `outputs/harvest/cninfo_c_class/raw/` · `normalized/`（离线 fill 核对）

## 红线确认

- 未请求 CNINFO · 未重跑 live harvest
- 未修改 raw / normalized · 未改 field inventory
- 未 YAML backfill · 未入库 / MinIO / RAG
- 未写 verified · 未升级 testing_stable_sample

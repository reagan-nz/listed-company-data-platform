# CNINFO C-Class Field Inventory Promotion Summary

_生成时间：2026-07-08_

> schema governance 升格落账。**无 CNINFO** · **无 harvest** · **raw/normalized 数据未修改**

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

# 1. Promotion Result

**before:**

- normalized_core = **64**
- approved_as_candidate = **10**

**after:**

- normalized_core = **74**
- approved_as_candidate = **0**

# 2. Promoted Fields

| field_name | normalized_field_name | source_id | reason |
|------------|----------------------|-----------|--------|
| F017V | education_candidate | cninfo_executive_profile | mapper 已映射、97% row fill；仅需 inventory 升格 approval |
| F006V | shareholder_type_candidate | cninfo_top_shareholders_profile | mapper 已映射、100% row fill；inventory 标记滞后 |
| F006V | shareholder_type_candidate | cninfo_top_float_shareholders_profile | mapper 已映射、fill 满；top_float source_partial caveat 不阻塞升格 candidate |
| (lineage) | source_status | cninfo_company_basic_profile | harvest lineage 已全量写入 normalized；升格需 QA/产品规则确认（none） |
| (lineage) | source_status | cninfo_executive_profile | harvest lineage 已全量写入 normalized；升格需 QA/产品规则确认（executive empty_but_valid 已接受） |
| (lineage) | source_status | cninfo_share_capital_profile | harvest lineage 已全量写入 normalized；升格需 QA/产品规则确认（share_capital source_partial） |
| (lineage) | source_status | cninfo_top_shareholders_profile | harvest lineage 已全量写入 normalized；升格需 QA/产品规则确认（empty_but_valid 已接受） |
| (lineage) | source_status | cninfo_top_float_shareholders_profile | harvest lineage 已全量写入 normalized；升格需 QA/产品规则确认（source_partial） |
| (lineage) | source_status | cninfo_dividend_financing_profile | harvest lineage 已全量写入 normalized；升格需 QA/产品规则确认（dividend partial/needs_review 已分类） |
| F010D | establishment_date | cninfo_company_basic_profile | mapper patch + offline remap 完成；863/863 establishment_date parsed；fixture 5/5 PASS |

# 3. Quality Requirements

字段正式进入 `normalized_core` 后仍需要：

- **source evidence** — 保留 `raw_record_json` / harvest lineage
- **quality status** — 按 [product quality rules](../plans/cninfo_c_class_product_quality_rules_draft.md) 展示 caveat
- **fill rate monitoring** — 继续跟踪 `field_fill_rate.csv`
- **caveat tracking** — empty_but_valid / source_partial / needs_review 政策不变

# 4. Not Promoted

以下分类保持不变：

- review_later = **19**
- raw_only = **13**
- observe_only = **14**

# 5. Gate

```
field_inventory_promotion_gate = PASS
```

| 项 | 值 |
|----|-----|
| promoted fields | **10** |
| normalized_core after | **74** |
| approved_as_candidate after | **0** |
| C-class status | **`HARVEST_COMPLETED_QA_ONGOING`** |
| field_inventory.csv（原始） | **未修改** |
| raw / normalized harvest | **未修改** |

**禁止：** completed · verified · testing_stable_sample

## 红线确认

- 未请求 CNINFO · 未重跑 harvest live
- raw / normalized 数据内容未修改
- 未入库 / MinIO / RAG · 未 registry backfill

详见 [cninfo_c_class_field_inventory_promotion_check.csv](cninfo_c_class_field_inventory_promotion_check.csv)。

# CNINFO C-Class Field Freeze Summary

_生成时间：2026-07-08_

> 离线 Field Freeze Review。**无 CNINFO** · **无 harvest 重跑** · **field inventory 未修改**

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

# 1. Field Overview

| status | count |
|--------|-------|
| normalized_core | **64** |
| approved_as_candidate | **10** |
| review_later | **19** |
| raw_only | **13** |
| observe_only | **14** |
| **total fields** | **120** |

**与 inventory 基线对照：**

| 基线 | 说明 |
|------|------|
| inventory `include=review`（31） | 10 已 promotion → `approved_as_candidate`；2 复判降级 → `raw_only`；**19** 仍为 `review_later` |
| inventory `include=no`（25） | 14 项 security 业务字段 → `observe_only`；**11** 项非 security → `raw_only`；另 2 项 review 降级并入 `raw_only` |

# 2. Source Coverage

| source_id | field_count | normalized_count | candidate_count | review_count | raw_only_count | observe_only_count |
|-----------|-------------|------------------|-----------------|--------------|----------------|---------------------|
| cninfo_company_basic_profile | 29 | 16 | 6 | 4 | 7 | 0 |
| cninfo_company_business_scope | 3 | 3 | 0 | 0 | 0 | 0 |
| cninfo_company_contact_profile | 8 | 8 | 0 | 0 | 0 | 0 |
| cninfo_company_industry_profile | 3 | 2 | 1 | 1 | 0 | 0 |
| cninfo_company_security_profile | 18 | 2 | 2 | 2 | 0 | 14 |
| cninfo_dividend_financing_profile | 9 | 7 | 2 | 1 | 0 | 0 |
| cninfo_executive_profile | 15 | 6 | 7 | 5 | 2 | 0 |
| cninfo_share_capital_profile | 13 | 6 | 5 | 4 | 2 | 0 |
| cninfo_top_float_shareholders_profile | 11 | 7 | 3 | 1 | 1 | 0 |
| cninfo_top_shareholders_profile | 11 | 7 | 3 | 1 | 1 | 0 |

# 3. Company Profile Coverage

一个上市公司当前可覆盖的模块（基于 863 harvest normalized + raw 证据）：

| module | coverage |
|--------|----------|
| identity | **partial** |
| business | **available** |
| industry | **partial** |
| financial | **available** |
| R&D | **not_modeled** |
| employees | **available** |
| shareholder | **available** |
| executive | **partial** |
| dividend | **available** |
| risk | **not_modeled** |
| event | **available** |
| document evidence | **available** |
| quality | **partial** |

# 4. Known Limitations

- **company_snapshot 未实现** — 尚无跨源聚合 snapshot 产物；当前为分源 normalized 文件。
- **security observe-only** — `cninfo_company_security_profile` 不纳入主 company profile gate。
- **BSE/abnormal side track 未覆盖** — 863 universe 不含 hold/BSE legacy/abnormal 侧轨公司。
- **registry backfill 未执行** — YAML registry 未因 harvest 结果批量回填。
- **review_later 未全部升级** — **19** 字段仍待 mapper patch / 语义定义 / 产品规则（inventory 原 review 桶 31 项，10 已 promotion、2 已降级）。
- **raw_only 未进入 normalized** — **13** 项 raw 证据字段 + **14** 项 security observe-only（inventory 原 `include=no` 共 25 项，freeze 评审将 security 单列 observe）。
- **10 promotion candidates 未 inventory 升格** — candidate approval 已完成，inventory `include` 列未改。
- **dividend manual review queue** — 10 条 needs_review 事件待人工复核；002019/002060 parser patch 待实施。

## 红线确认

- 未请求 CNINFO · 未重跑 harvest live
- raw / normalized / field_inventory **未修改**
- 未写 verified · 未升级 testing_stable_sample
- 未入库 / MinIO / RAG · 未 registry backfill

详见 [cninfo_c_class_final_field_catalog.csv](cninfo_c_class_final_field_catalog.csv) · [cninfo_c_class_field_freeze_v1.md](../../plans/cninfo_c_class_field_freeze_v1.md)。

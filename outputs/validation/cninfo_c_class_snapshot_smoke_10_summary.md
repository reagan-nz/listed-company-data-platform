# CNINFO C-Class Snapshot Smoke 10 Summary

_生成时间：2026-07-08_

> 离线 snapshot smoke batch。**无 CNINFO** · **normalized 只读** · **demo 未覆盖**

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

# 1. Sample Overview

公司数量：**10**

## 板块分布

| board | count |
|-------|-------|
| chinext | **2** |
| sse_main | **2** |
| star | **2** |
| szse_main | **4** |

# 2. Snapshot Status

| snapshot_status | count |
|-----------------|-------|
| complete_with_caveat | **10** |

# 3. Module Coverage（18 modules）

| module | available_count | partial_count | missing_count |
|--------|-----------------|---------------|---------------|
| company_identity | 10 | 0 | 0 |
| securities_profile | 10 | 0 | 0 |
| business_profile | 10 | 0 | 0 |
| industry_profile | 10 | 0 | 0 |
| financial_snapshot | 9 | 1 | 0 |
| technology_profile | 0 | 0 | 10 |
| organization_profile | 10 | 0 | 0 |
| shareholder_profile | 0 | 10 | 0 |
| executive_profile | 8 | 2 | 0 |
| governance_profile | 10 | 0 | 0 |
| dividend_profile | 7 | 3 | 0 |
| capital_action_profile | 0 | 10 | 0 |
| risk_profile | 0 | 10 | 0 |
| event_timeline | 9 | 1 | 0 |
| market_behavior | 0 | 10 | 0 |
| investor_relation | 0 | 10 | 0 |
| document_evidence | 10 | 0 | 0 |
| data_quality | 10 | 0 | 0 |

# 4. Schema Issues

## 4.1 跨公司字段结构一致性

- cross_company_field_drift:financial_snapshot:002267 missing=['float_share_capital', 'restricted_share_capital', 'total_share_capital']
- cross_company_field_drift:executive_profile:002267 missing=['birth_year_candidate', 'education_candidate', 'gender_candidate', 'person_name', 'position']
- cross_company_field_drift:dividend_profile:002267 missing=['dividend_parse_status', 'dividend_payment_date_candidate', 'dividend_plan_text']
- cross_company_field_drift:event_timeline:688750 missing=['events', 'report_date', 'total_share_capital']

## 4.2 Source alias

- dividend / business_scope derived 字段 alias 已在 builder 处理（`dividend_plan_text_raw` · `main_business` · `company_introduction`）
- security observe 使用 `secCode` 等 raw API 键，已 alias

## 4.3 字段冲突

- 本轮未观察到跨公司同字段值冲突（单源 cninfo_f10，无 multi-source merge）

## 4.4 Quality status

- 全部 10 家 `company_harvest_status=complete`
- `snapshot_status` 均为 `complete_with_caveat`（符合 QA 政策）
- executive empty 样本（002267/301332）`executive_profile` 为 partial/not_available 符合预期

## 4.5 是否需要增加 snapshot module

- **否** — 18 模块结构在 10 家样本上稳定；`technology_profile` 统一 `not_available`

## 记录项（notes，本轮不修代码）

- **mapper issue**: 无新增阻塞
- **source issue**: executive empty_but_valid 导致 2 家 executive 模块偏空（已知）
- **schema issue**: 数组模块（shareholder/dividend）item 键因 scope/parse_status 略有差异，属预期
- **quality issue**: 全部 complete_with_caveat；与 harvest QA 一致


# 5. Conclusion

```
snapshot_smoke_gate = PASS_WITH_CAVEAT
```

| 项 | 值 |
|----|-----|
| companies | **10** |
| output dir | `outputs/snapshot/cninfo_c_class/smoke/` |
| demo dir | **未覆盖** |
| field mapping | **120** |

## 红线确认

- 未请求 CNINFO · 未重跑 harvest
- raw / normalized / field_inventory **未修改**
- 未入库 / MinIO / RAG · 未写 verified

详见 [cninfo_c_class_snapshot_smoke_10_report.csv](cninfo_c_class_snapshot_smoke_10_report.csv)。

# CNINFO D 类 Schema Validation Summary

_生成时间：2026-07-05（离线 fixture validation）_

## 1. 目的

本次为 **离线 fixture schema validation**：使用 Phase 2 文档摘录的小样本 raw record，
经 mapper 草案转换为逻辑 record 后，用 `schemas/d_class/` JSON Schema 校验。
**不请求 CNINFO、不入库、不写 verified。**

## 2. 覆盖范围

| 项 | 数值 |
|----|------|
| fixture 数量 | **11** |
| source 数量 | **10** |
| 逻辑 schema 数量 | **5** |
| 含 snapshot schema | **6** |

Sources: `abnormal_trading`, `block_trade`, `disclosure_schedule`, `equity_pledge`, `executive_shareholding`, `fund_industry_allocation`, `margin_trading`, `restricted_shares_unlock`, `shareholder_change`, `shareholder_data`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_fixtures | **11** |
| pass | **11** |
| fail | **0** |
| skipped | **0** |
| generated_logical_records | **22** |

**总体结论：** **PASS**

## 4. 分 source 结果

### `abnormal_trading` — `single_day_paged`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/abnormal_trading/sample_raw.json` |
| target schema | `d_company_event` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | detail[] → d_event_party_detail deferred; main event validated only |

### `block_trade` — `tdate_daily`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/block_trade/sample_raw.json` |
| target schema | `d_company_event` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | optional d_company_metric_daily ETL not implemented in v1 |

### `disclosure_schedule` — `section_time_paged`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/disclosure_schedule/sample_raw.json` |
| target schema | `d_disclosure_schedule` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | — |

### `equity_pledge` — `tdate_daily`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/equity_pledge/sample_raw.json` |
| target schema | `d_company_event` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | — |

### `executive_shareholding` — `oneMonth_varyType_b`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/executive_shareholding/sample_raw.json` |
| target schema | `d_company_event` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | — |

### `fund_industry_allocation` — `default`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/fund_industry_allocation/sample_raw.json` |
| target schema | `d_industry_aggregate` |
| validation result | **PASS** |
| generated logical records | **3** |
| raw snapshot | **PASS** |
| notes | validates all 3 confirmed metric rows per raw record |

### `margin_trading` — `detailList_default`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/margin_trading/sample_raw.json` |
| target schema | `d_company_metric_daily` |
| validation result | **PASS** |
| generated logical records | **5** |
| raw snapshot | **PASS** |
| notes | validates all 5 confirmed metric rows per raw record |

### `restricted_shares_unlock` — `tdate_daily`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/restricted_shares_unlock/sample_raw.json` |
| target schema | `d_company_event` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | — |

### `shareholder_change` — `type_desc`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/shareholder_change_desc/sample_raw.json` |
| target schema | `d_company_event` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | — |

### `shareholder_change` — `type_inc`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/shareholder_change_inc/sample_raw.json` |
| target schema | `d_company_event` |
| validation result | **PASS** |
| generated logical records | **1** |
| raw snapshot | **PASS** |
| notes | — |

### `shareholder_data` — `rdate_report_period`

| 项 | 值 |
|----|-----|
| fixture path | `fixtures/d_class/shareholder_data/sample_raw.json` |
| target schema | `d_company_metric_periodic` |
| validation result | **PASS** |
| generated logical records | **6** |
| raw snapshot | **PASS** |
| notes | validates all 6 confirmed metric rows per raw record |

## 5. 已知限制

- fixtures 只是 Phase 2 文档摘录样本，**不代表全量**或长期稳定；
- mapper 为 **草案**，仅做最小字段转换；
- `abnormal_trading` 的 `detail[]` → `d_event_party_detail` **未实现**（deferred）；
- `block_trade` 可选 `d_company_metric_daily` ETL **未做**，仅验证 `d_company_event`；
- `margin_trading` / `shareholder_data` / `fund_industry_allocation` 从一个 raw row 拆多 metric，本版 **全部 confirmed 指标均校验**；
- **不写 verified**；schema pass 不等于生产 schema 锁定。

## 6. 下一步

1. 扩充 fixture（empty_but_valid、多 query_mode）；
2. 完善 mapper（party detail、block_trade metric ETL）；
3. 加入 CI：`lint_cninfo_d_class_registry.py` + `validate_cninfo_d_class_schema.py`；
4. 后续如入库，再由 schema draft 推 SQL migration。

## 附录：逐 record 明细

详见 [cninfo_d_class_schema_validation_report.csv](cninfo_d_class_schema_validation_report.csv)。

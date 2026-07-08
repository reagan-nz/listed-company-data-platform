# CNINFO C-Class Snapshot Builder Demo Summary

_生成时间：2026-07-08_

> 离线 snapshot builder PoC。**无 CNINFO** · **normalized 只读** · **无 DB**

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

## 1. Snapshot company

- **688750** — 金天钛业
- 说明：请求 demo `300750` 不在 863 harvest；选用 **688750**（科创板 · 字段覆盖完整）

## 2. Input normalized files

**10** 个分源文件：

- `outputs/harvest/cninfo_c_class/normalized/company_basic_profile/688750.json`
- `outputs/harvest/cninfo_c_class/normalized/contact_profile/688750.json`
- `outputs/harvest/cninfo_c_class/normalized/business_scope/688750.json`
- `outputs/harvest/cninfo_c_class/normalized/industry_profile/688750.json`
- `outputs/harvest/cninfo_c_class/normalized/executive_profile/688750.jsonl`
- `outputs/harvest/cninfo_c_class/normalized/share_capital_profile/688750.jsonl`
- `outputs/harvest/cninfo_c_class/normalized/top_shareholders_profile/688750.jsonl`
- `outputs/harvest/cninfo_c_class/normalized/top_float_shareholders_profile/688750.jsonl`
- `outputs/harvest/cninfo_c_class/normalized/dividend_history/688750.jsonl`
- `outputs/harvest/cninfo_c_class/normalized/security_observe/688750.json`

## 3. Generated modules

**18** 个一级模块（全部保留，无数据模块 `status=not_available`）

## 4. Available modules

- `company_identity`
- `securities_profile`
- `business_profile`
- `industry_profile`
- `financial_snapshot`
- `organization_profile`
- `executive_profile`
- `governance_profile`
- `dividend_profile`
- `event_timeline`
- `document_evidence`
- `data_quality`

## 5. Partial modules

- `shareholder_profile`
- `capital_action_profile`
- `risk_profile`
- `market_behavior`
- `investor_relation`

## 6. Not available modules

- `technology_profile`

## 7. Field mapping count

**120**（来自 cninfo_c_class_company_snapshot_field_mapping.csv）

## 8. Quality caveats

- company_harvest_status=complete; snapshot 映射为 complete_with_caveat 策略
- module technology_profile is not_available
- module shareholder_profile is partial
- module capital_action_profile is partial
- module risk_profile is partial
- module market_behavior is partial
- module investor_relation is partial

## 9. Schema issues

- **未发现阻塞性 schema 问题**
- dividend normalized 字段名与 catalog 存在 alias（`dividend_plan_text_raw` 等），builder 已映射
- security observe 字段名为 raw API 形态（`secCode` 等），已 alias 至 catalog 名

## 10. 是否建议扩展到 10 家公司

**是** — 建议按 [cninfo_c_class_snapshot_smoke_plan.md](../../plans/cninfo_c_class_snapshot_smoke_plan.md) 执行 smoke（本轮仅规划，未执行）。

## Build mode

- dry_run: **False**
- snapshot_status: **complete_with_caveat**

## Gate

```
snapshot_builder_prototype_gate = PASS
```

## 红线确认

- 未请求 CNINFO · 未重跑 harvest
- raw / normalized / field_inventory **未修改**
- 未入库 / MinIO / RAG · 未写 verified

# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot QA Summary

_生成时间：2026-07-09_

> 离线 snapshot QA review。**无 CNINFO** · **无 harvest rerun** · **无 snapshot rebuild**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

# Snapshot QA Result

json_count: **491**

valid_json_count: **491**

invalid_json_count: **0**

duplicate_company_code_count: **0**

excluded_code_present_count: **0**

# Snapshot Status Distribution

- complete: **0**
- complete_with_caveat: **491**
- partial: **0**
- failed: **0**

# Module Coverage

与 863 full / Phase2 smoke 188 模式一致：`technology_profile` 预期 `not_available`；`shareholder_profile` / `capital_action_profile` / `risk_profile` / `market_behavior` / `investor_relation` 等多为 `partial` 或 `available` 混合；核心 identity / securities / business 模块预期 `available`。

| module | available | partial | not_available | missing | gate |
|--------|-----------|---------|---------------|---------|------|
| company_identity | 487 | 4 | 0 | 0 | PASS_WITH_CAVEAT |
| securities_profile | 488 | 3 | 0 | 0 | PASS_WITH_CAVEAT |
| business_profile | 487 | 4 | 0 | 0 | PASS_WITH_CAVEAT |
| industry_profile | 487 | 4 | 0 | 0 | PASS_WITH_CAVEAT |
| financial_snapshot | 487 | 4 | 0 | 0 | PASS_WITH_CAVEAT |
| technology_profile | 0 | 0 | 491 | 0 | PASS_WITH_CAVEAT |
| organization_profile | 485 | 0 | 6 | 0 | PASS_WITH_CAVEAT |
| shareholder_profile | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| executive_profile | 487 | 4 | 0 | 0 | PASS_WITH_CAVEAT |
| governance_profile | 487 | 4 | 0 | 0 | PASS_WITH_CAVEAT |
| dividend_profile | 478 | 13 | 0 | 0 | PASS_WITH_CAVEAT |
| capital_action_profile | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| risk_profile | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| event_timeline | 488 | 3 | 0 | 0 | PASS_WITH_CAVEAT |
| market_behavior | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| investor_relation | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| document_evidence | 488 | 0 | 3 | 0 | PASS_WITH_CAVEAT |
| data_quality | 491 | 0 | 0 | 0 | PASS |

# Quality Flags

## By severity

| severity | count |
|----------|-------|
| info | **13011** |
| medium | **99** |

## By flag_type

| flag_type | count |
|-----------|-------|
| field_missing | **12979** |
| empty_module | **66** |
| source_missing | **63** |
| schema_drift | **2** |

# Status Tracking Correction

`outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/quality/company_snapshot_status.csv` 原为 dry-run 遗留（全部 `pending`）。本轮 QA 已从实际 JSON 输出重写：

- 行数: **491**
- `file_exists=true`
- `qa_review_status=reviewed`
- `snapshot_status` 取自各 JSON
- `retry_status=done`

# Output Isolation

- phase3 snapshot dir: `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/`
- full snapshot dir JSON count: **863**（未写入）
- phase2 snapshot dir JSON count: **188**（未写入）
- CNINFO calls: **0**
- harvest rerun: **none**

# Gate

```
phase3_batch_500_success_snapshot_qa_gate = PASS_WITH_CAVEAT
```

# Next Step

Recommend: **Phase 3 closure review**.

Do **not** recommend Phase 4 / full expansion until closure review is complete.

## 红线确认

- 未请求 CNINFO · 未 live · 未重跑 harvest · 未 rebuild snapshot
- snapshot JSON / raw / normalized / field_inventory **未修改**（仅 status CSV 校正）
- 未入库 / MinIO / RAG / registry / verified

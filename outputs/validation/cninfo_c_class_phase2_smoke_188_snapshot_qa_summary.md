# CNINFO C-Class Phase 2 Smoke 188 Snapshot QA Summary

_生成时间：2026-07-09_

> 离线 snapshot QA review。**无 CNINFO** · **无 harvest rerun** · **无 snapshot rebuild**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

# Snapshot QA Result

json_count: **188**

valid_json_count: **188**

invalid_json_count: **0**

duplicate_company_code_count: **0**

excluded_code_present_count: **0**

# Snapshot Status Distribution

- complete: **0**
- complete_with_caveat: **188**
- partial: **0**
- failed: **0**

# Module Coverage

与 863 full snapshot QA 模式一致：`technology_profile` 预期 `not_available`；`shareholder_profile` / `dividend_profile` / `risk_profile` / `market_behavior` 等多为 `partial` 或 `available` 混合。

| module | available | partial | not_available | missing | gate |
|--------|-----------|---------|---------------|---------|------|
| company_identity | 188 | 0 | 0 | 0 | PASS |
| securities_profile | 188 | 0 | 0 | 0 | PASS |
| business_profile | 188 | 0 | 0 | 0 | PASS |
| industry_profile | 188 | 0 | 0 | 0 | PASS_WITH_CAVEAT |
| financial_snapshot | 188 | 0 | 0 | 0 | PASS_WITH_CAVEAT |
| technology_profile | 0 | 0 | 188 | 0 | PASS_WITH_CAVEAT |
| organization_profile | 188 | 0 | 0 | 0 | PASS |
| shareholder_profile | 0 | 188 | 0 | 0 | PASS_WITH_CAVEAT |
| executive_profile | 188 | 0 | 0 | 0 | PASS_WITH_CAVEAT |
| governance_profile | 187 | 1 | 0 | 0 | PASS_WITH_CAVEAT |
| dividend_profile | 182 | 6 | 0 | 0 | PASS_WITH_CAVEAT |
| capital_action_profile | 0 | 188 | 0 | 0 | PASS_WITH_CAVEAT |
| risk_profile | 0 | 188 | 0 | 0 | PASS_WITH_CAVEAT |
| event_timeline | 188 | 0 | 0 | 0 | PASS_WITH_CAVEAT |
| market_behavior | 0 | 188 | 0 | 0 | PASS_WITH_CAVEAT |
| investor_relation | 0 | 188 | 0 | 0 | PASS_WITH_CAVEAT |
| document_evidence | 188 | 0 | 0 | 0 | PASS |
| data_quality | 188 | 0 | 0 | 0 | PASS |

# Quality Flags

## By severity

| severity | count |
|----------|-------|
| info | **4936** |
| medium | **9** |

## By flag_type

| flag_type | count |
|-----------|-------|
| field_missing | **4929** |
| empty_module | **8** |
| source_missing | **8** |

# Status Tracking Correction

`outputs/snapshot/cninfo_c_class/phase2_smoke_188/quality/company_snapshot_status.csv` 原为 dry-run 遗留（全部 `pending`）。本轮 QA 已从实际 JSON 输出重写：

- 行数: **188**
- `file_exists=true`
- `qa_review_status=reviewed`
- `snapshot_status` 取自各 JSON

# Output Isolation

- phase2 snapshot dir: `outputs/snapshot/cninfo_c_class/phase2_smoke_188/`
- full snapshot dir JSON count: **863**（未写入）

# Gate

```
phase2_smoke_188_snapshot_qa_gate = PASS_WITH_CAVEAT
```

# Next Step

Recommend: **Phase 2 smoke closure review**.

Do **not** recommend full 500 batch until closure review is complete.

## 红线确认

- 未请求 CNINFO · 未 live · 未重跑 harvest · 未 rebuild snapshot
- snapshot JSON / raw / normalized / field_inventory **未修改**（仅 status CSV 校正）
- 未入库 / MinIO / RAG / registry / verified

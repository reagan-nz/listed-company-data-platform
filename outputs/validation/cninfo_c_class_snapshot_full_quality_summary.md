# CNINFO C-Class Snapshot Full Quality Summary

_生成时间：2026-07-08_

> 离线 full snapshot QA review。**无 CNINFO** · **只读 snapshot JSON** · **不修改产物**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

# 1. Overall

snapshot_count: **863**
valid_json_count: **863**
invalid_json_count: **0**

duplicate_company_code: **0**

# 2. Module Coverage

| module | available | partial | not_available | coverage_rate |
|--------|-----------|---------|---------------|---------------|
| company_identity | 863 | 0 | 0 | 1.0 |
| securities_profile | 863 | 0 | 0 | 1.0 |
| business_profile | 863 | 0 | 0 | 1.0 |
| industry_profile | 860 | 3 | 0 | 1.0 |
| financial_snapshot | 853 | 10 | 0 | 1.0 |
| technology_profile | 0 | 0 | 863 | 0.0 |
| organization_profile | 859 | 0 | 4 | 0.9954 |
| shareholder_profile | 0 | 863 | 0 | 1.0 |
| executive_profile | 854 | 9 | 0 | 1.0 |
| governance_profile | 863 | 0 | 0 | 1.0 |
| dividend_profile | 825 | 38 | 0 | 1.0 |
| capital_action_profile | 0 | 863 | 0 | 1.0 |
| risk_profile | 0 | 863 | 0 | 1.0 |
| event_timeline | 855 | 8 | 0 | 1.0 |
| market_behavior | 0 | 863 | 0 | 1.0 |
| investor_relation | 0 | 863 | 0 | 1.0 |
| document_evidence | 863 | 0 | 0 | 1.0 |
| data_quality | 863 | 0 | 0 | 1.0 |

# 3. Top Missing Fields

| field | module | missing_rate | available_count |
|-------|--------|--------------|-----------------|
| change_amount_candidate | capital_action_profile | 1.0 | 0 |
| change_reason_or_source | capital_action_profile | 1.0 | 0 |
| unrestricted_share_candidate | capital_action_profile | 1.0 | 0 |
| listing_sponsor | company_identity | 1.0 | 0 |
| field_confidence | data_quality | 1.0 | 0 |
| source_status | data_quality | 1.0 | 0 |
| raw_record_hash | document_evidence | 1.0 | 0 |
| raw_record_json | document_evidence | 1.0 | 0 |
| person_id_candidate | executive_profile | 1.0 | 0 |
| row_sequence_id | executive_profile | 1.0 | 0 |
| shareholding_quantity_candidate | executive_profile | 1.0 | 0 |
| compensation_candidate | financial_snapshot | 1.0 | 0 |
| share_unit | financial_snapshot | 1.0 | 0 |
| total_capital_candidate | financial_snapshot | 1.0 | 0 |
| board_secretary_candidate | governance_profile | 1.0 | 0 |
| term_end_candidate | governance_profile | 1.0 | 0 |
| term_start_candidate | governance_profile | 1.0 | 0 |
| contact_email | investor_relation | 1.0 | 0 |
| contact_fax | investor_relation | 1.0 | 0 |
| contact_phone | investor_relation | 1.0 | 0 |

# 4. Top Quality Issues

| flag_type | count |
|-----------|-------|
| field_missing | **22820** |
| empty_module | **82** |
| source_missing | **74** |
| schema_drift | **1** |

rare_fields (available < 50 companies): **1**

# 5. Current Status

```
C-class status = SNAPSHOT_GENERATED_QA_REVIEW
```

- snapshot 863 家已生成
- QA review 完成；**非** completed / verified / testing_stable_sample

# 6. Recommended Next Step

- **company_snapshot schema adjustment**：记录 schema_drift / field_missing；优先文档化，非阻塞 patch
- **security observe decision**：market_behavior / risk_profile 为 observe_only partial；建议单独产品决策
- **BSE / abnormal side track**：26 all6 hold 未纳入 863；维持 HOLD 文档化
- **product layer**：可进入 product layer 规划（caveat 层）；technology_profile 待 future 源

## 红线确认

- 未请求 CNINFO · 未重跑 harvest
- snapshot / normalized / field_inventory **未修改**
- 未入库 / MinIO / RAG · 未写 verified

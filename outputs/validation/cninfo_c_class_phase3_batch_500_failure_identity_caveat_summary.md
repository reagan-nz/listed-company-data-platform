# CNINFO C-Class Phase 3 Batch 500 Failure Identity Caveat Summary

_生成时间：2026-07-09_

> Phase 3 batch 500 live harvest all-direct-failure 身份 caveat 离线分诊。**无 CNINFO** · **无 harvest 重跑** · **不解析 identity** · **不 merge**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

---

# Triage Input

| 项 | 值 |
|----|-----|
| primary input | `outputs/validation/cninfo_c_class_harvest_smoke_report.csv` |
| data source used | **phase3_batch_500_001 raw envelopes (offline; smoke_report on disk is phase2 snapshot)** |
| selection criteria | `http_status=500` · `business_code=9240002` · all **6** direct sources failed |

---

# Failed Company Count

| 项 | 值 |
|----|-----|
| all-direct-failure companies | **9** |
| failed direct source rows | **54** |
| batch universe | **500** |
| success subset candidate (excl. failures) | **491** |

---

# Source Failure Distribution

| source_id | failed companies |
|-----------|------------------|
| `cninfo_company_basic_profile` | **9** |
| `cninfo_dividend_financing_profile` | **9** |
| `cninfo_executive_profile` | **9** |
| `cninfo_share_capital_profile` | **9** |
| `cninfo_top_shareholders_profile` | **9** |
| `cninfo_top_float_shareholders_profile` | **9** |

**Pattern：** 全部失败均为 `HTTP 500` + `business_code=9240002`；6 个 direct 源每家公司各 1 条失败。

---

# Identity Risk Classification

| identity_risk_type | count |
|--------------------|-------|
| `delisted_or_reorganized` | **7** |
| `manual_identity_review` | **2** |

---

# Recommended Handling

| 项 | 建议 |
|----|------|
| identity resolution | **不做** — 仅记录 caveat，不 merge，不改 registry |
| harvest retry | **不自动重试** — 须 registry / universe 刷新后再评估 |
| exclude from success subset | **7** 家明确排除 |
| pending manual review | **2** 家待人工 identity 复核 |
| Phase 3 snapshot | 仅对 **491** 家成功子集构建；**9** 家 all-direct-failure **排除** |

---

# Snapshot Policy

| 项 | 决策 |
|----|------|
| phase3 success_subset snapshot | **应排除** 9 家 all-direct-failure |
| reason | 无 normalized direct 产物；9240002 表明 CNINFO data20 身份不可解析 |
| caveat ledger | [cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv](cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv) |

---

# Gate

```
phase3_batch_500_failure_identity_triage_gate = READY_FOR_REVIEW
```

---

# Company List

- `600102` 莱钢股份 · `delisted_or_reorganized` · snapshot=`exclude` · action=`exclude_from_phase3_success_subset`
- `600270` 外运发展 · `delisted_or_reorganized` · snapshot=`exclude` · action=`exclude_from_phase3_success_subset`
- `600317` 营口港 · `delisted_or_reorganized` · snapshot=`exclude` · action=`exclude_from_phase3_success_subset`
- `600625` PT水仙 · `delisted_or_reorganized` · snapshot=`exclude` · action=`exclude_from_phase3_success_subset`
- `600627` 上电股份 · `delisted_or_reorganized` · snapshot=`exclude` · action=`exclude_from_phase3_success_subset`
- `600705` 中航产融 · `manual_identity_review` · snapshot=`exclude_pending_review` · action=`hold_for_manual_identity_review`
- `600840` 新湖创业 · `delisted_or_reorganized` · snapshot=`exclude` · action=`exclude_from_phase3_success_subset`
- `601028` 玉龙股份 · `manual_identity_review` · snapshot=`exclude_pending_review` · action=`hold_for_manual_identity_review`
- `601989` 中国重工 · `delisted_or_reorganized` · snapshot=`exclude` · action=`exclude_from_phase3_success_subset`

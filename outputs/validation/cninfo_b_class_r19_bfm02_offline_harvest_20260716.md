# CNINFO B 类 B-FM-02（R19）— Offline Harvest 决策记录

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-02  
> **性质：** offline harvest 扫描 + 路径选择 · **CNINFO=0** · **NOT verified**

---

## 1. Deferred families（优先第二案）扫描结论

对既有 B 类 ERAD / phase 报告 CSV 做标题扫描（无新 CNINFO；承接 B-FM-01）：

| family | 独立第二案 | 结论 |
|--------|------------|------|
| `independent_director_meeting_review_known_002` | 无清晰第二案 | **薄** — 推迟 |
| `asset_valuation_explanation_known_002` | 无清晰第二案 | **薄** — 推迟 |
| `listing_sponsor_known_002` | 无清晰第二案；半年报污染仍在 | **薄/陷阱** — 推迟 |
| `continuous_supervision_training_known_002` | 无清晰第二案 | **薄** — 推迟 |
| `audit_report_known_002` | 川网传媒年报审计报告 | **拒绝** — 年报陷阱 |
| `equity_change_report_known_002` | 仍仅德林海 known_001 | **薄** — 推迟 |

---

## 2. Fallback：tracking_rating / bond_trustee 余量（meaningful scale）

| family | 余量（未晋升） | 本包 |
|--------|----------------|------|
| `tracking_rating_report` | 华阳国际 / 广联航空 / 立讯精密 / 天合光能 / 航新科技 等 | **执行 known_006–010（5 案）** |
| `bond_trustee_report` | 南方航空 A 股可转债 / 铜陵有色特定对象 / 美锦能源语序变体 等 | **执行 known_005–007（3 案）** |

### 选定晋升（8 案 coherent sample）

| case_id | harvest | company | ann_id | date |
|---------|---------|---------|--------|------|
| `tracking_rating_report_known_006` | BD2E558 可转债2025跟踪（无定期） | 华阳国际 002949 | 1223952243 | 2025-06-20 |
| `tracking_rating_report_known_007` | BD2E644 相关债券跟踪第二公司 | 广联航空 300900 | 1224016467 | 2025-06-27 |
| `tracking_rating_report_known_008` | BD2E156 可转债2025跟踪公司锚定 | 立讯精密 002475 | 1224016122 | 2025-06-27 |
| `tracking_rating_report_known_009` | B2E012 向不特定对象可转债跟踪 | 天合光能 688599 | 1223956820 | 2025-06-23 |
| `tracking_rating_report_known_010` | BD2E360 可转债定期跟踪第二公司 | 航新科技 300424 | 1224012941 | 2025-06-27 |
| `bond_trustee_report_known_005` | BD2E364 A股可转债受托 | 南方航空 600029 | 1224014795 | 2025-06-27 |
| `bond_trustee_report_known_006` | BD2E076 向特定对象可转债受托 | 铜陵有色 000630 | 1223997318 | 2025-06-26 |
| `bond_trustee_report_known_007` | BD2E208 「2024年度」前置语序受托 | 美锦能源 000723 | 1224016384 | 2025-06-29 |

路由：既有 B-FM-29 硬化已覆盖；本包 **不改路由**。  
不重开 known_001–005（tracking）/ known_001–004（bond）及更早 LIVE_PASS。

---

## 3. Gate（本阶段）

```text
b_class_r19_bfm02_offline_harvest_gate = PASS_OFFLINE
deferred_second_case_clear_hit = 0
fallback_residual_promoted = 8
cninfo_calls = 0
```

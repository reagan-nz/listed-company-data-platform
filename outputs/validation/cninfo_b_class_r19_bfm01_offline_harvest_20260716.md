# CNINFO B 类 B-FM-01（R19）— Offline Harvest 决策记录

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-01  
> **性质：** offline harvest 扫描 + 路径选择 · **CNINFO=0** · **NOT verified**

---

## 1. Deferred families（优先第二案）扫描结论

对既有 B 类 ERAD / phase 报告 CSV 做标题扫描（无新 CNINFO）：

| family | 独立第二案 | 结论 |
|--------|------------|------|
| `independent_director_meeting_review_known_002` | 无（仅金枫酒业 known_001） | **薄** — 推迟 |
| `asset_valuation_explanation_known_002` | 无（仅舍得酒业 known_001） | **薄** — 推迟 |
| `listing_sponsor_known_002` | 无清晰第二案；白云机场「上市保荐书」命中行含「半年报」污染 | **薄/陷阱** — 推迟 |
| `continuous_supervision_training_known_002` | 无（仅三联锻造 known_001） | **薄** — 推迟 |
| `audit_report_known_002` | 川网传媒年报审计报告 | **拒绝** — 年报陷阱 |

---

## 2. Fallback：tracking_rating / bond_trustee / equity_change 余量

| family | 余量 | 本包 |
|--------|------|------|
| `tracking_rating_report` | 多条 fuller/scale 余量（相关债券 / 主体及转债 / 可转债2025 等） | **执行 known_004 + known_005** |
| `bond_trustee_report` | 多条余量（可续期 / A股可转债 / 公司债整包等） | **执行 known_004（可续期）** |
| `equity_change_report` | 仅德林海 known_001 | **薄** — 本包不推 known_002 |

### 选定晋升（3 案，meaningful sample）

| case_id | harvest | company | ann_id | date |
|---------|---------|---------|--------|------|
| `tracking_rating_report_known_004` | BD2E606 相关债券跟踪评级 | 南京聚隆 300644 | 1224014161 | 2025-06-27 |
| `tracking_rating_report_known_005` | BD2E636 主体及转债联合跟踪评级 | 申昊科技 300853 | 1224016390 | 2025-06-27 |
| `bond_trustee_report_known_004` | B2E013 可续期公司债受托 | 京东方A 000725 | 1224036525 | 2025-06-30 |

路由：既有 B-FM-29 硬化已覆盖；本包 **不改路由**。

---

## 3. Gate（本阶段）

```text
b_class_r19_bfm01_offline_harvest_gate = PASS_OFFLINE
deferred_second_case_clear_hit = 0
fallback_residual_promoted = 3
cninfo_calls = 0
```

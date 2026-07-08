# CNINFO C-Class Field & Quality Consolidation Batch Summary

_生成时间：2026-07-08_

> Era C Phase 4 **字段层 + 质量规则层**一次性收口批次。**无 CNINFO** · **无 harvest 重跑** · **无 raw/normalized/inventory 修改**

---

## 1. 本轮完成了什么

| # | 工作包 | 产物 | 结果 |
|---|--------|------|------|
| 1 | **9 promotion candidates approval** | [approval CSV](cninfo_c_class_review_later_promotion_candidate_approval.csv) · [approval MD](cninfo_c_class_review_later_promotion_candidate_approval.md) | **9/9** `approved_as_candidate` · gate **PASS** |
| 2 | **establishment_date mapper patch planning** | [patch plan](cninfo_c_class_establishment_date_mapper_patch_plan.md) | `PLANNED_NOT_IMPLEMENTED` |
| 3 | **raw_only 25 policy review** | [policy CSV](cninfo_c_class_raw_only_field_policy_review.csv) · [policy MD](cninfo_c_class_raw_only_field_policy_review.md) | **25** 字段政策落账 |
| 4 | **product quality rules draft** | [rules draft](../../plans/cninfo_c_class_product_quality_rules_draft.md) | `product_quality_rules_draft_gate = PASS` |

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`（未整体完成）

---

## 2. 本轮没有做什么

- **no CNINFO**
- **no live**
- **no harvest** / harvest 重跑
- **no raw modification**
- **no normalized modification**
- **no field inventory modification**
- **no mapper patch implementation**（establishment_date 仅 planning）
- **no DB** · **no MinIO** · **no RAG**
- **no registry backfill**
- **no YAML backfill**
- **no verified**
- **no testing_stable_sample** 升级

---

## 3. Open Issues 更新

### 本轮推进

| 原开放项 | 本轮状态 |
|----------|----------|
| review_later promotion candidate approval | **完成**（9 approved） |
| establishment_date mapper patch | **planning 完成**；implementation 待下一轮 |
| raw_only 25 最终政策 | **policy review 完成** |
| product quality rules | **draft 完成** |

### 仍开放

| # | 开放项 |
|---|--------|
| 1 | establishment_date **mapper patch implementation** |
| 2 | company_snapshot planning |
| 3 | security observe decision |
| 4 | hold / BSE / abnormal side-track |
| 5 | registry backfill planning |
| 6 | field inventory 正式升格（9 candidate + establishment_date 待 patch 后） |
| 7 | dividend manual review queue（10）· parser patch later（2）— 已 classification，非阻塞 |

---

## 4. 关键指标汇总

| 指标 | 值 |
|------|-----|
| promotion_candidate_approval_gate | **PASS** |
| approved_as_candidate | **9** |
| establishment_date | **excluded**（mapper patch required） |
| raw_only policy reviewed | **25** |
| product_quality_rules_draft_gate | **PASS** |
| harvest_full_gate | **PASS_WITH_RESUME**（不变） |

### raw_only 政策分布

| policy | count |
|--------|-------|
| observe_only_excluded | 14 |
| keep_raw_only_permanently | 7 |
| keep_raw_only_for_now | 2 |
| convert_to_review_later_candidate | 1 |
| lineage_only | 1 |

---

## 5. 推荐下一步

**默认推荐：establishment_date mapper patch implementation**

范围：

1. `map_company_basic_profile()` 增加 `F010D` → `establishment_date`
2. fixture 4 case（normal · empty · nonstandard · null）
3. offline re-map `normalized/company_basic_profile/` only
4. **不请求 CNINFO** · **不修改 raw**

**并行可规划（本轮不执行）：** company_snapshot · security observe · hold/BSE 文档化

---

## 红线确认

- 未请求 CNINFO · 未重跑 harvest
- raw / normalized / field inventory **未改**
- 未写 verified · 未升级 testing_stable_sample

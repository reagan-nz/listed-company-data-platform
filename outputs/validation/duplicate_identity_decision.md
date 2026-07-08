# Duplicate Identity Decision（设计 · 未执行）

_生成时间：2026-07-08T09:26:48Z_

> **性质：** duplicate_identity 快速分诊决策备忘。**不合并** · **不修改 candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## 案例

| 项 | 值 |
|----|-----|
| review_id | REVIEW_0508 |
| conflict_id | CONFLICT_0508_839729_920729 |
| company_code_1 | 839729 |
| company_code_2 | 920729 |
| company_name | 永顺生物 |
| conflict_reason | legacy_code_duplicate |
| canonical_candidate | CNINFO_920729 |

---

## 设计决策（未执行）

| 项 | 决议 |
|----|------|
| **关系** | 同一公司 legacy_code 重复登记（839729 / 920729） |
| **recommended_action** | `approved_mapping_candidate`（与 BSE legacy 队列一致） |
| **canonical** | **CNINFO_920729** |
| **839729 行** | 保持独立 · 标 `duplicate_code` |
| **merge** | **禁止** |
| **review_status** | **pending**（待 manual signoff） |

---

## 红线

- 不合并 harvest / snapshot 数据
- 不修改 registry candidate CSV

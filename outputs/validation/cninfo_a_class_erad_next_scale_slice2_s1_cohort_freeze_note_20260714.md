# CNINFO A 类 Next-Scale Slice2 S1 Cohort — Freeze Note

_生成时间：2026-07-14_

> **offline cohort freeze note only** · **CNINFO = 0** · **NOT APPROVED live** · **NOT APPROVED runner** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

---

## 1. 冻结摘要

| 项 | 值 |
|----|-----|
| Task | **A-GEN-20260714-09** |
| Controller 决策 | **S1 ST-EXCLUDE** · **+100 non-ST** · **O3** |
| 批准来源 | Human APPROVED: A-class next-scale progression based on coverage-gap analysis |
| 主路径 candidate | `cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv` |
| lint 报告 | `cninfo_a_class_erad_next_scale_slice2_s1_plus100_lint_check_20260714.md` |
| case_id | **AD2E501** – **AD2E600**（连续） |
| cohort 标签 | `next_scale_slice2` |
| 行数 | **100** |
| ST 名称命中 | **0** |

---

## 2. 选取规则（冻结）

1. 源池：[remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv)（**156** 码 · 未 mutate）
2. ST 策略：**S1** — `FILTER_ST(company_name)` 剔除全部 `(?:\*?ST|S\*ST)` 命中（[strategy §3.1](cninfo_a_class_slice2_st_selection_strategy_20260714.md)）
3. 排序：`company_code` 升序
4. 规模：取前 **100** 非 ST 码
5. overlap 治理：**O3** — 严格_disjoint from A_ALL_U · B_CUM · AB_182（[overlap lint spec §4.3](cninfo_a_class_slice2_overlap_lint_spec_20260714.md)）

---

## 3. 被取代路径（superseded · 只读保留）

下列 planning draft **不再作为 primary path**；文件 **未 mutate**，仅供审计对照：

| 产物 | case_id | ST | L-D4 | 状态 |
|------|---------|-----|------|------|
| `cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv` | AD2E501–600 | **48**/100 | CAVEAT | **superseded**（S4 码升序） |
| `cninfo_a_class_erad_next_scale_slice2_plus50_candidate_draft_20260714.csv` | AD2E601–650 | **0**/50 | PASS | **superseded**（S4 complement） |

**说明：** 新 S1 +100 复用 AD2E501–600 case 区间，但 `company_code` 映射已按 ST-EXCLUDE 重算；不得将旧 draft 与 freeze note 混为同一 lineage。

---

## 4. Lint 签收（离线）

| 检查 | 结果 |
|------|------|
| L-A1..L-A4 vs slice1 / A cumulative | **PASS** |
| L-B1..L-B4 vs B disjoint | **PASS** |
| L-P1..L-P3 | **PASS** |
| L-D4 ST count | **0** — **PASS** |
| L-D5 unresolved side-track | **PASS** |
| S2 ∩ AB_182 | **PASS**（0） |
| 综合 lint verdict | **PASS** |

详见 [lint check](cninfo_a_class_erad_next_scale_slice2_s1_plus100_lint_check_20260714.md)。

---

## 5. 余量状态

| 池 | 码数 | 说明 |
|----|------|------|
| REMAINDER 全集 | 156 | 不变 |
| S1 +100 已选 | 100 | 全非 ST |
| 未选非 ST | 8 | 688777–688818 |
| 未选 ST | 48 | 低号段 · S1 永久排除 |
| 非 ST 可达上界 | 108 | +8 扩批仍可行（须新任务） |

---

## 6. 写保护与未批准项

| 约束 | 状态 |
|------|------|
| CNINFO 调用 | **0** |
| live / dry-run / runner | **NOT APPROVED** |
| mutate 182 台账 | **禁止**（[ab_overlap_182_ledger](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)） |
| mutate remainder CSV | **禁止** |
| mutate 旧 +100/+50 draft | **禁止** |
| gate flip / production_ready | **NOT claimed** |
| 182 治理 | **PENDING_CONTROLLER**（O3 记账） |
| push / commit | **未执行**（本任务范围外） |

---

## 7. 下一步（非本任务批准）

- Controller 182 治理选项终裁（O1–O4）仍为 `PENDING_CONTROLLER`
- live approval phrase · request budget · session 切分：**未批准**
- 若需 +8 非 ST complement 或 +108 全量非 ST：**须新任务** · 新 case_id 自 AD2E601 起

---

## 8. 证据链

- [S1 +100 candidate](cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv)
- [S1 lint check](cninfo_a_class_erad_next_scale_slice2_s1_plus100_lint_check_20260714.md)
- [st selection strategy](cninfo_a_class_slice2_st_selection_strategy_20260714.md)
- [remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv)
- [overlap lint spec](cninfo_a_class_slice2_overlap_lint_spec_20260714.md)
- [A∩B 182 ledger](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)

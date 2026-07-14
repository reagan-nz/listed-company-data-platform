# CNINFO A 类 Next-Scale Slice2 S1 +100 Candidate Universe — Lint Check

_生成时间：2026-07-14_

> **offline planning draft only** · **CNINFO = 0** · **NOT APPROVED live** · **NOT APPROVED runner** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

---

## 1. 任务与产物

| 项 | 值 |
|----|-----|
| Task | **A-GEN-20260714-09** |
| 产物 | `cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv` |
| ST 策略 | **S1 ST-EXCLUDE**（[st selection strategy](cninfo_a_class_slice2_st_selection_strategy_20260714.md) §3.1） |
| 选取规则 | REMAINDER 剔除 ST 名称命中码后 · 按 `company_code` 升序取前 **100** |
| case_id 区间 | **AD2E501** – **AD2E600**（连续无空洞） |
| cohort | `next_scale_slice2` |
| 治理选项 | **O3**（slice2 严格_disjoint · 182 仅记账 · `PENDING_CONTROLLER`） |
| 被取代 draft（只读引用） | `cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv`（S4 · 48 ST） · `cninfo_a_class_erad_next_scale_slice2_plus50_candidate_draft_20260714.csv`（AD2E601–650） |

---

## 2. 计数摘要

| 指标 | 值 |
|------|-----|
| REMAINDER 池 | **156** |
| REMAINDER 内 ST 名称命中 | **48** |
| REMAINDER 内非 ST | **108** |
| S2_S1_PLUS100 行数 | **100** |
| 未选用非 ST 余量 | **8**（688777–688818） |
| 首码 / 末码 | `603701` / `688772` |
| ST 名称命中（L-D4） | **0** / 100 |
| CNINFO 调用 | **0** |

### 2.1 ST 检测规则

```
ST_NAME_HIT := company_name 匹配 /(?:\*?ST|S\*ST)/
```

与 [st selection strategy §2.3](cninfo_a_class_slice2_st_selection_strategy_20260714.md) 一致。

### 2.2 未选用的 8 码（非 ST remainder 尾部）

| company_code | company_name |
|--------------|--------------|
| 688777 | 中控技术 |
| 688781 | 视涯科技 |
| 688785 | 恒运昌 |
| 688786 | 悦安新材 |
| 688795 | 摩尔线程 |
| 688797 | 臻宝科技 |
| 688809 | 强一股份 |
| 688818 | 电科蓝天 |

**说明：** 108 非 ST − 100 选取 = **8**；S1 下非 ST remainder 上界为 108。

### 2.3 与 slice1 cumulative 对照

| 对照集 | 规模 | S2_S1 ∩ 对照 | ST（对照侧） |
|--------|------|--------------|--------------|
| A_S1_U（slice1 universe） | 300 | **0** | 0 |
| A_CUM_EFF（scale-200 effective ∪ slice1 effective） | 486 | **0** | — |
| A_ALL_U | 500 | **0** | — |
| slice1 L-D4 基线 | 300 码 ST=0 | 同型对齐 | **PASS** |

---

## 3. Overlap Lint 结果

设 **S2_S1_PLUS100** = 本 candidate 的 `company_code` 集合（100 码）。

### 3.1 A 轨零 overlap

| 规则 ID | 断言 | 结果 | 交集计数 |
|---------|------|------|----------|
| **L-A1** | S2_S1_PLUS100 ∩ A_ALL_U | **PASS** | **0** |
| **L-A2** | S2_S1_PLUS100 ∩ A_CUM_EFF | **PASS** | **0** |
| **L-A3** | S2_S1_PLUS100 ∩ A_S200_U | **PASS** | **0** |
| **L-A4** | S2_S1_PLUS100 ∩ A_S1_U | **PASS** | **0** |

### 3.2 B 轨零 overlap

| 规则 ID | 断言 | 结果 | 交集计数 |
|---------|------|------|----------|
| **L-B1** | S2_S1_PLUS100 ∩ B_CUM | **PASS** | **0** |
| **L-B2** | S2_S1_PLUS100 ∩ B_S200_U | **PASS** | **0** |
| **L-B3** | S2_S1_PLUS100 ∩ B_S1_U | **PASS** | **0** |
| **L-B4** | S2_S1_PLUS100 ∩ B_S2_U | **PASS** | **0** |

### 3.3 源池与余量

| 规则 ID | 断言 | 结果 | 说明 |
|---------|------|------|------|
| **L-P1** | S2_S1_PLUS100 ⊆ POOL（889） | **PASS** | 100/100 在池内 |
| **L-P2** | S2_S1_PLUS100 ⊆ REMAINDER | **PASS** | 100/100 ⊆ remainder |
| **L-P3** | \|S2_S1_PLUS100\| ≤ 156 | **PASS** | 100 ≤ 156 |

### 3.4 草案内部完整性

| 规则 ID | 断言 | 结果 | 说明 |
|---------|------|------|------|
| **L-D1** | `company_code` 无重复 | **PASS** | unique = 100 |
| **L-D2** | `case_id` 无重复 · AD2E501+ 连续 | **PASS** | AD2E501–AD2E600 |
| **L-D3** | cohort = `next_scale_slice2` | **PASS** | 统一 |
| **L-D4** | 非 BSE · 非 ST | **PASS** | ST 名称命中 **0** |
| **L-D5** | 不含 unresolved side-track 码 | **PASS** | 对照 14 案无命中 |

### 3.5 A∩B 182 台账

| 检查项 | 结果 | 交集计数 |
|--------|------|----------|
| S2_S1_PLUS100 ∩ AB_182 | **PASS** | **0** |

**说明：** [182 台账](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv) 码已全部从 REMAINDER 扣减；O3 下本 cohort 不引入新 A∩B 交叉。

### 3.6 与已取代 S4 draft 的差异（信息性 · 非 FAIL）

| 对照 | 交集 | 说明 |
|------|------|------|
| S2_S1_PLUS100 ∩ 旧 +100 draft（S4） | **52** | 旧 draft 低号段非 ST 段重合 |
| S2_S1_PLUS100 ∩ 旧 +50 draft | **48** | 旧 +50 全非 ST · 落入 S1 前 100 非 ST 面 |
| 旧 +100 draft 独有（ST 码） | **48** | S1 已排除 · 不进入本 cohort |
| case_id AD2E501–600 | 复用 case 空间 | **company_code 映射已变更** · 旧文件未 mutate |

---

## 4. Lint 总判定

| 维度 | 判定 |
|------|------|
| L-A1..L-A4 | **PASS** |
| L-B1..L-B4 | **PASS** |
| L-P1..L-P3 | **PASS** |
| L-D1..L-D3 · L-D5 | **PASS** |
| **L-D4（ST）** | **PASS**（**0** / 100） |
| AB_182 disjoint | **PASS** |
| **综合 lint verdict** | **PASS** |

---

## 5. 选取影响

| 影响面 | 说明 |
|--------|------|
| A cumulative | 不变；与 A_S200_U ∪ A_S1_U 零交集 |
| B cumulative | 不变；与 B_S200 ∪ B_S1 ∪ B_S2 零交集 |
| REMAINDER | 156 中选取 100 非 ST · 余 **8** 非 ST + **48** ST 未选 |
| case 空间 | 占用 AD2E501–AD2E600（与旧 S4 +100 同区间 · 码映射不同） |
| slice1 同型 | ST=0 · 对齐 universe strategy §3.1 |
| 旧 +100/+50 draft | **superseded**（primary path）· 文件保留只读 |

---

## 6. Governance

| 字段 | 值 |
|------|------|
| live | **NOT APPROVED** |
| CNINFO | **0** |
| current gate | **HOLD preserved** |
| ST 策略 | **S1 ST-EXCLUDE** |
| cohort 规模 | **+100 non-ST planning candidate** |
| O3 / 182 | **PENDING_CONTROLLER**（记账 only） |
| verified / production_ready | **NOT claimed** |
| human freeze | 见 [cohort freeze note](cninfo_a_class_erad_next_scale_slice2_s1_cohort_freeze_note_20260714.md) |

---

## 7. 证据链

- [S1 +100 candidate universe](cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv)
- [st selection strategy](cninfo_a_class_slice2_st_selection_strategy_20260714.md)
- [remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv)
- [overlap lint spec](cninfo_a_class_slice2_overlap_lint_spec_20260714.md)
- [A∩B 182 ledger](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)
- [旧 +100 draft（superseded）](cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv)
- [旧 +50 draft（superseded）](cninfo_a_class_erad_next_scale_slice2_plus50_candidate_draft_20260714.csv)

# CNINFO A 类 Next-Scale Slice2 +50 Complement Candidate Draft — Lint Check

_生成时间：2026-07-14_

> **offline planning draft only** · **CNINFO = 0** · **NOT APPROVED live** · **NOT APPROVED runner** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

---

## 1. 任务与产物

| 项 | 值 |
|----|-----|
| Task | A-GEN-20260714-07 |
| 产物 | `cninfo_a_class_erad_next_scale_slice2_plus50_candidate_draft_20260714.csv` |
| 选取规则 | REMAINDER 扣除 +100 draft 后余 **56** 码 · 按 `company_code` 升序取前 **50** |
| case_id 区间 | **AD2E601** – **AD2E650**（连续无空洞） |
| cohort | `next_scale_slice2` |
| 治理选项 | **O3**（slice2 严格_disjoint · 182 仅记账 · `PENDING_CONTROLLER`） |
| 上游 +100 draft | `cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv`（AD2E501–AD2E600） |

---

## 2. 计数摘要

| 指标 | 值 |
|------|-----|
| REMAINDER 池 | **156** |
| +100 draft 已选 | **100** |
| +100 后余量（unused） | **56** |
| S2_PLUS50 行数 | **50** |
| 仍未选用（unused remainder） | **6** |
| 首码 / 末码 | `688351` / `688781` |
| ST 名称命中（L-D4 参考） | **0** / 50 |
| CNINFO 调用 | **0** |

### 2.1 仍未选用的 6 码（remainder 余量）

| company_code | company_name |
|--------------|--------------|
| 688785 | 恒运昌 |
| 688786 | 悦安新材 |
| 688795 | 摩尔线程 |
| 688797 | 臻宝科技 |
| 688809 | 强一股份 |
| 688818 | 电科蓝天 |

**说明：** 156 − 100（+100）− 50（+50）= **6**；若 Controller 后续冻结 +56 全量 complement，可直接取上述 6 码。

---

## 3. Overlap Lint 结果

设 **S2_PLUS50** = 本 draft 的 `company_code` 集合（50 码）。  
设 **S2_PLUS100** = +100 draft 的 `company_code` 集合（100 码）。

### 3.1 与 +100 draft 互斥（complement 硬约束）

| 检查项 | 断言 | 结果 | 交集计数 |
|--------|------|------|----------|
| **COMP-1** | S2_PLUS50 ∩ S2_PLUS100 | **PASS** | **0** |
| **COMP-2** | S2_PLUS50 ∪ S2_PLUS100 ⊆ REMAINDER | **PASS** | 150/150 ⊆ remainder |

### 3.2 A 轨零 overlap

| 规则 ID | 断言 | 结果 | 交集计数 |
|---------|------|------|----------|
| **L-A1** | S2_PLUS50 ∩ A_ALL_U | **PASS** | **0** |
| **L-A2** | S2_PLUS50 ∩ A_CUM_EFF | **PASS** | **0** |
| **L-A3** | S2_PLUS50 ∩ A_S200_U | **PASS** | **0** |
| **L-A4** | S2_PLUS50 ∩ A_S1_U | **PASS** | **0** |

### 3.3 B 轨零 overlap

| 规则 ID | 断言 | 结果 | 交集计数 |
|---------|------|------|----------|
| **L-B1** | S2_PLUS50 ∩ B_CUM | **PASS** | **0** |
| **L-B2** | S2_PLUS50 ∩ B_S200_U | **PASS** | **0** |
| **L-B3** | S2_PLUS50 ∩ B_S1_U | **PASS** | **0** |
| **L-B4** | S2_PLUS50 ∩ B_S2_U | **PASS** | **0** |

### 3.4 源池与余量

| 规则 ID | 断言 | 结果 | 说明 |
|---------|------|------|------|
| **L-P1** | S2_PLUS50 ⊆ POOL（889） | **PASS** | 50/50 在池内 |
| **L-P2** | S2_PLUS50 ⊆ REMAINDER | **PASS** | 50/50 ⊆ remainder |
| **L-P3** | \|S2_PLUS50\| ≤ 156 | **PASS** | 50 ≤ 156 |

### 3.5 草案内部完整性

| 规则 ID | 断言 | 结果 | 说明 |
|---------|------|------|------|
| **L-D1** | `company_code` 无重复 | **PASS** | unique = 50 |
| **L-D2** | `case_id` 无重复 · AD2E601+ 连续 | **PASS** | AD2E601–AD2E650 |
| **L-D3** | cohort = `next_scale_slice2` | **PASS** | 统一 |
| **L-D4** | 非 BSE · 非 ST | **PASS** | 0 码名称含 ST |
| **L-D5** | 不含 unresolved side-track 码 | **PASS** | 离线对照无命中 |

### 3.6 A∩B 182 台账

| 检查项 | 结果 | 交集计数 |
|--------|------|----------|
| S2_PLUS50 ∩ AB_182 | **PASS** | **0** |

**说明：** 182 码为历史 A slice1 ∩ B slice2 交叉记账（`resolution_status=PENDING_CONTROLLER`），已全部从 REMAINDER 扣减；本 complement draft 不引入新交叉。

---

## 4. 选取影响

| 影响面 | 说明 |
|--------|------|
| +100 draft | 互斥；S2_PLUS50 ∩ S2_PLUS100 = ∅ |
| A cumulative | 不变；S2_PLUS50 与 A_S200_U ∪ A_S1_U 零交集 |
| B cumulative | 不变；S2_PLUS50 与 B_S200 ∪ B_S1 ∪ B_S2 零交集 |
| REMAINDER | 156 → +100 占 100 · +50 占 50 · 余 **6** 未选 |
| case 空间 | 占用 AD2E601–AD2E650（接续 +100 的 AD2E501–AD2E600） |
| 合并 slice2 规划 | +100 ∪ +50 = **150** 码 · AD2E501–AD2E650 · 均 ⊆ REMAINDER |
| ST 占比 | +50 批次 ST 名称 **0** 码（高号段 688 科创板为主） |

---

## 5. Governance

| 字段 | 值 |
|------|-----|
| live | **NOT APPROVED** |
| CNINFO | **0** |
| current gate | **HOLD preserved** |
| cohort 规模 | **+50 complement planning draft only** |
| O3 / 182 | **PENDING_CONTROLLER**（记账 only · 不进入 S2_PLUS50） |
| verified / production_ready | **NOT claimed** |
| human freeze / approval | **NOT claimed** |

---

## 6. 证据链

- [+50 complement candidate draft](cninfo_a_class_erad_next_scale_slice2_plus50_candidate_draft_20260714.csv)
- [+100 candidate universe draft](cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv)
- [remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv)
- [overlap lint spec](cninfo_a_class_slice2_overlap_lint_spec_20260714.md)
- [A∩B 182 ledger](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)

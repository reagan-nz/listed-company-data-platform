# CNINFO A 类 Next-Scale Slice2 Candidate Universe Draft — Lint Check

_生成时间：2026-07-14_

> **offline planning draft only** · **CNINFO = 0** · **NOT APPROVED live** · **NOT APPROVED runner** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

---

## 1. 任务与产物

| 项 | 值 |
|----|-----|
| Task | A-GEN-20260714-06（replanned） |
| 产物 | `cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv` |
| 选取规则 | REMAINDER 按 `company_code` 升序 · 取前 **100** |
| case_id 区间 | **AD2E501** – **AD2E600**（连续无空洞） |
| cohort | `next_scale_slice2` |
| 治理选项 | **O3**（slice2 严格_disjoint · 182 仅记账 · `PENDING_CONTROLLER`） |

---

## 2. 计数摘要

| 指标 | 值 |
|------|-----|
| REMAINDER 池 | **156** |
| S2_DRAFT 行数 | **100** |
| REMAINDER 余量（未选） | **56** |
| 首码 / 末码 | `000416` / `688350` |
| ST 名称命中（L-D4 参考） | **48** / 100 |
| CNINFO 调用 | **0** |

---

## 3. Overlap Lint 结果

设 **S2_DRAFT** = 本 draft 的 `company_code` 集合（100 码）。

### 3.1 A 轨零 overlap

| 规则 ID | 断言 | 结果 | 交集计数 |
|---------|------|------|----------|
| **L-A1** | S2_DRAFT ∩ A_ALL_U | **PASS** | **0** |
| **L-A2** | S2_DRAFT ∩ A_CUM_EFF | **PASS** | **0** |
| **L-A3** | S2_DRAFT ∩ A_S200_U | **PASS** | **0** |
| **L-A4** | S2_DRAFT ∩ A_S1_U | **PASS** | **0** |

### 3.2 B 轨零 overlap

| 规则 ID | 断言 | 结果 | 交集计数 |
|---------|------|------|----------|
| **L-B1** | S2_DRAFT ∩ B_CUM | **PASS** | **0** |
| **L-B2** | S2_DRAFT ∩ B_S200_U | **PASS** | **0** |
| **L-B3** | S2_DRAFT ∩ B_S1_U | **PASS** | **0** |
| **L-B4** | S2_DRAFT ∩ B_S2_U | **PASS** | **0** |

### 3.3 源池与余量

| 规则 ID | 断言 | 结果 | 说明 |
|---------|------|------|------|
| **L-P1** | S2_DRAFT ⊆ POOL（889） | **PASS** | 100/100 在池内 |
| **L-P2** | S2_DRAFT ⊆ REMAINDER | **PASS** | 100/100 ⊆ remainder |
| **L-P3** | \|S2_DRAFT\| ≤ 156 | **PASS** | 100 ≤ 156 |

### 3.4 草案内部完整性

| 规则 ID | 断言 | 结果 | 说明 |
|---------|------|------|------|
| **L-D1** | `company_code` 无重复 | **PASS** | unique = 100 |
| **L-D2** | `case_id` 无重复 · AD2E501+ 连续 | **PASS** | AD2E501–AD2E600 |
| **L-D3** | cohort = `next_scale_slice2` | **PASS** | 统一 |
| **L-D4** | 非 BSE · 非 ST | **CAVEAT** | 48 码名称含 ST；来自 remainder 低号段确定性选取，非 overlap 违规 |
| **L-D5** | 不含 unresolved side-track 码 | **PASS** | 离线对照无命中 |

### 3.5 A∩B 182 台账

| 检查项 | 结果 | 交集计数 |
|--------|------|----------|
| S2_DRAFT ∩ AB_182 | **PASS** | **0** |

**说明：** 182 码为历史 A slice1 ∩ B slice2 交叉记账（`resolution_status=PENDING_CONTROLLER`），已全部从 REMAINDER 扣减；本 draft 不引入新交叉。

---

## 4. 选取影响

| 影响面 | 说明 |
|--------|------|
| A cumulative | 不变；S2_DRAFT 与 A_S200_U ∪ A_S1_U 零交集 |
| B cumulative | 不变；S2_DRAFT 与 B_S200 ∪ B_S1 ∪ B_S2 零交集 |
| REMAINDER | 156 → 已规划 100 · 余 **56** 可供后续 +50/+56 扩批 |
| case 空间 | 占用 AD2E501–AD2E600（A slice2 专用段） |
| ST 占比 | 首批 100 中 ST 名称 **48** 码；若 Controller 需 slice1 同型非 ST 批次，须改选取策略或重排 remainder（非本任务范围） |

---

## 5. Governance

| 字段 | 值 |
|------|------|
| live | **NOT APPROVED** |
| CNINFO | **0** |
| current gate | **HOLD preserved** |
| cohort 规模 | **+100 planning draft only** |
| O3 / 182 | **PENDING_CONTROLLER**（记账 only · 不进入 S2_DRAFT） |
| verified / production_ready | **NOT claimed** |
| human freeze / approval | **NOT claimed** |

---

## 6. 证据链

- [slice2 candidate universe draft](cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv)
- [remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv)
- [overlap lint spec](cninfo_a_class_slice2_overlap_lint_spec_20260714.md)
- [A∩B 182 ledger](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)

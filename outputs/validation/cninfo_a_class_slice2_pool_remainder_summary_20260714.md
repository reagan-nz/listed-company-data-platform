# CNINFO A 类 Next-Scale Slice2 — Pool Remainder Summary

_生成时间：2026-07-14_

> **offline draft only** · **CNINFO = 0** · **NOT APPROVED live** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

---

## 1. 任务与方法

本包自 [889 non-BSE 候选池](../../lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml) 扣减已知 A/B 已占用 `company_code`，产出 **slice2 remainder draft**（仅余量行，不含已排除码全量会计表）。

**CSV 行策略：** **remainder-only**（每行一条余量码）；`excluded_reason` 对余量行留空；`selected_for_slice2_candidate=false`（本包不选片，仅列余量池）。

**扣减优先级（池内码命中首项即排除）：**

1. `a_scale200_universe`
2. `a_slice1_universe`
3. `b_scale200_universe`
4. `b_slice1_universe`
5. `b_fuller_slice2_universe`

**说明：** scale-200 universe 各 200 码中仅 **20 / 48** 落在 889 池内（大量为 Phase3 retained 大盘，池外不影响 remainder）。A cumulative effective **486** 仅作对照，**本 draft 以 universe 级已执行槽位扣减**，避免 14 个 unresolved 被误放回余量池。

---

## 2. 源池与扣减集计数

| 集合 | 文件 | 全集计数 | 与 889 池交集 |
|------|------|----------|---------------|
| **889 源池** | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` | **889** | **889** |
| A scale-200 universe | `cninfo_a_class_erad_scale_200_universe_draft.csv` | **200** | **20** |
| A slice1 universe | `cninfo_a_class_erad_next_scale_candidate_universe_draft.csv` | **300** | **300** |
| B scale-200 universe | `cninfo_b_class_erad_scale_200_universe_draft.csv` | **200** | **48** |
| B slice1 universe | `cninfo_b_class_erad_next_scale_slice1_effective_accepted_ledger.csv` | **300** | **300** |
| B fuller slice2 universe | `b_class_erad_fuller_next_slice2_report.csv` | **300** | **300** |

**A cumulative effective（对照，非本 draft 主扣减）：** scale-200 **192** + slice1 **294** = **486**（零 code overlap）。

**C hold（`eval_companies_c_class_889_rerun_all6_hold.yaml`）：** **26** 码均在池内，且已全部落入上述 A/B 已占用集合，**不额外改变 remainder**。

---

## 3. Remainder 结果

| 指标 | 值 |
|------|-----|
| 池内已占用（去重） | **733** |
| **Remainder 计数** | **156** |
| 交付 CSV 行数 | **156**（remainder-only） |

**对照：**

| 口径 | 池内占用 | Remainder |
|------|----------|-----------|
| slice1 + B fuller slice2 三片（不含 scale-200 池交集） | **718** | **171** |
| effective + B universe 并集（非主口径） | **730** | **159** |

与 [universe strategy](cninfo_a_class_erad_next_scale_universe_strategy.md) 中 slice1 后 **~289** 估算一致（**889 − 300 − 300 = 289**）；B fuller slice2 再占 **300** 池内码后，理论余量 **≈ −11**，但因 **A slice1 ∩ B slice2** 存在大量交叉，实际去重后余量为 **156**。

---

## 4. 交叉完整性（诚实披露）

| 检查 | 结果 |
|------|------|
| A slice1 ∩ B slice1 | **0**（预期 0） |
| B slice1 ∩ B slice2 | **0**（预期 0） |
| **A slice1 ∩ B slice2** | **182**（全集）· 池内 **182** |
| A scale-200 ∩ B scale-200 | **17** |
| A 全部 universe ∩ B 全部 universe（池内） | **235** |

**解读：** B fuller slice2 与 A slice1 在池内共享 **182** 个码，违反跨轨 disjoint 预期；本 remainder 按**并集去重**扣减，故余量高于 naive「289−300」算术。Controller 在 slice2 universe 冻结前需决定：是否排除与 B slice2 重叠的 A slice1 码、或调整 B slice2 占用口径。

**缺失源文件：** 无

---

## 5. +200 / +300 可行性（自 remainder）

| 目标规模 | 需要码数 | Remainder **156** | 判定 |
|----------|----------|-------------------------------|------|
| **+200（保守）** | 200 | 缺口 **44** | **NOT FEASIBLE** |
| **+300（对称 B）** | 300 | 缺口 **144** | **NOT FEASIBLE** |

在 **零 overlap（A cumulative + B cumulative）** 与 **不扩池** 前提下，当前 remainder **不足以支撑 +200 或 +300** 完整 slice2 规模；可选路径包括：缩小 slice2 至 **≤156**、释放/重议跨轨重叠码、或扩池/新清洗轮次（均需 Controller 裁决，本包不执行）。

---

## 6. Governance

| 字段 | 值 |
|------|-----|
| live | **NOT APPROVED** |
| CNINFO（本包） | **0** |
| current gate | **HOLD preserved**（post-integration） |
| slice2 planning | **READY_FOR_APPROVAL**（remainder draft only） |
| verified / production_ready | **NOT claimed** |

---

## 7. 产出路径

- [remainder draft CSV](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv) — **156** rows
- 前置：[slice2 offline prep](cninfo_a_class_next_scale_slice2_offline_prep_20260714.md)

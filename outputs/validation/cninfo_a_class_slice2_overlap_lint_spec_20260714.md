# CNINFO A 类 Next-Scale Slice2 — Overlap Lint Specification

_生成时间：2026-07-14_

> **offline specification only** · **CNINFO = 0** · **NOT APPROVED live** · **NOT APPROVED runner** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

---

## 1. 目的与范围

本规格书为 **A-class next-scale slice2** 候选 universe draft CSV 的离线 overlap lint 规则，承接：

- [slice2 pool remainder summary](cninfo_a_class_slice2_pool_remainder_summary_20260714.md)（remainder **156**）
- [slice2 offline prep](cninfo_a_class_next_scale_slice2_offline_prep_20260714.md)
- [universe strategy](cninfo_a_class_erad_next_scale_universe_strategy.md)

**本包不：** 生成 slice2 candidate CSV · 调用 CNINFO · 升级 gate · 宣称 verified / production_ready · 发明 Controller 批准。

---

## 2. 输入源（lint 对照集）

| 符号 | 文件 | 计数 | lint 角色 |
|------|------|------|-----------|
| **POOL** | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` | **889** | 源池上界 |
| **A_S200_U** | `cninfo_a_class_erad_scale_200_universe_draft.csv` | 200 | A scale-200 universe |
| **A_S1_U** | `cninfo_a_class_erad_next_scale_candidate_universe_draft.csv` | 300 | A slice1 universe |
| **A_CUM_EFF** | scale-200 effective **192** ∪ slice1 effective **294** | **486** | A cumulative effective（零内部 overlap） |
| **A_ALL_U** | A_S200_U ∪ A_S1_U | **500** | A 全部已规划 universe |
| **B_S200_U** | `cninfo_b_class_erad_scale_200_universe_draft.csv` | 200 | B scale-200 universe |
| **B_S1_U** | `cninfo_b_class_erad_next_scale_slice1_effective_accepted_ledger.csv` | 300 | B slice1 accepted |
| **B_S2_U** | `cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv` | 300 | B fuller slice2 universe |
| **B_CUM** | B_S200_U ∪ B_S1_U ∪ B_S2_U | **800** | B cumulative universe |
| **REMAINDER** | `cninfo_a_class_slice2_pool_remainder_draft_20260714.csv` | **156** | slice2 可选余量池 |
| **AB_182** | [A∩B 冲突台账](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv) | **182** | 已知跨轨冲突（治理用，非 slice2 新增码） |

**扣减优先级（与 remainder draft 一致）：** 池内码命中下列首项即不得进入 slice2 候选：

1. A_S200_U → 2. A_S1_U → 3. B_S200_U → 4. B_S1_U → 5. B_S2_U

---

## 3. 硬规则（FAIL = 阻断 draft 进入 approval package）

设 **S2_DRAFT** 为待检 slice2 candidate universe 的 `company_code` 集合。

### 3.1 A 轨零 overlap

| 规则 ID | 断言 | 期望 |
|---------|------|------|
| **L-A1** | S2_DRAFT ∩ A_ALL_U | **∅** |
| **L-A2** | S2_DRAFT ∩ A_CUM_EFF | **∅** |
| **L-A3** | S2_DRAFT ∩ A_S200_U | **∅** |
| **L-A4** | S2_DRAFT ∩ A_S1_U | **∅** |

**说明：** L-A2 为 lineage 不重跑硬约束；L-A1 覆盖含 unresolved 槽位在内的全部 A universe 规划码。

### 3.2 B 轨零 overlap（跨类 disjoint）

| 规则 ID | 断言 | 期望 |
|---------|------|------|
| **L-B1** | S2_DRAFT ∩ B_CUM | **∅** |
| **L-B2** | S2_DRAFT ∩ B_S200_U | **∅** |
| **L-B3** | S2_DRAFT ∩ B_S1_U | **∅** |
| **L-B4** | S2_DRAFT ∩ B_S2_U | **∅** |

### 3.3 源池与余量

| 规则 ID | 断言 | 期望 |
|---------|------|------|
| **L-P1** | S2_DRAFT ⊆ POOL | 全部在 889 池内 |
| **L-P2** | S2_DRAFT ⊆ REMAINDER | 在未扩池前提下 **必须** |
| **L-P3** | \|S2_DRAFT\| ≤ \|REMAINDER\| = **156** | 不扩池时上界 |

**L-P2 例外：** 仅当 Controller 显式批准 **扩池 / 新清洗轮次** 后，方可放宽；须附带新 POOL 版本号与独立 approval phrase（本规格不预设）。

### 3.4 草案内部完整性

| 规则 ID | 断言 | 期望 |
|---------|------|------|
| **L-D1** | `company_code` 无重复 | unique |
| **L-D2** | `case_id` 无重复 · 起始于 **AD2E501** | 单调递增 · 与 B BD2E501+ **case 空间独立** |
| **L-D3** | cohort = `next_scale_slice2` | 统一 |
| **L-D4** | 非 BSE · 非 ST（与 slice1 同型） | 与 universe strategy §3.1 一致 |
| **L-D5** | 不得包含 scale-200 / slice1 **unresolved side-track** 码 | 引用 unresolved6 packaging |

### 3.5 写保护与 side-track

| 规则 ID | 政策 |
|---------|------|
| **L-W1** | Phase 3 production root **禁止 mutation** |
| **L-W2** | A3M017 **reference-only** · 不得进入 S2_DRAFT |
| **L-W3** | scale-200 8 unresolved · slice1 6 unresolved：**side-track only** · `live_needed=no` |

---

## 4. 已知 A slice1 ∩ B fuller slice2 = 182 冲突

### 4.1 事实（离线复核）

| 指标 | 值 | 源 |
|------|-----|-----|
| A_S1_U ∩ B_S2_U（全集） | **182** | 双 universe draft 交集 |
| 池内 | **182** | 全部 ∈ POOL |
| A slice1 effective 命中 | **180** `accepted_effective` · **2** 未入 effective ledger | [182 台账](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv) |
| B slice2 live 命中 | **179** `found` · **2** `empty_response` · **1** `network_error` | B fuller slice2 live report |

**性质：** 违反 [universe strategy §5](cninfo_a_class_erad_next_scale_universe_strategy.md) 跨类 **disjoint company_code** 预期；该 182 码**已**被 remainder 扣减（并集去重），**不会**出现在 REMAINDER **156** 中。

### 4.2 与 slice2 lint 的关系

- **L-B4 / L-A4 对 S2_DRAFT：** 182 码天然不满足「可入选 slice2」——它们已在 A_S1_U 与 B_S2_U 中；任何合规 S2_DRAFT 必与之不交。
- **治理问题：** 182 是 **历史规划交叉**，不是 slice2 新引入 overlap；需在 Controller 层裁决「双轨归属」口径，**本规格不代为批准**。

### 4.3 治理选项（仅文档 · 无默认批准）

| 选项 | 描述 | A-class slice2 影响 | 依赖 |
|------|------|---------------------|------|
| **O1 — B 保留 · A 承认交叉** | B fuller slice2 已 live（299/300）· A 在台账层标记 182 为 cross-track duplicate · slice2 从 REMAINDER 选码 | S2_DRAFT lint 不变 · 182 不进 S2_DRAFT | Controller 接受 A cumulative 与 B cumulative 在 182 码上 **非 disjoint 事实** |
| **O2 — A slice1 优先归属** | 182 在 B 轨视为 overlap 违规 · 需 B-track 重议/剔除（**非 A executor 范围**） | 若 B 释放码回池，REMAINDER 需 **重算**（可能 >156） | B-track approval · 新 remainder draft |
| **O3 — 双轨并行引用 · slice2 严格_disjoint** | 182 保持现状 · A slice2 仅从 REMAINDER 推进 · 交叉仅记账 | **推荐作为 lint 默认路径**（与当前 remainder 一致） | 无额外 live |
| **O4 — 扩池** | 889 池外增补候选 | L-P2 放宽 · 需新 POOL 版本 | Controller 扩池批准 |

**Executor 立场：** 在 Controller 未裁决前，slice2 candidate 生成与 lint **采用 O3**（从 REMAINDER 选取 · 零 overlap 硬检不变）· `resolution_status=PENDING_CONTROLLER` 保留于 182 台账。

---

## 5. Cohort 规模选项（remainder 156 约束）

在 **零 overlap · 不扩池 · 仅从 REMAINDER 选取** 前提下：

| 目标规模 | 需要码数 | REMAINDER | 余量/缺口 | 判定 | 备注 |
|----------|----------|-----------|-----------|------|------|
| **+50** | 50 | 156 | +106 | **FEASIBLE** | 烟雾 / 试点片 |
| **+100** | 100 | 156 | +56 | **FEASIBLE** | 保守首批 · 推荐下限 |
| **+150** | 150 | 156 | +6 | **FEASIBLE** | 接近余量上限 · 缓冲极小 |
| **+156** | 156 | 156 | 0 | **FEASIBLE** | **不扩池绝对上限** |
| **+200** | 200 | 156 | 缺口 **44** | **NOT FEASIBLE** | 需 O2/O4 或缩目标 |
| **+300** | 300 | 156 | 缺口 **144** | **NOT FEASIBLE** | 与 B fuller slice2 对称不可达 |

**规划建议（非批准）：**

- 若 Controller 冻结 slice2 首批：**+100** 或 **+150** 为当前池内可达区间。
- **+200 / +300** 需先完成：扩池 · 或 B 轨释放码 · 或跨轨重议（见 §4.3）— **不得** 假定 remainder 单独可满足。

---

## 6. 未来 slice2 draft CSV 验收清单

对 `cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft.csv`（名称待定）执行：

### 6.1 自动 lint（脚本 / dry-run 前）

```
PASS  L-A1 .. L-A4
PASS  L-B1 .. L-B4
PASS  L-P1, L-P2（或已批准扩池例外）
PASS  L-D1 .. L-D5
PASS  L-W1 .. L-W3（runner write-block 配置审计）
```

### 6.2 计数验收

| 检查项 | 期望 |
|--------|------|
| 行数 | = Controller 冻结目标（≤156 若不扩池） |
| AD2E501+ 连续 | 无空洞 · 无与 A/B 已用 case_id 冲突 |
| POOL 外码 | **0** |
| ST / BSE | **0**（除非显式例外表） |

### 6.3 交叉复核（与 remainder 对齐）

| 检查项 | 期望 |
|--------|------|
| S2_DRAFT \ REMAINDER | **∅**（不扩池时） |
| REMAINDER \ (A_ALL_U ∪ B_CUM) | 应等于 REMAINDER（余量定义自洽） |
| S2_DRAFT ∩ AB_182 | **∅**（182 已占用 · 不可重选） |

### 6.4 产出物

| 产物 | 条件 |
|------|------|
| overlap lint report CSV | 每码每条规则 pass/fail |
| lint summary md | 汇总 FAIL 规则与冲突码清单 |
| 若任一 L-A* / L-B* FAIL | gate 保持 **FAIL_REVIEW_REQUIRED** · 不得进入 live approval |

### 6.5 人工签收（Controller · 非本包）

- [ ] 冻结 cohort 规模（≤156 或扩池后新上限）
- [ ] 182 冲突治理选项（§4.3）择一
- [ ] 新 human approval phrase（slice1 phrase 已 spent）
- [ ] request budget 与 session 切分（参照 offline prep §5）

---

## 7. 182 台账

**已交付：** [cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)

| 字段 | 说明 |
|------|------|
| `company_code` | 冲突码 |
| `a_slice1_case_id` / `b_slice2_case_id` | 双轨 case 对照 |
| `a_slice1_final_effective_status` | A slice1 effective 状态 |
| `b_slice2_retrieval_status` | B slice2 live 检索状态 |
| `resolution_status` | 固定 **PENDING_CONTROLLER**（未发明批准） |

**缺失源文件：** 无（182 码可完全离线推导）

---

## 8. Governance

| 字段 | 值 |
|------|------|
| live | **NOT APPROVED** |
| CNINFO（本包） | **0** |
| current gate | **HOLD preserved**（post-integration） |
| slice2 planning | **READY_FOR_APPROVAL**（lint spec only） |
| lint spec gate | **READY_FOR_APPROVAL** |
| verified / production_ready | **NOT claimed** |

---

## 9. 证据链

- [remainder summary](cninfo_a_class_slice2_pool_remainder_summary_20260714.md)
- [remainder draft CSV](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv)
- [slice2 offline prep](cninfo_a_class_next_scale_slice2_offline_prep_20260714.md)
- [universe strategy](cninfo_a_class_erad_next_scale_universe_strategy.md)
- [A∩B 182 ledger](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)

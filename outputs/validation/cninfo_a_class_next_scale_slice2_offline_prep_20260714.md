# CNINFO A 类 Era D — Next-Scale Slice2 Offline Preparation

_生成时间：2026-07-14_

> **offline planning only** · **CNINFO = 0** · **NOT APPROVED live** · **NOT APPROVED runner** · **NOT verified** · **NOT production_ready**

---

## 1. Position in Staged Path

| 阶段 | case_id 范围 | 状态 | effective 信号 |
|------|-------------|------|----------------|
| Era D scale-200 | AD2E001–200 | committed `41dc049` · closed | **192/200** |
| Next-scale slice1 | AD2E201–500 | committed `4118974` · merge `71a83c1` · **HOLD** | **294/300** |
| **Next-scale slice2（本包）** | **AD2E501+** | **planning only** | **0**（未规划 live） |
| Fuller 第三阶段 | slice3+ | 占位 | toward non-BSE active ~889 |

**Cumulative 现状：** **486** effective company codes · **500** executed case slots · staged ~500 目标内 **97.2%**（见 [cumulative lineage summary](cninfo_a_class_erad_next_scale_slice1_cumulative_lineage_summary.md)）。

**Slice2 角色：** 在 slice1 收口后，将 A-class metadata lineage 从 ~500 staged 继续推向 **non-BSE fuller coverage** 的第一执行片（与 [next-scale plan](../../plans/cninfo_a_class_erad_next_scale_plan.md) Rank 1 第三阶段占位一致）。

---

## 2. Slice2 Goals（planning only）

| 目标 | 说明 |
|------|------|
| **G1 — 扩展 company-code lineage** | 从 cumulative **486** 向 fuller non-BSE 活跃集推进 · 首批新片建议 **+200 ~ +300** new codes（与 B fuller slice2 规模对称 · 最终规模待 Controller 冻结） |
| **G2 — 保持零 overlap** | 新 universe ∩ A cumulative effective **486** codes = ∅ · ∩ scale-200 universe = ∅ · ∩ slice1 universe = ∅ |
| **G3 — metadata-only 不变** | matching_logic **v2** · fresh_metadata only · 无 PDF / DB / MinIO / RAG |
| **G4 — side-track 不阻塞** | scale-200 unresolved **8** · slice1 unresolved **6** · Phase 3 / A3M017 保持 side-track · **不重跑** |
| **G5 — attribute baseline 挂钩** | slice2 规划与 [attribute gap ledger](cninfo_a_class_attribute_gap_ledger_20260714.md) 联动 · 新 cohort 纳入 offline catalog 对账计划 |

**非目标（本包）：** live 执行 · runner 扩展 · dry-run · commit · gate 升级 · verified / production_ready 宣称。

---

## 3. Overlap Rules（pointers）

完整规则见 [universe strategy](cninfo_a_class_erad_next_scale_universe_strategy.md) · 本节为 slice2 扩展摘要。

| 对照集 | slice2 政策 | 引用 |
|--------|-------------|------|
| AD2E001–500（已执行槽位） | **exclude rerun** · lineage-reference only | universe strategy §2 |
| cumulative **486** effective codes | **不重跑** · 仅计数引用 | cumulative lineage summary |
| scale-200 unresolved **8** | **side-track only** · 不在 slice2 primary | universe strategy §3.2 |
| slice1 unresolved **6** | **side-track only** · `live_needed=no` | [unresolved6 packaging](cninfo_a_class_unresolved6_offline_packaging_20260714.csv) |
| Phase 3 production root | **禁止 mutation** | universe strategy §4 |
| A3M017 | **side-track** · reference-only | universe strategy §4 |
| B-class cumulative（scale-200 + slice1 + fuller slice2） | **disjoint company_code** · cross-class lint 在 runner 阶段 | universe strategy §5 |
| Phase 1/2 tiny live | **exclude** | universe strategy §2 |
| 源池 | [889 non-BSE candidate](../../lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml) · slice1 后剩余约 **289** codes 可供 A/B fuller 分片（strategy §5） |

**Slice2 numbering 占位：** `next_scale_slice2` · case_id **AD2E501+**（与 B fuller slice2 BD2E501–800 **case_id 空间独立** · 以 **company_code** 为零 overlap 硬约束）。

---

## 4. Candidate Universe Direction（draft · 未生成 CSV）

| 项 | 规划值 |
|----|--------|
| cohort 名 | `next_scale_slice2` |
| case_id 起点 | **AD2E501** |
| 规模备选 | **+200**（保守）或 **+300**（与 B fuller slice2 对称） |
| 选取规则 | 非 BSE · 非 ST · SSE main / SZSE main / ChiNext / STAR 分层 · 与 slice1 draft 同型 |
| report_type  mix | annual_report + quarterly_report_q1（延续 slice1 / scale-200 new_erad 比例） |
| 源池扣减 | 889 pool − A slice1 **300** − B slice1 **300** − B fuller slice2 **300**（及 scale-200 已用 codes）→ 有序选取 remainder |

**本包不产出 slice2 candidate universe CSV** — 留给后续独立任务（需 overlap lint script + pool accounting 验证）。

---

## 5. Request Budget Pointer（future · not executed）

参照 slice1 [request budget](cninfo_a_class_erad_next_scale_request_budget.md) 比例：

| 组件 | slice2 规划参考 |
|------|----------------|
| 规模 | +200 → ~420 CNINFO 点估计 · cap ≤480；+300 → ~630 点估计 · cap ≤720 |
| session | **2×100** 或 **2×150** cases per approval |
| 日 cap | cases ≤200 · CNINFO ≤400 |
| inter-request sleep | ≥1.0s |

---

## 6. Output Root（planned · not created）

```
outputs/validation/cninfo_a_class_erad_next_scale_slice2/
├── reports/          # dry-run / live summary（future）
├── raw_metadata/     # bulk · local-only · not in git
└── ledgers/          # overlap / unresolved
```

**Write-block：** 禁止写入 scale-200 · slice1 · failed_retry · Phase 3 · A3M017 生产根。

---

## 7. Blocked Live Steps

| 动作 | 阻断原因 |
|------|----------|
| CNINFO 调用 / slice2 live | post-integration **HOLD** · `next_allowed_task = HOLD`（PROJECT_CONTROL §A-class） |
| runner 扩展 / dry-run | **NOT APPROVED runner** · 需独立 approval package |
| 对 unresolved 6 / scale-200 8 retry | `live_needed=no` · slice1 closure 已判定 no further live retry |
| gate 升级 verified / production_ready | Executor 无权限 |
| push / remote publication | PROJECT_CONTROL blocked |
| PDF / OCR / DB / MinIO / RAG | 不在 A-class Era D 授权范围 |

**Human approval phrase：** 未消费 · slice1 approval 已 spent · slice2 需新 phrase。

---

## 8. Safe Offline Next Steps

| 优先级 | 步骤 | 产出 |
|--------|------|------|
| P0 | 完成 [attribute gap ledger](cninfo_a_class_attribute_gap_ledger_20260714.md) + [skeleton CSV](cninfo_a_class_attribute_gap_skeleton_20260714.csv) | 本 run 已交付 |
| P1 | 889 pool 扣减脚本：A cumulative **486** + B cumulative ~**797** + C fuller 已规划 codes → remainder list | `slice2_pool_remainder_draft.csv`（future） |
| P2 | Overlap lint 规格书：slice2 draft ∩ A effective **486** = ∅ · ∩ B codes = ∅ | lint spec md（future） |
| P3 | 参照 slice1 产出 `cninfo_a_class_erad_next_scale_slice2_plan.md` + request budget + approval checklist | planning package（future） |
| P4 | Runner flag 设计草案：`--erad-a-next-scale-slice2`（命名待定） | command draft（future · 需独立任务） |
| P5 | Unresolved-6 offline raw_metadata 审计（不 live） | 延伸 unresolved6 packaging |

---

## 9. Cross-Track Coordination Notes

| Track | slice2 相关状态 | A-class 协调 |
|-------|----------------|--------------|
| B fuller slice2 | committed `f0bff3a` · **299/300** · **HOLD** | B 已占 BD2E501–800 case 空间 · A slice2 须 **company_code disjoint** |
| C fuller slice1 | ledger+QA PASS_WITH_CAVEAT · snapshot blocked | 共享 889 源池 · 联合日 cap 若未来并行 live |
| D shareholder_change | planning READY_FOR_APPROVAL | 无直接依赖 |

---

## 10. Governance

| 字段 | 值 |
|------|-----|
| verified | **NOT verified** |
| production_ready | **NOT production_ready** |
| current gate | **`PASS_WITH_CAVEAT`**（slice1 · post-integration **HOLD**） |
| slice2 planning gate | **`READY_FOR_APPROVAL`**（本包 · planning only） |
| live | **NOT APPROVED** |
| CNINFO（本包） | **0** |

---

## Evidence Paths

- [universe strategy](cninfo_a_class_erad_next_scale_universe_strategy.md)
- [next-scale plan](../../plans/cninfo_a_class_erad_next_scale_plan.md)
- [candidate universe draft（slice1 sample）](cninfo_a_class_erad_next_scale_candidate_universe_draft.csv)
- [coverage gap analysis](cninfo_a_class_mission_coverage_gap_analysis_20260714.md)
- [attribute gap ledger](cninfo_a_class_attribute_gap_ledger_20260714.md)

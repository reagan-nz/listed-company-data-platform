# CNINFO C-Class Phase 3 Batch Expansion Readiness Summary

_生成时间：2026-07-09_

> Phase 2 smoke closure 后的 Phase 3 **规划就绪**摘要。**无 live 授权** · **无 CNINFO**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Readiness

**Phase 3 planning can start.**

Phase 2 smoke 全链路（选股 → live harvest → harvest QA → snapshot subset → build → snapshot QA → closure review）已完成。

Closure gate: **`phase2_smoke_closure_gate = PASS_WITH_CAVEAT`**

本轮仅授权 **规划**；不授权 live harvest / snapshot build。

---

# Recommended Scope

| 项 | 建议 |
|----|------|
| batch size | **500** companies per batch |
| candidate pool | **matched_active** only（当前 refreshed candidate **~4647**） |
| first batch target | 从 matched_active 中剔除已覆盖与 caveat 集后 stratified 选取 **500** |
| output isolation | 每 batch 独立 `outputs/harvest/cninfo_c_class/phase3_batch_{n}/` 与对应 snapshot 目录 |

## Exclusions（Phase 3 选股须强制排除）

- `already_in_c_class`（含原 **863** + Phase 2 smoke **200** 已 harvest 公司）
- `hold`（26 all6 hold 子集）
- `BSE` / `BSE legacy`
- `identity_conflict`
- `manual_review`
- `delisted` / `inactive` caveat candidates（selection YAML `listing_status=delisted` 及 Phase 2 excluded ledger 模式）
- Phase 2 **12** all-direct-failure 公司（见 [excluded ledger](cninfo_c_class_phase2_smoke_excluded_company_caveat_ledger.csv)）

---

# Required Safeguards

1. **排除 Phase 2 all-direct-failure 模式** — 预筛 delisted/inactive；harvest QA 后再定义 clean subset
2. **保持 output-root 隔离** — 不复用 `phase2_smoke_200/` 或 `full/` 主轨
3. **显式用户批准** — live harvest / snapshot build 各自独立 approval flag
4. **live 前 dry-run** — universe validation + expected case matrix + command checklist
5. **snapshot 前 harvest QA** — 仅对 clean subset 规划 snapshot；排除 all-direct-failure
6. **snapshot 仅 clean subset** — 沿用 Phase 2 188 子集模式
7. **QA before closure** — 每 batch 完成后 offline snapshot QA + status CSV 校正
8. **不升级 verified** — C-class 保持 `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Phase 2 Lessons Applied to Phase 3

| Phase 2 教训 | Phase 3 对策 |
|-------------|-------------|
| 7 家 delisted 进入 smoke 200 | selection 阶段硬排除 `listing_status=delisted` |
| 9240002 与 inactive 共现 | harvest QA gate 保留 PASS_WITH_CAVEAT + excluded ledger |
| status CSV dry-run 遗留 | build 后强制 QA 校正 status |
| 全量 complete_with_caveat | 接受 caveat 层；不追求 pure complete |
| markdown vs terminal gate 不一致 | 统一 gate 文档与 runner 规则（规划项） |

---

# Gate

```
phase3_batch_planning_readiness_gate = READY_FOR_PLANNING
```

**含义：**

- Phase 3 batch expansion **规划文档**可启动
- **不**授权 Phase 3 live harvest
- **不**授权 6124 全量 harvest
- **不**授权 verified / testing_stable_sample 升级

---

# Recommended Next Task

**Phase 3 batch expansion planning** — 产出：

1. Phase 3 batch universe selection plan（500 × N batches）
2. Exclusion matrix refresh（含 Phase 2 smoke 200 已用代码）
3. Harvest / snapshot command checklist（复用 Phase 2 extension 模式）
4. Dry-run gate definitions

---

## References

- [Phase 2 closure review](../../plans/cninfo_c_class_phase2_smoke_closure_review.md)
- [closure metrics](cninfo_c_class_phase2_smoke_closure_metrics.csv)
- [excluded company caveat ledger](cninfo_c_class_phase2_smoke_excluded_company_caveat_ledger.csv)

## 红线确认

- 未请求 CNINFO · 未 live · 未 harvest rerun · 未 snapshot rebuild
- 未入库 / MinIO / RAG / registry / verified

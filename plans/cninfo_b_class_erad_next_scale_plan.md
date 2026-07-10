# CNINFO B 类 Era D — Next-Scale Plan（Toward Fuller Market）

_生成时间：2026-07-10_

> **性质：** Era D B 类扩规模 **离线规划 only** · **CNINFO = 0** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**
>
> **前置：** Era D ~200 live **198/200** · explicit-path commit **`e738fa9`** · closure **`PASS_WITH_CAVEAT`**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**B-class Phase 3 remote：** `5f29ae6`+`cb6ffcb` on **`origin/main`**（不变 · **不重跑 Phase 3 生产根**）

---

## 1. Goal

在 **phase1_freeze_v1 schema 不变**、**metadata + URL lineage only** 的前提下，将 B-class Era D 本地 metadata 覆盖从 **~200 effective** 分阶段扩至 **~500**，并为后续「非 BSE 活跃集 fuller coverage」预留 staged 路径。

**本包不执行 live** · **不重跑 BD2E001–200** · **不重跑 Phase 3 roots** · BD2E090/BD2E092 仅作 optional side-track。

---

## 2. Goal Options（Ranked）

| Rank | 方案 | 描述 | 优点 | 风险 |
|------|------|------|------|------|
| **1（推荐）** | **C) Staged 200→500→fuller + daily caps** | 下一执行片 **+300 new**（BD2E201–500）→ 累计 **500** lineage；fuller 市场留第三阶段 | 与 scale-200 教训一致；request cap 可控；失败隔离不阻塞整轨 | 需多批 live + 多轮收口 |
| 2 | A) ~500 metadata expansion（单批） | 一次扩至 ~500 新样本 | 收口快 | 单批 CNINFO ~600+；与 A/D 并行 live 风险高；network_error 放大 |
| 3 | B) Non-BSE active universe fuller coverage | 直接对齐 C 类 863/889 non-BSE 活跃集 | 终局覆盖完整 | 远超 500；需 harvest 级编排；B 类 metadata-only 轨不宜首跳 |

---

## 3. Primary Path Recommendation

**选择 Rank 1：C) Staged 200→500→fuller with daily caps**

| 项 | 值 |
|----|-----|
| 下一执行片 | **300 new**（`next_scale_slice1` · BD2E201–BD2E500） |
| 累计 lineage 目标 | **500**（200 已 live + 300 新片） |
| 已 effective 198 | **lineage-reference only** — 不重跑 · 不 refresh retained cohort |
| 独立输出根（规划） | `outputs/validation/cninfo_b_class_erad_scale_500/` |
| Fuller 第三阶段 | 500→non-BSE active（~800+）— **仅规划占位** · 本包不展开 live |

**理由：**

1. scale-200 live 已验证 staged cohort + request cap（397 CNINFO / 200 cases）可行。
2. 300 新片可将单批 request 控制在 **≤720**，配合 **2×150 case / day** 日 cap 可执行。
3. BD2E090/BD2E092 不阻塞 next-scale；optional retry 保持 side-track。
4. 与 `eraD_execution_plan.md` B 类 ~500 中期目标对齐，又不冒进至 full market。

---

## 4. Lessons Reused（from scale-200 + Phase 3）

| 教训 | 硬化要求 |
|------|----------|
| test cleanup 误删生产 sidecar | mock 仅写 `_mock_*`；cleanup guard 拒绝 `cninfo_b_class_erad_scale_*` 生产根 |
| 混杂 staging / supplemental gap | explicit-path commit only；bulk raw_metadata/quality 不入 git |
| output-root 隔离 | 新根 `cninfo_b_class_erad_scale_500/` · **禁止**写 Phase 1/2/2.5/3 / scale-200 生产根 |
| request cap | dry-run 硬上限 **≤720**；live 建议 **≤600** 保守执行 |
| network_error 隔离 | 失败 case 入 unresolved ledger · optional isolated retry · **不阻塞** next-scale slice |
| retained cohort refresh 风险 | **下一片不重跑 BD2E001–200**；198 effective 仅 lineage 引用 |

---

## 5. Output Root（Planned）

```
outputs/validation/cninfo_b_class_erad_scale_500/
├── reports/          # dry-run / live summary CSV+MD
├── quality/          # per-case quality JSON（bulk · local-only · not in git）
├── raw_metadata/     # per-case sidecars（bulk · local-only · not in git）
└── ledgers/          # overlap / unresolved ledgers
```

**红线：** metadata + pdf_url/adjunct_url lineage only · **无 PDF / DB / MinIO / RAG / verified**

---

## 6. Success Criteria（Future Live · Planning Only）

| 指标 | 阈值 | Gate 建议 |
|------|------|-----------|
| acceptable / executed（slice1 300） | **≥270/300（90%）** | `PASS_WITH_CAVEAT` |
| acceptable / executed | **≥285/300（95%）** | `PASS_WITH_CAVEAT` + 更小 caveat |
| acceptable / executed | **<270/300** | `FAIL_REVIEW_REQUIRED` |
| network_error | 参考 scale-200（1% retained） | isolated retry side-track |

**永不使用裸 `PASS`。**

---

## 7. Related Artifacts

| 文档 | 路径 |
|------|------|
| Universe strategy | [cninfo_b_class_erad_next_scale_universe_strategy.md](../outputs/validation/cninfo_b_class_erad_next_scale_universe_strategy.md) |
| Request budget | [cninfo_b_class_erad_next_scale_request_budget.md](../outputs/validation/cninfo_b_class_erad_next_scale_request_budget.md) |
| Candidate universe | [cninfo_b_class_erad_next_scale_candidate_universe_draft.csv](../outputs/validation/cninfo_b_class_erad_next_scale_candidate_universe_draft.csv) |
| Approval checklist | [cninfo_b_class_erad_next_scale_approval_checklist.md](../outputs/validation/cninfo_b_class_erad_next_scale_approval_checklist.md) |
| Command draft | [cninfo_b_class_erad_next_scale_command_draft.md](cninfo_b_class_erad_next_scale_command_draft.md) |
| Planning summary | [cninfo_b_class_erad_next_scale_planning_summary.md](../outputs/validation/cninfo_b_class_erad_next_scale_planning_summary.md) |

---

## 8. Gate

```text
b_class_erad_next_scale_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED live** · **NOT verified** · **NOT production_ready** · **CNINFO = 0**（本包）

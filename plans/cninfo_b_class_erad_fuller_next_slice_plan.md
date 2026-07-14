# CNINFO B 类 Era D — Fuller Next-Slice Plan（Beyond ~500）

_生成时间：2026-07-10_

> **性质：** Era D B 类 fuller 扩规模 **离线规划 only** · **CNINFO = 0** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**
>
> **前置：** slice1 commit **`350cdda`** · cumulative **498 effective** · staged 200→500 **essentially met**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）· C fuller-market slice1 **+200** planning complete（**NOT APPROVED live**）

**B-class Phase 3 remote：** `5f29ae6`+`cb6ffcb` on **`origin/main`**（不变 · **不重跑 Phase 3 生产根**）

---

## 1. Goal

在 **phase1_freeze_v1 schema 不变**、**metadata + URL lineage only** 的前提下，将 B-class Era D 本地 metadata 覆盖从 **cumulative ~498 effective** 分阶段扩向 **non-BSE active fuller coverage**（与 A next-scale · C fuller-market 方向对齐）。

**本包不执行 live** · **不重跑 BD2E001–500** · **不重跑 Phase 3 roots** · BD2E090/BD2E092 仅作 optional side-track。

---

## 2. Goal Options（Ranked）

| Rank | 方案 | 描述 | 优点 | 风险 |
|------|------|------|------|------|
| 1（推荐） | **C) Staged fuller slice2 (+200/+300) → later fuller** | 下一执行片 **+300 new**（BD2E501–800）→ 累计 **~798** effective；终局 non-BSE active 留 slice3+ | 与 slice1 教训一致；request cap 可控；不冒进 ~800+ 单跳 | 需多批 live + 收口 + 与 C/A 并行协调 |
| 2 | B) Single jump to full non-BSE active (~800+) | 一次对齐 smoke 889 / Era B 6124 活跃层 | 终局覆盖快 | 单批 CNINFO 极高；network_error 放大；B metadata-only 轨不宜首跳 |
| 3 | A) Close 2-case gap to nominal 500 only | 仅 optional retry BD2E090/092 | 名义 500 对齐 | **弱路径** · 不扩展市场面 · 090/092 已 side-track · 不解决 fuller 目标 |

---

## 3. Primary Path Recommendation

**选择 Rank 1：C) Staged fuller slice2 (+300) → cumulative ~798 → later fuller**

| 项 | 值 |
|----|-----|
| 下一执行片 | **+300 new**（`fuller_next_slice2` · BD2E501–BD2E800） |
| 累计 lineage 目标（slice2 后） | **~798**（498 已 effective + 300 新片） |
| BD2E001–500（498 effective） | **lineage-reference only** — 不重跑 |
| 独立输出根（规划） | `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/` |
| Fuller 第三阶段 | slice3+ toward non-BSE active remainder — **仅规划占位** |

**Slice2 规模备选：** +200（BD2E501–700 · 累计 ~698）若未来 request 压力或并行 live 过多；**本规划 draft 采用 +300** 与 slice1 对称。

**理由：**

1. slice1 live 已验证 **2×150 session** · **600 CNINFO** · **300/300 acceptable**。
2. +300 可将 dry-run cap 控制在 **≤720**，live 建议 **≤600**。
3. smoke 889 池在排除 B 累计 500 + C fuller 200 后仍有 **~493** 可用候选；draft 取前 **300** 有序码。
4. BD2E090/092 不阻塞 fuller slice2；optional retry 保持 side-track。
5. 与 `cninfo_b_class_erad_next_scale_plan.md` 第三阶段占位（500→non-BSE active）一致，但不单跳。

---

## 4. Lessons Reused（from scale-200 + slice1）

| 教训 | 硬化要求 |
|------|----------|
| explicit-path commit only | bulk raw_metadata/quality **local-only** · 不入 git |
| output-root 隔离 | 新根 `cninfo_b_class_erad_fuller_next_slice2/` · **禁止**写 scale-200 / slice1 / Phase 3 根 |
| request cap | dry-run 硬上限 **≤720**；live 建议 **≤600** |
| session split | **2×150** per approval budget · inter-session **≥4h** |
| network_error 隔离 | unresolved ledger · optional isolated retry · **不阻塞** 下一 slice |
| no rerun of effective | **不重跑** BD2E001–500 已 effective 498 · 仅 fresh_metadata 新片 |
| edge-case triage | empty_response / not_found → `accept_with_caveat` · 非 failed blocker |

---

## 5. Output Root（Planned）

```
outputs/validation/cninfo_b_class_erad_fuller_next_slice2/
├── reports/          # dry-run / live summary CSV+MD
├── quality/          # per-case quality JSON（bulk · local-only · not in git）
├── raw_metadata/     # per-case sidecars（bulk · local-only · not in git）
└── ledgers/          # overlap / unresolved ledgers
```

**红线：** metadata + pdf_url/adjunct_url lineage only · **无 PDF / DB / MinIO / RAG / verified**

---

## 6. Success Criteria（Future Live · Planning Only）

| 指标 | 阈值（300 cases） | Gate 建议 |
|------|-------------------|-----------|
| acceptable / executed | **≥270/300（90%）** | `PASS_WITH_CAVEAT` |
| acceptable / executed | **≥285/300（95%）** | `PASS_WITH_CAVEAT` + 更小 caveat |
| acceptable / executed | **<270/300** | `FAIL_REVIEW_REQUIRED` |

**永不使用裸 `PASS`。**

---

## 7. Related Artifacts

| 文档 | 路径 |
|------|------|
| Universe strategy | [cninfo_b_class_erad_fuller_next_slice_universe_strategy.md](../outputs/validation/cninfo_b_class_erad_fuller_next_slice_universe_strategy.md) |
| Request budget | [cninfo_b_class_erad_fuller_next_slice_request_budget.md](../outputs/validation/cninfo_b_class_erad_fuller_next_slice_request_budget.md) |
| Candidate universe | [cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv](../outputs/validation/cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv) |
| Approval checklist | [cninfo_b_class_erad_fuller_next_slice_approval_checklist.md](../outputs/validation/cninfo_b_class_erad_fuller_next_slice_approval_checklist.md) |
| Command draft | [cninfo_b_class_erad_fuller_next_slice_command_draft.md](cninfo_b_class_erad_fuller_next_slice_command_draft.md) |
| Planning summary | [cninfo_b_class_erad_fuller_next_slice_planning_summary.md](../outputs/validation/cninfo_b_class_erad_fuller_next_slice_planning_summary.md) |

---

## 8. Gate

```text
b_class_erad_fuller_next_slice_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED live** · **NOT APPROVED runner** · **NOT verified** · **NOT production_ready** · **CNINFO = 0**（本包）

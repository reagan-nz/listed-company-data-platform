# CNINFO A 类 Era D — Next-Scale Plan（Toward Fuller Market）

_生成时间：2026-07-10_

> **性质：** Era D A 类扩规模 **离线规划 only** · **CNINFO = 0** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**
>
> **前置：** Era D ~200 live **192/200 effective** · explicit-path commit **`41dc049`** · merge closure **`PASS_WITH_CAVEAT`**

**Phase 3 / A3M017：** production roots **untouched** · reference-only

---

## 1. Goal

在 **A-class metadata matching_logic v2 不变**、**metadata + URL lineage only** 的前提下，将 A-class Era D 本地 metadata 覆盖从 **~200 effective** 分阶段扩至 **~500**，并为后续「非 BSE 活跃集 fuller coverage」预留 staged 路径。

**本包不执行 live** · **不重跑 AD2E001–200 accepted** · **不重跑 8 unresolved** · **不重跑 Phase 3 / A3M017 production roots**。

---

## 2. Goal Options（Ranked）

| Rank | 方案 | 描述 | 优点 | 风险 |
|------|------|------|------|------|
| **1（推荐）** | **C) Staged 200→500→fuller + daily caps** | 下一执行片 **+300 new**（AD2E201–500）→ 累计 **500** lineage；fuller 市场留第三阶段 | 与 B-class next-scale 对齐；request cap 可控；8 unresolved 不阻塞 | 需多批 live + 多轮收口 |
| 2 | A) ~500 metadata expansion（单批） | 一次扩至 ~500 新样本 | 收口快 | 单批 CNINFO ~630+；network/matching 失败放大；与并行 live 风险高 |
| 3 | B) Non-BSE active universe fuller coverage | 直接对齐 C 类 889 non-BSE 活跃集 | 终局覆盖完整 | 远超 500；A-class metadata-only 轨不宜首跳 |

---

## 3. Primary Path Recommendation

**选择 Rank 1：C) Staged 200→500→fuller with daily caps**

| 项 | 值 |
|----|-----|
| 下一执行片 | **300 new**（`next_scale_slice1` · AD2E201–AD2E500） |
| 累计 lineage 目标 | **500**（200 已 live + 300 新片） |
| 已 effective 192 | **lineage-reference only** — 不重跑 · 不 refresh retained_phase3 cohort |
| 8 unresolved | **side-track only** — 不在 slice1 primary universe |
| 独立输出根（规划） | `outputs/validation/cninfo_a_class_erad_next_scale_slice1/` |
| Fuller 第三阶段 | 500→non-BSE active（~889）— **仅规划占位** · 本包不展开 live |

**理由：**

1. scale-200 live 已验证 staged cohort + request cap（423 CNINFO / 200 cases ≈ **2.1 req/case**）可行。
2. 300 新片单批 request 可控制在 **≤720**，配合 **2×150 case / session** 日 cap 可执行。
3. 8 unresolved（retry_again=no）不阻塞 next-scale；optional matching-logic follow-up 保持 side-track。
4. 与 B-class Era D next-scale（BD2E201–500 · +300）**并行对齐**，便于 cross-class universe sync。

---

## 4. Lessons Reused（from scale-200 + isolated retry + commit）

| 教训 | 硬化要求 |
|------|----------|
| 192 effective 不重跑 | AD2E001–200 **lineage-reference only** · slice1 **零 company_code overlap** |
| 8 unresolved side-track | AD2E066/088/119/121/122/185/190/146 **不在 slice1 universe** · **无 further live retry** |
| request cap | dry-run 硬上限 **≤720**；live 建议 **≤630** 保守执行 |
| network / empty response | 失败 case 入 slice1 unresolved ledger · isolated retry side-track · **不阻塞** slice2 |
| matching_logic_miss | AD2E121/122/185 教训 → slice1 仍用 v2 · 失败 offline raw_metadata review 另轨 |
| bulk raw_metadata local-only | main **200** + retry **7** 不入 git · slice1 bulk 同理 |
| explicit-path commit | 规划包 / runner / reports 入 git · bulk sidecar 排除 |
| output-root 隔离 | 新根 `cninfo_a_class_erad_next_scale_slice1/` · **禁止**写 scale-200 / failed_retry / Phase 3 / A3M017 生产根 |

---

## 5. Output Root（Planned）

```
outputs/validation/cninfo_a_class_erad_next_scale_slice1/
├── reports/          # dry-run / live summary CSV+MD
├── raw_metadata/     # per-case JSON（bulk · local-only · not in git）
└── ledgers/          # overlap / unresolved ledgers（if needed）
```

**红线：** metadata + pdf_url/adjunct_url lineage only · **无 PDF / DB / MinIO / RAG / verified**

---

## 6. Success Criteria（Future Live · Planning Only）

| 指标 | 阈值 | Gate 建议 |
|------|------|-----------|
| acceptable / executed（slice1 **300**） | **≥270/300（90%）** | `PASS_WITH_CAVEAT` |
| acceptable / executed | **≥285/300（95%）** | `PASS_WITH_CAVEAT` + 更小 caveat |
| acceptable / executed | **<270/300** | `FAIL_REVIEW_REQUIRED` |
| network_or_empty_response | 参考 scale-200 new_erad 失败率 | isolated retry side-track · 不阻塞 slice2 规划 |

**永不使用裸 `PASS`。**

---

## 7. Related Artifacts

| 文档 | 路径 |
|------|------|
| Universe strategy | [cninfo_a_class_erad_next_scale_universe_strategy.md](../outputs/validation/cninfo_a_class_erad_next_scale_universe_strategy.md) |
| Request budget | [cninfo_a_class_erad_next_scale_request_budget.md](../outputs/validation/cninfo_a_class_erad_next_scale_request_budget.md) |
| Candidate universe | [cninfo_a_class_erad_next_scale_candidate_universe_draft.csv](../outputs/validation/cninfo_a_class_erad_next_scale_candidate_universe_draft.csv) |
| Approval checklist | [cninfo_a_class_erad_next_scale_approval_checklist.md](../outputs/validation/cninfo_a_class_erad_next_scale_approval_checklist.md) |
| Command draft | [cninfo_a_class_erad_next_scale_command_draft.md](cninfo_a_class_erad_next_scale_command_draft.md) |
| Planning summary | [cninfo_a_class_erad_next_scale_planning_summary.md](../outputs/validation/cninfo_a_class_erad_next_scale_planning_summary.md) |

---

## 8. Gate

```text
a_class_erad_next_scale_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED live** · **NOT APPROVED runner** · **NOT verified** · **NOT production_ready** · **CNINFO = 0**（本包）

# CNINFO B 类 Era D ~200 Metadata Expansion Plan

_生成时间：2026-07-10_

> **性质：** Era D 本地扩规模规划 · **离线 only** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**
>
> **Era 归属：** B 类 **进入 Era D**；A/D 线继续收 Era C 尾巴。本包 **不调用 CNINFO** · **不 live** · **不实现 runner**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**B-class Phase 3 remote：** `5f29ae6`+`cb6ffcb` on **`origin/main`**（Case B accepted · **763/763** · **no further B push**）

---

## 1. Goal

在 **phase1_freeze_v1 schema 不变**、**metadata + URL lineage only** 的前提下，将 B-class 公告 metadata 本地稳定抽取从 Phase 3 **有效 100/100** 扩至 **~200** 家公司：

- **100 retained** — Phase 3 effective accepted cohort（BD2E001–BD2E100）
- **100 new** — 与 Phase 1/2/2.5/3 **零公司代码重叠** 的新扩样（BD2E101–BD2E200）
- 独立输出根：`outputs/validation/cninfo_b_class_erad_scale_200/`
- **Era D 本地 only** — 不入库 · 不写 verified · 不升级 testing_stable_sample

---

## 2. Universe Design Choice

| 方案 | 本包选择 |
|------|----------|
| 200 全新公司 | **否** |
| **100 retained + 100 new = 200** | **是** |

**理由：**

1. Phase 3 已在 `origin/main` 收口 **763/763** inventory；retained 100 保留有效 accepted 基线与 sidecar 连续性。
2. 新增 100 家专测 Era D 扩规模与 bucket 稳定性，overlap 可控。
3. 与 Era D MVP（B 线 ~200 metadata）对齐。

---

## 3. Overlap Policy

| 对照 | 政策 |
|------|------|
| Phase 3 effective 100 | **100 retained** — `phase3_overlap=yes`（by design） |
| Phase 1 / 2 / 2.5 / 3（new cohort） | **0 overlap** — `prior_b_phase_overlap=no` for BD2E101–200 |
| A-class / C-class / D-class live 根 | **禁止写入** · 本轨只读参照 |
| 北交所（BSE） | 默认 **排除**（与 Phase 3 一致） |

完整 overlap 见 [universe draft](../outputs/validation/cninfo_b_class_erad_scale_200_universe_draft.csv)。

---

## 4. Endpoint & Mix

| Endpoint | 角色 | Era D 200 覆盖 |
|----------|------|----------------|
| EP001 | 公告检索主入口 | **200/200** |
| EP002 | orgId 辅助（金融样本） | 按需（金融 bucket） |
| EP004 | 定期报告 metadata | **100** cases（50%） |
| EP005 | 一般公告 metadata | **100** cases（50%） |

**红线：** metadata + pdf_url/adjunct_url lineage only · **无 PDF 下载/解析/OCR/章节抽取**

---

## 5. Output Root

```
outputs/validation/cninfo_b_class_erad_scale_200/
├── reports/          # dry-run / live summary CSV+MD
├── quality/          # per-case quality JSON
├── raw_metadata/     # per-case per-endpoint raw JSON sidecars
└── ledgers/          # optional execution / overlap ledgers
```

**隔离要求：**

- **不得**写入 Phase 1/2/2.5/3 expansion / failed-retry / retry_v2 生产根
- **不得**触碰 A/C/D live 根
- 测试 mock 输出必须在 `_mock_*` 子目录

---

## 6. Request Cap Proposal（Conservative）

| 项 | 估值 |
|----|------|
| universe size | **200** |
| EP001 baseline | **200** requests |
| EP004 / EP005 path | **~100** each（按 announcement_type 分轨） |
| EP002（金融子集） | **≤40**（约 20% 金融样本 × 2） |
| **planned_request_count_total（dry-run 上限）** | **≤480** |
| live 执行建议 sleep | **≥1.0s** between CNINFO calls（live 阶段；本包不执行） |
| 单日 live 批次建议 | **≤200** cases 单批；更大需分批 + 人批 |

---

## 7. Success Criteria（Future Live）

本规划包 **不执行 live**；以下为后续 live 收口建议：

| 指标 | 阈值 | Gate 建议 |
|------|------|-----------|
| acceptable / executed | **≥180/200（90%）** | `PASS_WITH_CAVEAT` |
| acceptable / executed | **≥190/200（95%）** | 可考虑 `PASS_WITH_CAVEAT` + 更小 caveat |
| acceptable / executed | **<180/200** | `FAIL_REVIEW_REQUIRED` |
| network_error 比例 | 参考 Phase 3（10/91 on recovery） | 保留 sidecar · 可选 isolated retry |
| PDF / DB / MinIO / RAG | **0** | 红线 |

**永不使用裸 `PASS`。**

---

## 8. Cleanup / Resume Risks（Phase 3 Lesson）

| 风险 | Phase 3 教训 | Era D 硬化要求 |
|------|--------------|----------------|
| 测试 cleanup 删除生产 sidecar | `test_cninfo_b_class_phase3_100_retry_v2_live_path` 曾删 185 个生产文件 | mock 仅写 `_mock_*`；`_cleanup_*` **拒绝** `cninfo_b_class_erad_scale_200` 生产根 |
| 混杂 staging | supplemental commit 前 artifact 缺失 | explicit-path staging only；dry-run 与 live 根分离 |
| network_error 批次 | recovery 81/91 acceptable | 保留 network_error sidecar；不强制重跑 closed Phase 3 |
| resume 中断 | Era D 需可重跑单 case | 规划 ledger + case_id 稳定（BD2E001–200） |

参考：[test cleanup hardening summary](../outputs/validation/cninfo_b_class_phase3_100_retry_v2_test_cleanup_hardening_summary.md)

---

## 9. Planned Runner Surface（Document Only — NOT IMPLEMENTED）

| 项 | 占位 |
|----|------|
| CLI flag | `--erad-b-scale-200` |
| approval flag | `--approve-b-class-erad-scale-200` |
| universe CSV | `--universe-csv outputs/validation/cninfo_b_class_erad_scale_200_universe_draft.csv` |
| output root flag | `--output-root outputs/validation/cninfo_b_class_erad_scale_200/` |
| runner 文件（预期） | `lab/run_cninfo_b_class_phase25_expansion_validation.py` 扩展（**本任务不改**） |

```
approval_status = NOT_APPROVED
approved_for_live = false
```

---

## 10. Gate

```
b_class_erad_scale_200_planning_gate = READY_FOR_APPROVAL
```

---

## 11. Related Artifacts

| 文档 | 路径 |
|------|------|
| universe draft | [cninfo_b_class_erad_scale_200_universe_draft.csv](../outputs/validation/cninfo_b_class_erad_scale_200_universe_draft.csv) |
| approval checklist | [cninfo_b_class_erad_scale_200_approval_checklist.md](../outputs/validation/cninfo_b_class_erad_scale_200_approval_checklist.md) |
| command draft | [cninfo_b_class_erad_scale_200_command_draft.md](cninfo_b_class_erad_scale_200_command_draft.md) |
| planning summary | [cninfo_b_class_erad_scale_200_planning_summary.md](../outputs/validation/cninfo_b_class_erad_scale_200_planning_summary.md) |
| next-step | [cninfo_b_class_erad_scale_200_next_step_recommendation.md](../outputs/validation/cninfo_b_class_erad_scale_200_next_step_recommendation.md) |
| Era D master | [eraD_execution_plan.md](eraD_execution_plan.md) |

---

## 12. Red Lines（本包）

- **无 CNINFO** · **无 live** · **无 runner 实现** · **无 commit** · **无 push**
- **无 PDF** · **无 DB/MinIO/RAG** · **无 verified/production_ready/testing_stable_sample**
- **不修改** A/C/D 生产输出 · **不 amend** Phase 3 已落地 commit

# CNINFO C 类 Era D Resume / Local-Stability 规划

_生成时间：2026-07-10_

> **Era 归属：** C 类 **进入 Era D**（本地稳定抽取 / resume 硬化）；A/D 仍在收 Era C 尾巴。  
> **并行约束：** offline planning only · **无 CNINFO** · **无 live harvest** · **本任务不重建 snapshot JSON** · **无 DB/MinIO/verified**

**上级计划：** [eraD_execution_plan.md](eraD_execution_plan.md) · **Phase 3.5 收口：** [cninfo_c_class_phase35_clean_push_status.md](../outputs/validation/cninfo_c_class_phase35_clean_push_status.md)

---

## 0. 背景

| 项 | 状态 |
|----|------|
| Phase 3.5 expanded snapshot | **491** 本地 JSON（gitignore） |
| Phase 3.5 holdout | **9** closed-with-caveat · **no promotion** |
| 远端 landing | `a12d5fb` + `522c89b` on **`origin/main`**（Case B accepted） |
| `phase35_clean_push_gate` | **`PASS_WITH_CAVEAT`**（保持） |
| 863 full snapshot | 本地存在 · Era C 经验基线 |
| Era D 目标 | 本地 harvest/snapshot **可 resume、可重跑、清理不误删** |

---

## 1. 目标（Era D · C 线）

### 1.1 主目标

1. **Resume / cleanup 硬化** — 测试与 runner teardown 不得删除生产 harvest / snapshot 根；resume 断点语义文档化并可 dry-run 验证。  
2. **本地全量或大批次重跑就绪** — 在硬化完成后，为 863 harvest 审计或 491/863 snapshot 重跑建立批准包与预算帽；**本规划包不执行重跑**。

### 1.2 明确不做（本轨 · Era D 红线继承）

- PostgreSQL / MinIO / MongoDB / RAG / verified / production_ready  
- PDF 下载 / 解析 / OCR / 章节抽取  
- C35R016 / hold_for_review **promotion**  
- 修改 A/B/D live 根或产物  
- 本任务内 live harvest · snapshot JSON 重建

---

## 2. 首选第一执行切片（Primary Recommendation）

**推荐：Slice-C-EraD-01 — Resume/cleanup 硬化 + 保护根审计（offline dry-path）**

| 项 | 内容 |
|----|------|
| 类型 | D1 稳定性底座（先于任何大规模 live 或 snapshot rebuild） |
| 范围 | 审计 C-class live-path / builder 测试中的 `tearDown` / cleanup；为生产根加硬拒绝；补 `test_cleanup_refuses_production_*` 回归 |
| 参考先例 | B-class `test_cninfo_b_class_phase3_100_retry_v2_live_path` 硬化（§B ED 经验） |
| 产出 | 硬化 PR 级代码变更 + offline 测试 PASS + protected roots ledger 对齐 |
| 为何优先 | B 线已证明 test cleanup 可删生产 sidecar；C 线 harvest/snapshot 体积更大，误删成本更高 |
| 明确延后 | 491/863 snapshot rebuild · 863 harvest live 重跑 — 待 Slice-C-EraD-01 gate **`READY_FOR_APPROVAL`** 后人批 |

**次选（不首选）：** 863 harvest resume 审计 dry-run — 依赖硬化完成后再开。

**不首选：** 491 snapshot rebuild readiness — 属 D2；需在硬化 + harvest 根保护之后。

---

## 3. 风险

| ID | 风险 | 严重度 | 缓解 |
|----|------|--------|------|
| R-C-01 | 测试 cleanup 删除生产 harvest / snapshot | **高** | 硬化 + 保护根 CSV + 回归测试 |
| R-C-02 | 混合 working tree（与 B/A/D 并行）误改 C 根 | **高** | 独立分支 `c-class-erad-resume`；status 由 Prompt Manager 收口 |
| R-C-03 | 磁盘：863 harvest + 491/863 snapshot 体量 | **中** | 策略文档 + dry-run 预算帽；不默认全量重跑 |
| R-C-04 | dry-run / mock 写入生产根 | **中** | runner 强制 `--output-root` 隔离；测试用 `_mock_*` 子目录 |
| R-C-05 | holdout 9 被误纳入扩样或 promotion | **中** | ledger 锁定 closed-with-caveat；QA 排除规则保持 |
| R-C-06 | 四线并行时踩 A/B/D 输出根 | **高** | [protected_output_roots.csv](../outputs/validation/cninfo_c_class_erad_protected_output_roots.csv) 只列 C 根；禁止跨线写 |

---

## 4. 须保护的输出根（摘要）

完整清单见 [cninfo_c_class_erad_protected_output_roots.csv](../outputs/validation/cninfo_c_class_erad_protected_output_roots.csv)。

| 类别 | 代表路径 | 保护级别 |
|------|----------|----------|
| Phase 3.5 harvest 原批 | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` | **production · read-only for Era D planning** |
| Phase 3.5 resume harvest | `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/` | **production** |
| 863 full harvest（若存在） | `outputs/harvest/cninfo_c_class/`（非 mock 子树） | **production** |
| 491 expanded snapshot | `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/` | **production · gitignore** |
| 863 full snapshot | `outputs/snapshot/cninfo_c_class/full/` | **production · gitignore** |
| 测试 mock 区 | `**/_mock_*/`、`**/_mock_live_test/` | **ephemeral only** |

---

## 5. Holdout 政策（不变）

- **9** holdout：**closed-with-caveat**（8 hold_for_review + C35R016 `closed_with_caveat_still_partial`）  
- `promotion_allowed_now = no` for all 9  
- Era D 扩样 / 重跑 **不得** 自动 promote C35R016 或 reopen hold_for_review  
- 491 success track 保持 closed-with-caveat

---

## 6. Era D 本地 only 说明

- 本轨验收以 **本地 `outputs/` 可重复、可 resume** 为准  
- snapshot JSON **可继续 gitignore**；不入库 git  
- 远端发布与 Era D 本地验收 **解耦**  
- 入库研究 **延后到 Era D 之后**（见 eraD §0.4）

---

## 7. 建议执行顺序（gate 纪律）

```text
Slice-C-EraD-01 planning（本包 · offline）
→ hardening implementation + tests（CNINFO=0）
→ hardening dry-run / closure review（offline）
→ human approve（若需后续 live / rebuild 切片）
→ （可选）Slice-C-EraD-02 863 harvest resume audit dry-run
→ （可选）Slice-C-EraD-03 491/863 snapshot rebuild readiness（人批后）
```

---

## 8. Gate

```
c_class_erad_resume_stability_planning_gate = READY_FOR_APPROVAL
```

**不是 bare PASS** · **不是 verified** · **approval_status = NOT_APPROVED**

---

## 9. 产出索引

| 产出 | 路径 |
|------|------|
| 本规划 | `plans/cninfo_c_class_erad_resume_stability_plan.md` |
| 保护根 ledger | `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` |
| 风险 ledger | `outputs/validation/cninfo_c_class_erad_resume_risk_ledger.csv` |
| 批准清单 | `outputs/validation/cninfo_c_class_erad_resume_stability_approval_checklist.md` |
| 命令草稿 | `plans/cninfo_c_class_erad_resume_stability_command_draft.md` |
| 规划摘要 | `outputs/validation/cninfo_c_class_erad_resume_stability_planning_summary.md` |
| 下一步建议 | `outputs/validation/cninfo_c_class_erad_resume_stability_next_step_recommendation.md` |

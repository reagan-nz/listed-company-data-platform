# CNINFO C 类 Era D Snapshot Rebuild Readiness 规划

_生成时间：2026-07-10_

> **Slice：** Slice-C-EraD-03 · **offline planning only**  
> **approved_for_snapshot_rebuild = false** · **NOT APPROVED rebuild**  
> **无 CNINFO** · **无 live harvest** · **无 snapshot JSON 重建**

**上级：** [eraD_execution_plan.md](eraD_execution_plan.md) §9.4 · [resume/stability plan](cninfo_c_class_erad_resume_stability_plan.md)  
**输入：** [harvest resume audit summary](../outputs/validation/cninfo_c_class_erad_harvest_resume_audit_summary.md) · [protected roots](../outputs/validation/cninfo_c_class_erad_protected_output_roots.csv) · [risk ledger](../outputs/validation/cninfo_c_class_erad_resume_risk_ledger.csv)

---

## 0. 背景（已收口 · 不重做）

| 前置切片 | Gate | 摘要 |
|----------|------|------|
| Slice-C-EraD-01 cleanup hardening | **`PASS_OFFLINE`** | 35/35 PASS · 生产根清理硬化 |
| Slice-C-EraD-02 harvest resume audit | **`PASS_OFFLINE`** | 7/7 PASS · CNINFO **0** |
| 863_primary harvest | — | complete **805** · needs_review **58** · partial **0** · missing **0** |
| Live resume 运营决策 | — | **HOLD**（首选 Option 1） |
| Phase 3.5 remote | — | `origin/main` closed（`a12d5fb`+`522c89b`） |
| Holdout | — | **9** closed-with-caveat · **no promotion** |

---

## 1. 范围

本规划包评估 **491 Phase 3.5 success-subset** 与 **863_primary full snapshot** 的 rebuild readiness；**不执行** rebuild、不调用 builder `--execute`、不写入生产 snapshot 根。

### 1.1 纳入评估的 cohort

| Cohort | Universe | 现有 snapshot 根 | Harvest 输入 |
|--------|----------|------------------|--------------|
| **phase35_491** | expanded success 491 YAML | `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/` | phase3_batch + phase35_resume merge |
| **863_primary** | `eval_companies_c_class_harvest_863_non_bse.yaml`（863） | `outputs/snapshot/cninfo_c_class/full/` | `outputs/harvest/cninfo_c_class/` 主轨 |
| **holdout_9** | holdout ledger（9） | **不在** 491 根内 | 各 batch 子树 · **禁止 promote** |

### 1.2 明确排除

- holdout **9** 纳入 **block** 矩阵行，不作为 rebuild 候选  
- Slice-C-EraD-02b targeted live resume（58 needs_review）— **DEFERRED**  
- A/B/D 输出根 · DB/MinIO/RAG · verified · production_ready

---

## 2. Readiness 判定标准（文档化 · 本包不执行）

### 2.1 必要条件（全部满足才 *考虑* 人批 rebuild）

| # | 条件 | 当前状态 |
|---|------|----------|
| R1 | `c_class_erad_cleanup_hardening_gate = PASS_OFFLINE` | **满足** |
| R2 | harvest resume audit 完成且无 partial/missing（863_primary） | **满足**（0 partial · 0 missing） |
| R3 | 人批 `approved_for_snapshot_rebuild = true` | **未满足**（**false**） |
| R4 | dry-run 输出根隔离（`_mock_*` 或专用 validation 子树） | 设计已有 · **未执行 rebuild dry-run** |
| R5 | holdout 9 保持 closed-with-caveat | **满足** |
| R6 | 磁盘预算与备份策略文档化 | 本包 §4 |

### 2.2 充分条件（为何可能 *不需要* rebuild）

| # | 条件 | phase35_491 | 863_primary |
|---|------|-------------|-------------|
| S1 | 生产 snapshot JSON 已存在且数量对齐 | **491** JSON（~25M） | **863** JSON（~45M） |
| S2 | Era C QA / closure gate 已收口 | **`PASS_WITH_CAVEAT`** | **`complete_with_caveat=863`** |
| S3 | Harvest 主轨无 blocking partial/missing | merge 轨已 closed | **805 complete** · 58 ledger-only needs_review |
| S4 | Rebuild 无新增业务价值（Era D MVP） | 491 track closed | full 已覆盖 research MVP |

**结论：** R1–R2、R5–S4 支持 **HOLD rebuild**；R3 未开 · **NOT APPROVED**。

---

## 3. 输入清单（只读）

### 3.1 Snapshot 根（production · gitignore）

| 根 | 磁盘 | 文件计数（含 quality sidecar） |
|----|------|--------------------------------|
| `phase35_batch_500_001_expanded_success_491/` | ~25M | **492**（491 JSON + sidecar） |
| `full/` | ~45M | **864**（863 JSON + quality） |

### 3.2 Harvest 完备性（Slice-C-EraD-02）

| 指标 | 863_primary |
|------|-------------|
| complete | **805** |
| needs_review | **58** |
| partial / missing | **0** |

**needs_review 解读：** 多为 `company_harvest_status.csv` 与 normalized 源计数不一致；**863 full snapshot 已基于历史 harvest 生成**；rebuild **不会自动修复** ledger 语义，且 **无明确 harvest 缺口**。

### 3.3 Builder / runner 参考（延后执行）

- `lab/build_cninfo_c_class_snapshot_batch.py` — `--dry-run` / `--execute` + approval flags  
- Phase 3.5 expanded：`--approve-phase35-expanded-snapshot` + 隔离 output root  
- 硬化：`lab/cninfo_c_class_erad_cleanup_guard.py` · `assert_safe_erad_audit_write_path` 模式可复用于 rebuild dry-run 写入

---

## 4. 风险

| ID | 风险 | 严重度 | 缓解 |
|----|------|--------|------|
| SR-01 | 误写生产 snapshot 根（491/863） | **高** | protected roots CSV + cleanup guard + `_mock_*` only |
| SR-02 | 全量 rebuild 磁盘翻倍（~70M snapshot + 临时） | **中** | 默认 HOLD；若人批则 mock 根或版本化子目录 |
| SR-03 | holdout 9 被 merge 进 491 rebuild universe | **高** | YAML/manifest 排除 · ledger 锁定 |
| SR-04 | 58 needs_review 触发误 rebuild | **中** | 本包 **Option A HOLD**；triage 前不 rebuild |
| SR-05 | 与 B/A/D 并行 working tree 混改 | **高** | C 独立分支建议 · 只读生产根 |
| SR-06 | rebuild 后 QA 回归成本 | **中** | 491/863 QA 已 closed；rebuild 需新 closure 包 |
| SR-07 | git 误提交 snapshot JSON | **中** | 继续 gitignore · safe-to-commit 清单纪律 |

---

## 5. 决策矩阵

| 选项 | 描述 | 491 | 863 | 人批 | 本包推荐 |
|------|------|-----|-----|------|----------|
| **Rebuild now** | `--execute` 写生产根 | 否 | 否 | 需 `approved_for_snapshot_rebuild=true` | **拒绝** |
| **HOLD** | 沿用现有 snapshot · Era D MVP 足够 | 是 | 是 | 否 | **首选 · Option A** |
| **Partial rebuild later** | 仅 mock 根 dry-run / 小 cohort | 延后 | 延后 | 另开切片 | 仅文档化 · Option B 设计 |
| **Defer until triage** | 等 58 needs_review 人工分诊 | — | — | 是 | **Option C 延后** |

### 5.1 首选结论（Primary Recommendation）

**Option A — HOLD rebuild**

- **491** 本地 JSON **491/491** · QA **`PASS_WITH_CAVEAT`** · track **closed-with-caveat**  
- **863** full snapshot **863/863** · 已满足 Era D 本地研究 MVP  
- **58 needs_review** 不构成 rebuild 触发器（无 partial/missing · snapshot 已存在）  
- **holdout 9** 不得 promote · rebuild 无净收益  
- **`approved_for_snapshot_rebuild = false`** 保持

### 5.2 次选（仅规划 · 不执行）

**Option B — offline rebuild readiness dry-run 脚本设计**

- 未来切片：扩展 builder dry-run → 写入 `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/` 或 `_mock_erad_rebuild_*`  
- 须 **`c_class_erad_snapshot_rebuild_readiness_planning_gate`** 人批后才实现  
- **本包不实现、不执行**

### 5.3 延后

**Option C — 等 58 needs_review 人工 triage**

- 仅当 triage 发现 **明确 harvest 缺口** 且 live resume 人批后，才重新评估 partial rebuild  
- 与 Slice-C-EraD-02b 绑定 · **当前 DEFERRED**

---

## 6. 若未来人批 rebuild 的前置 gate 链（预告）

```text
c_class_erad_snapshot_rebuild_readiness_planning_gate = READY_FOR_APPROVAL（本包）
→ human approve rebuild readiness checklist
→ approved_for_snapshot_rebuild = true（显式）
→ Slice-C-EraD-03b mock-root rebuild dry-run（CNINFO=0）
→ human approve execute
→ Slice-C-EraD-03c isolated rebuild（仍非 verified）
```

**本包止于第一步。**

---

## 7. Gate

```
c_class_erad_snapshot_rebuild_readiness_planning_gate = READY_FOR_APPROVAL
```

**不是 PASS** · **不是 approved_for_snapshot_rebuild** · **不是 verified**

保留：

- `c_class_erad_cleanup_hardening_gate = PASS_OFFLINE`
- `c_class_erad_harvest_resume_audit_gate = PASS_OFFLINE`
- `phase35_holdout_closed_with_caveat_signoff_gate = PASS_WITH_CAVEAT`
- `approval_status = NOT_APPROVED` · `approved_for_live = false`

---

## 8. 产出物索引

| 文件 | 说明 |
|------|------|
| [readiness checklist](../outputs/validation/cninfo_c_class_erad_snapshot_rebuild_readiness_checklist.md) | 人批清单 |
| [candidate matrix](../outputs/validation/cninfo_c_class_erad_snapshot_rebuild_candidate_matrix.csv) | cohort 矩阵 |
| [readiness summary](../outputs/validation/cninfo_c_class_erad_snapshot_rebuild_readiness_summary.md) | 执行摘要 |
| [next-step recommendation](../outputs/validation/cninfo_c_class_erad_snapshot_rebuild_next_step_recommendation.md) | 下一步 |

---

## 9. 红线

No CNINFO · no snapshot rebuild · no harvest live · no holdout promotion · production roots read-only · no A/B/D mutation · no commit/push（本任务）

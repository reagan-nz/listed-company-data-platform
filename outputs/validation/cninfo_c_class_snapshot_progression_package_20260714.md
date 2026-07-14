# CNINFO C 类 — Snapshot Rebuild Progression Offline Package

_生成时间：2026-07-14 · Task **C-GEN-20260714-06** · CNINFO **0**_

> **offline only** · **no production snapshot rebuild execute** · **no commit/push** · **no live** · **no PDF/OCR/DB/MinIO/RAG**

---

## 1. 任务与审批记录

| 项 | 值 |
|----|-----|
| Task ID | **C-GEN-20260714-06** |
| Human gate | **AQ-C-SNAP** — C snapshot rebuild / next snapshot progression |
| 审批来源 | [controller_state_refresh_20260714_run6.md](controller_state_refresh_20260714_run6.md) |
| 解锁范围 | snapshot 相关自主任务 · validation · evidence · snapshot **preparation** |
| 仍禁止 | production_ready 膨胀 · 未受保护生产根覆写 · push · CNINFO |

**AQ-C-SNAP 语义：** 允许本 progression 包（排除清单 · mock-root 计划 · 准备路径文档化）；**不**等同于授权对 `outputs/snapshot/cninfo_c_class/full/` 或 `phase35_batch_500_001_expanded_success_491/` 执行 production rebuild。

---

## 2. 双层排除规则（partial7 + caveat10）

### 2.1 规则来源

| 文档 | 路径 |
|------|------|
| 双层语义校验规则 | [cninfo_c_class_dual_layer_validation_rules_20260714.md](cninfo_c_class_dual_layer_validation_rules_20260714.md) |
| 规则矩阵 | [cninfo_c_class_dual_layer_rule_matrix_20260714.csv](cninfo_c_class_dual_layer_rule_matrix_20260714.csv) |
| Caveat10 索引 | [cninfo_c_class_caveat10_registry_20260714.md](cninfo_c_class_caveat10_registry_20260714.md) / [.csv](cninfo_c_class_caveat10_registry_20260714.csv) |

### 2.2 Partial7（规则族 B · applies_to: partial）

| 规则 ID | 要点 |
|---------|------|
| **DLVR-P01** | ledger `partial (4/10)` · audit `partial` · 打包 raw 6x http_error/500 + security_observe delisted=true |
| **DLVR-P02** | partial 保留 · business_code=9240002 · disposition=`accept_with_caveat` |
| **DLVR-P03** | 禁止将 4/10 标为 complete |
| **DLVR-P04** | **7 家 partial 显式排除于 snapshot complete pool** · `approved_for_snapshot_rebuild` 不得因 partial 翻转 |

证据包：[cninfo_c_class_partial7_evidence_completeness_20260714.md](cninfo_c_class_partial7_evidence_completeness_20260714.md) · 矩阵 [cninfo_c_class_partial7_offline_qa_matrix_20260714.csv](cninfo_c_class_partial7_offline_qa_matrix_20260714.csv)

### 2.3 Empty-Dividend-3（规则族 C · applies_to: empty_dividend）

| 规则 ID | 要点 |
|---------|------|
| **DLVR-E01** | ledger `complete (10/10 含零字节 dividend)` · audit `needs_review` — **合法双层分歧** |
| **DLVR-E02** | raw dividend `valid_empty` http 200 · audit source_ledger dividend_history=no |
| **DLVR-E03** | security_observe delisted=false · 与 partial7 delisted=true 模式区分 |
| **DLVR-E04** | 禁止因 audit needs_review 将 ledger 降级为 partial |
| **DLVR-E05** | 零字节 dividend 存在性 vs 内容 present 语义错位登记为已知 caveat |

证据包：[cninfo_c_class_empty_dividend_evidence_20260714.md](cninfo_c_class_empty_dividend_evidence_20260714.md) · 矩阵 [cninfo_c_class_empty_dividend_offline_matrix_20260714.csv](cninfo_c_class_empty_dividend_offline_matrix_20260714.csv)

### 2.4 全局守门（规则族 D）

| 规则 ID | 要点 |
|---------|------|
| **DLVR-G01** | closure 193 complete / 7 partial / 0 missing · audit 190 complete / 7 partial / 3 needs_review · gate=`PASS_WITH_CAVEAT` |
| **DLVR-G02** | 禁止 verified / production_ready / bare PASS 升级 |
| **DLVR-G03** | 规则包本身不触发 snapshot rebuild（本包在 AQ-C-SNAP 下仅翻转**准备路径**标志，见 §5） |
| **DLVR-G04** | 下游须联立读取 ledger 与 audit 两层 |

### 2.5 Holdout9（Phase 3.5 · 与 slice1 caveat10 正交）

| 来源 | 要点 |
|------|------|
| [cninfo_c_class_erad_snapshot_rebuild_readiness_plan.md](../../plans/cninfo_c_class_erad_snapshot_rebuild_readiness_plan.md) §1.1–1.2 | holdout **9** 不在 491 根内 · **禁止 promote** · 纳入 block 矩阵 |
| [cninfo_c_class_phase35_holdout_closed_with_caveat_ledger.csv](cninfo_c_class_phase35_holdout_closed_with_caveat_ledger.csv) | 9 行 · 全部 `promotion_allowed_now=no` |
| 风险 **SR-03** | holdout 9 被 merge 进 rebuild universe — **高** · YAML/manifest 排除 |

**注：** `000003`（PT金田A）同时出现在 partial7（CE1E061）与 holdout9；两轨排除语义不同，排除清单保留两行（见 [exclusion universe CSV](cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv)）。

---

## 3. Readiness 矩阵评估 — production rebuild 是否有价值

### 3.1 候选矩阵（Slice-C-EraD-03 · 只读复核）

来源：[cninfo_c_class_erad_snapshot_rebuild_candidate_matrix.csv](cninfo_c_class_erad_snapshot_rebuild_candidate_matrix.csv) · [readiness summary](cninfo_c_class_erad_snapshot_rebuild_readiness_summary.md) · [next-step recommendation](cninfo_c_class_erad_snapshot_rebuild_next_step_recommendation.md) · [readiness plan](../../plans/cninfo_c_class_erad_snapshot_rebuild_readiness_plan.md)

| Cohort | Count | Snapshot present | `rebuild_candidate` | 阻塞原因摘要 |
|--------|-------|------------------|----------------------|--------------|
| phase35_491 | 491 | yes_491_local_json | **no** | QA closed · 491 track closed on origin/main · MVP 足够 |
| 863_primary | 863 | yes_863_local_json | **no** | full 已存在 · 58 needs_review 为 ledger 语义非 harvest 缺口 |
| 863_primary_complete_only | 805 | yes_863_subset | **no** | harvest complete · snapshot 已 present |
| needs_review_58 | 58 | yes_863_subset | **no** | deferred triage · rebuild 不修复 ledger |
| holdout_9 | 9 | no_not_in_491 | **no** | closed-with-caveat · promotion forbidden |
| holdout_8_hold_for_review | 8 | no | **no** | not in 491 success subset |
| holdout_C35R016 | 1 | no | **no** | still_partial · not promoted |

**结论：** 全部 cohort **`rebuild_candidate = no`**。Production snapshot rebuild **无净增量价值**（491/863 本地 JSON 已完整 · QA/closure 已收口 · holdout 锁定 · slice1 caveat10 已文档化）。

### 3.2 Slice1 fuller-market 200 与 complete pool

| 指标 | 值 |
|------|-----|
| universe | 200（CE1E001–CE1E200） |
| ledger complete | **193** |
| ledger partial | **7**（partial7） |
| audit needs_review | **3**（empty-dividend3 · ledger complete） |
| 可纳入 complete snapshot pool | **190**（audit complete）+ 策略性排除 empty-dividend3 |
| 本包排除行数 | **19**（7+3+9）→ [exclusion universe CSV](cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv) |

---

## 4. 选项建议

### Option A — HOLD production rebuild（**首选 · 本包推荐**）

| 依据 | 详情 |
|------|------|
| Readiness 矩阵 | 全部 cohort `rebuild_candidate=no` |
| 生产根 | `full/`（863）与 `phase35_batch_500_001_expanded_success_491/`（491）已存在且受保护 |
| Era D MVP | snapshot 已足够研究 MVP |
| Holdout / caveat | 9 holdout + 10 slice1 caveat 保持 `accept_with_caveat` |
| 58 needs_review | ledger 语义问题 · **非** rebuild 触发器 |

**动作：** 保持生产 snapshot 根只读 · 不执行 `--execute` 写生产根 · progression 限于 audit/mock 文档化。

### Option B — Mock-root dry-run（**准备路径 · 计划已文档化 · 本包不执行**）

| 依据 | 详情 |
|------|------|
| AQ-C-SNAP | 解锁 snapshot preparation · mock-root 设计 |
| 执行状态 | **plan only** — 见 [mock rebuild plan](cninfo_c_class_snapshot_mock_rebuild_plan_20260714.md) |
| 输出根 | `outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_*`（**非**生产根） |
| 前置 | `c_class_erad_snapshot_rebuild_dryrun_gate` 未来另开 · 本包不调用 builder |

**何时选用：** 团队需要在**不触碰生产根**前提下验证 builder dry-run · exclusion manifest · cleanup guard 时；**不是**当前 production rebuild 的必要条件（因矩阵全部为 no）。

---

## 5. 规划标志（preparation path only）

AQ-C-SNAP 批准后，本包登记以下**分层**标志（文档化 · 非 runner 自动翻转）：

```
approved_for_snapshot_rebuild = true          # preparation path only（AQ-C-SNAP）
execute_production_snapshot_rebuild = false   # matrix rebuild_candidate=all no
production_rebuild_still_requires = separate_human_execute_approval_if_matrix_flips_yes
c_class_snapshot_progression_gate = PACKAGE_COMPLETE
```

| 标志 | 值 | 含义 |
|------|-----|------|
| `approved_for_snapshot_rebuild` | **true** | 允许 snapshot progression 准备工件（排除清单 · mock 计划 · validation 包） |
| `execute_production_snapshot_rebuild` | **false** | **禁止**对 C-ROOT-004 / C-ROOT-005 生产根执行 rebuild overwrite |
| `rebuild_candidate`（全 cohort） | **no** | progression = **mock/audit packaging**，**不是** prod rebuild |
| `production_ready` | **未授权** | 无 validation 支撑不得膨胀 |

**显式边界：** `approved_for_snapshot_rebuild=true` **不**自动授权 production execute。仅当未来 readiness 矩阵出现 `rebuild_candidate=yes` 且人批 **execute** 短语时，才可另开 production rebuild 切片。

---

## 6. 伴生产物

| 文件 | 说明 |
|------|------|
| [cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv](cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv) | 19 行排除清单（partial7 + empty-dividend3 + holdout9） |
| [cninfo_c_class_snapshot_mock_rebuild_plan_20260714.md](cninfo_c_class_snapshot_mock_rebuild_plan_20260714.md) | mock-root dry-run 计划（不执行） |

---

## 7. 红线确认

| 项 | 状态 |
|----|------|
| CNINFO 调用 | **0** |
| Production snapshot rebuild execute | **未执行** |
| `outputs/snapshot/cninfo_c_class/full/` | **未触碰** |
| `phase35_batch_500_001_expanded_success_491/` | **未触碰** |
| Holdout promotion | **禁止** |
| commit / push | **无** |

---

## 8. Gate

```
task_id = C-GEN-20260714-06
aq_c_snap_recorded = true
c_class_snapshot_progression_gate = PACKAGE_COMPLETE
approved_for_snapshot_rebuild = true（preparation path only）
execute_production_snapshot_rebuild = false
rebuild_candidate_all_cohorts = no
primary_recommendation = Option_A_HOLD
secondary_path = Option_B_mock_dryrun_plan_only
```

**不是 verified** · **不是 production_ready** · **不是 execute_production_snapshot_rebuild**

---

## 9. 下一步（Controller / Human）

1. Evidence Auditor 核验 exclusion CSV 行数（19）与 partial7/empty-dividend/holdout ledger 一致。
2. 若需可执行 mock dry-run：另批 Slice-C-EraD-03b · 引用 mock plan · 仍用 `_mock_*` 根。
3. Production rebuild：**保持 HOLD** 直至矩阵与 execute 审批同时翻转。

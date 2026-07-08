# CNINFO C-Class Phase 2 Expansion Smoke Execution Checklist

_生成时间：2026-07-08_

> **性质：** Phase 2 smoke **未来执行**检查清单。**本轮不执行**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [Phase 2 smoke plan](cninfo_c_class_phase2_expansion_smoke_plan.md)
- [smoke universe output design](cninfo_c_class_phase2_smoke_universe_output_design.md)

---

# Pre-Execution Checks

| # | 检查项 | 期望 | 状态 |
|---|--------|------|------|
| 1 | selected companies count | **= 200** | 待执行 |
| 2 | all rows classification | **= matched_active** | 待执行 |
| 3 | requires_manual_review | **= false**（全部） | 待执行 |
| 4 | harvest_support_status | **= candidate_supported** | 待执行 |
| 5 | snapshot_support_status | **= not_built** | 待执行 |
| 6 | no hold rows | hold_flag=false · 无 matched_hold | 待执行 |
| 7 | no BSE legacy rows | 无 matched_bse_legacy_hold · board=bse=0 | 待执行 |
| 8 | no identity_conflict rows | conflict count=0 | 待执行 |
| 9 | expected request count calculated | **200 × 7 = 1400** HTTP cases | 待执行 |
| 10 | rollback strategy documented | 见下文 | 待执行 |

---

# Expected Request Count

| 项 | 值 |
|----|-----|
| 公司数 | **200** |
| HTTP 主源/公司 | **7**（security observe-only） |
| **总 HTTP cases** | **1400** |
| derived 源 | 不单独请求（依赖 basic） |

---

# Rollback Strategy

| 场景 | 动作 |
|------|------|
| harvest reach 崩溃 | halt live · 保留 partial raw · **不触碰** 863 产物 |
| 限流/封禁 | 立即 stop · resume 后续续跑 |
| 分类错误公司混入 | 剔除 smoke YAML · 重跑 selection · 不 merge |
| snapshot 批量失败 | 单公司隔离 · status CSV 标记 failed · 不回写 863 |
| QA 不达标 | 不升级 C-class 状态 · 产出 residual queue |

**原则：** 863 已验证 universe **只读** · merge_executed=false

---

# Future Execution Steps

| Step | 动作 | 产出 | 本轮 |
|------|------|------|------|
| **1** | generate smoke YAML | `eval_companies_c_class_phase2_smoke_200.yaml` | 未启动 |
| **2** | run harvest dry-run | dry-run report | 未启动 |
| **3** | manual approval | approval record | 未启动 |
| **4** | execute harvest | raw/normalized/quality（200） | 未启动 |
| **5** | offline QA | QA report | 未启动 |
| **6** | snapshot build | 200 JSON | 未启动 |
| **7** | snapshot QA | QA summary | 未启动 |

## Step 1 细节（未来）

- 输入：refreshed CSV · stratified sample seed=20260708
- 验证：10 项 pre-execution checks 全 PASS

## Step 2 细节（未来）

- 脚本：`harvest_cninfo_c_class.py --dry-run --universe <yaml>`
- 验证：universe=200 · hold_overlap=0

## Step 3 细节（未来）

- 须显式 flag：`--approve-phase2-smoke-harvest`（规划名）
- 无批准 **禁止** Step 4

## Step 4–7 细节（未来）

- 沿用 863 runner resume / per-company isolation
- snapshot：`build_cninfo_c_class_snapshot_batch.py`
- QA：`review_cninfo_c_class_snapshot_full_quality.py`

---

# Gate（未来执行后）

| Gate | 条件 |
|------|------|
| `phase2_smoke_harvest_gate` | reach ≥95% · 0 schema blocker |
| `phase2_smoke_snapshot_gate` | valid JSON 100% · caveat 合法 |
| `phase2_smoke_closure_gate` | QA 完成 · C-class 状态 **不自动升级** verified |

---

# 红线

执行阶段 **禁止：**

- 无批准 live
- 修改 863 raw/normalized
- identity merge
- registry implementation / DB
- verified / testing_stable_sample

**本轮：** 全部步骤 **not started**

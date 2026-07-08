# CNINFO C-Class Full Market Phased Execution Plan

_生成时间：2026-07-08_

> **性质：** 全市场扩展分阶段执行计划。**仅规划** · **execution not started** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [universe reconciliation plan](cninfo_c_class_full_market_universe_reconciliation_plan.md)
- [expansion readiness review](cninfo_c_class_full_market_expansion_readiness_review.md)
- [harvest architecture](cninfo_c_class_full_market_harvest_architecture.md)
- [reconciliation matrix](../outputs/validation/cninfo_c_class_full_market_universe_reconciliation_matrix.csv)

---

# 0. 执行总览

```mermaid
flowchart LR
    P0[Phase 0 Reconciliation] --> P1[Phase 1 Registry Refresh]
    P1 --> P2[Phase 2 Smoke 100-200]
    P2 --> P3[Phase 3 Batch 500]
    P3 --> P4[Phase 4 Full Expansion]
```

| 阶段 | 规模 | 本轮 | 需 CNINFO/live |
|------|------|------|----------------|
| Phase 0 | 6124 对账 | 规划完成 | **否** |
| Phase 1 | candidate refresh | 未启动 | **否** |
| Phase 2 | 100–200 | 未启动 | **是**（smoke） |
| Phase 3 | 500/批 | 未启动 | **是** |
| Phase 4 | ~5000+ | 未启动 | **是** |

**全局红线：** merge_executed=false · 不改写 863 历史 · registry Layer 2 未实现前不跳 DB

---

# Phase 0: Universe Reconciliation

## Goal

将 Era B 6124 与 Era C 863 / hold / BSE / identity ledger 完成离线对账分类。

## Input

| 输入 | 路径 |
|------|------|
| Era B baseline | `lab/eval_companies_full_market_2024.yaml` |
| Era C active | `lab/eval_companies_c_class_harvest_863_non_bse.yaml` |
| Hold | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml` |
| Registry candidate | `outputs/validation/cninfo_c_class_company_registry_candidate_draft.csv` |
| Decision ledger | `outputs/validation/cninfo_c_class_registry_identity_decision_ledger.csv` |
| Conflict triage | `outputs/validation/cninfo_c_class_registry_conflict_triage.csv` |

## Output

| 产出 | 说明 |
|------|------|
| `company_registry_reconciliation_candidate.csv` | 对账分类叠加层（规划） |
| `cninfo_c_class_universe_reconciliation_summary.md` | 分类计数 · manual 清单 |
| phased universe YAML 草案 | 按分类分轨（active / hold / bse / manual） |

## Gate

| Gate | 条件 |
|------|------|
| `universe_reconciliation_gate` | 6124 行均有 canonical_status · 8 manual 有 disposition · hold/BSE 分轨明确 |

## Rollback Strategy

| 场景 | 回滚 |
|------|------|
| 分类逻辑错误 | 删除 reconciliation 产物 · 重跑离线脚本 · **不触碰** harvest/snapshot |
| manual 激增 | 暂停 Phase 1+ · 回到 identity signoff |
| Era B 口径变更 | 冻结 reconciliation 版本 · 重新对账 |

---

# Phase 1: Registry Candidate Generation (Refresh)

## Goal

基于 Phase 0 对账结果刷新 registry candidate 分类字段（离线）；**不实现** company_registry 表。

## Input

| 输入 | 说明 |
|------|------|
| Phase 0 reconciliation CSV | canonical_status · hold_status · bse_status |
| 既有 candidate draft | 6124 行 base |
| Decision ledger | 267 decisions |

## Output

| 产出 | 说明 |
|------|------|
| `company_registry_candidate_reconciled.csv` | candidate + reconciliation 字段 |
| `full_market_phased_universe_manifest.yaml` | Phase 2–4 批次输入清单草案 |

## Gate

| Gate | 条件 |
|------|------|
| `registry_candidate_refresh_gate` | 分类与 ledger 一致 · 无未解释 conflict 进入 active 池 |

## Rollback Strategy

| 场景 | 回滚 |
|------|------|
| 字段污染 | 回退到 `company_registry_candidate_draft.csv` · reconciliation 层可重建 |
| registry implementation 决策变更 | 冻结 refresh · 不进入 Phase 2 |

---

# Phase 2: Small Expansion Smoke (100–200)

## Goal

在 Phase 0 active 池中抽样 100–200 家未验证公司，验证 harvest → normalized → snapshot 链路在全市场扩展域的可行性。

## Input

| 输入 | 说明 |
|------|------|
| Phase 1 manifest | `expansion_smoke_100_200.yaml`（未来） |
| 排除 | already_in_c_class 863 · hold · bse_legacy · identity_conflict · manual |

## Output

| 产出 | 说明 |
|------|------|
| raw / normalized / quality | 100–200 家（**未来执行**） |
| snapshot JSON | 100–200 家（**未来执行**） |
| smoke QA report | reach · completeness · failure taxonomy |

## Gate

| Gate | 条件 |
|------|------|
| `expansion_smoke_gate` | non-BSE reach ≥95%（延续 863 政策）· 0 schema blocker · resume 正常 |

## Rollback Strategy

| 场景 | 回滚 |
|------|------|
| reach 崩溃 | 停止 Phase 3+ · 诊断 source / mapper · 863 不受影响 |
| 限流/封禁 | 立即 halt live · 保留 partial raw · resume 续跑 |
| 分类错误公司混入 | 剔除 smoke 批次 · 回 Phase 0 重分类 |

**批准要求：** `--approve-expansion-smoke`（未来 flag · 本轮不实现）

---

# Phase 3: Batch Expansion (500/批)

## Goal

按 500 家/批对 non-BSE active 池执行 phased harvest + snapshot。

## Input

| 输入 | 说明 |
|------|------|
| Phase 1 manifest | 分批次 YAML（batch_001 … batch_N） |
| 863 已有产物 | resume 跳过 complete |
| Smoke gate | Phase 2 **PASS** 为前提 |

## Output

| 产出 | 说明 |
|------|------|
| 每批 harvest 产物 | raw / normalized / quality |
| 每批 snapshot | `outputs/snapshot/cninfo_c_class/full/{code}.json` |
| batch status CSV | per-company 终态 |
| batch QA summary | 每批 gate 报告 |

## Gate

| Gate | 条件 |
|------|------|
| `batch_expansion_gate` | 单批 failed=0 或 failed 在 retry 政策内 · QA valid JSON 100% |

## Rollback Strategy

| 场景 | 回滚 |
|------|------|
| 单批灾难性失败 | 冻结该批 · 不污染其他批 · status CSV 标记 failed |
| 磁盘/运行时超限 | 减小 batch size（200）· 已完成的批不回滚 |
| mapper 回归 | 停止后续批 · 离线 patch normalized · 不重跑已完成公司 |

**批准要求：** `--approve-batch-expansion --batch-id N`（未来 flag）

**估算批次：** ~5235 non-hold new ÷ 500 ≈ **11 批**（粗估 · 不含 BSE 轨）

---

# Phase 4: Full Expansion

## Goal

完成全部 non-BSE active 池 + BSE 920 子轨 harvest + snapshot + QA，达到全市场覆盖（hold / legacy 侧轨除外）。

## Input

| 输入 | 说明 |
|------|------|
| Phase 3 剩余批次 | non-BSE active |
| BSE 920 universe | ~326 candidate · 独立 gate |
| BSE legacy | 侧轨 · 不并入主 gate |

## Output

| 产出 | 说明 |
|------|------|
| full market harvest | ~5500+ 公司（粗估） |
| full market snapshot | 对应 JSON |
| full market QA | completeness · caveat 分布 |
| expansion closure summary | gate 与 residual 清单 |

## Gate

| Gate | 条件 |
|------|------|
| `full_market_expansion_gate` | active 池覆盖率 ≥ 目标阈值 · hold/legacy 有明确 disposition · **非 verified** |

## Rollback Strategy

| 场景 | 回滚 |
|------|------|
| BSE 轨失败 | BSE 独立回滚 · non-BSE 进度保留 |
| 全市场 QA 不达标 | 不升级 C-class 状态 · 产出 residual queue |
| registry implementation 就绪 | 可并行接入 Layer 2 · 不回写历史 |

**批准要求：** `--approve-full-market-expansion`（未来 flag）

---

# 并行轨道

| 轨道 | 与主相位关系 | 政策 |
|------|-------------|------|
| Hold 26 | 全程侧轨 | Option B · hold_no_retry |
| BSE legacy 251 | Phase 4 后或独立 | legacy probe · 3 manual 先结案 |
| Identity manual 8 | Phase 0 前/并行 | 不阻塞 Phase 0 设计 · 阻塞自动 reconciliation |
| Registry Layer 2 | 产品决策后 | implementation deferred · 不阻塞 Phase 0–1 |

---

# 阶段依赖与阻塞

| 阻塞项 | 阻塞阶段 | 说明 |
|--------|----------|------|
| Universe reconciliation 未执行 | Phase 1+ | Phase 0 必须先完成 |
| Registry implementation 未决策 | Phase 4 入库 | 不阻塞 harvest/snapshot |
| BSE legacy policy | BSE 920 Phase 4 | 920 可先 smoke |
| Hold policy 未固化 | hold 公司 | 已侧轨排除 |
| Phase 2 smoke 失败 | Phase 3–4 | 须诊断后重试 |

---

# 本轮状态

| 项 | 值 |
|----|-----|
| 规划 gate | **`phased_execution_plan_gate = DESIGN_COMPLETE`** |
| execution | **not started** |
| 推荐下一步 | Phase 0 离线 reconciliation 脚本构建与 dry-run |

---

# 红线

本轮 **不做：**

- CNINFO / live / harvest / snapshot build
- registry implementation / DB / MinIO / RAG
- identity merge
- raw / normalized / field_inventory 修改
- verified / testing_stable_sample

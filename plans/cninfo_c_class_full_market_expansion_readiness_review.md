# CNINFO C-Class Full Market Expansion Readiness Review

_生成时间：2026-07-08_

> **性质：** C 类从 863 snapshot universe 向 A 股全市场扩展的就绪度评估。**仅评估** · **不执行扩展** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [863 universe](../lab/eval_companies_c_class_harvest_863_non_bse.yaml)
- [全市场基准 universe](../lab/eval_companies_full_market_2024.yaml)
- [identity decision ledger](../outputs/validation/cninfo_c_class_registry_identity_decision_ledger.csv)
- [863 snapshot](../outputs/snapshot/cninfo_c_class/full/)
- [expansion planning summary](../outputs/validation/cninfo_c_class_full_market_expansion_planning_summary.md)
- [harvest architecture](cninfo_c_class_full_market_harvest_architecture.md)

---

# 1. Current State

## 1.1 当前已验证范围

| 项 | 值 |
|----|-----|
| **已验证 universe** | **863** 家 non-BSE（`harvest_863_non_bse`） |
| **harvest** | 完成 · `PASS_WITH_RESUME` |
| **snapshot** | **863** JSON · 全部 `complete_with_caveat` |
| **snapshot QA** | **863/863** valid JSON · 0 failed |
| **C-class 状态** | `SNAPSHOT_GENERATED_QA_REVIEW` |

## 1.2 863 已支持能力

| 能力层 | 863 状态 | 说明 |
|--------|----------|------|
| company identity | 已验证 | 基于 company_code · org_id 冲突已治理（元数据层） |
| business profile | 已验证 | basic_profile + derived business_scope |
| financial snapshot | 已验证 | 模块级 snapshot 组装 |
| shareholder profile | 已验证 | top_shareholders · top_float_shareholders（含 empty-but-valid 政策） |
| executive profile | 已验证 | executive_profile 主源 |
| dividend profile | 已验证 | dividend_history |
| document evidence | 已验证 | B 类文档引用链路（metadata） |
| quality layer | 已验证 | quality flags · completeness · `complete_with_caveat` 合法 |

## 1.3 结论

**863 snapshot 流水线已在非 BSE 子 universe 上完成端到端验证。**

| 确认项 | 结论 |
|--------|------|
| harvest → normalized → snapshot → QA | **已证明** |
| snapshot_status | `complete_with_caveat`（合法终态） |
| **全市场支持** | **否** — 本轮不声称 full market support |

```mermaid
flowchart LR
    H863[863 Harvest] --> N863[863 Normalized]
    N863 --> S863[863 Snapshot]
    S863 --> QA863[863 QA Review]
    QA863 --> Proven[Pipeline Proven]
    Proven -.->|NOT YET| FM[Full Market]
```

---

# 2. Full Market Target

## 2.1 目标基准

| 项 | 值 |
|----|-----|
| **目标 universe 基准** | Era B · `eval_companies_full_market_2024.yaml` |
| **基准公司数** | **~6124** |
| **扩展倍数** | ~7.1×（6124 / 863） |
| **当前缺口** | ~5261 家 non-BSE 未入 863 + BSE 板块 + hold 侧轨 |

## 2.2 重要 caveat

**Era B universe 是年报口径基准，不等于 CNINFO C-class 原生可达 universe。**

| 维度 | Era B 6124 | C-class CNINFO |
|------|------------|----------------|
| 来源 | 2024 年报公司列表 | F10 / profile endpoint 可达性 |
| 退市/ST | 含历史年报公司 | 需单独政策 |
| BSE | 含 BSE 公司 | 920 / 83·87 分轨 |
| hold | 未显式建模 | 26 all6 hold 已识别 |

## 2.3 未来 reconciliation 需求

全市场扩展前须完成以下对账（**本轮仅识别，不执行**）：

```
Era B universe (6124)
  + CNINFO identity governance (decision ledger)
  + BSE policy (920 active / 83·87 legacy)
  + hold policy (26 all6 hold)
  → reconciled full-market universe (未来产物)
```

| 输入 | 角色 |
|------|------|
| Era B 6124 | 数量与板块基准 |
| Identity governance | canonical / rename / legacy mapping 元数据 |
| BSE policy | 920 主轨 · legacy 侧轨 |
| hold policy | 排除或侧轨复审 |

---

# 3. Expansion Readiness Matrix

| Component | Current Status | Full Market Readiness | Blocker | Priority |
|-----------|----------------|----------------------|---------|----------|
| **Universe Registry** | 863 YAML proven | **NOT_READY** | Era B vs CNINFO 未 reconciliation | **P0** |
| **Identity Governance** | **READY** | **READY_FOR_EXPANSION** | none architecture-level | **P1** |
| **Harvest Runner** | 863 proven | **UNTESTED_AT_SCALE** | 5000+ 分批/退避未实测 | **P1** |
| **Snapshot Builder** | 863 proven | **UNTESTED_AT_SCALE** | 规模扩展未实测 | **P1** |
| **QA Framework** | 863 proven | **READY_WITH_CAVEAT** | `complete_with_caveat` 仍合法 | **P2** |
| **BSE Support** | partial | **NOT_READY** | legacy 83/87 · 3 manual mapping | **P0** |
| **Hold Universe** | 26 excluded | **POLICY_PENDING** | all6 hold 政策未固化执行 | **P1** |
| **Source Registry** | 6 testing + 4 candidate | **UNTESTED_AT_SCALE** | 6124 规模 reach 未验证 | **P1** |
| **Mapper** | 863 stable | **UNTESTED_AT_SCALE** | 无已知架构阻塞 | **P2** |
| **Registry (Layer 2)** | governance ready | **IMPLEMENTATION_DEFERRED** | company_registry 未实现 | **P1** |

详细矩阵见 [cninfo_c_class_full_market_expansion_readiness_matrix.csv](../outputs/validation/cninfo_c_class_full_market_expansion_readiness_matrix.csv)。

---

# 4. Expansion Risks

## 4.1 Identity scale

| 风险 | 说明 |
|------|------|
| 规模 | **6124** 家公司需 identity reconciliation |
| 治理完成度 | decision ledger **267** 条 · **259** approved · **8** manual |
| 未 merge | `merge_executed=false` — 历史记录未改写 |
| 影响 | 不阻塞架构批准 · 阻塞全量自动 reconciliation |

## 4.2 Universe differences

| 风险 | 说明 |
|------|------|
| Era B vs CNINFO | 6124 年报列表 ≠ F10 可达列表 |
| 重叠/缺口 | 863 已验证子集与 6124 的差集须 registry 派生 |
| ST/delisted | 需产品政策（纳入/排除/侧轨） |

## 4.3 BSE

| 轨道 | 状态 | 说明 |
|------|------|------|
| BSE 920 | partial ready | candidate 已生成 · 仅 smoke 验证 |
| BSE 83/87 legacy | separate track | `legacy_code_incompatible` · **3** manual mapping |
| 863 范围 | 不含 BSE | 全市场扩展须独立 BSE gate |

## 4.4 ST / delisted

| 项 | 说明 |
|----|------|
| 政策 | 未固化 — 须决定纳入 harvest 或 hold 侧轨 |
| 影响 | universe reconciliation 前置依赖 |

## 4.5 Source scaling

| 项 | 说明 |
|----|------|
| 863 成功 | 不代表 6124 规模同等 reach |
| 已知弱点 | top_float_shareholders 93% reach · share_capital empty-but-valid |
| 缓解 | phased smoke（200–500/批）+ source validation gate |

## 4.6 Quality

| 项 | 说明 |
|----|------|
| 终态 | `complete_with_caveat` **仍合法** |
| 预期 | 全市场 field_missing_flags 数量上升 |
| 政策 | partial / caveat 不视为 pipeline 失败 |

---

# 5. Readiness Gate

| Gate | 值 |
|------|-----|
| **full_market_expansion_readiness_gate** | **`PASS_WITH_CAVEAT`** |

## 5.1 通过理由

| # | 理由 |
|---|------|
| 1 | 863 harvest → snapshot → QA 流水线已证明 |
| 2 | Identity governance layer **READY** |
| 3 | 全市场 harvest/snapshot 架构已规划 |
| 4 | QA 框架可复用 · caveat 政策已确立 |

## 5.2 Caveat 理由

| # | Caveat |
|---|--------|
| 1 | 全市场 **execution not started** |
| 2 | Universe reconciliation 未完成 |
| 3 | Registry Layer 2 implementation **deferred**
| 4 | BSE legacy + hold 政策待固化 |
| 5 | 5000+ 规模 harvest/snapshot **untested_at_scale** |

## 5.3 明确不做（本轮）

- 不执行 full-market harvest / snapshot
- 不 run CNINFO / live
- 不实现 registry · 不建 DB
- 不 merge identities · 不修改 raw / normalized / field_inventory
- 不写 verified · 不升级 testing_stable_sample

---

# 6. Recommended Next Phase

**Full-market universe reconciliation and phased execution planning**

（非 full-market harvest 执行 · 非 registry implementation）

| 并行可选 | 说明 |
|----------|------|
| 8 例 manual identity 结案 | 不阻塞扩展规划 |
| BSE legacy probe 计划细化 | 侧轨政策固化 |

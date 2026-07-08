# CNINFO C-Class Phase 2 Expansion Smoke Plan

_生成时间：2026-07-08_

> **性质：** 全市场扩展 Phase 2 smoke 批次规划。**仅规划** · **不执行 harvest** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [refreshed candidate](../outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv)
- [refresh summary](../outputs/validation/cninfo_c_class_company_registry_candidate_refresh_summary.md)
- [phased execution plan](cninfo_c_class_full_market_phased_execution_plan.md)
- [harvest architecture](cninfo_c_class_full_market_harvest_architecture.md)

---

# 1. Purpose

## 1.1 目标

Phase 2 expansion smoke 验证 C-class **harvest → normalized → snapshot** 流水线能否在已证明的 **863** universe 之外扩展运行。

| 项 | 本轮 | 未来执行 |
|----|------|----------|
| 验证假设 | 4647 `matched_active` 池可安全抽样 | 200 家 live harvest + snapshot |
| 范围 | **规划 only** | 须人工批准 |
| CNINFO | **不调用** | 未来阶段 |

## 1.2 边界

- **不执行** harvest / snapshot / live
- **不生成** smoke YAML（本轮）
- **不修改** raw / normalized / field_inventory
- refreshed CSV 为 **validation artifact only**

```mermaid
flowchart LR
    Refresh[refreshed candidate] --> Pool[matched_active pool 4647]
    Pool --> Sample[stratified sample 200]
    Sample -.->|NOT NOW| Harvest[smoke harvest]
    Harvest -.->|NOT NOW| Snapshot[smoke snapshot]
```

---

# 2. Candidate Pool

## 2.1 主选池（Primary pool）

从 `cninfo_c_class_company_registry_candidate_refreshed.csv` 筛选：

| 字段 | 条件 |
|------|------|
| `reconciliation_classification` | **matched_active** |
| `refresh_action` | **full_market_active_candidate** |
| `harvest_support_status` | **candidate_supported** |
| `snapshot_support_status` | **not_built** |
| `requires_manual_review` | **false** |

**符合条件：4647 行**

## 2.2 排除分类

| classification | count | 排除原因 |
|----------------|-------|----------|
| already_in_c_class | 863 | 863 已验证 · resume 跳过 |
| matched_hold | 26 | hold 侧轨 |
| matched_bse_supported_candidate | 320 | BSE 920 独立 gate |
| matched_bse_legacy_hold | 242 | legacy 侧轨 |
| identity_conflict | 10 | 双行保留 · 禁止自动扩展 |
| needs_manual_review | 16 | 人工未结案 |
| not_found_in_cninfo | 0 | 未解析 |

## 2.3 附加排除（smoke 执行前）

| 规则 | 说明 |
|------|------|
| `board = bse` | 主池内约 **4** 行 BSE 标签 · Phase 2 为 **non-BSE smoke** |
| `listing_status = delisted` | 主池内约 **155** 行 · 可选降采样或分层标注 |
| 与 863 overlap | 已由 `already_in_c_class` 排除 |

---

# 3. Smoke Size

## 3.1 两个选项

| 选项 | 规模 | 优点 | 缺点 |
|------|------|------|------|
| **Option A** | **100** | 风险更低 · 更快反馈 | 分层覆盖较薄 |
| **Option B** | **200** | 与 stable 200 经验一致 · 分层更稳 | 请求量翻倍 |

## 3.2 推荐

**推荐 Option B：200 家公司**

| 理由 | 说明 |
|------|------|
| 规模足够 | 可检验 reach / empty-but-valid / resume 在扩展域的表现 |
| 风险可控 | 远低于 500 batch · 可 halt |
| 历史对齐 | 已有 stable 200 smoke 运维经验 |
| HTTP 可算 | 200 × 7 = **1400** cases（主源 · security observe-only） |

---

# 4. Sampling Strategy

## 4.1 分层维度（优先）

| 维度 | 主池分布（4647） | 200 抽样目标（粗估） |
|------|------------------|---------------------|
| **exchange** | SZSE 2612 · SSE 2031 · BSE 4 | SZSE ~113 · SSE ~87 · BSE **0** |
| **board** | sse_main 1544 · szse_main 1406 · chinext 1206 · star 487 · bse 4 | 按比例 · bse **0** |
| **listing_status** | listed 4492 · delisted 155 | listed ~193 · delisted ~7（或全 listed） |
| **security_type** | 部分缺失 | 有值则分层 · 缺失则跳过 |
| **active_status** | active 4647 | 全 active |
| **confidence** | low 4647 | 全 low（预期） |

## 4.2 回退策略

字段缺失时按以下顺序回退：

1. `company_code` 前缀（000/002/300/600/688 等）
2. `exchange` + `board` 联合分布
3. `source` 字段（full_market_2024 fill）
4. 确定性排序 + 固定 seed（可复现）

## 4.3 抽样原则

| 原则 | 说明 |
|------|------|
| 确定性 | 固定 seed · 同输入同输出 |
| 无重叠 863 | 排除 already_in_c_class |
| 无 manual | requires_manual_review=false |
| 无 BSE 主轨混入 | board=bse 排除（Phase 2 non-BSE smoke） |
| 不 merge | 每 code 独立一行 |

---

# 5. Gate

## 5.1 执行前门槛（未来）

| # | 检查项 |
|---|--------|
| 1 | smoke universe YAML 已生成 |
| 2 | harvest dry-run 计划就绪 |
| 3 | expected HTTP count 已计算（200 × 7 = **1400**） |
| 4 | 无 manual_review 行 |
| 5 | 无 hold 行 |
| 6 | 无 BSE legacy 行 |
| 7 | 无 identity_conflict 行 |
| 8 | 人工批准 checklist 完成 |

## 5.2 本轮 planning gate

**`phase2_expansion_smoke_planning_gate = DESIGN_COMPLETE`**

**Execution status：** **not started**

---

# 6. 红线

本轮 **不做：**

- CNINFO / live / harvest / snapshot
- smoke YAML 生成
- production registry / DB
- identity merge
- raw / normalized / field_inventory 修改
- verified / testing_stable_sample

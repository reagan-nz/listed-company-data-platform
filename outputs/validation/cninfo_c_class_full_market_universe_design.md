# CNINFO C-Class Full Market Universe Design

_生成时间：2026-07-08_

> **性质：** 863 → 全市场 universe 扩展设计说明。**仅规划** · **本轮不生成公司名单** · **无 CNINFO**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## 1. 当前 vs 未来

| 维度 | 当前（863） | 未来（全市场） |
|------|-------------|----------------|
| universe_id | `harvest_863_non_bse` | `full_market_a_share`（规划名） |
| company_count | **863** | **~6124**（基准见下） |
| 板块 | SSE/SZSE/ChiNext/STAR | + **BSE**（分 920 / legacy 侧轨） |
| harvest | **完成** | 待 phased 扩展 |
| snapshot | **863 JSON** · QA 完成 | 待 full market batch |
| 状态 | `SNAPSHOT_GENERATED_QA_REVIEW` | 扩展后仍为 QA 驱动，非 verified |

---

## 2. Universe 来源与派生链

### 2.1 当前 863 派生链（已执行）

```
eval_companies_1000.yaml (1020)
  → 清洗规则 §6（-131）
  → smoke_1000_non_bse_candidate.yaml (889)
  → 排除 26 all6 hold
  → harvest_863_non_bse.yaml (863)
```

### 2.2 未来全市场基准

| 来源 | 路径 | 数量 | 口径说明 |
|------|------|------|----------|
| **全市场基准** | `lab/eval_companies_full_market_2024.yaml` | **6124** | Era B 2024 年报 universe；**非** C-class 原生 CNINFO 列表 |
| C-class 近端母本 | `lab/eval_companies_1000.yaml` | 1020 | C-class scale 样本父本 |
| 863 已验证子集 | `lab/eval_companies_c_class_harvest_863_non_bse.yaml` | 863 | 当前主线 |

**重要 caveat：** 6124 与 C-class F10 endpoint 可达性**尚未**在全量上交叉验证。扩展前须做 registry 派生 + 抽样 live 探测（未来阶段，本轮不执行）。

### 2.3 预计新增公司数量（粗估）

| 扩展段 | 估算 | 说明 |
|--------|------|------|
| non-BSE 未入 863 | **~5261** | 6124 − 863（含重叠/退市待 registry 去重） |
| BSE 920 active | **~200+** | 全市场 BSE 待与 6124 统计 |
| BSE 83/87 legacy | **~数十** | 侧轨 hold，不并入主 gate |
| 26 all6 hold | **26** | 已明确 hold，见 hold policy |
| **净新增 harvest 目标** | **~5000–5500** | 去重后粗估，非本轮精确值 |

**本轮不生成实际名单。**

---

## 3. 新增板块

| 板块 | 当前 863 | 全市场扩展 |
|------|----------|------------|
| sse_main | 281 | 扩展 + 已覆盖部分 |
| szse_main | 226 | 扩展 |
| chinext | 231 | 扩展 |
| star | 125 | 扩展 |
| **bse** | **0**（863 显式 non-BSE） | **新增** · 分 920 / legacy 子轨 |

---

## 4. 新增风险

| 风险 | 级别 | 说明 |
|------|------|------|
| **规模** | 高 | 5000+ 公司 × 10 源 ≈ 50000+ HTTP cases（未来 live 阶段） |
| **Endpoint 限流** | 高 | 须沿用 harvest runner 退避/重试；禁止大规模无节制请求 |
| **ST/退市增长** | 中 | 全市场含更多异常公司；hold 池可能扩大 |
| **BSE legacy** | 高 | 83/87 代码 `legacy_code_incompatible`；不可假设 scode 通用 |
| **名称变更** | 中 | registry 须以 code+org_id 为稳定键 |
| **6124 vs CNINFO 偏差** | 中 | Era B 年报列表与 F10 活跃列表可能不一致 |
| **source_partial 放大** | 中 | shareholder/dividend empty_but_valid 在全市场更常见 |
| **磁盘/运行时** | 中 | snapshot JSON 粗估 3–6 GB（863 约 500–900 MB 外推） |

---

## 5. 扩展策略（规划）

### Phase A — Registry 与清洗规则固化
- 从 6124 + 现有 YAML 派生 registry draft（不执行）
- 统一 hold / BSE / abnormal 分类

### Phase B — BSE 子轨
- 920 active 单独 smoke → harvest
- 83/87 legacy hold + targeted probe

### Phase C — non-BSE 分批扩展
- 按板块分批：`--limit` smoke → 批准 → phased harvest
- 复用 `--resume` / failure isolation

### Phase D — Full market snapshot + QA
- 扩展 snapshot batch universe
- 全量 QA review（只读）

---

## 6. 与 863 关系

- **863 不废弃**：作为 `completed_863` 已验证基准子集
- 扩展为 **增量**，非重写
- smoke 10 / full batch runner / QA review 脚本可复用

---

## 7. 红线确认

- 本轮 **不生成** 全市场公司名单
- 不请求 CNINFO · 不 harvest · 不 snapshot build
- raw / normalized / field_inventory **未修改**
- 不写 verified · 不 testing_stable_sample

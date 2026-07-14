# CNINFO A 类 Next-Scale Slice2 — ST 选取策略

_生成时间：2026-07-14_

> **offline planning only** · **CNINFO = 0** · **NOT APPROVED live** · **NOT APPROVED runner** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

---

## 1. 任务定位

| 项 | 值 |
|----|-----|
| Task | **A-GEN-20260714-08** |
| 目的 | 为 slice2 draft 扩批定义 **ST（Special Treatment / ST / \*ST / S\*ST）** 纳入/排除策略，替代无 mission 价值的 **+6 buffer churn** |
| 输入状态（Run4 链） | remainder **156** · A∩B overlap **182** · O3 下 **+100 + +50 = 150** planning draft 已存在 |
| Executor 立场 | 仅文档与离线 checklist · 不 mutate 既有 draft CSV · 不 flip gate |

**前置引用（不重写）：**

- [remainder summary](cninfo_a_class_slice2_pool_remainder_summary_20260714.md)（156）
- [overlap lint spec](cninfo_a_class_slice2_overlap_lint_spec_20260714.md)（L-D4 · O1–O4）
- [+100 lint check](cninfo_a_class_erad_next_scale_slice2_draft_lint_check_20260714.md)（48/100 ST · L-D4 **CAVEAT**）
- [+50 lint check](cninfo_a_class_erad_next_scale_slice2_plus50_lint_check_20260714.md)（0/50 ST · L-D4 **PASS**）
- [universe strategy §3.1](cninfo_a_class_erad_next_scale_universe_strategy.md)（非 ST 硬规则）

---

## 2. ST 事实基线（离线复核）

### 2.1 Remainder 池 ST 分布

| 指标 | 值 | 方法 |
|------|-----|------|
| REMAINDER 总计 | **156** | `cninfo_a_class_slice2_pool_remainder_draft_20260714.csv` |
| ST 名称命中 | **48** | 正则 `(?:\*?ST\|S\*ST)` 匹配 `company_name` |
| 非 ST | **108** | 余量 |
| ST 占 remainder 比 | **30.8%** | 48/156 |
| AB_182 ∩ REMAINDER | **0** | 182 已全部扣减 · 与 ST 策略无新增交叉 |

**ST 板块分布（remainder 内 48 码）：**

| 板块 | ST 码数 |
|------|---------|
| 深市主板（00xxxx） | 22 |
| 沪市主板（60xxxx） | 17 |
| 创业板（300xxx） | 7 |
| 科创板（688xxx） | 2 |

**非 ST 板块分布（remainder 内 108 码）：**

| 板块 | 非 ST 码数 |
|------|------------|
| 沪市主板（60xxxx） | 47 |
| 科创板（688xxx） | 61 |

**结构特征：** 48 个 ST 码全部落在 **低 `company_code` 段**（000416–603838 区间）；按码升序取前 N 时 **确定性耗尽全部 ST**。

### 2.2 既有 slice2 draft 与 L-D4

| 批次 | 行数 | ST 命中 | L-D4 | 选取规则（现状） |
|------|------|---------|------|------------------|
| +100（AD2E501–600） | 100 | **48** | **CAVEAT** | REMAINDER 码升序前 100 |
| +50（AD2E601–650） | 50 | **0** | **PASS** | +100 后余 56 码中取前 50 |
| 合并 150 | 150 | **48**（32.0%） | **CAVEAT** | — |
| 未选用 remainder | **6** | **0** | — | 688785–688818 科创板非 ST |

**对照：** slice1 universe draft **300 码 · ST = 0**（与 universe strategy §3.1 一致）。

### 2.3 ST 检测规则（lint 用 · 离线）

```
ST_NAME_HIT := company_name 匹配 /(?:\*?ST|S\*ST)/
```

| 模式 | 示例 | 命中 |
|------|------|------|
| `*ST` 前缀 | `*ST民控` | yes |
| `ST` 前缀 | `ST得润` | yes |
| `S*ST` | `S*ST国瓷` | yes |
| 非 ST | `德宏股份` | no |

**局限（诚实披露）：** 仅名称启发式 · 不调用 CNINFO · 不校验实时 ST 状态变更 · 退市码可能仍留旧名。

---

## 3. 策略选项（Controller 择一 · 无默认 live 批准）

### 3.1 S1 — ST-EXCLUDE（**推荐默认 · slice1 同型**）

| 项 | 说明 |
|----|------|
| 规则 | 从 REMAINDER 剔除全部 ST 命中码后，再按既定排序（建议 `company_code` 升序）选取 |
| L-D4 | **PASS**（目标） |
| 与 universe strategy | **一致** §3.1「非 ST」 |
| 可达规模上界 | **108**（= 非 ST remainder 全集） |
| 对既有 +100 draft | **不兼容** — 须重生成 candidate CSV（本任务不执行） |

**推荐排序（S1 下）：**

1. `FILTER_ST(rem)` → 108 码
2. `SORT(company_code ASC)`
3. 取前 `N`，`N ≤ 108`

### 3.2 S2 — ST-CAP（有条件纳入）

| 项 | 说明 |
|----|------|
| 规则 | 允许 ST，但 `|ST ∩ S2_DRAFT| ≤ CAP_ST` |
| 建议 CAP_ST | **0**（等同 S1）或 **≤5**（试点）或 **≤10%·N**（需写明分母） |
| L-D4 | CAP_ST=0 → PASS；否则 **CAVEAT** + 须 Controller 显式 ST 例外表 |
| 适用 | 刻意覆盖风险披露/异常披露形态 · **非** slice1 默认同型路径 |

### 3.3 S3 — ST-SIDE-TRACK（隔离记账）

| 项 | 说明 |
|----|------|
| 规则 | 48 个 ST remainder 码进入独立 `st_side_track_ledger` · **永不**进入 primary `next_scale_slice2` cohort |
| primary S2_DRAFT | 仅非 ST 108 码 · 等同 S1 选取面 |
| L-D4 | primary **PASS** · side-track 单独 cohort 标签 |
| live | side-track **NOT APPROVED** · 需独立 approval phrase |

### 3.4 S4 — STATUS-QUO（码升序 · 当前 +100/+50 行为）

| 项 | 说明 |
|----|------|
| 规则 | 不滤 ST · REMAINDER 码升序直接切片 |
| 现状 | +100 含 48 ST · +50 无 ST · 合计 150 |
| L-D4 | **CAVEAT**（与 slice1 / universe strategy 不一致） |
| 风险 | 首批 metadata lineage **富集退市/ST 边缘码** · attribute gap 与 B 轨可比性下降 |
| Executor 立场 | **不作为推荐冻结路径** · 仅保留为已存在 planning draft 的事实记录 |

---

## 4. 纳入 / 排除规则矩阵

### 4.1 硬排除（任一策略均适用）

| 规则 ID | 条件 | 依据 |
|---------|------|------|
| **ST-X1** | `company_code ∈ AB_182` | overlap lint §4 · 已占用 |
| **ST-X2** | `company_code ∈ A_ALL_U` | L-A1 |
| **ST-X3** | `company_code ∈ B_CUM` | L-B1 |
| **ST-X4** | BSE 码段 | universe strategy §3.1 |
| **ST-X5** | unresolved side-track 码 | L-D5 |
| **ST-X6** | `company_code ∉ REMAINDER`（不扩池时） | L-P2 |

### 4.2 ST 专用纳入门（仅 S2 / S4）

| 规则 ID | 条件 | S1/S3 | S2 | S4 |
|---------|------|-------|----|----|
| **ST-I1** | ST 名称命中 | exclude | cap 内 allow | allow |
| **ST-I2** | Controller ST 例外表行 | — | required if cap>0 | optional |
| **ST-I3** | 单批 ST 占比 ≤ 阈值 | — | 建议 ≤10% | 现状 32%（+150 合并） |

### 4.3 与 L-D4 关系

| 策略 | L-D4 期望 | gate 语义 |
|------|-----------|-----------|
| S1 / S3 primary | **PASS** | 可进入 approval package lint（overlap 仍须全 PASS） |
| S2 cap>0 | **CAVEAT** | 须 ST 例外签收 |
| S4 | **CAVEAT** | 当前 +100/+150 状态 · 须 Controller 接受 slice1 非同型 |

---

## 5. 与 O1–O4 overlap 治理的交互

**原则：** ST 策略与 A∩B **182** 治理 **正交** — 182 码已从 REMAINDER 扣除；ST 选取 **不引入** 新 A∩B 交叉。

| 选项 | ST 策略影响 | 说明 |
|------|-------------|------|
| **O1** B 保留 · A 承认交叉 | 无 | 182 记账 · slice2 仍从 REMAINDER |
| **O2** A slice1 优先 | 可能 **重算 REMAINDER** | 若 B 释放码回池 · ST 计数须重跑 §2.1 |
| **O3** 严格_disjoint · 182 记账（**当前 lint 默认**） | **无变更** | +100/+50 draft 已采用 O3 |
| **O4** 扩池 | ST 池可能扩大 | 新 POOL 须独立 ST 扫描 · L-P2 例外 |

**Executor 立场（延续 A-05）：** 在 Controller 未裁决 182 前，slice2 lint 与 ST 策略均假设 **O3** · `resolution_status=PENDING_CONTROLLER`。

---

## 6. 与 unused remainder 池的关系

| 池 | 码数 | ST | 与 ST 策略 |
|----|------|-----|------------|
| REMAINDER 全集 | 156 | 48 | 源 |
| +100 draft 已占 | 100 | 48 | S4 行为 · S1 下视为 **待废弃选取** |
| +50 draft 已占 | 50 | 0 | S1/S3 下 **可保留**（全非 ST） |
| **仍未选用** | **6** | **0** | 688785–688818 · S1 下并入非 ST 尾部 |

**S1 重选示意（非本任务产出 CSV）：**

| 目标 N | 非 ST 需求 | 可行 | 备注 |
|--------|------------|------|------|
| +100 | 100 | **yes** | 108 非 ST 中码升序前 100 |
| +108 | 108 | **yes** | 非 ST remainder **全集** |
| +150 | 150 | **no** | 非 ST 仅 108 · 缺口 42 |
| +156 | 156 | **no** | 同上 |

**+6 buffer churn：** 将 6 码补入 S4 路径仅清 buffer · **不**解决 +100 中 48 ST 的 L-D4 CAVEAT · **不推荐**作为独立任务。

---

## 7. A∩B 碰撞风险（ST 视角）

| 风险面 | 评估 | 缓解 |
|--------|------|------|
| ST 码 ∈ AB_182 后重入 slice2 | **无** — AB_182 ∩ REMAINDER = ∅ | L-B4 + 182 台账 |
| ST 策略导致 **新** A∩B code 交叉 | **无** — ST 仅滤名称 · 不扩 universe 来源 | 保持 O3 + L-B* |
| ST 码与 B live 隐性重叠 | **无** — 当前 draft L-B1..B4 全 PASS | 未来重选仍须跑 lint |
| 182 治理翻转为 O2 后 ST 池变化 | **中** — remainder 重算可能增减 ST | O2 批准后重跑 §2.1 |
| ST 边缘码 metadata 异常抬高 unresolved 率 | **中** — 48 码多为低号段历史 ST | S1 规避 · S4 须 caveat 签收 |

---

## 8. 推荐规模 cap（规划 · 非批准）

在 **O3 · 不扩池 · ST-EXCLUDE（S1）** 前提下：

| 冻结档位 | 码数 | ST | L-D4 | 判定 | 备注 |
|----------|------|-----|------|------|------|
| **+100 非 ST** | 100 | 0 | PASS | **FEASIBLE** | 对齐 slice1 风格 · 余 8 非 ST |
| **+108 非 ST** | 108 | 0 | PASS | **FEASIBLE** | 非 ST remainder 上限 |
| **+150（S4 现状）** | 150 | 48 | CAVEAT | FEASIBLE | 须接受 ST 富集 |
| **+156（S4 全量）** | 156 | 48 | CAVEAT | FEASIBLE | 含 6 未选非 ST |
| **+150（S1）** | — | — | — | **NOT FEASIBLE** | 非 ST 不足 |

**Controller 推荐 cap（单选 · 非 live）：**

1. **首选：+100 · S1（ST-EXCLUDE）** — mission 价值最高 · L-D4 PASS · 与 slice1 同型  
2. **次选：+108 · S1** — 吃满非 ST remainder · 仍 PASS  
3. **若坚持已生成 +100/+50 合并 150：须显式择 S4 + L-D4 CAVEAT 签收** — 不推荐静默冻结  

**明确反对：** 仅为清空 6 码 buffer 而增批 · 不改变 ST 组成 · 不提升 lint 质量。

---

## 9. 未来 draft 重生成验收（ST 专项 · 离线）

若 Controller 冻结 S1 并授权 **新** candidate CSV 任务（非本包）：

```
PASS  ST-X1 .. ST-X6
PASS  ST 名称命中 = 0（S1/S3 primary）
PASS  L-A1..L-B4, L-P1..L-P3, L-D1..L-D5（L-D4 目标 PASS）
PASS  S2_DRAFT ∩ AB_182 = ∅
```

| 产物 | 条件 |
|------|------|
| ST 扫描附表 CSV | 每码 `st_name_hit` · `st_policy` · `included` |
| lint summary | 标注 ST 策略版本（S1/S2/S3/S4） |

---

## 10. 非目标（显式）

| 非目标 | 说明 |
|--------|------|
| live / dry-run / runner | **NOT APPROVED** |
| CNINFO 调用 | **0** |
| mutate 既有 +100/+50 draft CSV | 本包仅策略 · 重选须新任务 |
| mutate 182 台账 / remainder / 既有 report | 写保护 |
| cohort freeze / gate flip | 不宣称 human freeze · 不升 PASS/verified/production_ready |
| +6 buffer 清单 churn | 已由本 ST 策略替代 |
| 扩池 O4 | 不预设 |
| ST 实时状态 API 校验 | 无 CNINFO |

---

## 11. Governance

| 字段 | 值 |
|------|-----|
| Task | A-GEN-20260714-08 |
| live | **NOT APPROVED** |
| CNINFO（本包） | **0** |
| current gate | **HOLD preserved**（post-integration） |
| slice2 planning | **READY_FOR_APPROVAL**（ST strategy only） |
| 推荐 ST 策略 | **S1 ST-EXCLUDE**（默认 lint 路径） |
| O3 / 182 | **PENDING_CONTROLLER** |
| verified / production_ready | **NOT claimed** |

---

## 12. 证据链

- [ST selection checklist CSV](cninfo_a_class_slice2_st_selection_checklist_20260714.csv)
- [remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv)
- [+100 candidate draft](cninfo_a_class_erad_next_scale_slice2_candidate_universe_draft_20260714.csv)
- [+50 complement draft](cninfo_a_class_erad_next_scale_slice2_plus50_candidate_draft_20260714.csv)
- [overlap lint spec](cninfo_a_class_slice2_overlap_lint_spec_20260714.md)
- [A∩B 182 ledger](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv)

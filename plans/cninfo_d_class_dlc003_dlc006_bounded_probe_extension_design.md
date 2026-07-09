# CNINFO D 类 DLC003 / DLC006 Bounded Probe Extension Design

_生成时间：2026-07-09_

> **性质：** Option B 离线设计 only；**无 CNINFO** · **无 live** · **无 rerun** · **NOT APPROVED**

**关联边界：** commit `7a62539` · `d_class_phase1_boundary_gate = PASS_WITH_CAVEAT` · `d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION`

**关联输入：** [v1 tiny live report](../outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_report.csv) · [calibration review](cninfo_d_class_dlc003_dlc006_calibration_review.md) · [probe matrix](../outputs/validation/cninfo_d_class_dlc003_dlc006_bounded_probe_matrix.csv)

---

## 1. Objective

在 D-class Phase 1 边界收口后，为 **DLC003**（restricted_shares_unlock）与 **DLC006**（shareholder_change）设计 **有界 probe 扩展**（Option B），用于未来 v2 tiny live 回合在 **不修改 v1 报告**、**不发明 replacement 公司代码** 的前提下，验证 expectation mismatch 是否可由 **probe-window 扩展** 解决。

**本回合仅设计，不执行。**

---

## 2. Why Bounded Probing Is Needed

| 事实 | 含义 |
|------|------|
| v1 tiny live **5/7 acceptable** | pipeline · schema · quality policy 整体可用 |
| DLC003 · DLC006 **expectation mismatch** | 预期 `captured_normal`，观测 `empty_but_valid` |
| v1 probe 窗口有限 | DLC003：8 个半周年 `tdate`；DLC006：5 个 mode/date 组合 |
| 组件尚无 captured_normal tiny 样本 | restricted_shares_unlock · shareholder_change 均缺 live captured 证据 |
| 校准推荐 Option B 或 C | 本设计覆盖 **Option B**；Option C（人工 replacement）并行保留 |

**有界扩展的目标：** 在 **请求预算硬上限** 内，系统性扩大日期/模式覆盖，判断原 universe 公司（300009 · 000550）是否在更广窗口内存在公司级行；若仍为空，为人工决策（维持 mismatch / 转 Option C / 评估 Option A）提供 **充分探测证据**。

---

## 3. Why DLC003 / DLC006 Are Not Schema Failures

| 维度 | DLC003 | DLC006 |
|------|--------|--------|
| HTTP | 200 | 200 |
| JSON | 可解析 · `data.records` 路径有效 | 可解析 · inc/desc 双 mode 有效 |
| retrieval_status | `empty_but_valid`（合法） | `empty_but_valid`（合法） |
| quality_status | `pass` | `pass` |
| 全市场证据 | 各 `tdate` 全市场有解禁行 | `type=desc` 全市场 ~28 行 |
| registry | `liftBan/detail` 一致 | `shareholeder/detail` 一致 |
| freeze v1 contract | **无需修订** | **无需修订** |

**结论：** 差异属于 **expectation mismatch / probe-window limitation**，不是 schema · registry · mapper 缺陷。

---

## 4. Current Probe Limitation

### 4.1 DLC003 — restricted_shares_unlock（300009 安科生物）

| 项 | v1 覆盖 |
|----|---------|
| endpoint | `liftBan/detail` |
| 参数维度 | `tdate` only |
| 探测数 | **8** |
| tdate 集合 | 2026-06-08 · 2026-07-03 · 2025-12-31 · 2025-06-30 · 2024-12-31 · 2024-06-28 · 2023-12-29 · 2023-06-30 |
| 公司级结果 | **全部 0 行** |
| 缺口 | 无月度密度 · 无连续 12m/24m 系统性窗口 · 无与 v1 集合并集的 dedup 上限策略 |

### 4.2 DLC006 — shareholder_change（000550 江铃汽车）

| 项 | v1 覆盖 |
|----|---------|
| endpoint | `shareholeder/detail` |
| 参数维度 | `type`（inc/desc）× `tdate` |
| 探测数 | **5** |
| 组合 | `desc`；`inc`×3 tdate；`desc`+tdate |
| 公司级结果 | **全部 0 行** |
| 缺口 | inc 仅 3 个 tdate · desc 仅 1 个带 tdate · 无 12m/24m 季度系统性覆盖 · 无 bounded union cap |

---

## 5. Proposed Bounded Extension

### 5.1 Design Principles

1. **仅 DLC003 / DLC006** — 其余 case（DLC001/002/004/005/007）保持 v1 baseline，不重探或只读对照。
2. **系统性日历窗口** — 使用月尾/季尾日期序列；**不猜测**具体解禁或增减持事件日。
3. **硬请求上限** — DLC003 cap **24**；DLC006 cap **20**（含 v1 baseline replay）。
4. **dedup 优先** — 扩展探测与 v1 参数去重后计入预算。
5. **早停（early stop）** — 任一探测命中公司级 `>=1` 行即停止该 case 后续请求（计入 success）。
6. **v2 输出隔离** — 全部写入 `outputs/validation/cninfo_d_class_tiny_live_validation_v2/`。

### 5.2 DLC003 — Bounded Date-Window Probing

| 扩展维度 | 范围 | 新增请求上限 |
|----------|------|--------------|
| `v1_baseline_replay` | 复现 v1 八日期（对照） | 8（与 v1 一致，dedup 后可能更少） |
| `recent_12m_monthly` | 过去 12 个自然月月末 `tdate` | 12 |
| `recent_24m_quarterly` | 过去 24 个月季末 `tdate`（3/6/9/12 月最后交易日近似为季末日历日） | 8 |
| `reporting_window_quarterly` | 与 `recent_24m_quarterly` 同集（审计披露季窗） | 0（与上 dedup） |
| **`bounded_union_cap`** | v1 ∪ 12m monthly ∪ 24m quarterly，dedup 后 **≤24** | **24（硬顶）** |

**不发明**已知成功解禁日；若 24 次 capped 探测仍全空 → 记录 `still_empty_but_valid`，供人工转 Option C。

### 5.3 DLC006 — Bounded Mode/Date Probing

| 扩展维度 | 范围 | 新增请求上限 |
|----------|------|--------------|
| `v1_baseline_replay` | 复现 v1 五组合 | 5 |
| `recent_12m_quarterly_inc` | `type=inc` × 过去 4 个季末 tdate | 4 |
| `recent_12m_quarterly_desc` | `type=desc` × 过去 4 个季末 tdate | 4 |
| `recent_24m_quarterly_both` | inc+desc × 过去 8 个季末 tdate（dedup） | 16 |
| `expanded_mode_date_union` | v1 ∪ 12m ∪ 24m 组合 dedup | **20（硬顶）** |

**不发明**已知增减持事件日；desc 无 tdate 的 v1 探测保留为 baseline 之一。

---

## 6. Safety Limits

| 限制 | 值 |
|------|-----|
| 作用 case | **仅 DLC003 · DLC006** |
| DLC003 max requests | **24** |
| DLC006 max requests | **20** |
| v2 总 CNINFO 上限（DLC003+DLC006） | **44** |
| baseline cases 重探 | **禁止**（DLC001/002/004/005/007 只读 v1 对照） |
| v1 报告/快照覆盖 | **禁止** |
| universe v2 placeholder 修改 | **禁止** |
| DB / MinIO / RAG | **0** |
| harvest | **禁止** |
| verified / production_ready | **禁止** |

---

## 7. Request Budget

| case | v1 已用 | v2 设计 cap | 说明 |
|------|---------|-------------|------|
| DLC003 | 8 | **24** | dedup 后仍受硬顶约束 |
| DLC006 | 5 | **20** | mode×date union dedup |
| DLC001–007 其余 | — | **0** | v2 bounded 回合不新增 CNINFO |
| **v2 回合合计** | — | **≤44** | 仅 mismatch cases |

---

## 8. Timeout / Retry Limits

| 参数 | 建议值 | 说明 |
|------|--------|------|
| per-request timeout | **15s** | 与 v1 runner 一致 |
| connect timeout | **10s** | 与 v1 runner 一致 |
| retry on http_5xx | **0** | tiny live 不重试，避免预算膨胀 |
| retry on timeout | **0** | 记录失败继续下一参数 |
| retry on invalid_json | **0** | 记录 `invalid_json` 停止该 case 后续探测 |
| inter-request delay | **0.5s** | 礼貌间隔，可配置 |

---

## 9. Output Isolation

| 路径 | 用途 |
|------|------|
| `outputs/validation/cninfo_d_class_tiny_live_validation_v2/` | v2 根目录（**NOT APPROVED**） |
| `.../reports/d_class_tiny_live_v2_report.csv` | v2 执行报告 |
| `.../reports/d_class_tiny_live_v2_comparison_report.csv` | v1 vs v2 对照 |
| `.../reports/d_class_tiny_live_v2_summary.md` | v2 摘要 |
| `.../live_snapshots/DLC003_*.json` | DLC003 快照（仅 v2） |
| `.../live_snapshots/DLC006_*.json` | DLC006 快照（仅 v2） |

**v1 根目录** `outputs/validation/cninfo_d_class_tiny_live_validation/` **只读**，runner 写保护。

---

## 10. Approval Requirement

| 门槛 | 状态 |
|------|------|
| Phase 1 boundary reviewed | required |
| DLC003/DLC006 calibration reviewed | required |
| bounded probe scope approved | **pending** |
| request cap approved | **pending** |
| explicit user flag | `--approve-d-class-tiny-live-v2-bounded-probe` |
| universe | `cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv`（placeholder 行 **不执行**） |
| overall status | **NOT APPROVED** |

---

## 11. Risks

| 风险 | 等级 | 缓解 |
|------|------|------|
| 扩窗后仍全空 | medium | 不自动改 expectation；转 Option C 人工选股 |
| CNINFO 负载 | low | 硬 cap 44 · inter-request delay |
| 误判为 schema 问题 | low | 保持 empty_but_valid 语义；对照全市场行 |
| v1 产物污染 | high | 输出根隔离 + runner 写保护 |
| 无界探测漂移 | medium | 仅日历窗口 · 禁止事件日猜测 |
| 过早 Option A | medium | 即使 v2 仍空，不自动 reclassify |
| placeholder 误执行 | high | v2 universe 中 `*_CANDIDATE_REQUIRED` 行 skip |
| verified / production 误标 | high | gate 仅 `READY_FOR_APPROVAL` |

---

## 12. Gate（本设计回合）

```text
d_class_tiny_live_v2_bounded_probe_design_gate = READY_FOR_APPROVAL
```

**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**

**CNINFO calls（本回合）：0**

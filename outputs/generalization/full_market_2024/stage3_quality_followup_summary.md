# full_market_2024 第 3a 阶段质量跟进汇总

_生成日期：2026-06-25 | Issue #28 — Stage 3a 关单文档_

> 术语见文首；正文使用中文表述。代码标识符（如 `usable`、`run_name`）保持英文。

---

## 1. 范围与完成声明

本文档汇总 **full_market_2024 2024 年报基线** 的 **Stage 3a 质量跟进**（#24–#28）。

**范围内（已完成）：**

- #24 北交所严格质量审计规则修正（TOP_KW）
- #25 `rnd_investment` 抽取修复 + 小范围定向刷新
- #26 收入跨页抽取修复 + 小范围定向刷新
- #27 金融专用严格质量审计框架（盘点 + 自动化严格质量审计 + 校准表）
- #28 本汇总与文档同步

**范围外（明确未做）：**

- 全量 CNINFO 重下或全字段重抽
- 全量人工验证 62,890 行 SQLite 记录
- 金融抽取/标签签核（校准表人工打分待完成）
- 多年份扩展（2025 / 2023 / 2022）
- 将金融指标混入非金融 9.43/11 核心指标

**方法口径：** 自动化严格质量审计 + **对已缓存 PDF 的小范围定向刷新** + 抽样/人工校准**支持** — **非**全量人工复核。

**关单决定：** **full_market_2024 Stage 3a 质量跟进通过。** 残留问题已文档化并暂缓；**不**阻塞基线关单。**完整 Stage 3**（ROADMAP）仍对残留项、金融人工打分、多年份规划（Stage 3b）开放。

---

## 2. 最终非金融质量快照

最新 SQLite `run_name`：**`full_market_2024_revenue_refresh`**

| 指标 | 数值 |
|---|---:|
| 评估全集总数 | 6,124 |
| ok | 5,707 |
| no_announcement | 417 |
| error | **0** |
| 非金融 ok 公司 | **5,621** |
| 审计人口 | 5,621 × 11 = **61,831 字段单元格** |
| **自动合理性分数** | **10.67 / 11** |
| **严格质量审计下 usable** | **9.43 / 11** |
| **严格质量审计宽松口径** | **10.80 / 11** |
| 全字段 strict **wrong** | **566**（#26 前 876） |
| `rnd_investment` **found** | **5,297 / 5,621 (94.2%)** |
| rnd 字段级 strict usable | **5,086 / 5,621** |
| `revenue_by_region` strict **wrong** | **38**（#26 前 258） |
| `revenue_by_segment` strict **wrong** | **19**（#26 前 109） |
| SQLite evaluation_result 行 | **62,890** |

**各板块 strict usable（非金融，收入刷新后）：**

| 板块 | strict usable / 11 |
|---|---:|
| bse | **8.82** |
| sse_main | **9.35** |
| szse_main | **9.43** |
| star | **9.61** |
| chinext | **9.67** |

**校准支持（非金融）：** 55 家公司 × 7 个定向字段（样本 CSV）；15 家公司 PDF 深度阅读（105 个字段单元格）。人工 vs 自动一致率：45/105（43%）。**非**全量人工验证。

详情：[strict_audit_summary.md](strict_audit_summary.md)

---

## 3. 金融严格质量审计快照（单独核心指标）

**不得**混入非金融 9.43/11。

| 指标 | 数值 |
|---|---:|
| YAML `financial: true` | **87** 已标记 / **86 ok**（000562 no_announcement） |
| 子类型 | bank **43** / broker **37** / insurer **2** / other **4** |
| 自动化审计字段单元格 | **1,059** |
| **bank strict usable** | **9.00 / 13** |
| **broker strict usable** | **7.66 / 12** |
| **insurer strict usable** | **9.25 / 12**（n=2 — 仅作参考） |
| **other_financial strict usable** | **5.75 / 8** |
| 校准表 | **30 家公司 × 325 个字段单元格** — **`manual_grade` 待填** |
| 人口标签 | usable 557 / partial 310 / wrong 81 / not_found_missed 75 / not_found_unverified 36 |

**#27 状态：** 严格质量审计**框架已完成** — **非**金融抽取签核。校准表已生成；人工打分未完成。

详情：[financial_audit_summary.md](financial_audit_summary.md)

---

## 4. 严格质量审计指标轨迹（仅 full_market_2024 内）

同一评估全集内、初始混合审计后的演化：

| 步骤 | 触发 | 非金融 strict usable | 说明 |
|---|---|---:|---|
| 初始审计 | 全市场合并后 | **9.01 / 11** | 自动化对抗式复核 + 15 家 PDF 样本 |
| #24 | 北交所 TOP_KW 审计规则 | **9.06 / 11** | 仅审计规则；北交所 **7.14 → 7.71** |
| #25 | rnd 小范围定向刷新 | **9.38 / 11** | 抽取 + 已缓存 PDF 刷新；北交所 **7.71 → 8.71** |
| #26 | revenue 小范围定向刷新 | **9.43 / 11** | 抽取 + 已缓存 PDF 刷新；北交所 **8.71 → 8.82** |

```
9.01  →  9.06  →  9.38  →  9.43
 ^         ^         ^         ^
initial   #24       #25       #26
```

> 此轨迹描述**同一 full_market_2024 评估全集上**小范围审计/刷新演化。**不得**将 9.43/11 与 eval1000 strict **10.16/11** 比较为「改善」— 自动合理性规则、审计范围、评估全集规模均不同。

---

## 5. #24–#27 变更记录

### #24 — 北交所严格质量审计规则修正

- **变更：** 在 `lab/strict_audit_full_market.py` 中扩展北交所客户/供应商表列头 TOP_KW（`年度销售占比`、`年度采购占比` 等）。
- **类型：** 仅审计规则修正 — **无**抽取变更。
- **效果：** 北交所 strict **7.14 → 7.71**；整体 strict **9.01 → 9.06**。
- **产物：** [bse_quality_followup.md](bse_quality_followup.md)

### #25 — rnd_investment 小范围定向刷新

- **变更：** 北交所研发支出锚点 + 汇总合计优先；extractors 中 P2.1 候选回退；对已缓存 PDF 的小范围 rnd 刷新。
- **类型：** 抽取修复 + 小范围定向刷新。
- **效果：** rnd found **67.9% → 94.2%**；北交所 rnd **22.8% → 99.2%**；strict **9.06 → 9.38**；proxy **10.35 → 10.61/11**。
- **产物：** [rnd_refresh_summary.md](rnd_refresh_summary.md) | SQLite `run_name=full_market_2024_rnd_refresh`

### #26 — 收入跨页小范围定向刷新

- **变更：** Tier 3 续页拼接 + Tier 2 堆叠修剪；对 `revenue_by_region`、`revenue_by_segment` 的小范围 revenue 刷新。
- **类型：** 抽取修复 + 小范围定向刷新。
- **效果：** wrong→usable **297**；usable 回归 **0**；region wrong **258 → 38**；segment wrong **109 → 19**；strict **9.38 → 9.43**；全字段 wrong **876 → 566**。
- **产物：** [revenue_refresh_summary.md](revenue_refresh_summary.md) | SQLite `run_name=full_market_2024_revenue_refresh`

### #27 — 金融严格质量审计框架

- **变更：** 人口盘点；自动化金融 strict audit；30 家公司校准表（`seed=20260627`）。
- **类型：** 审计框架 + 文档 — **非**抽取修复。
- **效果：** 1,059 个字段单元格单独审计；校准表 **325 个字段单元格**，`manual_grade` 空白。
- **产物：** [financial_audit_summary.md](financial_audit_summary.md)

---

## 6. 修复分类

| Issue | 审计规则修正 | 抽取修复 | 小范围定向刷新 | 审计框架 / 文档 |
|---|---:|---:|---:|---:|
| #24 | **是** | — | — | — |
| #25 | — | **是** | **是**（仅 rnd） | — |
| #26 | — | **是** | **是**（revenue 字段） | — |
| #27 | 部分（金融 strict 规则） | — | — | **是** |
| #28 | — | — | — | **是**（本汇总） |

**全局约束：** 所有字段刷新均为**对已缓存 PDF 的小范围定向刷新** — 非全量 CNINFO 重跑。

---

## 7. 校准与验证口径

| 层级 | 非金融 | 金融 |
|---|---|---|
| 人口自动化 strict | 5,621 × 11 = 61,831 字段单元格 | 86 ok × 子 schema = 1,059 字段单元格 |
| 抽样支持 | 55 家 × 7 字段 CSV；15 家 PDF 深度阅读（105 字段单元格） | 30 家 × 325 字段单元格校准表 |
| 人工打分 | 仅深度阅读标签（非完整校准表） | **`manual_grade` 空白 — 待完成** |
| 允许声称 | 自动化 strict 估计 + 校准**支持** | 单独自动化 strict；打分**待完成** |
| **不得**声称 | 62,890 行全量人工验证 | 金融质量已签核 |

混合方法见 [strict_audit_summary.md](strict_audit_summary.md) §1。金融校准表打分（`CORRECT | PARTIAL | WRONG | MISSED | ABSENT-OK`）将在人工复核后细化 broker `not_found_missed` 解读。

---

## 8. 残留问题

| ID | 问题 | 范围 | 严重度 | 暂缓至 |
|---|---|---|---|---|
| R1 | revenue strict-wrong 残留 | region **38** + segment **19** ≈ **57 字段单元格** | 中 | 后续：小范围抽取/审计 |
| R2 | rnd 残留回归 | 约 **8 家公司**（sse_main 费用化研发投入；如 600011 + 301221 partial） | 低 | 小范围修复 |
| R3 | 北交所板块差距 | **8.82/11** vs chinext 9.67 | 中 | 观察 / 可选板块跟进 |
| R4 | risk_factors strict-wrong | **221 字段单元格**（误报最多字段） | 中 | 审计或抽取分流 |
| R5 | major_subsidiaries（非金融） | **0 usable / 5549 partial** — 结构性 | 低 | 审计行为；勿过度解读 |
| R6 | 金融人工打分 | **325 字段单元格**，`manual_grade` 空白 | **高** | 人工校准打分 |
| R7 | broker `not_found_missed` | **约 58/75** 召回提示 — **非已确认真值** | 中 | 人工打分后细化 |
| R8 | 金融子类型注意事项 | **000402 / 600816 / 600318** 存储 schema | 中 | 标签复核 |
| R9 | 金融漏标 | YAML 完整性未扫描 | 中 | 漏标扫描 |
| R10 | 金融数值/表格噪声 | broker proxy−strict 差距 **7.5%** | 中 | 金融合理性规则 |
| R11 | 保险样本过小 | **n=2** 保险公司 | 信息 | 扩展标记后再信均值 |
| R12 | major_subsidiaries（金融） | **0/86 usable** — 工业 in_region 门控 | 低 | 结构性 partial；非抽取回归 |

收入抽取**尚未完全修复**。金融审计框架已完成；**抽取尚未签核**。

---

## 9. 后续待办（Stage 3a 之后）

| 优先级 | 主题 | 说明 |
|---|---|---|
| 1 | **金融人工校准打分** | 填写 `financial_audit_sample.csv` → `--score` |
| 2 | **broker `not_found_missed` 细化** | 打分后收紧审计规则 |
| 4 | **rnd 残留回归** | ~~#32c 小范围 P0 写回已验证~~ — 72/104 P0 池仍 partial；全量研发推广暂缓 |
| 3 | **剩余 revenue strict-wrong** | 约 57 字段单元格；仅小范围定向刷新（#32b Tier 4） |
| 5 | **金融漏标扫描** | YAML `financial: true` 完整性 |
| 6 | **金融抽取/标签修复** | 数值合理性、子类型标签（000402 等） |
| 7 | **2025 / 2023 / 2022 扩展决策** | 范围、批次策略、run_name — **默认不全量 CNINFO 重跑** |

可选低优先级：`strict_audit_result` DB loader；BrowserUser 试点（ROADMAP Phase 4）。

---

## 10. Stage 3a 关单决定

**结论：full_market_2024 Stage 3a 质量跟进通过。**

**不得声称：**

- 完整 Stage 3 已完成
- 全部抽取问题已修复
- 全量人工验证
- 金融指标合并入非金融核心指标

**ROADMAP：** Stage **3a** 已完成（#24–#28）；Stage **3b** 进行中。

---

## 11. 产物索引

| 产物 | Issue | 说明 |
|---|---|---|
| [bse_quality_followup.md](bse_quality_followup.md) | #24 | 北交所 TOP_KW 审计规则前后对比 |
| [rnd_refresh_summary.md](rnd_refresh_summary.md) | #25 | rnd 小范围定向刷新指标 |
| [revenue_refresh_summary.md](revenue_refresh_summary.md) | #26 | revenue 小范围定向刷新指标 |
| [strict_audit_summary.md](strict_audit_summary.md) | 基线 + 刷新后 | 非金融混合 strict audit |
| [strict_audit_sample.csv](strict_audit_sample.csv) | 基线 | 55 家 × 7 字段样本 |
| [financial_audit_summary.md](financial_audit_summary.md) | #27 | 金融自动化 strict |
| [financial_audit_population.csv](financial_audit_population.csv) | #27 | 1,059 审计行 |
| [financial_audit_sample.csv](financial_audit_sample.csv) | #27 | 30 家校准表（打分待完成） |
| [financial_population_inventory.csv](financial_population_inventory.csv) | #27 | 87 家已标记盘点 |
| [full_market_2024_summary.md](full_market_2024_summary.md) | Stage 2 | 全量抽取运行报告 |
| **本文件** | #28 | Stage 3a 汇总与关单 |

交叉链接：[CURRENT_STATUS.md](../../CURRENT_STATUS.md) | [ROADMAP.md](../../ROADMAP.md) | [docs/evaluation_method.md](../../docs/evaluation_method.md)

Stage 3b 金融跟进延续于 `#30`；见 [financial_audit_fix_30_summary.md](financial_audit_fix_30_summary.md)。

**#32c 更新（2026-06-26）：** 小范围 P0 研发写回验证已完成 — 104 个目标公司，32 份 profile 更新，应用后验证通过；全局非金融核心指标 **9.43/11 不变**。见 [rnd_residual_fix_32c_post_apply_verify.md](rnd_residual_fix_32c_post_apply_verify.md)。

**#32 关单（2026-06-26）：** #32 当前范围完成（盘点 + #32c + #32b 只读诊断）；收入生产修复暂缓；非金融核心指标 **9.43/11 不变**。见 [revenue_rnd_fix_32_final_summary.md](revenue_rnd_fix_32_final_summary.md)。

**#33 决策（2026-06-26）：** 多年份扩展策略已文档化 — 2025 优先、分阶段推广；parent #23 **可以关单**。见 [multiyear_expansion_decision_33.md](multiyear_expansion_decision_33.md)。

---

## 12. 不得声称清单

| 声称 | 是否允许 |
|---|---|
| Stage 3a 质量跟进通过 | **是** |
| 完整 Stage 3 / ROADMAP Phase 3 全部完成 | **否** |
| 非金融 strict **9.43/11** 作为最新核心指标 | **是** — 与金融分开 |
| 将金融指标混入 9.43/11 | **否** |
| 9.43/11 相对 eval1000 **10.16/11** 为「改善」 | **否** |
| 62,890 行全量人工验证 | **否** |
| 全部抽取 / 全部字段已修复 | **否** |
| 金融抽取已签核 | **否** |
| 自动化 strict + 小范围定向刷新 + 校准支持 | **是** |

---

## 13. 可提交与勿动指引

### 可提交（明确路径）

**Stage 3a 汇总 + 文档同步（#28）：**

```
outputs/generalization/full_market_2024/stage3_quality_followup_summary.md
CURRENT_STATUS.md
CHANGELOG.md
ROADMAP.md
docs/evaluation_method.md
README.md
```

**此前 Stage 3 产物（若尚未提交 — 使用明确 `git add`）：**

```
outputs/generalization/full_market_2024/bse_quality_followup.md
outputs/generalization/full_market_2024/rnd_refresh_summary.md
outputs/generalization/full_market_2024/revenue_refresh_summary.md
outputs/generalization/full_market_2024/strict_audit_summary.md
outputs/generalization/full_market_2024/strict_audit_sample.csv
outputs/generalization/full_market_2024/financial_audit_summary.md
outputs/generalization/full_market_2024/financial_audit_population.csv
outputs/generalization/full_market_2024/financial_audit_sample.csv
outputs/generalization/full_market_2024/financial_population_inventory.csv
lab/strict_audit_financial_full_market.py
lab/financial_calibration_sample.py
docs/financial_company_schema.md
```

使用 `git add <paths>` — 勿用 `git add -A`。

### 勿提交 / 文档任务中勿修改

| 类别 | 路径 |
|---|---|
| 运行时 JSON | `eval_results.json`, `company_profile.json`, batch 子目录 `[0-9]*/` |
| PDF / 缓存 | `*.pdf`, `.cache/` |
| SQLite | `outputs/db/*.db` |
| 刷新增量 | `rnd_refresh_changes.csv`, `revenue_refresh_changes.csv`, `revenue_refresh_changes_targeted.csv`, overnight reports |
| 日志 / 备份 | `*.log`, backups |
| 生成批次 YAML | `lab/batch_*_2024.yaml` |

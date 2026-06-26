# 当前状态

_最后更新：2026-06-26_

> **主进度页，建议老师 / 评审从这里开始。** 技术细节见 [docs/](docs/)，变更见 [CHANGELOG.md](CHANGELOG.md)。

---

## 老师阅读版

本项目已完成 **2024 年 A 股年报结构化数据底座的第一阶段质量闭环**。系统可以批量抽取字段、保留来源证据、运行严格质量审计，并对问题字段做小范围修复。

它**还不是**完整的智能问答产品，**也不是**全量人工验证后的最终数据库。父任务 #23（#24–#33）**可以关单**；下一步是 2025 年试点（待人工确认）。

---

## 当前阶段（一句话）

**2024 全市场基线已完成，第 3a 阶段质量闭环已通过；#30 / #32 / #33 当前范围已关闭，等待启动 2025 试点。**

---

## 核心结论

| 项目 | 状态 |
|---|---|
| 2024 全市场抽取 | 6124 家全集，5707 家成功，SQLite 入库 62,890 行 |
| 第 3a 阶段质量闭环 | **通过**（#24–#28） |
| 父任务 #23 | **可以关单** |
| 产品形态 | 数据底座 + 质量审计，非完整 RAG / 知识页产品 |
| 下一步 | 2025 试点（待人工确认） |

---

## 当前关键数字

运行名称：`full_market_2024_revenue_refresh`（2026-06-24 收入刷新后）

### 非金融公司（工业类 11 字段）

| 指标 | 数值 | 说明 |
|---|---:|---|
| 严格审计下可用（核心指标） | **9.43 / 11** | 5621 家公司；11 为每家公司检查的目标字段数 |
| 自动合理性分数 | **10.67 / 11** | 比严格审计更宽松的结构估计 |
| `rnd_investment` 找到率 | **94.2%** | 5297 / 5621 |
| `revenue_by_region` 审计错误 | **38** | #26 前为 258 |
| `revenue_by_segment` 审计错误 | **19** | #26 前为 109 |

### 抽取规模

| 指标 | 数值 |
|---|---:|
| 公司全集 | 6124 |
| 成功抽取 | 5707 |
| 未找到公告 | 417 |
| 技术错误 | 0 |
| SQLite 字段记录 | 62,890 |

### 金融公司（单独核心指标，不得与非金融混报）

| 类型 | 严格审计下可用 |
|---|---:|
| 银行 | **9.00 / 13** |
| 券商 | **7.66 / 12** |
| 保险 | **9.25 / 12**（仅 2 家，仅供参考） |
| 其他金融 | **5.75 / 8** |

> **#32c 小范围写回未更新全局 9.43/11。** 仅 104 家 P0 池本地档案有变更；全局核心指标需有意安排全量严格质量审计重跑后才变更。

---

## 已完成工作（摘要）

| 类别 | 内容 |
|---|---|
| 2024 全市场抽取 | 6124 家全集，5 板块批次，合并入库 — [full_market_2024_summary.md](outputs/generalization/full_market_2024/full_market_2024_summary.md) |
| 研发字段小范围刷新 | `rnd_investment` 找到率 67.9%→94.2% — [rnd_refresh_summary.md](outputs/generalization/full_market_2024/rnd_refresh_summary.md) |
| 收入字段小范围刷新 | 297 个错误→可用 — [revenue_refresh_summary.md](outputs/generalization/full_market_2024/revenue_refresh_summary.md) |
| 严格质量审计 | 非金融 9.43/11 — [strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md) |
| 金融审计框架 | #27 + #30 跟进 — [financial_audit_fix_30_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md) |
| 第 3a 阶段汇总 | 通过 — [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) |
| #32 收入与研发残留 | 已关闭 — [revenue_rnd_fix_32_final_summary.md](outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md) |
| #33 多年份决策 | 已关闭 — [multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md) |

---

## 能达到什么标准

- 已完成 2024 年 A 股年报结构化数据底座的**第一阶段质量闭环**。
- 可批量抽取、记录证据（页码 / 证据句 / URL）、运行严格质量审计，并做小范围定向刷新或写回。
- 数据可支撑内部分析、字段查询、公司档案，以及检索增强问答原型的底层数据层。
- 非金融核心指标 9.43/11 与金融指标**分开报告**。

---

## 不能宣称什么

- **不是**全量人工验证。
- **不是**完整的 RAG 产品或大模型知识页产品。
- **不是**所有字段都已完全修复（收入仍有 57 个错误字段单元待后续试点；研发部分可用仍有残留）。
- **不能**将金融公司指标与非金融 9.43/11 混报。
- **不能**声称 #32c 小范围写回已更新全局 9.43/11。
- **不能**将 9.43/11 与 eval1000 基线 10.16/11 直接比较为「改善」（规则与样本规模不同）。
- **未做** CNINFO 全量重跑、SQLite 重新导入（除非后续任务明确执行）。

---

## 已知问题

1. **北交所**严格审计指标 8.82/11，仍低于其他板块；客户/供应商表格规则已修正。
2. **研发**：#32c 在 104 家 P0 池中写回 32 家，72 家仍部分可用；000333、301221 暂缓。
3. **收入**：分地区 38 + 分业务 19 个审计错误仍待 Tier4 试点；生产写回暂缓。
4. **金融**：#30 批次已完成，全量推广暂缓；000402 / 600816 / 600318 标签复核进入 #31。
5. **浏览器智能体**未启动，非当前优先级。

---

## 下一步

| 优先级 | 事项 |
|---|---|
| 1 | 2025 试点：100 家 → 北交所板块 → 全市场（待 #33 人工确认） |
| 2 | #31 金融漏标扫描与标签复核 |
| 3 | 收入 Tier4 与错表排序试点 |
| 4 | 研发部分可用残留人工复核 |
| 5 | 2023/2022 历史年份回填（2025 通过验证门槛后） |

> 非金融核心指标 **9.43/11** 保持不变，直至有意安排全量严格质量审计重跑。

---

## 术语表

| 术语 | 含义 |
|---|---|
| `full_market_2024` | 2024 年全 A 股年报抽取运行 |
| `run_name` | 运行名称，标识一次抽取/刷新批次 |
| 严格质量审计 | 对已存字段做更严规则复核 |
| 自动合理性分数 | 抽取时的结构合理性估计 |
| `usable` / `partial` / `wrong` | 审计标签：可用 / 部分可用 / 错误 |
| `not_found_missed` | PDF 中应有披露但抽取为未找到 |
| 小范围定向刷新 | 用已缓存 PDF 仅重抽部分字段 |
| 小范围写回 | 经验证修复写回少量公司档案 |
| 只读诊断 | 不写回，仅评估修复效果 |
| 核心指标 | 对外主质量数字 |
| 分组样本 | 按规则选出的公司集合 |
| 试点 | 小规模试跑后再扩全市场 |
| 历史年份回填 | 补跑 2023/2022 等历史年报 |
| CNINFO | 巨潮资讯网 |
| SQLite | 轻量数据库原型 |
| RAG | 检索增强生成；本项目仅提供底层数据 |
| LLM Wiki | 大模型知识页原型；尚未交付 |

指标详细解释见 [docs/evaluation_method.md](docs/evaluation_method.md)。

---

## 文档入口

| 文档 | 用途 |
|---|---|
| [ROADMAP.md](ROADMAP.md) | 分阶段路线图 |
| [CHANGELOG.md](CHANGELOG.md) | 变更记录 |
| [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) | 第 3a 阶段汇总 |
| [strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md) | 非金融审计详情 |
| [financial_audit_summary.md](outputs/generalization/full_market_2024/financial_audit_summary.md) | 金融审计详情 |

---

## 附录：指标明细与板块分布

<details>
<summary>点击展开：full_market_2024 完整指标表、板块分布、SQLite 批次、近期里程碑</summary>

### 板块严格审计下可用（非金融）

| 板块 | 指标 |
|---|---:|
| 北交所 bse | 8.82 |
| 沪市主板 sse_main | 9.35 |
| 深市主板 szse_main | 9.43 |
| 科创板 star | 9.61 |
| 创业板 chinext | 9.67 |

### 与受控评估对比（非金融自动合理性分数）

| 运行 | 样本 | 成功 | 分数 |
|---|---:|---:|---:|
| eval1000_v2 | 1020 | 947 | 10.33/11 |
| independent eval1000 | 1000 | 918 | 10.30/11 |
| full_market_2024 | 6124 | 5707 | 10.67/11 |

### SQLite 运行名称

| run_name | 字段记录行数 |
|---|---:|
| `full_market_2024` | 62,890 |
| `full_market_2024_rnd_refresh` | 62,890 |
| `full_market_2024_revenue_refresh` | 62,890 |

### 近期里程碑

- **2026-06-26**：#33 多年份决策完成；#23 可以关单
- **2026-06-26**：#32 关闭（收入与研发残留盘点、研发小范围写回、收入只读诊断）
- **2026-06-25**：#30 金融跟进完成；第 3a 阶段收尾
- **2026-06-24**：收入/研发小范围刷新；全市场抽取完成

</details>

---

## 附录：关键产物路径

```
outputs/generalization/full_market_2024/
  full_market_2024_summary.md          # 可提交
  strict_audit_summary.md              # 可提交
  stage3_quality_followup_summary.md   # 可提交
  revenue_rnd_fix_32_final_summary.md  # 可提交
  multiyear_expansion_decision_33.md   # 可提交
  eval_results.json                    # 不提交（gitignore）
  bse/ star/ .../                      # 不提交（含 PDF）

outputs/db/listed_companies_v1.db      # 不提交
```

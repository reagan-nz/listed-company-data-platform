# 路线图

_最后更新：2026-06-26（#32c R&D P0 scoped apply docs sync）_

## 第一阶段：年报数据获取与基础字段抽取

**目标**：从巨潮资讯网稳定获取 A 股年报 PDF，抽取 11 项基础字段，建立证据链。

| 事项 | 状态 |
|---|---|
| CNINFO 年报查询与 PDF 下载 | 已完成 |
| 11 字段确定性抽取器 | 已完成 |
| 4 公司泛化验证 + 通用修复 | 已完成 |
| 200 家分层评估（eval200） | 已完成 |
| 1000 家受控评估 + 严格审计（eval1000） | 已完成 |
| rnd / 表格规则收紧（Issue #1/#2） | 已完成 |
| 金融公司子 schema 实现（Issue #4） | 已完成 |
| eval1000_v2 同 cohort 全量重跑 | 已完成（2026-06-22） |
| independent eval1000 泛化验证 | 已完成（2026-06-23）|
| SQLite 原型（db_init / db_import） | 已完成 |

## 第二阶段：full_market_2024 全量提取（已完成）

**目标**：覆盖全部 A 股 2024 年报，建立可查询的基础数据库。

| 事项 | 状态 |
|---|---|
| `lab/make_full_market_yaml.py` | 已完成 |
| 5 board 批次顺序执行 | 已完成 |
| 失败公司重试（688267 中触媒） | 已完成 |
| merge + SQLite 导入 `run_name=full_market_2024` | 已完成 |
| 与 eval1000_v2 / independent 对比 proxy 率 | 已完成（10.35/11，一致） |
| 混合 strict 审计 | 已完成（9.01/11 自动化 adversarial） |

**最终结果**：6124 total / 5707 ok / 417 no_announcement / 0 error；非金融 proxy **10.35/11**；strict usable **9.01/11**；SQLite **62,890** 字段行。

> **完成含义**：管道执行 + 数据库导入 + 混合 strict 审计均已完成。**不等于** 62,890 行全量人工验证。详见 [strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md)。Post–Stage 3a latest non-fin strict **9.43/11** — 见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)。

## 第三阶段：质量 follow-up 与多年度扩展

### 3a — full_market_2024 质量 follow-up（**Done**, #24–#28）

**目标**：针对性提升 2024 基线字段质量；建立金融 audit 框架；形成 closure 文档。

| 事项 | 状态 |
|---|---|
| #24 BSE strict audit-rule（TOP_KW） | **Done** — BSE strict 7.14→7.71 |
| #25 rnd scoped refresh | **Done** — rnd found 94.2%；strict 9.06→9.38 |
| #26 revenue scoped refresh | **Done** — wrong→usable 297；strict 9.38→9.43 |
| #27 金融 audit 框架 | **Done** — 1,059 cells automated strict + 325-cell worksheet（grading 待 Stage 3b） |
| #28 Stage 3a 汇总 | **Done** — [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) |

**Stage 3a 结论**：**full_market_2024 Stage 3a quality follow-up PASS** — automated strict audit + targeted scoped refreshes (cached PDF) + sampled/manual calibration support。**非**全量人工验证；**非** extraction 全部修复。

### 3b — residuals、grading 与多年度（**In Progress**）

**目标**：在不声称金融 extraction fully signed off 的前提下，完成 `#30` 收尾；`#32c` R&D P0 scoped fix 已 verified；推进 `#32b` / `#32` 剩余 / `#33`。

| 事项 | 状态 |
|---|---|
| `#30` financial follow-up（`#30a–#30g`） | **Done / closing** — audit-only + extraction helper + subtype diagnosis；wider financial rollout deferred |
| `#31` financial under-tagging scan | 下一项 — 含 `000402` / `600816` / `600318` retagging review |
| `#32c` R&D P0 scoped fix | **Done / verified** — guarded helper + apply 104（32 updated, 0 errors）+ post-apply verify PASS；**scoped P0 only** |
| `#32b` revenue Tier 4 / wrong-table | 下一项 — revenue 剩余 strict-wrong（57 cells） |
| `#32` R&D remaining partial / unresolved | 进行中 — 72/104 P0 池仍 partial；000333/301221 deferred；**非** full rollout |
| `#33` multiyear expansion decision | 下一项 — 2025 / 2023 / 2022 scope / run naming |
| BSE 模板 residual gap | 部分 — strict 8.82/11（≥8.5 阈值已满足） |
| `strict_audit_result` loader 入库 | 可选 |
| Post-apply **full** strict audit rerun | **Deferred** — 仅在有 intentional schedule 时更新 headline |

**3b 完成标准（draft）**：`#30` docs closeout completed；`#32c` scoped P0 verified；`#31` / `#32b` / `#33` 有明确范围；金融 wider rollout 仍单独评估，不混入 non-fin `9.43/11` headline。

## 第四阶段：BrowserUser 爬虫智能体补充数据

> **时序说明**：BrowserUser 在 full_market_2024 基线稳定后启动，不是当前直接下一步。

**目标**：用 BrowserUser 获取 PDF 抽取无法覆盖的数据，扩充数据库宽度与深度。

- 投资者互动平台（e 互动 / 上证 e 互动）
- 公司官网 IR 页面（非 PDF 披露）
- 交易所公告（非年报类）
- 政府采购 / 招投标

**原则**：仅补充，不替代已稳定的 PDF 抽取；强反爬/付费/需登录源先记录为限制。

**完成标准**：至少 2 个新数据源试点成功，产出可入库的结构化记录。详见 [plans/v0.5_next_step_browser_agent_plan.md](plans/v0.5_next_step_browser_agent_plan.md)。

## 第五阶段：公司分析、变化追踪与产业链线索

**目标**：基于基础数据库，提供分析能力。

- 跨年度字段变化追踪（主营业务迁移、R&D 趋势、客户集中度变化）
- 行业聚合统计（板块 R&D 中位数、区域收入分布）
- 产业链线索挖掘（客户/供应商名称 → 关联公司）
- 简单查询 API 或导出接口
- 可视化 dashboard（可选）

**完成标准**：支持按行业/板块的聚合查询与单公司时间序列对比。

# 路线图

_最后更新：2026-06-26（#33 多年份扩展决策备忘录）_

## 第一阶段：年报数据获取与基础字段抽取

**目标**：从巨潮资讯网 CNINFO（中国上市公司信息披露平台）稳定获取 A 股年报 PDF，抽取 11 项基础字段，建立证据链。

| 事项 | 状态 |
|---|---|
| CNINFO 年报查询与 PDF 下载 | 已完成 |
| 11 字段确定性抽取器 | 已完成 |
| 4 公司泛化验证 + 通用修复 | 已完成 |
| 200 家分层评估（eval200） | 已完成 |
| 1000 家受控评估 + strict audit（严格质量审计）（eval1000） | 已完成 |
| rnd / 表格规则收紧（Issue #1/#2） | 已完成 |
| 金融公司子 schema（字段体系）实现（Issue #4） | 已完成 |
| eval1000_v2 同 cohort（分组样本）全量重跑 | 已完成（2026-06-22） |
| independent eval1000 泛化验证 | 已完成（2026-06-23）|
| SQLite（轻量数据库）原型（db_init / db_import） | 已完成 |

## 第二阶段：full_market_2024（2024 全市场运行）全量提取（已完成）

**目标**：覆盖全部 A 股 2024 年报，建立可查询的基础数据库。

| 事项 | 状态 |
|---|---|
| `lab/make_full_market_yaml.py` | 已完成 |
| 5 board（板块）批次顺序执行 | 已完成 |
| 失败公司重试（688267 中触媒） | 已完成 |
| merge（合并）+ SQLite 导入 `run_name`（运行名称）=`full_market_2024` | 已完成 |
| 与 eval1000_v2 / independent 对比 proxy（自动合理性分数）率 | 已完成（10.35/11，一致） |
| 混合 strict audit（严格质量审计） | 已完成（9.01/11 自动化 adversarial（对抗式复核）） |

**最终结果**：6124 total（总数）/ 5707 ok（成功）/ 417 no_announcement（未找到公告）/ 0 error（错误）；非金融 proxy plausible（自动合理性分数）**10.35/11**；strict usable（严格审计下可用）**9.01/11**；SQLite **62,890** 字段行。

> **完成含义**：管道执行 + 数据库导入 + 混合 strict audit（严格质量审计）均已完成。**不等于** 62,890 行 full manual validation（全量人工验证）。详见 [strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md)。Post–Stage 3a 最新 non-fin（非金融）strict usable（严格审计下可用）**9.43/11** — 见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)。

## 第三阶段：质量 follow-up（质量跟进）与多年度扩展

### 3a — full_market_2024（2024 全市场运行）质量 follow-up（质量跟进）（**已完成**, #24–#28）

**目标**：针对性提升 2024 基线字段质量；建立金融 audit（审计）框架；形成 closure（关单）文档。

| 事项 | 状态 |
|---|---|
| #24 BSE strict audit-rule（严格审计规则）（TOP_KW） | **已完成** — BSE strict usable（严格审计下可用）7.14→7.71 |
| #25 rnd scoped refresh（小范围定向刷新） | **已完成** — rnd found（找到率）94.2%；strict usable（严格审计下可用）9.06→9.38 |
| #26 revenue scoped refresh（小范围定向刷新） | **已完成** — wrong→usable（错误→可用）297；strict usable（严格审计下可用）9.38→9.43 |
| #27 金融 audit（审计）框架 | **已完成** — 1,059 cells（字段单元格）automated strict（自动化严格审计）+ 325-cell worksheet（校准表）（grading（人工打分）待 Stage 3b） |
| #28 Stage 3a 汇总 | **已完成** — [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) |

**Stage 3a 结论**：**full_market_2024 Stage 3a quality follow-up（质量跟进）PASS（通过）** — automated strict audit（自动化严格质量审计）+ targeted scoped refresh（小范围定向刷新）（cached PDF（已缓存 PDF））+ sampled/manual calibration（抽样/人工校准）**支持**。**非** full manual validation（全量人工验证）；**非** extraction（抽取）全部修复。

### 3b — residuals（残留问题）、grading（人工打分）与多年度（**#23 可以关单**）

**目标**：`#30` / `#32` / `#33` 当前范围已关闭；下一执行阶段 = **2025 pilot（试点）**（人工签核后）。

| 事项 | 状态 |
|---|---|
| `#30` financial follow-up（金融 follow-up（跟进））（`#30a–#30g`） | **已完成** — wider financial rollout（更大范围金融推广）**暂缓** |
| `#32` revenue + R&D residual（收入与研发残留） | **已完成 / 已关闭** — 见 [revenue_rnd_fix_32_final_summary.md](outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md) |
| `#33` multiyear expansion decision（多年份扩展决策） | **已完成 / 已关闭** — 见 [multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md) |
| **2025 pilot（试点）implementation（实施）** | **下一步** — 100-co → board → `full_market_2025`（2025 全市场运行）；待 §12 人工签核 |
| `#31` financial under-tagging scan（金融漏标扫描） | **待办** — 建议 pilot（试点）前或并行 |
| Revenue Tier4 + wrong-table pilot（试点） | **待办** — post-#32b harness（试跑框架） |
| R&D remaining partial / unresolved（研发部分可用/未解） | **待办** — 72/104 P0 + full-population partial（全人口部分可用） |
| Revenue partial full methodology（收入 partial 全量方法论） | **待办** — ~753 partial 未在 #32 全量枚举 |
| **2023/2022 backfill（历史年份回填）** | **待办** — after `full_market_2025`（2025 全市场运行）gates（验证关卡） |
| BSE 模板 residual gap（残留差距） | 部分 — strict usable（严格审计下可用）8.82/11（≥8.5 阈值已满足） |
| `strict_audit_result` loader 入库 | 可选 |
| Post-apply full strict audit rerun（2024）（应用后全量 strict audit（严格质量审计）重跑） | **暂缓** — 9.43/11 不变 |

**3b 完成标准（草案）**：`#23` 子 issue 全部 closed（已关闭）；2025 pilot（试点）有明确 `run_name`（运行名称）/ gate（验证关卡）方案 — **已满足**；执行待新 implementation issue（实施 issue）。

### 3c — 2025 多年份扩展执行（**下一阶段**）

**目标**：分阶段扩展至 2025 全市场，再 backfill（历史年份回填）2023/2022。

| 阶段 | `run_name`（运行名称） | 状态 |
|---|---|---|
| 100-co pilot（100 家试点） | `full_market_2025_pilot` | **计划中** |
| Board pilot（板块试点）(BSE) | `full_market_2025_pilot_bse` | **计划中** |
| Full 2025（2025 全市场） | `full_market_2025` | **计划中** |
| 2023 backfill（2023 回填） | `full_market_2023_backfill` | **待办** |
| 2022 backfill（2022 回填） | `full_market_2022_backfill` | **待办** |

详见 [multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md)。

## 第四阶段：BrowserUser（浏览器智能体）爬虫智能体补充数据

> **时序说明**：BrowserUser（浏览器智能体）在 `full_market_2024`（2024 全市场运行）基线稳定后启动，不是当前直接下一步。

**目标**：用 BrowserUser（浏览器智能体）获取 PDF 抽取无法覆盖的数据，扩充数据库宽度与深度。

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

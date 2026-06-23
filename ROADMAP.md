# 路线图

_最后更新：2026-06-23_

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
| independent eval1000 泛化验证（新 cohort） | 已完成（2026-06-23）|
| SQLite 原型（db_init / db_import） | 已完成 |

> **泛化结论**：非金融 proxy **10.30–10.33/11**；strict-usable **10.16/11**（eval1000 基线，v2/independent 尚未重跑）。管道可进入全量提取阶段。

## 第二阶段：full_market_2024 全量提取（下一步）

**目标**：覆盖全部 ~5300 家 A 股 2024 年报，建立可查询的基础数据库。

| 事项 | 状态 |
|---|---|
| `lab/make_full_market_yaml.py`（无抽样全市场 YAML 生成） | 待做 |
| 按 board 拆 5 批次顺序执行（sse_main / star / szse_main / chinext / bse） | 待做 |
| 失败公司重试（VPN off；网络错误） | 待做 |
| 合并 5 批次 → SQLite 导入 `run_name=full_market_2024` | 待做 |
| 与 eval1000_v2 / independent 对比 proxy 率 | 待做 |
| full_market_2024 strict 审计 | 待做（全量 proxy 稳定后） |

> **前置条件**：磁盘 ≥80 GiB 可用；VPN 关闭；可 overnight 运行 20–26 h。详见 [plans/v0.6_full_market_2024_plan.md](plans/v0.6_full_market_2024_plan.md)。

**完成标准**：≥ 85% A 股 status=ok；non-fin proxy 在 10.2–10.4/11 范围内；SQLite ~55000–58000 extracted_field 行。

## 第三阶段：多年度扩展与字段质量提升

**目标**：扩展至多年度，提升字段准确率与行业适配。

- 2023 / 2022 年报增量提取（依赖全量 2024 基线）
- full_market_2024 strict 审计（若未在第二阶段完成）
- rnd 与表格字段持续优化
- 北交所 / 科创板特殊模板适配
- 金融公司专用字段 plausible 规则（Phase 3 of financial schema）
- `sample_universe` 增加「资本」等关键词补丁

**完成标准**：全 A 股 strict-usable ≥ 95%；支持多年度时间序列查询。

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

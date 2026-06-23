# 更新日志

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [Unreleased]

### 新增
- **数据库存储方案 v1**（Issue #7）：`docs/database_schema.md` 定义四表（company_basic / report_source / extracted_field / evaluation_result）；推荐 SQLite 原型，后续迁 PostgreSQL
- **SQLite 建表与导入原型**（Issue #8）：`lab/db_init.py`（建表）、`lab/db_import.py`（从 eval1000 导入小样本）；`.db` 写入 `outputs/db/` 且已 gitignore
- **金融公司 schema 设计 v1**（Issue #3）：`docs/financial_company_schema.md` 定义银行/券商/保险三类子 schema，明确各类适用字段与不适用字段，并给出评估分开报告建议
- **金融公司子 schema 实现**（Issue #4）：`BANK/BROKER/INSURER/OTHER_FINANCIAL_FIELD_SPECS`、`detect_profile`/`resolve_profile`/`get_field_specs`；eval 对 `financial: true` 启用子 schema

### 变更
- **Independent eval1000 泛化验证**：新 cohort 1000 家（seed 20260623，重叠 159/15.9%）；**918 ok / 82 no_announcement / 0 error**（18 ChunkedEncodingError 经 VPN-off 重试恢复）；非金融 proxy **10.30/11**（vs v2 10.33，Δ −0.04 PASS）；SQLite 10112 行 — 见 `outputs/generalization/eval1000_independent_20260623/independent_comparison.md`
- **eval1000_v2 同 cohort 全量重跑**：1020 家 / 947 ok / 73 no_announcement / 0 error；非金融 proxy **10.33/11**（baseline 10.54，−0.21 为更严 proxy 所致）；SQLite 10428 行 — 见 `outputs/generalization/eval1000_v2/eval1000_v2_comparison.md`
- **schema_profile 可追溯性**：`eval_generalize.py` 写入 `company_profile.json` 时同步记录 `schema_profile` / `suggested_profile`
- **金融标签补全 — 601825 沪农商行**：`financial: true`；`_BANK_NAME_KW` / `sample_universe` 增加 农商行/城商行
- **金融标签人工复核 — 资本类**：000987 越秀资本、600061 国投资本、600390 五矿资本 → `financial: true`（other_financial）；列表共 **16 家** tagged
- **CURRENT_STATUS.md 重构**：作为主阶段进度页，面向 supervisor 可读；含目标、成果、关键数字、已知问题、下一步与进度查看指引
- **Cached validation**（eval1000 缓存）：SQLite 全量导入 PASS；rnd/revenue 新 proxy 在 10417 字段上验证；无其他字段回归 — 见 `outputs/validation/recent_changes_cached_validation.md`
- **SQLite 导入加固**：单公司 `company_profile.json` 失败不中断全量导入；`in_region`/`anchor_matched` 入库；`evaluation_result` 主键含 `report_year`；启用 FK；移除冗余索引
- **rnd_investment 抽取收紧**（Issue #1）：`extract_rnd_numeric` 优先总额标签、拒绝 ratio-only / 资本化 0.00 / 列表编号 / 利润表行；proxy 同步收紧
- **收入表格 proxy 收紧**（Issue #2）：`revenue_table_plausible` 要求 `revenue_by_region` / `revenue_by_segment` preview 含至少一行非表头数据行

### 文档
- **文档同步**（2026-06-23）：所有主要文档与 eval1000_v2 / independent eval1000 里程碑对齐；ROADMAP 阶段重排（full_market_2024 → strict 审计 → 多年度 → BrowserUser）；docs/evaluation_method 增加同 cohort 重跑与独立泛化验证说明；docs/database_schema 注明三批次 SQLite 导入状态；docs/financial_company_schema 补充 strict 未重跑说明；docs/crawler_strategy 明确 BrowserUser 在 full_market_2024 基线稳定后才启动；新增 plans/v0.6_full_market_2024_plan.md

### 计划
- full_market_2024 全量提取（~5300 家，下一主要里程碑）
- strict 审计重跑（全量基线稳定后）
- 多年度扩展
- BrowserUser 数据源试点（full_market_2024 基线稳定后）

## 2026-06-18

### 新增
- **1000 家受控评估**（eval1000）：1020 家样本，946 家成功，非金融 10.5/11 plausible
- **严格二次审计**：全量 9937 plausible 单元格 adversarial 复核，strict-usable 10.16/11（92.4%）
- **人工校准工具增强**：MISSED 分级、分层评分、calibrated population estimate
- **sample_universe.py --scale**：支持 5× 分层抽样生成 1000 公司列表
- **金融公司标签**：eval 列表增加 `financial: true` 标记，summary 单独统计

### 修复
- **risk_factors 召回**：扩展锚点（面临的风险/可能面临的风险），增加 pointer avoid（详见/请见）
- **revenue_by_region 精度**：移除 bare 境内/境外 anchor；combined-table preview 从分地区行开始
- **major_products 召回**：fallback_anchors 机制，从业务概述段落回退抽取
- **A+H 报告选择**：`pick_full_report` 优先 A 股年报，降级 H 股/境外版
- **no_announcement clean failure**：eval 不再因无公告而 hard crash
- **heading 识别**：带编号前缀的标题（如「（五）公司2025年度可能面临的风险」）不再误判为 partial
- **page-boundary snippet**：页底 heading 自动续接下一页内容

### 文档
- GitHub 协作结构与中文文档整理（README、docs/、plans/、CURRENT_STATUS）

## 2026-06-17

### 新增
- **200 家分层评估**（eval200）：按板块分层抽样，184 家成功抽取
- **calibration_sample.py**：40 格分层校准样本 + 评分器
- **eval_generalize.py 断点续跑**：已缓存 PDF + meta.json 跳过网络

### 修复
- eval200 hard crash（16 家 no_announcement 导致 TypeError）→ clean status 记录

## 2026-06-16

### 新增
- **4 公司泛化测试**（CATL / 三一重工 / 招商银行 / 澜起科技）
- **5 项通用鲁棒性修复**：prose concentration、avoid 负上下文、narrative anchors、header-aware table、full-report filter

### 变更
- 项目重心从多数据源覆盖率验证转向年报 PDF 基础字段抽取（Plan B）

## 2026-06-15（及更早）

### 新增
- 多数据源验证框架（`main.py` + 15 类 collector + `config/sources.yaml`）
- CNINFO 年报 probe（`lab/probe_cninfo.py`）
- 确定性年报抽取器 v1（`lab/extract_annual_report.py` + `lab/field_schema.py`）
- 11 字段 schema 定义（工业/制造业模板）

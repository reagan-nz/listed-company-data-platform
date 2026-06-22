# 当前状态

_最后更新：2026-06-22_

## 当前主方向

搭建中国上市公司**基础数据库**。短期目标：基于巨潮资讯网公开年报 PDF，抽取所有上市公司的 11 项基础标签字段；中期目标：覆盖全部 A 股；长期目标：用 BrowserUser 爬虫智能体补充程序化难以获取的数据，扩充数据库宽度与深度。

当前处于**第一阶段末期 → 第二阶段启动前**：年报程序化抽取与 1000 家评估已完成；**SQLite 建表与导入原型（Issue #8）已实现**（见 [docs/database_schema.md](docs/database_schema.md)）。

## 当前进行中

- **SQLite 原型验证**：`lab/db_init.py` + `lab/db_import.py` 可从 eval1000 导入样本至 `outputs/db/listed_companies_v1.db`（本地生成，不提交 Git）；已加固导入（单公司容错、审计元数据、FK 约束、`evaluation_result.report_year`）；全量 `--limit 0` 导入与 PostgreSQL 迁移尚未做。

## 已完成工作

- 巨潮资讯网（CNINFO）年报获取链路验证（orgId 解析、全文筛选、PDF 下载）
- 确定性年报抽取器（`lab/extract_annual_report.py`）+ 11 字段 schema（`lab/field_schema.py`）
- 4 公司泛化测试 + 5 项通用鲁棒性修复（客户/供应商 prose 抽取、表格选择、A+H 报告优先等）
- 200 家分层抽样评估（eval200），修复 hard crash、`major_products` 召回、A+H 报告选择
- 人工校准工具（`lab/calibration_sample.py`），引入 MISSED 分级与分层评分
- 字段修复：`risk_factors` 锚点扩展、`revenue_by_region` 表格预览切片、heading 识别改进
- **1020 家受控评估**（eval1000，200 家的 strict superset，复用 184 份缓存 PDF）
- **严格二次审计**：对全部 9937 个 plausible 单元格做 adversarial 规则复核（非 60 格样本）
- **SQLite 建表与导入原型**（Issue #8）：`lab/db_init.py`、`lab/db_import.py`，四表 v1 schema
- **SQLite 导入加固**：单公司 profile 容错、审计字段入库、`evaluation_result.report_year`、FK 启用
- **rnd_investment 抽取收紧**（Issue #1）：优先总额标签、拒绝 ratio-only / 资本化 0.00 / 列表编号 / 利润表研发费用行

## 1000 家测试结果（eval1000）

| 指标 | 数值 |
|---|---|
| 测试样本 | **1020 家**（200 家 strict superset + 820 新增） |
| 成功抽取（status=ok） | **946 家** |
| no_announcement | **73 家**（退市/无 2024 年报，属正常发现） |
| hard error | **0** |
| 非金融公司数 | 936 家 |
| 金融公司（单独统计） | 10 家 |

### 自动 proxy 指标（plausible）

非金融公司平均 **10.5 / 11** plausible（96%）。

各字段 proxy plausible 率（非金融，936 家）：

| 字段 | proxy |
|---|---|
| major_subsidiaries | 100% |
| major_products / mda / main_business_segments | 99% |
| revenue_by_segment | 98% |
| top_suppliers | 98% |
| top_customers | 97% |
| revenue_by_region | 96% |
| industry_discussion | 98% |
| risk_factors | 91% |
| **rnd_investment** | **79%** |

> 自动 plausible 仅表示 `status=found` + 值形态合法，**不等于人工准确率**。详见 [docs/evaluation_method.md](docs/evaluation_method.md)。

## 严格二次审计结果

对 eval1000 全部 **9937 个 plausible 单元格**做独立 adversarial 复核（检查 stored value 是否含实质数据，而非仅看 proxy 标记）：

| 指标 | 数值 |
|---|---|
| 严格 PASS（实质正确） | **96.4%** |
| hard-wrong（真 false positive） | **1.9%** |
| 非金融 strict-usable 均值 | **10.16 / 11（≈ 92.4%）** |

### 严格后各字段（非金融，936 家）

| 字段 | proxy | strict | 差距 |
|---|---|---|---|
| rnd_investment | 79.3% | **67.7%** | −11.5 |
| revenue_by_region | 96.0% | **90.7%** | −5.3 |
| revenue_by_segment | 98.3% | 95.7% | −2.6 |
| 其余 8 字段 | ≥90% | ≥90% | ≤0.4 |

200 家子集对比：**27 处改进，0 处回归**（eval200 结果与改进后 pipeline 一致）。

## 当前主要问题

1. **研发投入（rnd_investment）**：已收紧抽取与 proxy 规则（优先总额标签、拒绝 ratio-only / 资本化 0.00 / 列表编号）；eval1000 全量 strict 数字待重跑验证。
2. **收入分地区/分行业表格**：部分公司表格预览为 header-only（如 `-` 占位行），或 pdfplumber 无法解析合并单元格；严格后 region 约 90.7%。
3. **金融公司 schema**：当前 11 字段按工业/制造业设计，银行/券商/保险的 segment、客户、R&D 等字段不适用，需单独 schema。
4. **客户/供应商集中度**：偶发抓取单个客户占比而非前五名合计（如 `利亚德` 10.40% vs 实际 74.42%）。
5. **major_subsidiaries**：约 132 家「无/不适用」披露被标 plausible，内容为空但不算错误；另有少量 cross-reference 指针误匹配。

## 下一步建议

1. 全量 eval1000 → SQLite 导入（当前原型默认 `--limit 10` 小样本）
2. 表格抽取增加「至少一行含数字的数据行」校验
3. 金融公司单独 schema（或标记 N/A 并排除 headline 统计）
4. concentration 字段优先提取「合计/前五名合计」比例
5. 启动 BrowserUser 试点（见 [plans/v0.5_next_step_browser_agent_plan.md](plans/v0.5_next_step_browser_agent_plan.md)）

## 关键产物路径

```
outputs/generalization/eval1000/
  eval_summary.md              # 自动评估汇总（可提交 Git）
  calibration_sample.csv       # 60 格校准样本
  calibration_sample_graded.csv
  calibration_sample.md
  run.log
  eval_results.json            # ~1.9MB，不建议提交 Git
  <code>/company_profile.json  # 单公司结构化结果（本地保留）
  <code>/<code>.pdf           # 不提交 Git

outputs/db/
  listed_companies_v1.db       # SQLite 原型（lab/db_init.py + db_import.py 生成，不提交 Git）
```

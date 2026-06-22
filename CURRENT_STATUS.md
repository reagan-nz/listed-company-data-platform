# 当前状态

_最后更新：2026-06-22_

> **本文档是项目主进度页。** 老师或项目 supervisor 建议从这里开始阅读；技术细节见 [docs/](docs/)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。

---

## 1. 当前目标

搭建中国上市公司**基础但完整的数据库**。

- **当前数据来源**：巨潮资讯网（CNINFO）公开年报 PDF，程序化抽取 11 项基础字段（工业/制造类公司为主）。
- **中期目标**：覆盖全部 A 股，将抽取结果持久化到 SQLite（后续迁 PostgreSQL）。
- **后续扩展（尚未实现）**：
  - **BrowserUser** 爬虫智能体，补充程序化难以获取的数据；
  - **向量数据库**，支持文档检索与 RAG 式问答。

当前阶段：**从脚本 + JSON 输出，过渡到可维护的数据平台原型**（见第 3 节）。

---

## 2. 已完成工作

| 类别 | 内容 |
|---|---|
| **协作与文档** | GitHub 仓库与 Project 看板；中文 README、`docs/` 技术文档、`plans/` 方案归档 |
| **评估与审计** | 1020 家受控评估（eval1000）；9937 个 plausible 单元格严格二次审计；人工校准工具（60 格样本） |
| **数据库设计** | [docs/database_schema.md](docs/database_schema.md) 四表 v1 schema（Issue #7） |
| **SQLite 原型** | `lab/db_init.py` 建表 + `lab/db_import.py` 从 eval1000 导入（Issue #8） |
| **SQLite 导入加固** | 单公司容错、审计元数据（`in_region` / `anchor_matched`）、FK 约束、`evaluation_result.report_year`（Issue #9） |
| **字段质量改进** | `rnd_investment` 抽取收紧（Issue #1）；收入表格 proxy 收紧（Issue #2） |
| **金融公司 schema 设计** | [docs/financial_company_schema.md](docs/financial_company_schema.md) 银行/券商/保险三类子 schema v1（Issue #3，文档 only） |
| **Cached validation** | eval1000 缓存数据验证 Issue #1/#2 proxy 与 SQLite 全量导入 — 见 [outputs/validation/recent_changes_cached_validation.md](outputs/validation/recent_changes_cached_validation.md) |

**更早的基础工作**（支撑上述里程碑）：

- 巨潮年报获取链路（orgId 解析、PDF 下载）
- 确定性抽取器（`lab/extract_annual_report.py`）+ 11 字段 schema（`lab/field_schema.py`）
- 200 家分层评估（eval200）、4 公司泛化测试、多项鲁棒性修复

---

## 3. 当前阶段性成果

项目已从「单次脚本 + 散落 JSON」演进为**可维护的数据平台原型**：

```
年报 PDF（CNINFO）
    ↓  lab/extract_annual_report.py
company_profile.json（单公司结构化结果）
    ↓  lab/eval_generalize.py
eval1000 批量评估 + plausible / strict 指标
    ↓  lab/db_import.py
SQLite 本地库（outputs/db/listed_companies_v1.db）
    ↓  （计划）PostgreSQL 生产库
```

- **可复现**：eval 公司列表、seed、评估脚本均已版本化。
- **可审计**：每个字段保留 `page`、`evidence_sentence`、`source_url`。
- **可导入**：四表 relational schema 支持 UPSERT 与 FK 约束。
- **可迭代**：Issue 驱动的字段修复与 schema 扩展（金融公司等）。

---

## 4. 当前关键数字

基于 **eval1000**（2026-06-18 前后跑完的全量评估）。**2026-06-22 cached validation** 已在现有 profile 上重算 proxy，**全量 eval 管道与 strict 审计尚未重跑**。

### 样本与成功率

| 指标 | 数值 |
|---|---|
| 测试样本 | **1020 家**（200 家 strict superset + 820 新增） |
| 成功抽取（status=ok） | **946 家** |
| no_announcement | **73 家**（退市/无 2024 年报，属正常发现） |
| hard error | **0** |
| 非金融公司 | 936 家（headline 统计范围） |
| 金融公司 | 12 家（单独统计，不计入非金融 headline） |

### 质量指标（非金融，936 家）

| 指标 | 数值 | 说明 |
|---|---|---|
| proxy plausible（eval 跑完时） | **10.54 / 11** | 非金融 936 家，stored |
| proxy plausible（cached 重算） | **10.36 / 11** | Issue #1/#2 新规则，−0.18；**非最终 headline** |
| strict-usable | **10.16 / 11（≈ 92.4%）** | 全量 9937 plausible 单元格 adversarial 复核（**未重跑**） |
| hard-wrong 率 | **1.9%** | 真 false positive |

> **注意**：cached validation 仅重算 proxy，未重跑抽取与 strict 审计。rnd −101 / revenue −75 单元格被新规则拒绝；详见 [validation report](outputs/validation/recent_changes_cached_validation.md)。

### Cached validation 摘要（2026-06-22）

| 项目 | 结果 |
|---|---|
| SQLite `--limit 0` | 1020 / 1020 / 10417 / 10417 行；0 profile_errors；可重复导入 |
| rnd_investment 新 proxy | 745 found → **644 pass**（−101：list-marker 39, ratio-only 28, no-amount 28, 0.00-only 6） |
| revenue_by_region 新 proxy | 902 found → **851 pass**（−51） |
| revenue_by_segment 新 proxy | 922 found → **898 pass**（−24） |
| 其他字段回归 | **0** 处 plausible 逻辑变化 |

### 最弱字段（修复前 baseline）

| 字段 | proxy | strict |
|---|---|---|
| rnd_investment | 79.3% | **67.7%** |
| revenue_by_region | 96.0% | **90.7%** |
| revenue_by_segment | 98.3% | 95.7% |

评估方法详见 [docs/evaluation_method.md](docs/evaluation_method.md)。

---

## 5. 已知问题

1. **eval1000 strict 审计未重跑**：cached validation 已确认 proxy 改进方向；strict-usable 仍为修复前 **10.16/11**。
2. **收入表格 empty-label 行**：603132、605090 共 4 字段实例 — pdfplumber 丢失行标签导致误拒（validation 已确认）。
3. **金融 schema 仅设计未实现**：`docs/financial_company_schema.md` 已完成；`field_schema.py` 仍为 generic `FINANCIAL_FIELD_SPECS`，bank/broker/insurer 子 schema 未写入代码。
4. **BrowserUser 扩展未启动**：见 [plans/v0.5_next_step_browser_agent_plan.md](plans/v0.5_next_step_browser_agent_plan.md)，尚无实现或试点。
5. **`strict_audit_result` loader 未实现**：数据库 schema 已预留该列（`evaluation_result.strict_audit_result`），但 `db_import.py` 尚未从 strict audit 结果回填。
6. **其他字段级问题**（非 blocking）：客户/供应商集中度偶抓单项而非合计；`major_subsidiaries` 约 132 家「无/不适用」披露内容为空。

---

## 6. 下一步计划

1. **路线决策**（cached validation **PASS**，可并行推进）：
   - **金融 schema 实现**（Issue #4）：按 [docs/financial_company_schema.md](docs/financial_company_schema.md)；
   - **BrowserUser 规划/试点**：见 [plans/v0.5_next_step_browser_agent_plan.md](plans/v0.5_next_step_browser_agent_plan.md)。
2. **可选**：小子集重抽取验证 rnd 抽取逻辑（Issue #1 改动了 extraction，不仅是 proxy）；或预算允许时全量 eval 重跑。
3. **补 `strict_audit_result` loader**；SQLite 全量导入已完成（10417 行）。

---

## 7. 如何查看进度

| 入口 | 用途 |
|---|---|
| **本文档**（`CURRENT_STATUS.md`） | 项目阶段、关键数字、已知问题、下一步 — **主进度页** |
| **GitHub Project 看板** | Todo / In Progress / Done 任务状态；当前重点：数据库、字段优化、金融 schema、BrowserUser |
| **[CHANGELOG.md](CHANGELOG.md)** | 每次重要变更的记录（Keep a Changelog 格式） |
| **[docs/](docs/)** | 技术细节：数据源、抽取流程、评估方法、数据库 schema、金融 schema 设计 |
| **[ROADMAP.md](ROADMAP.md)** | 分阶段路线图 |

协作流程见 [docs/github_workflow.md](docs/github_workflow.md)。

---

## 附录：关键产物路径

```
outputs/generalization/eval1000/
  eval_summary.md              # 自动评估汇总
  calibration_sample*.csv/md    # 人工校准样本
  eval_results.json            # 批量结果（~1.9MB，本地保留）
  <code>/company_profile.json  # 单公司结构化结果
  <code>/<code>.pdf           # 年报 PDF（不提交 Git）

outputs/db/
  listed_companies_v1.db       # SQLite 全量导入（1020 公司，gitignored）

outputs/validation/
  recent_changes_cached_validation.md   # Issue #1/#2/SQLite cached 验证报告
```

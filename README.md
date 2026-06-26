# 上市公司基础数据库

本项目从**中国 A 股上市公司公开年报 PDF** 中，程序化抽取结构化字段，建立**可证据追溯**的公司基础数据层。

**项目定位**：这是**数据底座与质量闭环**项目，不是已上线的完整 RAG（检索增强生成）产品或 LLM Wiki（大模型辅助知识页）产品。抽取结果可支撑内部分析、字段查询、公司 profile（公司档案）以及 RAG prototype（检索增强问答原型）的底层数据，但**不等于**全量人工验证过的“最终答案库”。

**当前阶段**：`full_market_2024`（2024 全市场运行）基线已完成；**Stage 3a（第 3a 阶段）质量 follow-up（质量跟进）已通过**。最新指标与后续任务见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)**；Stage 3a 汇总见 **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)**。

---

## 项目是做什么的

1. **收集**：从巨潮资讯网 CNINFO（中国上市公司信息披露平台）获取年报 PDF。
2. **抽取**：从 PDF 中抽取 11 项工业类基础字段（如 `rnd_investment`（研发投入字段）、`revenue_by_region`（分地区收入字段）等）。
3. **留证**：每个字段记录来源页码、证据句子和 `source_url`（来源链接），便于回溯核对。
4. **评估**：自动 plausibility（合理性检查）与 strict audit（严格质量审计）并行，衡量字段质量。
5. **修复**：对问题字段做 scoped refresh（小范围定向刷新）或 scoped apply（小范围定向应用），而非每次全量重跑 CNINFO。

---

## 如何查看当前进度

**主进度页：[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 建议老师 / 评审从这里开始。内容包括：当前阶段、已完成工作、核心指标、能达到的标准、不能宣称的内容、已知问题与下一步。

建议阅读顺序：

1. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 项目阶段与核心指标；
2. **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)** — Stage 3a 质量 follow-up（质量跟进）汇总（#24–#28）；
3. **GitHub Project 看板** — 待办 / 进行中 / 已完成；
4. **[CHANGELOG.md](CHANGELOG.md)** — 变更记录；
5. **[docs/](docs/)** — 技术细节（数据源、抽取、评估、数据库）。

**当前后续重点**（Stage 3b 之后）：

- #31 金融公司漏标扫描与标签复核；
- revenue Tier4（收入字段第四层修复）与 wrong-table ranking（错表排序）试点；
- 2025 年 `pilot`（试点）实施（待人工签核）；
- BrowserUser（浏览器智能体爬虫，全量基线稳定后再启动）。

---

## 术语说明（简表）

| 术语 | 含义 |
|---|---|
| **strict audit（严格质量审计）** | 对已存字段值做更严规则复核，产出 `usable`（可用）/ `partial`（部分可用）/ `wrong`（错误）等标签。 |
| **strict usable（严格审计下可用）** | strict audit（严格质量审计）中仅计 `usable`（可用）字段的均值，如非金融 **9.43/11**（11 为每家公司平均检查字段数）。 |
| **proxy plausible（自动合理性分数）** | 抽取时的结构合理性估计，比 strict audit（严格质量审计）更宽松。 |
| **scoped refresh（小范围定向刷新）** | 仅用已缓存 PDF 重抽部分字段，不重新从 CNINFO 全量下载。 |
| **scoped apply（小范围定向应用）** | 将试跑验证通过的修复，小范围写回 `company_profile.json`（公司档案 JSON）。 |
| **headline（核心指标/对外口径）** | 对外报告用的主质量数字；非金融与金融 cohort（分组样本）**分开报告**。 |
| **run_name（运行名称）** | 一次运行的标识，如 `full_market_2024`（2024 全市场运行），用于输出目录与 SQLite（轻量数据库）导入。 |
| **cohort（分组样本）** | 一组按规则选出的公司集合，如 eval1000（1000 家受控评估）。 |
| **pilot（试点）** | 小规模试跑，如 100 家公司分层试点，验证管道后再扩全市场。 |
| **backfill（历史年份回填）** | 在 2025 基线稳定后，再补跑 2023/2022 等历史年报。 |
| **not_found_missed（应该找到但没有找到）** | PDF 中应有披露但抽取结果为 not_found（未找到）。 |
| **RAG（检索增强生成）** | 先检索资料再让大模型回答；本项目提供其底层结构化数据，非完整 RAG 产品。 |
| **LLM Wiki（大模型辅助知识页）** | 由大模型辅助生成/更新的公司或行业知识页；本项目尚未交付此类产品。 |
| **CNINFO** | 巨潮资讯网，A 股法定信息披露来源。 |
| **SQLite** | 项目使用的轻量关系数据库原型，存放字段级抽取与评估结果。 |

完整术语见 [CURRENT_STATUS.md](CURRENT_STATUS.md) §4.1 与 [docs/evaluation_method.md](docs/evaluation_method.md)。

---

## 快速开始

```bash
cd listed_company_data_collector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

```bash
# 单公司抽取（需本地 PDF + 官方 URL）
python lab/extract_annual_report.py \
  --pdf path/to/report.pdf --stock-code 600031 \
  --source-url https://static.cninfo.com.cn/...

# 批量评估（需网络，可断点续跑）
python lab/eval_generalize.py \
  --companies lab/eval_companies_1000.yaml \
  --out outputs/generalization/eval1000 --throttle 1.0

# 人工校准抽样
python lab/calibration_sample.py --eval-dir outputs/generalization/eval1000 --n 60
```

---

## 当前结果（摘要）

**不在此重复 headline（核心指标/对外口径）数字**（避免文档过期）。最新指标见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)** §4。

**阅读提醒**：

- strict usable（严格审计下可用）来自 automated adversarial（自动化对抗式规则复核）+ 抽样/人工 calibration（校准）**支持**，**不是** full manual validation（全量人工验证）。
- 不得将 full_market_2024（2024 全市场运行）的 strict usable（严格审计下可用）与 eval1000 baseline（基线）10.16/11 直接比较为「改善」。
- 金融 cohort（金融公司分组）指标**不得**与非金融 headline（核心指标/对外口径）混报。

---

## 文档

| 文档 | 说明 |
|---|---|
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | **主进度页** — 阶段成果、关键数字、已知问题、下一步 |
| [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) | Stage 3a 质量 follow-up（质量跟进）汇总（#24–#28） |
| [ROADMAP.md](ROADMAP.md) | 分阶段路线图 |
| [CHANGELOG.md](CHANGELOG.md) | 关键更新记录 |
| [docs/](docs/) | 技术文档（数据源、抽取、评估、协作） |
| [plans/](plans/) | 历史方案记录（v0.1–v0.6） |

---

## GitHub Project 看板建议

**列**：待办（Backlog）→ 待开始（To Do）→ 进行中（In Progress）→ 测试中（Testing）→ 已完成（Done）→ 阻塞（Blocked）

**任务类型标签**：Data Source / Crawler / Extractor / Database / Evaluation / Documentation / Bug Fix / Research

协作流程见 [docs/github_workflow.md](docs/github_workflow.md)。

---

## 项目结构

```
listed_company_data_collector/
  lab/           # 年报抽取与评估（核心）
  config/        # 公司与数据源配置
  collectors/    # 多数据源采集器（早期框架）
  outputs/       # 运行产物（PDF 不提交 Git）
  docs/          # 中文技术文档
  plans/         # 方案归档
```

---

## 附录：早期数据源验证框架

项目最初用于验证多数据源覆盖率的 `main.py` + `config/sources.yaml` 仍可用，产出 `outputs/source_coverage.csv`。详见 [docs/data_sources.md](docs/data_sources.md) 与 [plans/v0.1_initial_data_source_plan.md](plans/v0.1_initial_data_source_plan.md)。

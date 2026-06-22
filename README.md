# 上市公司基础数据库

基于中国 A 股上市公司**公开年报 PDF**，程序化抽取 11 项基础字段，构建可证据追溯的公司基础标签库。后续计划用 BrowserUser 爬虫智能体补充普通程序难以获取的数据。

**当前阶段**：第一阶段末期 — 年报抽取链路已跑通，1000 家受控评估已完成。

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

## 当前结果（摘要）

| 指标 | 数值 |
|---|---|
| 1000 家测试样本 | 1020 家 |
| 成功抽取 | 946 家 |
| 非金融 proxy plausible | 10.5 / 11 |
| 严格可用（strict-usable） | **10.16 / 11（≈ 92.4%）** |

详细数字与问题分析见 [CURRENT_STATUS.md](CURRENT_STATUS.md)。

## 文档

| 文档 | 说明 |
|---|---|
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | 当前状态与最新测试结果 |
| [ROADMAP.md](ROADMAP.md) | 分阶段路线图 |
| [CHANGELOG.md](CHANGELOG.md) | 关键更新记录 |
| [docs/](docs/) | 技术文档（数据源、抽取、评估、协作） |
| [plans/](plans/) | 历史方案记录（v0.1–v0.5） |

## GitHub Project 看板建议

**列**：Backlog → To Do → In Progress → Testing → Done → Blocked

**任务类型标签**：Data Source / Crawler / Extractor / Database / Evaluation / Documentation / Bug Fix / Research

协作流程见 [docs/github_workflow.md](docs/github_workflow.md)。

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

## 附录：早期数据源验证框架

项目最初用于验证多数据源覆盖率的 `main.py` + `config/sources.yaml` 仍可用，产出 `outputs/source_coverage.csv`。详见 [docs/data_sources.md](docs/data_sources.md) 与 [plans/v0.1_initial_data_source_plan.md](plans/v0.1_initial_data_source_plan.md)。

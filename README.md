# 上市公司基础数据库

基于中国 A 股上市公司**公开年报 PDF**，程序化抽取 11 项基础字段，构建可证据追溯的公司基础标签库。

**当前阶段**：full_market_2024 全 A 股 2024 年报提取、SQLite 入库与混合 strict 审计均已完成（2026-06-24）。Headline：非金融 proxy **10.35/11**，strict usable **9.01/11**。指标含义见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)** 第 4.1 节。

## 如何查看当前进度

**主进度页：[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 项目目标、已完成工作、关键数字、已知问题与下一步计划。

建议查看顺序：

1. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 项目阶段进度（老师 / supervisor 建议从这里开始）；
2. **GitHub Project 看板** — Todo / In Progress / Done 任务状态；
3. **[CHANGELOG.md](CHANGELOG.md)** — 变更记录；
4. **[docs/](docs/)** — 技术细节（数据源、抽取、评估、数据库）。

当前看板重点包括：

- 质量 follow-up：BSE 模板、rnd 召回、revenue 跨页切片；
- 金融公司字段质量专项 review；
- 多年度扩展（2023 / 2022）；
- BrowserUser（全量基线稳定后，暂不启动）。

我会在后续每次本地更新后，同步更新 GitHub 文档、提交记录和项目看板，方便持续追踪项目进度。

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

最新数字与**指标解释**见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)**（full_market_2024，2026-06-24）：

| 指标 | full_market_2024 |
|---|---|
| total / ok | 6124 / **5707** |
| 非金融 proxy | **10.35 / 11** |
| 非金融 strict usable | **9.01 / 11** |

> strict usable 为自动化 adversarial 估计 + 小样本 PDF 校准，**非全量人工验证**。不得与旧 eval1000 baseline 10.16/11 直接比较「改善」。

## 文档

| 文档 | 说明 |
|---|---|
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | **主进度页** — 阶段成果、关键数字、已知问题、下一步 |
| [ROADMAP.md](ROADMAP.md) | 分阶段路线图 |
| [CHANGELOG.md](CHANGELOG.md) | 关键更新记录 |
| [docs/](docs/) | 技术文档（数据源、抽取、评估、协作） |
| [plans/](plans/) | 历史方案记录（v0.1–v0.6） |

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

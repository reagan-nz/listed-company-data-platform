# 上市公司基础数据库

基于中国 A 股上市公司**公开年报 PDF**，程序化抽取 11 项基础字段，构建可证据追溯的公司基础标签库。

**当前阶段**：eval1000_v2 同 cohort 重跑（2026-06-22）与 independent eval1000 泛化验证（2026-06-23）均已完成，管道泛化良好；SQLite 数据平台原型就绪；下一步为 full_market_2024 全量提取。

## 如何查看当前进度

**主进度页：[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 项目目标、已完成工作、关键数字、已知问题与下一步计划。

建议查看顺序：

1. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 项目阶段进度（老师 / supervisor 建议从这里开始）；
2. **GitHub Project 看板** — Todo / In Progress / Done 任务状态；
3. **[CHANGELOG.md](CHANGELOG.md)** — 变更记录；
4. **[docs/](docs/)** — 技术细节（数据源、抽取、评估、数据库）。

当前看板重点包括：

- full_market_2024 全量提取（~5300 家，规划中）；
- 磁盘与运行时间准备；
- strict 审计重跑（延期至全量基线稳定后）；
- BrowserUser 数据扩展（全量基线稳定后，暂不启动）。

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

最新数字见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)**：

| run | 样本 | ok | 非金融 proxy |
|---|---:|---:|---:|
| eval1000_v2（同 cohort，2026-06-22） | 1020 | 947 | **10.33 / 11** |
| independent eval1000（新 cohort，2026-06-23） | 1000 | 918 | **10.30 / 11** |

> strict-usable **10.16/11**（eval1000 审计，尚未在 v2/independent 上重跑）。详细对比、SQLite 行数与已知问题见 [CURRENT_STATUS.md](CURRENT_STATUS.md)。

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

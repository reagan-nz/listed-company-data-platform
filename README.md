# 上市公司基础数据库

基于中国 A 股上市公司**公开年报 PDF**，程序化抽取 11 项基础字段，构建可证据追溯的公司基础标签库。

**当前阶段**：full_market_2024 2024 基线 + **Stage 3a 质量 follow-up PASS**（2026-06-25）。最新指标与 Stage 3b backlog 见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)**；Stage 3a 汇总见 **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)**。

## 如何查看当前进度

**主进度页：[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 项目目标、已完成工作、关键数字、已知问题与下一步计划。

建议查看顺序：

1. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 项目阶段进度（老师 / supervisor 建议从这里开始）；
2. **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)** — Stage 3a 质量 follow-up 汇总（#24–#28）；
3. **GitHub Project 看板** — Todo / In Progress / Done 任务状态；
4. **[CHANGELOG.md](CHANGELOG.md)** — 变更记录；
5. **[docs/](docs/)** — 技术细节（数据源、抽取、评估、数据库）。

当前看板重点（Stage 3b）：

- 金融 manual calibration grading（325-cell worksheet）；
- revenue / rnd 剩余 strict-wrong follow-up；
- financial under-tagging scan 与 extraction/tag fixes；
- 多年度扩展决策（2025 / 2023 / 2022）；
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

**不在此重复 headline 数字**（避免 stale）。最新指标见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)** §4；Stage 3a 汇总见 **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)**。

> strict usable 为 automated adversarial 估计 + sampled/manual calibration support，**非全量人工验证**。不得与 eval1000 baseline 10.16/11 直接比较为「改善」；金融指标**不得**与非金融 headline 混报。

## 文档

| 文档 | 说明 |
|---|---|
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | **主进度页** — 阶段成果、关键数字、已知问题、下一步 |
| [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) | Stage 3a 质量 follow-up 汇总（#24–#28） |
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

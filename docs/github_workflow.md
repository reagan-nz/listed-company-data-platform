# GitHub 协作流程

## 日常工作流（8 步）

1. **本地修改**代码或文档
2. **本地运行**必要测试（单公司抽取 / 小样本 eval，不重跑 1000 家除非必要）
3. **更新** [CHANGELOG.md](../CHANGELOG.md)（记录本次变更）
4. **更新** [CURRENT_STATUS.md](../CURRENT_STATUS.md)（如有里程碑变化）
5. `git add` 相关文件
6. `git commit`（见 commit 规范）
7. `git push`
8. 在 **GitHub Project 看板**更新任务状态

## GitHub Project 看板

### 建议列

| 列 | 用途 |
|---|---|
| **Backlog** | 已识别但未排期的任务 |
| **To Do** | 已排期、待开始 |
| **In Progress** | 正在执行 |
| **Testing** | 代码/抽取改动已完成，正在验证 |
| **Done** | 已完成并合并 |
| **Blocked** | 被外部依赖阻塞（合规、API、数据源不可用） |

### 建议任务类型标签

| 标签 | 示例 |
|---|---|
| **Data Source** | 接入 e 互动数据源 |
| **Crawler** | CNINFO 断点续跑优化 |
| **Extractor** | rnd_investment 数值规则收紧 |
| **Database** | company_profile 入库格式设计 |
| **Evaluation** | 200 家 re-eval |
| **Documentation** | 更新 CURRENT_STATUS |
| **Bug Fix** | no_announcement crash 修复 |
| **Research** | BrowserUser 试点调研 |

## Commit 规范

```
<type>: <简要描述>

<可选正文：影响范围、关联 issue>
```

**type 取值**：

| type | 用途 |
|---|---|
| `feat` | 新功能（新字段、新 collector） |
| `fix` | bug 修复 |
| `docs` | 文档变更 |
| `refactor` | 重构（不改变行为） |
| `eval` | 评估相关（新测试、校准） |
| `chore` | 工具/配置变更 |

**示例**：

```
fix: risk_factors 扩展锚点，提升召回至 91%

添加「面临的风险」系列锚点；增加 pointer avoid（详见/请见）。
eval1000 非金融 risk_factors proxy: 848/936 (91%)。
```

## 分支策略

- `main`：稳定分支，评估结果可信
- 功能分支：`feat/rnd-numeric-fix`、`docs/github-setup` 等
- 合并前：至少跑单公司或 10 家 smoke test

## 首次 Git 初始化

```bash
cd listed_company_data_collector
git init

# 核心代码与文档
git add README.md CURRENT_STATUS.md ROADMAP.md CHANGELOG.md
git add docs/ plans/ .gitignore
git add lab/ config/ main.py requirements.txt
git add collectors/ parsers/ utils/

# 评估公司列表（可复现）
git add lab/eval_companies_1000.yaml lab/sample_universe.py

# 轻量评估产物（不含 PDF / cache / 大 JSON）
git add outputs/generalization/eval1000/eval_summary.md
git add outputs/generalization/eval1000/calibration_sample*.csv
git add outputs/generalization/eval1000/calibration_sample.md

# 确认：不应出现 .pdf / .cache / .venv / eval_results.json
git status

git commit -m "$(cat <<'EOF'
docs: 整理 GitHub 协作结构与中文项目文档

添加 CURRENT_STATUS、ROADMAP、CHANGELOG、docs/ 与 plans/；
重写 README 以反映年报基础字段抽取主线与 1000 家评估结果；
不改动抽取逻辑与 outputs 数据。
EOF
)"

git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## 什么该提交、什么不该

| 类别 | 提交？ | 说明 |
|---|---|---|
| 源代码（lab/, collectors/, etc.） | 是 | |
| 配置文件（config/, eval_companies_1000.yaml） | 是 | |
| 文档（docs/, plans/, *.md） | 是 | |
| eval_summary.md | 是 | ~48KB，可读汇总 |
| calibration_sample*.csv | 是 | 人工校准数据 |
| eval_results.json | **否** | ~1.9MB，本地生成 |
| *.pdf | **否** | 体积大，可从 CNINFO 重新下载 |
| .cache/ | **否** | 解析缓存，可重建 |
| .venv/ | **否** | 虚拟环境 |
| run.log | 可选 | 按需 |
| company_profile.json（单公司） | **否** | 1020 份，体积大；eval_summary 已汇总 |

## Code Review 要点

- 抽取逻辑改动：是否影响已有 946 家 OK 的结果？要求 smoke test
- 新字段/schema：是否更新 field_schema.py + database_schema.md + CHANGELOG
- 新数据源：是否更新 data_sources.md + 合规评估
- 评估改动：是否更新 evaluation_method.md + CURRENT_STATUS

## Issue 模板建议

创建 Issue 时标注：
- **类型标签**（见上表）
- **优先级**（P0 阻塞 / P1 本 sprint / P2 后续）
- **关联字段**（如 rnd_investment）
- **预期产出**（代码改动 / 文档 / 评估结果）

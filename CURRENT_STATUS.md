# 当前状态

_最后更新：2026-06-22（eval1000_v2 重跑 + 金融标签审计完成）_

> **本文档是项目主进度页。** 老师或项目 supervisor 建议从这里开始阅读；技术细节见 [docs/](docs/)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。

**2026-06-22 日结**：同 cohort 全量重跑 eval1000_v2 完成；Issue #1/#2/#4 变更经全量验证；金融 YAML 标签补全至 16 家；baseline eval1000 保留未覆盖。

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
| **金融公司 schema 设计** | [docs/financial_company_schema.md](docs/financial_company_schema.md) 银行/券商/保险三类子 schema v1（Issue #3） |
| **金融公司子 schema 实现** | `BANK/BROKER/INSURER/OTHER_FINANCIAL_FIELD_SPECS` + `detect_profile` / `resolve_profile` / `get_field_specs`（Issue #4） |
| **Cached validation** | eval1000 缓存数据验证 Issue #1/#2 proxy 与 SQLite 全量导入 — 见 [outputs/validation/recent_changes_cached_validation.md](outputs/validation/recent_changes_cached_validation.md) |
| **eval1000_v2 全量重跑** | 同 cohort 1020 家，验证 Issue #1/#2/#4 后最新代码 — 见 [outputs/generalization/eval1000_v2/eval1000_v2_comparison.md](outputs/generalization/eval1000_v2/eval1000_v2_comparison.md) |
| **schema_profile 可追溯性** | `eval_generalize.py` 写入 `company_profile.json` 时同步记录 `schema_profile` / `suggested_profile` |
| **金融 YAML 标签审计** | 601825 沪农商行（bank）；000987/600061/600390 资本类（other_financial）；`financial: true` 共 **16 家** |

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

**最新 headline 来自 eval1000_v2**（2026-06-22 全量重跑，同 cohort `lab/eval_companies_1000.yaml`）。**strict 审计尚未重跑**。

> **关于 proxy 下降（10.54 → 10.33）**：成功率不变（947 ok / 73 no_announcement / 0 error），下降来自 Issue #1/#2 更严格的抽取与 proxy 规则主动拒绝低质量命中，**不是管道故障**。其他 8 个工业字段 plausible 零回归。

### 样本与成功率（eval1000_v2）

| 指标 | 数值 |
|---|---|
| 测试样本 | **1020 家**（与 eval1000 相同 cohort） |
| 成功抽取（status=ok） | **947 家** |
| no_announcement | **73 家**（与 baseline 一致） |
| hard error | **0** |
| 非金融公司 | 936 家（headline 统计范围） |
| 金融公司（ok） | 11 家（**16 家 tagged**，1 家 no_announcement；601825/资本类补标待下次 eval 生效） |

### 质量指标（非金融，936 家 — eval1000_v2）

| 指标 | eval1000 (baseline) | eval1000_v2 (latest) | Delta |
|---|---:|---:|---:|
| proxy plausible | **10.54 / 11** | **10.33 / 11** | −0.21 |
| rnd_investment plausible | 742/936 | 619/936 | −123（抽取收紧） |
| revenue_by_region plausible | 899/936 | 849/936 | −50（proxy 收紧） |
| revenue_by_segment plausible | 920/936 | 896/936 | −24（proxy 收紧） |
| strict-usable | **10.16 / 11** | **未重跑** | — |

> rnd −123 = 抽取层拒绝（742→619 found）；revenue −74 = proxy 层拒绝（found 不变）。其他 8 个工业字段 **0 回归**。详见 [comparison report](outputs/generalization/eval1000_v2/eval1000_v2_comparison.md)。

### 金融子 schema（eval1000_v2 首次全量数字）

| 子类型 | 数量 | 代表 |
|---|---:|---|
| bank | 4 | 601988, 601398, 601939, 601328 |
| broker | 5 | 600958, 601901, 601162, 002500, 002736 |
| insurer | 1 | 601336 |
| other_financial | 1 | 600927 |

### SQLite 导入（eval1000_v2，run_name=`eval1000_v2`）

| 表 | 行数 |
|---|---:|
| company_basic | 1020 |
| report_source | 1020 |
| extracted_field | 10428 |
| evaluation_result | 10428 |

（baseline eval1000 为 10417 行；+11 来自金融子 schema 字段数差异。DB 文件 gitignored。）

### Cached validation 摘要（2026-06-22，eval1000 缓存 proxy 重算）

| 项目 | 结果 |
|---|---|
| SQLite `--limit 0` | 1020 / 1020 / 10417 / 10417 行；0 profile_errors |
| rnd_investment 新 proxy | 745 found → **644 pass**（−101） |
| revenue_by_region 新 proxy | 902 found → **851 pass**（−51） |
| revenue_by_segment 新 proxy | 922 found → **898 pass**（−24） |

### 最弱字段（eval1000_v2 proxy）

| 字段 | v2 proxy | baseline proxy |
|---|---:|---:|
| rnd_investment | **66.1%** (619/936) | 79.3% (742/936) |
| revenue_by_region | **90.7%** (849/936) | 96.0% (899/936) |
| revenue_by_segment | **95.7%** (896/936) | 98.3% (920/936) |

评估方法详见 [docs/evaluation_method.md](docs/evaluation_method.md)。

---

## 5. 已知问题

1. **strict-usable 未重跑**：eval1000_v2 proxy headline 已更新（10.33/11）；strict-usable 仍为 eval1000 修复前 **10.16/11** — 不能据此声称 strict 改善。
2. **rnd 召回下降**：更严格规则后 found 742→619（−123）；换取更高命中质量，但 recall 下降需后续评估。
3. **金融字段质量未 strict 审计**：11 家 ok 金融公司已分 bank/broker/insurer/other_financial；numeric 抽取（如 year-noise）未 adversarial 复核。
4. **金融 YAML 标签**：审计完成，`financial: true` 共 16 家；601825/资本类 4 家补标待下次 eval 生效（eval1000_v2 跑在补标前）。
5. **收入表格 empty-label 行**：603132、605090 共 4 字段实例 — pdfplumber 丢失行标签导致误拒。
6. **BrowserUser 扩展未启动**：见 [plans/v0.5_next_step_browser_agent_plan.md](plans/v0.5_next_step_browser_agent_plan.md)。
7. **`strict_audit_result` loader 未实现**：`db_import.py` 尚未从 strict audit 结果回填。
8. **其他字段级问题**（非 blocking）：客户/供应商集中度偶抓单项而非合计；`major_subsidiaries` 约 132 家「无/不适用」披露内容为空。

---

## 6. 下一步计划

1. **strict 审计重跑**（eval1000_v2 plausible 单元格 adversarial 复核）— 更新 strict-usable headline。
2. **BrowserUser 规划/试点**：见 [plans/v0.5_next_step_browser_agent_plan.md](plans/v0.5_next_step_browser_agent_plan.md)。
3. **补 `strict_audit_result` loader**。
4. **可选**：对 601825/资本类 4 家补标公司做 targeted re-eval（无需全量重跑）。

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
outputs/generalization/eval1000/          # baseline（保留，未覆盖）
  eval_summary.md
  eval_results.json
  <code>/company_profile.json

outputs/generalization/eval1000_v2/       # 最新全量重跑（2026-06-22）
  eval_summary.md
  eval1000_v2_comparison.md               # vs baseline 对比报告
  eval_results.json
  <code>/company_profile.json

outputs/db/
  listed_companies_v1.db                  # eval1000_v2 导入（10428 行，gitignored）

outputs/validation/
  recent_changes_cached_validation.md
```

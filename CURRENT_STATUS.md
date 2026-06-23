# 当前状态

_最后更新：2026-06-23（independent eval1000 泛化验证完成）_

> **本文档是项目主进度页。** 老师建议从这里开始阅读；技术细节见 [docs/](docs/)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。

**2026-06-23 日结**：独立 cohort 1000 家 eval 完成；18 家 ChunkedEncodingError 经 VPN-off 重试全部恢复；最终 **918 ok / 0 error / 82 no_announcement**（91.8%）；非金融 proxy **10.30/11**，泛化验证 **PASS**。

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
| **Independent eval1000** | 新 cohort 1000 家（seed 20260623，841 新样本）；泛化验证 PASS — 见 [independent_comparison.md](outputs/generalization/eval1000_independent_20260623/independent_comparison.md) |

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

**泛化 headline 来自 independent eval1000**（2026-06-23，新 cohort seed 20260623，与 eval1000 重叠 159 家 / 15.9%）。**strict 审计尚未重跑**。

> **泛化结论**：独立样本非金融 proxy **10.30/11** vs eval1000_v2 **10.33/11**（Δ −0.03，在 ±0.15 内）。rnd/revenue 字段率与 v2 一致。**管道在新公司上泛化良好**。

### 样本与成功率（independent eval1000，2026-06-23）

| 指标 | 数值 |
|---|---|
| 测试样本 | **1000 家**（seed 20260623；与 eval1000 重叠 159 家） |
| 成功抽取（status=ok） | **918 家**（91.8%） |
| no_announcement | **82 家** |
| hard error | **0**（18 家 ChunkedEncodingError 经 VPN-off 重试已恢复） |
| 非金融公司 | 907 家（headline 统计范围） |
| 金融公司（ok） | 11 家 |

### 质量指标（非金融，907 家 — independent，post-retry）

| 指标 | independent | eval1000_v2 | Delta |
|---|---:|---:|---:|
| proxy plausible | **10.30 / 11** | 10.33 / 11 | **−0.04** |
| rnd_investment plausible | 605/907 (66.7%) | 619/936 (66.1%) | +0.6 pp |
| revenue_by_region plausible | 816/907 (90.0%) | 849/936 (90.7%) | −0.7 pp |
| revenue_by_segment plausible | 861/907 (94.9%) | 896/936 (95.7%) | −0.8 pp |
| strict-usable | **未重跑** | **未重跑** | — |

详见 [independent_comparison.md](outputs/generalization/eval1000_independent_20260623/independent_comparison.md)。

### 同 cohort 参考（eval1000_v2，2026-06-22）

| 指标 | 数值 |
|---|---|
| 测试样本 | 1020 家 |
| ok / no_announcement / error | 947 / 73 / 0 |
| 非金融 proxy | 10.33 / 11 |

> proxy 从 baseline 10.54 降至 10.33 系 Issue #1/#2 更严规则所致，非管道故障。详见 [eval1000_v2_comparison.md](outputs/generalization/eval1000_v2/eval1000_v2_comparison.md)。

### 金融子 schema（independent，11 ok）

| 子类型 | 数量 |
|---|---:|
| bank | 3 |
| broker | 8 |

### SQLite 导入（independent，run_name=`eval1000_independent_20260623`）

| 表 | 行数 |
|---|---:|
| company_basic | 1000 |
| report_source | 1000 |
| extracted_field | 10112 |
| evaluation_result | 10112 |

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

1. **strict-usable 未重跑**：不能据此声称 strict 改善。
2. **独立样本资本类未 auto-tag**：重叠公司 600061 国投资本在 independent YAML 仍为 `financial: false`。
3. **BrowserUser 扩展未启动**。
4. **`strict_audit_result` loader 未实现**。

---

## 6. 下一步计划

1. **strict 审计重跑**（eval1000_v2 + independent plausible 单元格）。
2. **BrowserUser 规划/试点**。
3. **补 `strict_audit_result` loader**；考虑 `sample_universe` 增加「资本」关键词。

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

outputs/generalization/eval1000_independent_20260623/  # 独立 cohort（2026-06-23）
  eval_summary.md
  independent_comparison.md
  eval_results.json
  <code>/company_profile.json

outputs/generalization/eval1000_v2/       # 同 cohort 重跑（2026-06-22）
  eval_summary.md
  eval1000_v2_comparison.md               # vs baseline 对比报告
  eval_results.json
  <code>/company_profile.json

outputs/db/
  listed_companies_v1.db                  # eval1000_v2 导入（10428 行，gitignored）

outputs/validation/
  recent_changes_cached_validation.md
```

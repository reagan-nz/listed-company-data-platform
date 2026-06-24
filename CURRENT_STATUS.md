# 当前状态

_最后更新：2026-06-24（full_market_2024 + scoped rnd_investment refresh + strict 审计重跑）_

> **本文档是项目主进度页。** 老师建议从这里开始阅读；技术细节见 [docs/](docs/)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。

**2026-06-24 日结（rnd refresh）**：scoped rnd_investment 刷新完成（cached PDF，非 CNINFO 重跑）；rnd found **67.9% → 93.7%**（5,269/5,621）；BSE rnd **22.8% → 99.2%**；非金融 proxy **10.61/11**；strict usable **9.38/11**；BSE strict **8.71/11**；15 个 found→not_found/partial 回归待 follow-up。详见 [rnd_refresh_summary.md](outputs/generalization/full_market_2024/rnd_refresh_summary.md)。

**2026-06-24 日结（full_market）**：full_market_2024 全 A 股 2024 年报提取完成（6124 家 universe）；5707 ok / 417 no_announcement / 0 error；SQLite **62,890** 行。

**2026-06-23 日结**：独立 cohort 1000 家 eval 完成；918 ok / 0 error / 82 no_announcement；非金融 proxy **10.30/11**，泛化验证 **PASS**。

---

## 1. 当前目标

搭建中国上市公司**基础但完整的数据库**。

- **当前数据来源**：巨潮资讯网（CNINFO）公开年报 PDF，程序化抽取 11 项基础字段（工业/制造类公司为主）。
- **已完成**：全 A 股 2024 年报首次全量提取 + SQLite 入库 + 混合 strict 审计。
- **后续扩展（尚未实现）**：
  - 多年度扩展（2023 / 2022 年报）；
  - 金融公司字段质量专项 review；
  - **BrowserUser** 爬虫智能体（全量基线稳定后，非当前直接下一步）。

当前阶段：**可维护的数据平台原型已覆盖全 A 股 2024 基线**（见第 3 节）。

---

## 2. 已完成工作

| 类别 | 内容 |
|---|---|
| **full_market_2024 全量提取** | 6124 家 universe；5707 ok；5 board 批次 + merge + SQLite 导入 — 见 [full_market_2024_summary.md](outputs/generalization/full_market_2024/full_market_2024_summary.md) |
| **full_market_2024 scoped rnd refresh** | rnd_investment 仅字段重抽取（cached PDF）；+1,460 not_found→found — 见 [rnd_refresh_summary.md](outputs/generalization/full_market_2024/rnd_refresh_summary.md) |
| **full_market_2024 混合 strict 审计** | 5621 非金融 × 11 字段；post-rnd strict **9.38/11** — 见 [strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md) |
| **工具链** | `make_full_market_yaml.py`、`merge_full_market_batches.py`、`strict_audit_full_market.py`、`refresh_rnd_full_market.py`、`run_full_market_2024.sh` |
| **Independent eval1000** | 新 cohort 1000 家；泛化验证 PASS |
| **eval1000_v2** | 同 cohort 1020 家全量重跑 |
| **SQLite 原型** | 四表 v1 schema；eval1000 / v2 / independent / full_market_2024 均已导入 |
| **金融子 schema** | bank/broker/insurer/other_financial 实现（Issue #4） |
| **更早** | eval1000 受控评估 + strict 审计（10.16/11 baseline）；eval200；4 公司泛化 |

---

## 3. 当前阶段性成果

```
CNINFO 全 A 股列表 (6124)
    ↓  lab/make_full_market_yaml.py
lab/eval_companies_full_market_2024.yaml
    ↓  lab/eval_generalize.py × 5 board batches
outputs/generalization/full_market_2024/{bse,star,...}/
    ↓  lab/merge_full_market_batches.py
eval_results.json + root symlinks
    ↓  lab/db_import.py (run_name=full_market_2024)
SQLite（62,890 extracted_field 行）
    ↓  lab/refresh_rnd_full_market.py（scoped rnd only, cached PDF）
rnd found 67.9% → 93.7%；merge + strict audit 重跑
    ↓  lab/strict_audit_full_market.py
strict_audit_summary.md（9.38/11 非金融 strict usable）
```

- **可复现**：universe YAML、batch 脚本、审计脚本均已版本化。
- **可审计**：每个字段保留 `page`、`evidence_sentence`、`source_url`。
- **可导入**：四表 relational schema；full_market_2024 已入库。
- **已审计（混合）**：自动化 adversarial 全 population + 小样本 PDF 校准；**非全量人工验证**。

---

## 4. 当前关键数字

**Headline 来自 full_market_2024**（2026-06-24）。指标含义见第 4.1 节。

### full_market_2024 最终结果

| 指标 | 数值 |
|---|---|
| **total**（universe 总数） | **6124** |
| **ok**（成功抽取） | **5707**（93.2%） |
| no_announcement | 417（6.8%） |
| error | **0** |
| 非金融 ok | 5621 |
| 金融 ok | 86 |
| **非金融 proxy plausible** | **10.61 / 11**（post-rnd refresh） |
| **非金融 strict usable**（自动化 adversarial） | **9.38 / 11** |
| strict lenient（usable + partial） | 10.73 / 11 |
| rnd_investment found | **5,269 / 5,621（93.7%）** |

### 与受控评估对比（非金融 proxy）

| run | 样本 | ok | proxy |
|---|---:|---:|---:|
| eval1000_v2 | 1020 | 947 | 10.33/11 |
| independent eval1000 | 1000 | 918 | 10.30/11 |
| **full_market_2024** | **6124** | **5707** | **10.61/11** |

> proxy 在全市场规模上与 v2/independent 一致，说明管道规模泛化良好。

### strict 审计（full_market_2024，非金融）

| 指标 | 数值 |
|---|---|
| 自动化 recheck 范围 | 5621 家 × 11 字段 = **61,831** cells |
| strict usable（usable only） | **9.38 / 11** |
| strict lenient（usable + partial） | **10.73 / 11** |
| rnd strict usable（field-level） | **5,078 / 5,621** |
| 样本 CSV | 55 家 × 7 字段 = 476 rows |
| 手动 PDF deep-read | 15 家 = 105 rows |
| 手动 vs 自动化一致率 | 46/105（44%） |

**板块 strict usable（非金融，mean /11）**：

| board | 中文 | strict usable |
|---|---|---:|
| bse | 北交所 | **8.71** |
| sse_main | 沪市主板 | **9.25** |
| szse_main | 深市主板 | 9.41 |
| star | 科创板 | **9.56** |
| chinext | 创业板 | 9.65 |

> **不得声称 strict 优于旧 baseline 10.16/11**：旧数字来自 eval1000（proxy 10.5/11，规则更松）。post-rnd strict **9.38/11** 是 scoped refresh 后的自动化 adversarial 估计，**非 62,890 行全量人工验证**。

### SQLite

| run_name | extracted_field | evaluation_result |
|---|---:|---:|
| `full_market_2024` | 62,890 | 62,890 |
| `full_market_2024_rnd_refresh`（post-rnd） | 62,890 | 62,890 |

| 表 | 行数 | 说明 |
|---|---:|---|
| company_basic | 6124 | 公司数 |
| report_source | 6124 | 公司数 |
| extracted_field | **62,890** | **公司-字段记录数**，非公司数 |

---

## 4.1 指标解释

| 术语 | 含义 |
|---|---|
| **total** | full_market_2024 universe 中的 A 股公司总数（6124）。 |
| **ok** | 脚本成功找到 2024 年报公告/PDF、下载/访问、解析并写出 `company_profile.json`。**不等于每个字段都完全正确。** |
| **no_announcement** | 在 CNINFO 当前查询规则下未找到可用 2024 年报公告/PDF。不一定是代码 bug（可能是未披露、退市、查询窗口等）。 |
| **error** | 网络/下载/解析等技术失败。full_market_2024 最终为 0（688267 中触媒经重试恢复）。 |
| **proxy plausible** | 抽取评估时的自动 plausibility 分数：字段在结构上看起来合理（如 snippet 够长、表格有数据行）。**不等于人工确认正确。** |
| **strict usable** | 更严格的 adversarial 审计标签（usable only）。post-rnd refresh 后 **9.38/11**。比 proxy 更保守。 |
| **strict lenient** | usable + partial 的上界估计（10.73/11）。 |
| **manual PDF deep-read** | 对 15 家公司读取 PDF 页文本，检查 evidence 是否支撑字段、`not_found` 是否可能为 missed。非全量人工验证。 |
| **非金融 headline** | 11 字段 headline 仅统计 `financial: false` 的工业类公司；金融公司使用独立子 schema，**不混入** 11 字段 headline。 |
| **SQLite 行数** | `extracted_field` / `evaluation_result` 行数 = **公司 × 字段** 记录数，不是公司数。6124 公司约产生 62890 条字段记录。 |

**板块名称对照**：

| 代码 | 中文 |
|---|---|
| bse | 北交所 |
| star | 科创板 |
| szse_main | 深市主板 |
| chinext | 创业板 |
| sse_main | 沪市主板 |

---

## 5. 已知问题

1. **BSE strict 已改善**（8.71/11，post-rnd）；客户/供应商表格 strict 规则已修正（P0 TOP_KW）。
2. **rnd 8 家回归**（sse_main 费用化研发投入 锚点）：600011 等 7 家 + 301221 partial — 小 follow-up。
3. **revenue 表格 page-boundary 问题**：evidence 不在 cited page 上（表格切片/跨页）。
4. **金融字段质量未 strict 审计**：86 家 ok；数值字段可能有噪声。
5. **BrowserUser 未启动**（计划中，非当前优先级）。

---

## 6. 下一步计划

1. **质量 follow-up**：revenue 表格跨页切片；rnd 8 家回归；金融 review。
2. **金融公司专项 review**（qualitative + 子 schema plausible 规则）。
3. **多年度扩展**（2023 / 2022 年报）。
4. **BrowserUser 试点**（PDF 无法覆盖的数据；全量基线稳定后）。
5. **`strict_audit_result` loader** 入库（低优先级）。

---

## 7. 如何查看进度

| 入口 | 用途 |
|---|---|
| **本文档** | 主进度页 — 含指标解释 |
| **[ROADMAP.md](ROADMAP.md)** | 分阶段路线图 |
| **[CHANGELOG.md](CHANGELOG.md)** | 变更记录 |
| **[docs/evaluation_method.md](docs/evaluation_method.md)** | 评估方法与术语 glossary |
| **[full_market_2024_summary.md](outputs/generalization/full_market_2024/full_market_2024_summary.md)** | 全市场 run 详细报告 |
| **[strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md)** | strict 审计详细报告 |

---

## 附录：关键产物路径

```
outputs/generalization/full_market_2024/
  eval_summary.md                         # 可 commit
  full_market_2024_summary.md             # 可 commit
  rnd_refresh_summary.md                  # 可 commit
  strict_audit_summary.md                 # 可 commit
  strict_audit_sample.csv                 # 可 commit
  eval_results.json                       # gitignored
  rnd_refresh_changes.csv                 # gitignored
  bse/ star/ szse_main/ chinext/ sse_main/  # gitignored（含 PDF）

outputs/generalization/eval1000_v2/         # 保留
outputs/generalization/eval1000_independent_20260623/  # 保留

outputs/db/listed_companies_v1.db         # gitignored；含 full_market_2024 批次
```

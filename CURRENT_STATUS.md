# 当前状态

_最后更新：2026-06-25（#30 financial follow-up docs sync）_

> **本文档是项目主进度页。** 老师建议从这里开始阅读；技术细节见 [docs/](docs/)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。Stage 3a 汇总见 **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)**。

**2026-06-25 日结（#30 financial follow-up 完结待关单）**：`#30a–#30g` 已完成并完成文档同步；涵盖 broker `not_found_missed` 收紧、ratio/table audit calibration、bank ratio helper、broker recall、financial table plausibility、insurer low-n audit hardening、subtype/tag diagnosis。**#30 ready to close after docs commit**；金融 wider rollout 仍 **deferred**。详见 [financial_audit_fix_30_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md)。

**2026-06-25 日结（Stage 3a 收尾 #28）**：full_market_2024 **Stage 3a quality follow-up PASS** — 汇总 #24–#27（BSE audit rule、rnd/revenue scoped refresh、金融 audit 框架）；非金融 strict **9.43/11**（latest `run_name=full_market_2024_revenue_refresh`）；金融 **单独 headline**，worksheet grading 待办。**非**全量人工验证；**非** extraction 全部修复。Stage **3b**（residuals、grading、多年度）进行中。详见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)。

**2026-06-25 日结（金融 audit #30d）**：broker 收入 / 两融 recall sample-only apply **PASS**；4/4 confirmed MISSED（`601878` 投行 / 资管 / 融出资金，`600030` 投行净收入）→ strict `usable`；23/23 ABSENT-OK 控制保持非 usable；broker population `usable` **+4**、`not_found_missed` **-4**；joined agreement **233/325→229/325**（MISSED→usable 口径下降，非新回归）。详见 [financial_audit_fix_30d_apply_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30d_apply_summary.md)。

**2026-06-25 日结（金融 audit #30b）**：ratio/table 语义拒绝 + `major_subsidiaries` out-of-region usable 门控；joined agreement **226/325→233/325 (69.5%→71.7%)**；broker missed 与 #30a 相同（sample 4 / pop 7）。详见 [financial_audit_fix_30b_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30b_summary.md)。

**2026-06-25 日结（金融 audit #30a）**：收紧 broker `not_found_missed` PDF 规则；joined agreement **202/325→226/325 (62%→69.5%)**；详见 [financial_audit_fix_30a_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30a_summary.md)。

**2026-06-25 日结（金融 audit #27/#29）**：金融字段质量 **audit 框架**完成（Phase 0–1B）；325/325 校准 grading 完成（#29 baseline agreement 62%）；86 ok 金融公司 × 1,059 cells 自动化 financial strict audit。详见 [financial_calibration_report.md](outputs/generalization/full_market_2024/financial_calibration_report.md)、[financial_audit_fix_30a_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30a_summary.md)。

**2026-06-24 日结（revenue refresh #26）**：scoped `revenue_by_region` / `revenue_by_segment` 刷新完成（cached PDF，非 CNINFO 重跑）；Tier 3 跨页 continuation stitch 为主驱动（343/346）；wrong→usable **297**；0 回归；region wrong **258→38**；segment wrong **109→19**；非金融 strict **9.38→9.43/11**；proxy **10.61→10.67/11**。详见 [revenue_refresh_summary.md](outputs/generalization/full_market_2024/revenue_refresh_summary.md)。

**2026-06-24 日结（rnd refresh + P2.1）**：scoped rnd_investment 刷新完成（cached PDF，非 CNINFO 重跑）；P2.1 candidate-fallback 修复 15 个回归；rnd found **67.9% → 94.2%**（5,297/5,621）；BSE rnd **22.8% → 99.2%**。详见 [rnd_refresh_summary.md](outputs/generalization/full_market_2024/rnd_refresh_summary.md)。

**2026-06-24 日结（full_market）**：full_market_2024 全 A 股 2024 年报提取完成（6124 家 universe）；5707 ok / 417 no_announcement / 0 error；SQLite **62,890** 行。

**2026-06-23 日结**：独立 cohort 1000 家 eval 完成；918 ok / 0 error / 82 no_announcement；非金融 proxy **10.30/11**，泛化验证 **PASS**。

---

## 1. 当前目标

搭建中国上市公司**基础但完整的数据库**。

- **当前数据来源**：巨潮资讯网（CNINFO）公开年报 PDF，程序化抽取 11 项基础字段（工业/制造类公司为主）。
- **已完成**：全 A 股 2024 年报首次全量提取 + SQLite 入库 + 混合 strict 审计 + scoped rnd/revenue 字段刷新。
- **Stage 3a（Done）**：#24–#28 质量 follow-up — 见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)。
- **Stage 3b（进行中）**：`#30` ready to close；后续聚焦 `#31` 金融漏标扫描、`#32` revenue/rnd residuals、`#33` 多年份扩展决策。
- **#30（Done / docs closeout）**：`#30a`、`#30b`、`#30c`、`#30d`、`#30e`、`#30f`、`#30g` 均已完成；`#30` 在 docs commit 后可关闭。
- **BrowserUser** 爬虫智能体（全量基线稳定后，非当前直接下一步）。

当前阶段：**full_market_2024 2024 基线 + Stage 3a 质量 follow-up 已 PASS**； residuals 见 §5–§6（见第 3 节）。

---

## 2. 已完成工作

| 类别 | 内容 |
|---|---|
| **full_market_2024 全量提取** | 6124 家 universe；5707 ok；5 board 批次 + merge + SQLite 导入 — 见 [full_market_2024_summary.md](outputs/generalization/full_market_2024/full_market_2024_summary.md) |
| **full_market_2024 scoped rnd refresh** | rnd_investment 仅字段重抽取（cached PDF）；+1,460 not_found→found — 见 [rnd_refresh_summary.md](outputs/generalization/full_market_2024/rnd_refresh_summary.md) |
| **full_market_2024 scoped revenue refresh (#26)** | revenue_by_region/segment 仅字段重抽取（cached PDF）；wrong→usable 297；stitch 343 — 见 [revenue_refresh_summary.md](outputs/generalization/full_market_2024/revenue_refresh_summary.md) |
| **full_market_2024 混合 strict 审计** | 5621 非金融 × 11 字段；post-revenue strict **9.43/11** — 见 [strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md) |
| **full_market_2024 金融 audit（#27 + #30）** | 86 ok × 子 schema；`#30a–#30g` follow-up 已完成（audit-only + extraction helper + diagnosis-only）；金融 wider rollout 仍 deferred — 见 [financial_audit_fix_30_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md) |
| **Stage 3a 质量 follow-up 汇总（#28）** | #24–#27 合并快照 + closure — 见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) |
| **工具链** | `make_full_market_yaml.py`、`merge_full_market_batches.py`、`strict_audit_full_market.py`、`strict_audit_financial_full_market.py`、`financial_calibration_sample.py`、`refresh_rnd_full_market.py`、`refresh_revenue_full_market.py`、`run_full_market_2024.sh` |
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
rnd found 67.9% → 94.2%（P2.1 candidate-fallback）；merge + strict audit 重跑
    ↓  lab/refresh_revenue_full_market.py（scoped revenue only, cached PDF, #26）
revenue wrong→usable 297（Tier 3 stitch 343）；merge + strict audit 重跑
    ↓  lab/strict_audit_full_market.py
strict_audit_summary.md（9.43/11 非金融 strict usable）
    ↓  lab/strict_audit_financial_full_market.py（#27，金融 only）
financial_audit_summary.md（bank 9.00/13、broker 7.66/12 等；不混入 non-fin headline）
    ↓  lab/financial_calibration_sample.py（#27 Phase 1B）
financial_audit_sample.csv（30 公司 × 325 cells；manual_grade 待填写）
```

- **可复现**：universe YAML、batch 脚本、审计脚本均已版本化。
- **可审计**：每个字段保留 `page`、`evidence_sentence`、`source_url`。
- **可导入**：四表 relational schema；full_market_2024 已入库。
- **已审计（混合）**：自动化 adversarial 全 population + 小样本 PDF 校准；**非全量人工验证**。

---

## 4. 当前关键数字

**Headline 来自 full_market_2024**（2026-06-24，post rnd + revenue refresh）。指标含义见第 4.1 节。

### full_market_2024 最终结果

| 指标 | 数值 |
|---|---|
| **total**（universe 总数） | **6124** |
| **ok**（成功抽取） | **5707**（93.2%） |
| no_announcement | 417（6.8%） |
| error | **0** |
| 非金融 ok | 5621 |
| 金融 ok | 86 |
| **非金融 proxy plausible** | **10.67 / 11**（post-revenue refresh） |
| **非金融 strict usable**（自动化 adversarial） | **9.43 / 11** |
| strict lenient（usable + partial） | **10.80 / 11** |
| rnd_investment found | **5,297 / 5,621（94.2%）** |
| revenue_by_region strict wrong | **38**（was 258 pre-#26） |
| revenue_by_segment strict wrong | **19**（was 109 pre-#26） |

### 与受控评估对比（非金融 proxy）

| run | 样本 | ok | proxy |
|---|---:|---:|---:|
| eval1000_v2 | 1020 | 947 | 10.33/11 |
| independent eval1000 | 1000 | 918 | 10.30/11 |
| **full_market_2024** | **6124** | **5707** | **10.67/11** |

> proxy 在全市场规模上与 v2/independent 一致，说明管道规模泛化良好。

### strict 审计（full_market_2024，非金融）

| 指标 | 数值 |
|---|---|
| 自动化 recheck 范围 | 5621 家 × 11 字段 = **61,831** cells |
| strict usable（usable only） | **9.43 / 11** |
| strict lenient（usable + partial） | **10.80 / 11** |
| population wrong（all fields） | **566**（was 876 pre-#26） |
| rnd strict usable（field-level） | **5,086 / 5,621** |
| 样本 CSV | 55 家 × 7 字段 = 490 rows |
| 手动 PDF deep-read | 15 家 = 105 rows |
| 手动 vs 自动化一致率 | 45/105（43%） |

**板块 strict usable（非金融，mean /11）**：

| board | 中文 | strict usable |
|---|---|---:|
| bse | 北交所 | **8.82** |
| sse_main | 沪市主板 | **9.35** |
| szse_main | 深市主板 | 9.43 |
| star | 科创板 | **9.61** |
| chinext | 创业板 | 9.67 |

> **不得声称 strict 优于旧 baseline 10.16/11**：旧数字来自 eval1000（proxy 10.5/11，规则更松）。post-revenue strict **9.43/11** 是 scoped refresh 后的自动化 adversarial 估计，**非 62,890 行全量人工验证**。**金融 strict 见 §4.2，不得与此 headline 混报。**

### 金融 strict 审计（#27，86 ok，单独 headline）

| 指标 | 数值 |
|---|---|
| YAML `financial: true` | **87**（86 ok；1 no_announcement：000562） |
| 审计 field-cells | **1,059** |
| bank / broker / insurer / other | **43 / 37 / 2 / 4** |
| **bank strict usable** | **9.00 / 13**（lenient 11.28/13；proxy 8.98/13） |
| **broker strict usable** | **7.66 / 12**（lenient 9.00/12；proxy 8.57/12） |
| **insurer strict usable** | **9.25 / 12**（lenient 10.50/12） |
| **other_financial strict usable** | **5.75 / 8**（lenient 7.00/8） |
| 校准 worksheet | **30 公司 × 325 cells**（`manual_grade` **待填写**） |

> **#27 = audit 框架 + automated review + worksheet**；非 extraction 修复；非全量人工验证。`not_found_missed`（75 cells，**broker-heavy ~58/75**）为 **recall hint 非确认 truth**，待 worksheet manual grade。`major_subsidiaries` 0/86 usable 为 **结构性 partial**（industrial in_region 门控），非金融抽取专项失败。**insurer n=2**，subtype 均值勿过度解读。**financial under-tagging scan** deferred **Stage 3b**。Subtype caveats：000402 / 600816 / 600318。

### SQLite

| run_name | extracted_field | evaluation_result |
|---|---:|---:|
| `full_market_2024` | 62,890 | 62,890 |
| `full_market_2024_rnd_refresh` | 62,890 | 62,890 |
| `full_market_2024_revenue_refresh`（post-#26） | 62,890 | 62,890 |

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
| **strict usable** | 更严格的 adversarial 审计标签（usable only）。post-revenue refresh 后 **9.43/11**。比 proxy 更保守。 |
| **strict lenient** | usable + partial 的上界估计（10.80/11）。 |
| **manual PDF deep-read** | 对 15 家公司读取 PDF 页文本，检查 evidence 是否支撑字段、`not_found` 是否可能为 missed。非全量人工验证。 |
| **非金融 headline** | 11 字段 headline 仅统计 `financial: false` 的工业类公司；金融公司使用独立子 schema，**不混入** 11 字段 headline（9.43/11）。 |
| **金融 strict headline** | 按 bank/broker/insurer/other 子 schema 单独报告（#27）；**不得**与 non-fin 9.43/11 混报。 |
| **financial not_found_missed** | 自动化 PDF anchor **recall hint**（75 cells，**broker-heavy**）；**非确认 truth**，须 worksheet 人工 grade。 |
| **major_subsidiaries（金融 audit）** | 0/86 usable 为 industrial-style 门控导致的 **结构性 partial**；勿过度解读为金融抽取专项失败。 |
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

1. **BSE strict**（8.82/11，post-revenue）；客户/供应商表格 strict 规则已修正（P0 TOP_KW）。
2. **rnd 8 家回归**（sse_main 费用化研发投入 锚点）：600011 等 7 家 + 301221 partial — 小 follow-up。
3. **revenue 剩余 strict-wrong**：region **38** + segment **19**（#26 已修复 header-only 跨页 split；非 fully fixed）。
4. **金融 residuals 仍存在，但 #30 tranche 已完成**：金融 audit / extraction / subtype review 已在 `#30a–#30g` 完成并单独文档化；wider rollout deferred；000402 / 600816 / 600318 retagging 进入后续 issue。
5. **BrowserUser 未启动**（计划中，非当前优先级）。

---

## 6. 下一步计划（Stage 3b）

1. **#31 Financial under-tagging scan / 金融公司漏标扫描** — 含 `000402` / `600816` / `600318` retagging follow-up（需单独审批，非本轮自动改 YAML）。
2. **#32 Revenue + rnd residual fixes / 收入与研发字段残留问题** — revenue 剩余 strict-wrong + rnd 小范围残留回归。
3. **#33 Multiyear expansion decision / 多年份扩展决策** — 2025 / 2023 / 2022 范围与 `run_name` 策略。
4. **BrowserUser 试点**（全量基线稳定后）；**`strict_audit_result` loader**（低优先级）。

---

## 7. 如何查看进度

| 入口 | 用途 |
|---|---|
| **本文档** | 主进度页 — 含指标解释 |
| **[ROADMAP.md](ROADMAP.md)** | 分阶段路线图 |
| **[CHANGELOG.md](CHANGELOG.md)** | 变更记录 |
| **[docs/evaluation_method.md](docs/evaluation_method.md)** | 评估方法与术语 glossary |
| **[full_market_2024_summary.md](outputs/generalization/full_market_2024/full_market_2024_summary.md)** | 全市场 run 详细报告 |
| **[revenue_refresh_summary.md](outputs/generalization/full_market_2024/revenue_refresh_summary.md)** | #26 revenue scoped refresh 报告 |
| **[financial_audit_summary.md](outputs/generalization/full_market_2024/financial_audit_summary.md)** | #27 金融 strict audit（单独 headline） |
| **[strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md)** | 非金融 strict 审计详细报告 |
| **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)** | Stage 3a 汇总与 closure（#28） |

---

## 附录：关键产物路径

```
outputs/generalization/full_market_2024/
  eval_summary.md                         # 可 commit
  full_market_2024_summary.md             # 可 commit
  rnd_refresh_summary.md                  # 可 commit
  revenue_refresh_summary.md              # 可 commit
  strict_audit_summary.md                 # 可 commit（non-fin）
  financial_audit_summary.md              # 可 commit（#27 金融，单独 headline）
  financial_audit_population.csv          # 可 commit
  financial_audit_sample.csv              # 可 commit（grading 进行中可更新）
  financial_population_inventory.csv      # 可 commit
  stage3_quality_followup_summary.md      # 可 commit（#28 Stage 3a）
  strict_audit_sample.csv                 # 可 commit
  eval_results.json                       # gitignored
  rnd_refresh_changes.csv                 # gitignored
  revenue_refresh_changes.csv             # gitignored
  bse/ star/ szse_main/ chinext/ sse_main/  # gitignored（含 PDF）

outputs/generalization/eval1000_v2/         # 保留
outputs/generalization/eval1000_independent_20260623/  # 保留

outputs/db/listed_companies_v1.db         # gitignored；含 full_market_2024 批次
```

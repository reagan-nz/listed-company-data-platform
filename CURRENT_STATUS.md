# 当前状态

_最后更新：2026-06-26（#33 多年份扩展决策备忘录）_

> **本文档是项目主进度页，建议老师 / 评审从这里开始。** 技术细节见 [docs/](docs/)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。Stage 3a（第 3a 阶段）汇总见 **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)**。

---

## 当前项目阶段（一览）

| 项目 | 状态 |
|---|---|
| **数据底座** | 已完成 `full_market_2024`（2024 全市场运行）：6124 家公司 universe（评估全集），5707 家 ok（成功抽取），SQLite（轻量数据库）入库 62,890 行字段记录 |
| **质量闭环 Stage 3a** | **通过（PASS）** — #24–#28 质量 follow-up（质量跟进）已完成；详见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) |
| **Stage 3b / 父 issue #23** | **可以关单** — #30 / #32 / #33 当前范围均已关闭；下一步为 2025 年 `pilot`（试点）实施（待人工签核） |
| **产品形态** | **数据底座 + 质量审计**，非完整 RAG（检索增强生成）/ LLM Wiki（大模型辅助知识页）产品 |

---

## 当前核心指标

**非金融 cohort（非金融公司分组）headline（核心指标/对外口径）**（`run_name`（运行名称）=`full_market_2024_revenue_refresh`，2026-06-24 后）：

- **strict usable（严格审计下可用）**：**9.43 / 11** — 5621 家非金融 ok 公司 × 11 个工业字段；11 表示每家公司平均检查的目标字段数，9.43 表示 strict audit（严格质量审计）下平均可用字段数。
- **proxy plausible（自动合理性分数）**：**10.67 / 11**
- **rnd_investment（研发投入字段）found（找到）率**：5,297 / 5,621（94.2%）
- **revenue_by_region / revenue_by_segment（分地区/分业务收入字段）strict wrong（严格审计下错误）**：38 / 19

**金融 cohort（金融公司分组）**：单独 headline（核心指标/对外口径），如 bank（银行）strict usable（严格审计下可用）**9.00 / 13**、broker（券商）**7.66 / 12**；**不得**与非金融 9.43/11 混报。详见 §4.2。

> **#32c scoped apply（小范围定向应用）未更新全局 9.43/11 headline（核心指标/对外口径）。** 仅 104 家 P0 池本地 profile（公司档案）有更新；全局指标需 intentional full strict audit rerun（有意安排的全量 strict audit（严格质量审计）重跑）后才变更。

---

## 能达到的标准 / 不能宣称的内容

### 当前可以说

- 已完成 **2024 年 A 股年报结构化数据底座**的第一阶段质量闭环（Stage 3a 通过）。
- 系统可以**批量抽取**年报字段、**记录来源证据**（页码 / 证据句 / URL）、运行 **strict audit（严格质量审计）**，并支持 **scoped refresh（小范围定向刷新）** / **scoped apply（小范围定向应用）** 做定向修复。
- 数据可支撑**内部分析、字段查询、公司 profile（公司档案）、RAG prototype（检索增强问答原型）** 的底层数据层。
- 非金融 strict usable（严格审计下可用）**9.43/11** 与金融指标**分开报告**。

### 当前不能说

- **不是** full manual validation（全量人工验证）— 62,890 行 SQLite 字段记录未逐条人工核对。
- **不是**完整 RAG（检索增强生成）/ LLM Wiki（大模型辅助知识页）**产品**。
- **不是**所有字段都已完全修复 — revenue strict wrong（严格审计下收入错误）仍有 57 个 field-cell（字段单元格）待后续试点；R&D partial（研发部分可用）仍有残留。
- **不能**将金融 cohort（金融公司分组）指标混入 non-fin headline（非金融核心指标/对外口径）9.43/11。
- **不能**声称 #32c scoped apply（小范围定向应用）已更新全局 9.43/11 headline（核心指标/对外口径）。
- **不能**将 9.43/11 与 eval1000 baseline（基线）10.16/11 直接比较为「改善」— 规则、样本规模不同。

---

## 术语说明

| 术语 | 含义 |
|---|---|
| **strict audit（严格质量审计）** | 对已存字段值做 adversarial（对抗式）规则复核，标签含 `usable`（可用）、`partial`（部分可用）、`wrong`（错误）等。 |
| **strict usable（严格审计下可用）** | strict audit（严格质量审计）中仅计 `usable`（可用）的字段均值。 |
| **proxy plausible（自动合理性分数）** | 抽取时的结构合理性估计，通常高于 strict usable（严格审计下可用）。 |
| **scoped refresh（小范围定向刷新）** | 用已缓存 PDF 仅重抽部分字段，非 CNINFO 全量重下。 |
| **scoped apply（小范围定向应用）** | 经验证的修复小范围写回 `company_profile.json`（公司档案 JSON）。 |
| **headline（核心指标/对外口径）** | 对外主质量数字；非金融与金融**分开**。 |
| **run_name（运行名称）** | 运行标识，如 `full_market_2024`（2024 全市场运行）。 |
| **cohort（分组样本）** | 按规则选出的公司集合。 |
| **pilot（试点）** | 小规模试跑后再扩全市场。 |
| **backfill（历史年份回填）** | 补跑 2023/2022 等历史年报。 |
| **not_found_missed（应该找到但没有找到）** | PDF 中应有披露但抽取为 not_found（未找到）。 |
| **not_found_unverified（未找到且尚未确认是否应存在）** | 未找到且 strict audit（严格质量审计）尚未确认是否应存在。 |
| **dry-run（只读试跑/诊断）** | 不写回 profile（公司档案），仅评估修复效果。 |
| **RAG（检索增强生成）** | 先检索再让大模型回答；本项目提供底层数据，非完整产品。 |
| **LLM Wiki（大模型辅助知识页）** | 大模型辅助生成的知识页；本项目尚未交付。 |
| **CNINFO** | 巨潮资讯网，法定信息披露来源。 |
| **SQLite** | 轻量数据库，存放字段级抽取与评估结果。 |

详细指标解释见 §4.1；评估方法见 [docs/evaluation_method.md](docs/evaluation_method.md)。

---

## 近期日结摘要

**2026-06-26（#33 多年份决策 + #23 可以关单）**：`#33` 决策备忘录已完成 — **2025 优先**、按年重建 universe（评估全集）、分阶段 rollout（推广）：100 家 `pilot`（试点）→ 单板块 `pilot`（试点）→ 全市场 2025 → `backfill`（历史年份回填）2023/2022；**不**覆盖 2024 产出；**不**立即全量 CNINFO。**#23**（#24–#33）当前范围**可以关单**。下一执行：**2025 pilot（试点）**（待 §12 人工签核 + 年份参数化脚本）。详见 [multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md)。

**2026-06-26（#32 关闭）**：`#32` 当前范围已关闭：已完成收入与研发残留盘点、`#32c` 研发字段 P0 小范围 `scoped apply`（小范围定向应用）与后验验证、`#32b` 收入 strict wrong（严格审计下错误）只读 `dry-run`（诊断）分类。**#32c**：104 家 / 32 更新 / 0 errors（错误）/ 后验 **PASS（通过）**。**#32b**：57/57 wrong（错误）已分类，harness（试跑框架）改善 17，生产 apply **暂缓**。**non-fin（非金融）9.43/11 headline（核心指标/对外口径）不变**。详见 [revenue_rnd_fix_32_final_summary.md](outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md)。

**2026-06-26（#32c 研发 P0 scoped apply 已验证）**：`#32c-R2`–`R5` 完成 — guarded R&D situation-table helper（带防护的研发情况表解析辅助函数）已入生产路径；`scoped apply`（小范围定向应用）**104** 家、**32** 更新、**0** errors（错误）、**14** not_found→found（未找到→找到）、**0** found→not_found（找到→未找到）；post-apply verification（应用后验证）**PASS（通过）**。Scoped 池 strict（严格审计）分布：**usable（可用）=32 / partial（部分可用）=71 / not_found_unverified（未找到且未确认）=1**。**非**全市场 R&D rollout（推广）；**非** global strict audit（严格质量审计）重跑；non-fin（非金融）**9.43/11 headline（核心指标/对外口径）不变**。详见 [rnd_residual_fix_32c_apply_summary.md](outputs/generalization/full_market_2024/rnd_residual_fix_32c_apply_summary.md)、[rnd_residual_fix_32c_post_apply_verify.md](outputs/generalization/full_market_2024/rnd_residual_fix_32c_post_apply_verify.md)。

**2026-06-25（#30 金融 follow-up 完结）**：`#30a–#30g` 已完成；涵盖 broker（券商）`not_found_missed`（应该找到但没有找到）收紧、ratio/table audit calibration（比率/表格审计校准）、bank ratio helper（银行比率解析辅助）、broker recall（券商召回修复）等。**#30 可以关单**；金融 wider rollout（更大范围推广）仍**暂缓**。详见 [financial_audit_fix_30_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md)。

**2026-06-25（Stage 3a 收尾 #28）**：`full_market_2024`（2024 全市场运行）**Stage 3a quality follow-up（质量跟进）PASS（通过）**；非金融 strict usable（严格审计下可用）**9.43/11**（`run_name`（运行名称）=`full_market_2024_revenue_refresh`）；金融**单独 headline（核心指标/对外口径）**。**非**全量人工验证。详见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)。

_更早日结见 CHANGELOG.md 与 stage3 汇总文档。_

---

## 1. 当前目标

搭建中国上市公司**基础但完整的数据库**。

- **当前数据来源**：巨潮资讯网（CNINFO）公开年报 PDF，程序化抽取 11 项基础字段（工业/制造类公司为主）。
- **已完成**：全 A 股 2024 年报首次全量提取 + SQLite 入库 + 混合 strict 审计 + scoped rnd/revenue 字段刷新。
- **Stage 3a（已完成）**：#24–#28 质量 follow-up（质量跟进）— 见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)。
- **Stage 3b / #23（可以关单）**：`#30` / `#32` / `#33` 当前范围已关闭；下一执行：**2025 pilot（试点）**（人工签核后）；并行待办：#31、revenue Tier4（收入第四层修复）。
- **#33（已完成 / 决策备忘录）**：多年份扩展策略已文档化 — 2025 优先、分阶段 rollout（推广）；见 [multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md)。
- **#32c（已完成 / 仅 P0 小范围）**：guarded R&D situation-table extraction（带防护的研发情况表抽取）+ `scoped apply`（小范围定向应用）（104 targets（目标公司）, 32 updated（更新）, 0 errors（错误））+ post-apply verification（应用后验证）PASS（通过）；**非** full R&D rollout（全市场研发推广）。
- **BrowserUser（浏览器智能体）**：全量基线稳定后的爬虫智能体，**非**当前直接下一步。

当前阶段：**`full_market_2024`（2024 全市场运行）基线 + Stage 3a 质量 follow-up（质量跟进）已通过**；残留问题见 §5–§6。

---

## 2. 已完成工作

| 类别 | 内容 |
|---|---|
| **full_market_2024 全量提取** | 6124 家 universe；5707 ok；5 board 批次 + merge + SQLite 导入 — 见 [full_market_2024_summary.md](outputs/generalization/full_market_2024/full_market_2024_summary.md) |
| **#32 revenue + R&D residual（已关闭）** | 盘点 + #32c `scoped apply`（小范围定向应用）已验证 + #32b revenue `dry-run`（只读诊断）— 见 [revenue_rnd_fix_32_final_summary.md](outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md) |
| **#33 multiyear expansion decision（已关闭）** | 2025 优先、分阶段 rollout（推广）决策备忘录 — 见 [multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md) |
| **full_market_2024 scoped rnd refresh** | `rnd_investment`（研发投入字段）仅字段重抽取（cached PDF（已缓存 PDF））；+1,460 not_found→found（未找到→找到）— 见 [rnd_refresh_summary.md](outputs/generalization/full_market_2024/rnd_refresh_summary.md) |
| **full_market_2024 scoped revenue refresh (#26)** | `revenue_by_region` / `revenue_by_segment`（分地区/分业务收入字段）仅字段重抽取；wrong→usable（错误→可用）297 — 见 [revenue_refresh_summary.md](outputs/generalization/full_market_2024/revenue_refresh_summary.md) |
| **full_market_2024 混合 strict audit（严格质量审计）** | 5621 非金融 × 11 字段；post-revenue strict usable（严格审计下可用）**9.43/11** — 见 [strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md) |
| **full_market_2024 金融 audit（#27 + #30）** | 86 ok × 子 schema（字段体系）；`#30a–#30g` follow-up（跟进）已完成；金融 wider rollout（更大范围推广）仍**暂缓** — 见 [financial_audit_fix_30_summary.md](outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md) |
| **Stage 3a 质量 follow-up 汇总（#28）** | #24–#27 合并快照 + closure（关单）— 见 [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) |
| **工具链** | `make_full_market_yaml.py`、`merge_full_market_batches.py`、`strict_audit_full_market.py`、`strict_audit_financial_full_market.py`、`financial_calibration_sample.py`、`refresh_rnd_full_market.py`、`refresh_revenue_full_market.py`、`run_full_market_2024.sh` |
| **Independent eval1000** | 新 cohort（分组样本）1000 家；泛化验证 **PASS（通过）** |
| **eval1000_v2** | 同 cohort（分组样本）1020 家全量重跑 |
| **SQLite 原型** | 四表 v1 schema（字段体系）；eval1000 / v2 / independent / `full_market_2024`（2024 全市场运行）均已导入 |
| **金融子 schema（字段体系）** | bank/broker/insurer/other_financial 实现（Issue #4） |
| **更早** | eval1000 受控评估 + strict audit（严格质量审计）（10.16/11 baseline（基线））；eval200；4 公司泛化 |

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

**Headline（核心指标/对外口径）来自 full_market_2024（2024 全市场运行）**（2026-06-24，post rnd + revenue refresh（研发与收入刷新后））。指标含义见 §4.1。

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

1. **BSE strict usable（严格审计下可用）**（8.82/11，post-revenue（收入刷新后））；客户/供应商表格 strict audit（严格质量审计）规则已修正（P0 TOP_KW）。
2. **rnd P0 scoped apply（#32c，已关闭）**：104 家 / 32 strict（严格审计）改善；72/104 仍 partial（部分可用）— **暂缓**；`000333`/`301221` narrative（累计叙述类）**暂缓**。
3. **revenue strict wrong（#32b 已分类，生产暂缓）**：region（分地区）**38** + segment（分业务）**19** — Tier4 / wrong-table ranking（错表排序）待 scoped pilot（小范围试点）。
4. **金融 residuals（残留问题）仍存在，但 #30 批次已完成**：金融 audit（审计）/ extraction（抽取）/ subtype review（子类型复核）已在 `#30a–#30g` 完成；wider rollout（更大范围推广）**暂缓**；000402 / 600816 / 600318 retagging（重打标签）进入 #31。

5. **BrowserUser（浏览器智能体）未启动**（计划中，非当前优先级）。

---

## 6. 下一步计划（post-#23）

1. **2025 pilot（试点）实施** — 100 家分层 pilot（试点）→ BSE board pilot（板块试点）→ `full_market_2025`（2025 全市场运行）（**待** #33 §12 人工签核 + 年份参数化脚本）。
2. **#31 金融漏标扫描 / retag review（重打标签复核）** — 含 `000402` / `600816` / `600318` 及 8 个 financial-like revenue wrong（金融控股类收入 strict wrong（严格审计下错误））；建议于 2025 pilot（试点）前或并行完成。
3. **Revenue Tier4 + wrong-table ranking pilot（试点）** — `#32b` harness（试跑框架）信号验证通过后，经人工签核再做 scoped production pilot（小范围生产试点）。
4. **R&D remaining partial（研发部分可用残留）** — 72/104 P0 + full-population partial（全人口部分可用）；`000333`/`301221` manual review（人工复核）。
5. **2023/2022 backfill（历史年份回填）** — 仅在 `full_market_2025`（2025 全市场运行）通过 validation gates（验证关卡）后启动。
6. **BrowserUser（浏览器智能体）试点**（全量基线稳定后）；**`strict_audit_result` loader**（低优先级）。

> **Headline（核心指标/对外口径）政策**：non-fin（非金融）**9.43/11** 保持不变，直至 intentional full strict audit rerun（有意安排的全量 strict audit（严格质量审计）重跑）。

---

## 7. 如何查看进度

| 入口 | 用途 |
|---|---|
| **本文档** | 主进度页 — 含术语与指标解释 |
| **[ROADMAP.md](ROADMAP.md)** | 分阶段路线图 |
| **[CHANGELOG.md](CHANGELOG.md)** | 变更记录 |
| **[docs/evaluation_method.md](docs/evaluation_method.md)** | 评估方法与术语表 |
| **[full_market_2024_summary.md](outputs/generalization/full_market_2024/full_market_2024_summary.md)** | `full_market_2024`（2024 全市场运行）详细报告 |
| **[revenue_refresh_summary.md](outputs/generalization/full_market_2024/revenue_refresh_summary.md)** | #26 revenue scoped refresh（小范围定向收入刷新）报告 |
| **[financial_audit_summary.md](outputs/generalization/full_market_2024/financial_audit_summary.md)** | #27 金融 strict audit（严格质量审计）（单独 headline（核心指标/对外口径）） |
| **[strict_audit_summary.md](outputs/generalization/full_market_2024/strict_audit_summary.md)** | 非金融 strict audit（严格质量审计）详细报告 |
| **[rnd_residual_fix_32c_apply_summary.md](outputs/generalization/full_market_2024/rnd_residual_fix_32c_apply_summary.md)** | #32c-R4 scoped P0 R&D apply（小范围 P0 研发应用）报告 |
| **[multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md)** | #33 多年份扩展决策备忘录 |
| **[revenue_rnd_fix_32_final_summary.md](outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md)** | #32 收入与研发残留关单汇总 |
| **[revenue_residual_fix_32b_dryrun_summary.md](outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_summary.md)** | #32b revenue dry-run（收入只读诊断） |
| **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)** | Stage 3a 汇总与关单（#28） |

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
  rnd_residual_fix_32c_apply_summary.md  # 可 commit（#32c-R4 apply）
  rnd_residual_fix_32c_post_apply_verify.md  # 可 commit（#32c-R5 verify）
  revenue_rnd_fix_32_final_summary.md     # 可 commit（#32 closure）
  multiyear_expansion_decision_33.md      # 可 commit（#33 decision）
  revenue_residual_fix_32b_dryrun_summary.md  # 可 commit（#32b）
  strict_audit_sample.csv                 # 可 commit
  eval_results.json                       # gitignored
  rnd_refresh_changes.csv                 # gitignored
  rnd_refresh_changes_32c_apply.csv     # gitignored（apply 产物，除非明确批准）
  revenue_refresh_changes.csv             # gitignored
  bse/ star/ szse_main/ chinext/ sse_main/  # gitignored（含 PDF）

outputs/generalization/eval1000_v2/         # 保留
outputs/generalization/eval1000_independent_20260623/  # 保留

outputs/db/listed_companies_v1.db         # gitignored；含 full_market_2024 批次
```

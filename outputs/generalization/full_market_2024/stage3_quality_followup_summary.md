# full_market_2024（2024 全市场运行）Stage 3a 质量 follow-up（质量跟进）汇总

_生成日期：2026-06-25 | Issue #28 — Stage 3a 关单文档_

## 1. 范围与完成声明

本文档汇总 **full_market_2024（2024 全市场运行）2024 年报基线**的 **Stage 3a quality follow-up（质量跟进）**（#24–#28）。

**范围内（已完成）：**

- #24 BSE strict audit-rule（严格审计规则）修正（TOP_KW）
- #25 `rnd_investment`（研发投入字段）extraction（抽取）修复 + scoped cached-PDF refresh（小范围已缓存 PDF 刷新）
- #26 revenue page-boundary extraction（收入跨页抽取）修复 + scoped cached-PDF refresh（小范围已缓存 PDF 刷新）
- #27 financial-only audit（金融专用审计）框架（inventory（盘点）+ automated strict（自动化严格审计）+ calibration worksheet（校准表））
- #28 本汇总与文档同步

**范围外（明确未做）：**

- Full CNINFO re-download（全量 CNINFO 重下）或 full-field re-extraction（全字段重抽）
- Full manual validation（全量人工验证）62,890 行 SQLite（轻量数据库）记录
- Financial extraction/tag sign-off（金融抽取/标签签核）（worksheet grading（人工打分）待完成）
- Multiyear expansion（多年份扩展）（2025 / 2023 / 2022）
- 将金融指标混入 non-financial（非金融）9.43/11 headline（核心指标/对外口径）

**方法口径：** automated strict audit（自动化 strict audit（严格质量审计））+ **targeted scoped refresh（小范围定向刷新）over cached PDFs（已缓存 PDF）** + sampled / manual calibration（抽样/人工校准）**支持** — **非** population-wide human review（全人口人工复核）。

**关单决定：** **full_market_2024 Stage 3a quality follow-up（质量跟进）PASS（通过）。** Residual issues（残留问题）已文档化并暂缓；**不**阻塞基线关单。**Full Stage 3（完整第 3 阶段）**（ROADMAP（路线图））仍对 residuals（残留）、financial grading（金融人工打分）、multiyear planning（多年份规划）（Stage 3b）开放。

---

## 2. 最终 non-fin（非金融）质量快照

最新 SQLite（轻量数据库）`run_name`（运行名称）：**`full_market_2024_revenue_refresh`**

| 指标 | 数值 |
|---|---:|
| Universe total（评估全集总数） | 6,124 |
| ok（成功抽取） | 5,707 |
| no_announcement（未找到公告） | 417 |
| error（错误） | **0** |
| Non-fin ok companies（非金融成功公司） | **5,621** |
| Audit population（审计人口） | 5,621 × 11 = **61,831 cells（字段单元格）** |
| **Proxy plausible（自动合理性分数）** | **10.67 / 11** |
| **Strict usable（严格审计下可用）** | **9.43 / 11** |
| **Strict lenient（严格审计宽松口径）** | **10.80 / 11** |
| All-field strict **wrong（严格审计下错误）** | **566**（#26 前 876） |
| `rnd_investment`（研发投入字段）**found（找到）** | **5,297 / 5,621 (94.2%)** |
| rnd strict usable（field-level）（字段级严格可用） | **5,086 / 5,621** |
| `revenue_by_region`（分地区收入字段）strict **wrong（错误）** | **38**（#26 前 258） |
| `revenue_by_segment`（分业务收入字段）strict **wrong（错误）** | **19**（#26 前 109） |
| SQLite evaluation_result rows（评估结果行） | **62,890** |

**Board strict usable（板块严格审计下可用）（non-fin（非金融），post-revenue（收入刷新后））：**

| board（板块） | strict usable（严格审计下可用）/ 11 |
|---|---:|
| bse（北交所） | **8.82** |
| sse_main（沪市主板） | **9.35** |
| szse_main（深市主板） | **9.43** |
| star（科创板） | **9.61** |
| chinext（创业板） | **9.67** |

**Calibration support（校准支持）（non-fin（非金融））：** 55 companies × 7 targeted fields（定向字段）（sample CSV（样本 CSV））；15-company PDF deep-read（PDF 深度阅读）（105 cells（字段单元格））。Manual vs automated agreement（人工 vs 自动一致率）：45/105（43%）。**非** full manual validation（全量人工验证）。

详情：[strict_audit_summary.md](strict_audit_summary.md)

---

## 3. 金融 audit（审计）快照（单独 headline（核心指标/对外口径））

**不得**混入 non-fin（非金融）9.43/11。

| Metric | Value |
|---|---:|
| YAML `financial: true` | **87** tagged / **86 ok** (000562 no_announcement) |
| Subtypes | bank **43** / broker **37** / insurer **2** / other **4** |
| Automated audit cells | **1,059** |
| **bank strict usable** | **9.00 / 13** |
| **broker strict usable** | **7.66 / 12** |
| **insurer strict usable** | **9.25 / 12** (n=2 — illustrative only) |
| **other_financial strict usable** | **5.75 / 8** |
| Calibration worksheet | **30 companies × 325 cells** — **`manual_grade` pending** |
| Population labels | usable 557 / partial 310 / wrong 81 / not_found_missed 75 / not_found_unverified 36 |

**#27 状态：** audit（审计）**框架已完成** — **非** financial extraction（金融抽取）签核。Worksheet（校准表）已生成；grading（人工打分）未完成。

详情：[financial_audit_summary.md](financial_audit_summary.md)

---

## 4. Strict（严格审计）指标轨迹（仅 full_market_2024（2024 全市场运行）内）

同一 universe（评估全集）内、初始 hybrid audit（混合审计）后的演化：

| 步骤 | 触发 | Non-fin strict usable（非金融严格审计下可用） | 说明 |
|---|---|---:|---|
| Initial audit（初始审计） | Post–full_market merge（全市场合并后） | **9.01 / 11** | Automated adversarial（自动化对抗式复核）+ 15-co PDF sample（15 家 PDF 样本） |
| #24 | BSE TOP_KW audit rule（审计规则） | **9.06 / 11** | 仅 audit-rule（审计规则）；BSE **7.14 → 7.71** |
| #25 | rnd scoped refresh（小范围定向刷新） | **9.38 / 11** | Extraction（抽取）+ cached-PDF refresh；BSE **7.71 → 8.71** |
| #26 | revenue scoped refresh（小范围定向刷新） | **9.43 / 11** | Extraction（抽取）+ cached-PDF refresh；BSE **8.71 → 8.82** |

```
9.01  →  9.06  →  9.38  →  9.43
 ^         ^         ^         ^
initial   #24       #25       #26
```

> 此轨迹描述**同一 full_market_2024（2024 全市场运行）universe（评估全集）上** scoped audit/refresh（小范围审计/刷新）演化。**不得**将 9.43/11 与 eval1000 strict（严格审计）**10.16/11** 比较为「改善」— proxy（自动合理性）规则、audit（审计）范围、universe（评估全集）规模均不同。

---

## 5. #24–#27 changelog

### #24 — BSE strict audit-rule correction

- **Change:** Expanded `TOP_KW` in `lab/strict_audit_full_market.py` for BSE customer/supplier table column headers (`年度销售占比`, `年度采购占比`, etc.).
- **Type:** Audit-rule correction only — **no extraction change**.
- **Effect:** BSE strict **7.14 → 7.71**; overall strict **9.01 → 9.06**.
- **Artifact:** [bse_quality_followup.md](bse_quality_followup.md)

### #25 — rnd_investment scoped refresh

- **Change:** BSE 研发支出 anchors + summary-total priority; P2.1 candidate-fallback in extractors; scoped rnd refresh over cached PDFs.
- **Type:** Extraction fix + scoped cached-PDF refresh.
- **Effect:** rnd found **67.9% → 94.2%**; BSE rnd **22.8% → 99.2%**; strict **9.06 → 9.38**; proxy **10.35 → 10.61/11**.
- **Artifact:** [rnd_refresh_summary.md](rnd_refresh_summary.md) | SQLite `run_name=full_market_2024_rnd_refresh`

### #26 — revenue page-boundary scoped refresh

- **Change:** Tier 3 continuation stitch + Tier 2 stacked trim; scoped revenue refresh (`revenue_by_region`, `revenue_by_segment`) over cached PDFs.
- **Type:** Extraction fix + scoped cached-PDF refresh.
- **Effect:** wrong→usable **297**; usable regressions **0**; region wrong **258 → 38**; segment wrong **109 → 19**; strict **9.38 → 9.43**; all-field wrong **876 → 566**.
- **Artifact:** [revenue_refresh_summary.md](revenue_refresh_summary.md) | SQLite `run_name=full_market_2024_revenue_refresh`

### #27 — financial audit framework

- **Change:** Population inventory; automated financial strict audit; 30-company calibration worksheet (`seed=20260627`).
- **Type:** Audit framework + documentation — **not extraction repair**.
- **Effect:** 1,059 cells audited separately; worksheet **325 cells** with blank `manual_grade`.
- **Artifact:** [financial_audit_summary.md](financial_audit_summary.md)

---

## 6. Fix taxonomy

| Issue | Audit-rule correction | Extraction fix | Scoped cached-PDF refresh | Audit framework / docs |
|---|---:|---:|---:|---:|
| #24 | **Yes** | — | — | — |
| #25 | — | **Yes** | **Yes** (rnd only) | — |
| #26 | — | **Yes** | **Yes** (revenue fields) | — |
| #27 | Partial (financial strict rules) | — | — | **Yes** |
| #28 | — | — | — | **Yes** (this summary) |

**Global constraint:** All field refreshes were **targeted scoped refreshes over cached PDFs** — not full CNINFO reruns.

---

## 7. Calibration and validation posture

| Layer | Non-fin | Financial |
|---|---|---|
| Population automated strict | 5,621 × 11 = 61,831 cells | 86 ok × sub-schema = 1,059 cells |
| Sampled support | 55 co × 7 fld CSV; 15 co PDF deep-read (105 cells) | 30 co × 325 cells worksheet |
| Manual grades | Deep-read labels only (not full worksheet) | **`manual_grade` blank — pending** |
| Claim allowed | Automated strict estimate + calibration **support** | Separate automated strict; grading **pending** |
| Claim **not** allowed | Full manual validation of 62,890 rows | Financial quality signed off |

Hybrid method matches [strict_audit_summary.md](strict_audit_summary.md) §1. Financial worksheet grades (`CORRECT | PARTIAL | WRONG | MISSED | ABSENT-OK`) will refine broker `not_found_missed` interpretation after manual review.

---

## 8. Remaining issues

| ID | Issue | Scope | Severity | Deferred to |
|---|---|---|---|---|
| R1 | Revenue strict-wrong residual | region **38** + segment **19** ≈ **57 cells** | Medium | Follow-up: scoped extraction/audit |
| R2 | rnd residual regressions | ~**8 companies** (sse_main 费用化研发投入; e.g. 600011 + 301221 partial) | Low | Small scoped fix |
| R3 | BSE board gap | **8.82/11** vs chinext 9.67 | Medium | Monitor / optional board follow-up |
| R4 | risk_factors strict-wrong | **221 cells** (top false-positive field) | Medium | Audit or extraction triage |
| R5 | major_subsidiaries (non-fin) | **0 usable / 5549 partial** — structural | Low | Audit behavior; do not overread |
| R6 | Financial manual grading | **325 cells**, `manual_grade` blank | **High** | Manual calibration grading |
| R7 | Broker `not_found_missed` | **~58/75** recall hints — **not confirmed truth** | Medium | Refine after manual grade |
| R8 | Financial subtype caveats | **000402 / 600816 / 600318** stored schema | Medium | Tag review |
| R9 | Financial under-tagging | YAML completeness not scanned | Medium | Under-tagging scan |
| R10 | Financial numeric/table noise | broker proxy−strict gap **7.5%** | Medium | Financial plausible rules |
| R11 | Insurer low-n | **n=2** insurers | Info | Expand tagging before trusting means |
| R12 | major_subsidiaries (financial) | **0/86 usable** — industrial in_region gate | Low | Structural partial; not extraction regression |

Revenue extraction is **not fully fixed**. Financial audit framework is complete; **extraction is not signed off**.

---

## 9. Follow-up backlog (post–Stage 3a)

| Priority | Topic | Notes |
|---|---|---|
| 1 | **Financial manual calibration grading** | Fill `financial_audit_sample.csv` → `--score` |
| 2 | **Broker `not_found_missed` refinement** | After grading; tighten audit rules |
| 4 | **rnd residual regressions** | ~~#32c scoped P0 apply verified~~ — 72/104 P0 pool still partial; full R&D rollout deferred |
| 3 | **Remaining revenue strict-wrong** | ~57 cells; scoped cached-PDF refresh only (#32b Tier 4) |
| 5 | **Financial under-tagging scan** | YAML `financial: true` completeness |
| 6 | **Financial extraction/tag fixes** | Numeric plausible, subtype tags (000402 etc.) |
| 7 | **2025 / 2023 / 2022 expansion decision** | Scope, batch strategy, run naming — **no default full CNINFO rerun** |

Optional lower priority: `strict_audit_result` DB loader; BrowserUser pilot (ROADMAP Phase 4).

---

## 10. Stage 3a 关单决定

**结论：full_market_2024 Stage 3a quality follow-up（质量跟进）PASS（通过）。**

**不得声称：**

- Full Stage 3（完整第 3 阶段）已完成
- 全部 extraction（抽取）问题已修复
- Full manual validation（全量人工验证）
- 金融指标 merged（合并）入 non-fin headline（非金融核心指标/对外口径）

**ROADMAP（路线图）：** Stage **3a** 已完成（#24–#28）；Stage **3b** 进行中。

---

## 11. Artifact index

| Artifact | Issue | Description |
|---|---|---|
| [bse_quality_followup.md](bse_quality_followup.md) | #24 | BSE TOP_KW audit-rule before/after |
| [rnd_refresh_summary.md](rnd_refresh_summary.md) | #25 | rnd scoped refresh metrics |
| [revenue_refresh_summary.md](revenue_refresh_summary.md) | #26 | revenue scoped refresh metrics |
| [strict_audit_summary.md](strict_audit_summary.md) | baseline + post-refresh | Non-fin hybrid strict audit |
| [strict_audit_sample.csv](strict_audit_sample.csv) | baseline | 55 co × 7 fld sample |
| [financial_audit_summary.md](financial_audit_summary.md) | #27 | Financial automated strict |
| [financial_audit_population.csv](financial_audit_population.csv) | #27 | 1,059 audit rows |
| [financial_audit_sample.csv](financial_audit_sample.csv) | #27 | 30 co worksheet (grading pending) |
| [financial_population_inventory.csv](financial_population_inventory.csv) | #27 | 87 tagged inventory |
| [full_market_2024_summary.md](full_market_2024_summary.md) | Stage 2 | Full extraction run report |
| **This file** | #28 | Stage 3a consolidation + closure |

Cross-links: [CURRENT_STATUS.md](../../CURRENT_STATUS.md) | [ROADMAP.md](../../ROADMAP.md) | [docs/evaluation_method.md](../../docs/evaluation_method.md)

Stage 3b financial follow-up continued in `#30`; see [financial_audit_fix_30_summary.md](financial_audit_fix_30_summary.md).

**#32c 更新（2026-06-26）：** Scoped P0 R&D apply（小范围 P0 研发定向应用）verification（验证）已完成 — 104 targets（目标公司），32 profile（公司档案）更新，post-apply verify（应用后验证）PASS（通过）；global non-fin headline（全局非金融核心指标/对外口径）**9.43/11 不变**。见 [rnd_residual_fix_32c_post_apply_verify.md](rnd_residual_fix_32c_post_apply_verify.md)。

**#32 关单（2026-06-26）：** #32 当前范围完成（inventory（盘点）+ #32c + #32b dry-run（只读诊断））；revenue production fix（收入生产修复）暂缓；non-fin headline（非金融核心指标/对外口径）**9.43/11 不变**。见 [revenue_rnd_fix_32_final_summary.md](revenue_rnd_fix_32_final_summary.md)。

**#33 决策（2026-06-26）：** Multiyear expansion（多年份扩展）策略已文档化 — 2025 优先、staged rollout（分阶段推广）；parent #23 **可以关单**。见 [multiyear_expansion_decision_33.md](multiyear_expansion_decision_33.md)。

---

## 12. 不得声称清单（anti-claims checklist）

| 声称 | 是否允许 |
|---|---|
| Stage 3a quality follow-up（质量跟进）PASS（通过） | **是** |
| Full Stage 3 / ROADMAP Phase 3 全部完成 | **否** |
| Non-fin strict（非金融严格审计）**9.43/11** 作为最新 headline（核心指标/对外口径） | **是** — 与金融分开 |
| 将金融指标混入 9.43/11 | **否** |
| 9.43/11 相对 eval1000 **10.16/11** 为「改善」 | **否** |
| 62,890 行 full manual validation（全量人工验证） | **否** |
| 全部 extraction（抽取）/ 全部字段已修复 | **否** |
| Financial extraction（金融抽取）已签核 | **否** |
| Automated strict（自动化严格审计）+ scoped refresh（小范围定向刷新）+ calibration support（校准支持） | **是** |

---

## 13. Safe-to-commit and do-not-touch guidance

### Safe to commit (explicit paths)

**Stage 3a summary + doc sync (#28):**

```
outputs/generalization/full_market_2024/stage3_quality_followup_summary.md
CURRENT_STATUS.md
CHANGELOG.md
ROADMAP.md
docs/evaluation_method.md
README.md
```

**Prior Stage 3 artifacts (if not yet committed — use explicit `git add`):**

```
outputs/generalization/full_market_2024/bse_quality_followup.md
outputs/generalization/full_market_2024/rnd_refresh_summary.md
outputs/generalization/full_market_2024/revenue_refresh_summary.md
outputs/generalization/full_market_2024/strict_audit_summary.md
outputs/generalization/full_market_2024/strict_audit_sample.csv
outputs/generalization/full_market_2024/financial_audit_summary.md
outputs/generalization/full_market_2024/financial_audit_population.csv
outputs/generalization/full_market_2024/financial_audit_sample.csv
outputs/generalization/full_market_2024/financial_population_inventory.csv
lab/strict_audit_financial_full_market.py
lab/financial_calibration_sample.py
docs/financial_company_schema.md
```

Use `git add <paths>` — not `git add -A`.

### Do not commit / do not modify in doc-only tasks

| Category | Paths |
|---|---|
| Runtime JSON | `eval_results.json`, `company_profile.json`, batch subdirs `[0-9]*/` |
| PDFs / cache | `*.pdf`, `.cache/` |
| SQLite | `outputs/db/*.db` |
| Refresh deltas | `rnd_refresh_changes.csv`, `revenue_refresh_changes.csv`, `revenue_refresh_changes_targeted.csv`, overnight reports |
| Logs / backups | `*.log`, backups |
| Generated batch YAML | `lab/batch_*_2024.yaml` |

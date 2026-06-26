# 金融 audit（审计）修复 #30 汇总

_生成日期：2026-06-25 | 文档汇总 #30a–#30g_

## 范围与边界

本文档汇总 **#30 金融 follow-up（跟进）系列**：

- `#30a` broker（券商）`not_found_missed`（应该找到但没有找到）audit（审计）收紧
- `#30b` ratio/table audit calibration（比率/表格审计校准）+ `major_subsidiaries`（主要子公司字段）门控
- `#30c` bank ratio extraction helper（银行比率抽取辅助）
- `#30d` broker income / margin recall（券商收入/两融召回）
- `#30e` financial table plausibility audit hardening（金融表格合理性审计加固）
- `#30f` insurer（保险）low-n audit hardening（小样本审计加固）
- `#30g` subtype/tag diagnosis only（子类型/标签仅诊断）

**边界 / 不得声称（anti-claims）：**

- **无** full financial rollout（全量金融推广）
- **无** full CNINFO rerun（全量 CNINFO 重下）
- **无** SQLite（轻量数据库）import（导入）
- **无** YAML tag changes（标签变更）
- **无** non-fin（非金融）`9.43/11 headline（核心指标/对外口径）` 变更
- 金融 extraction（抽取）**尚未** fully signed off（完全签核）
- 金融指标仍**单独**于 non-financial headline（非金融核心指标/对外口径）

## #30a–#30g 变更记录

| 步骤 | 主题 | 类型 | 主要结果 | 推广状态 |
|---|---|---|---|---|
| `#30a` | broker（券商）`not_found_missed`（应该找到但没有找到）收紧 | audit-only（仅审计） | 减少 broker 过度召回；冻结 agreement（一致率）`202/325 -> 226/325` | 已提交代码 |
| `#30b` | ratio/table calibration（比率/表格校准）+ `major_subsidiaries`（主要子公司字段）门控 | audit-only（仅审计） | joined agreement（合并一致率）`226/325 -> 233/325` | 已提交代码 |
| `#30c` | bank ratio helper（银行比率辅助） | extraction（抽取）+ targeted sample apply（定向样本应用） | `6/6` bank-ratio `MISSED`（漏抽）恢复；`0/11` WRONG（错误）对照变为 usable（可用） | wider rollout（更大范围推广）**暂缓** |
| `#30d` | broker income / margin recall（券商收入/两融召回） | extraction（抽取）+ targeted sample apply（定向样本应用） | `4/4` 已确认 broker `MISSED`（漏抽）恢复；`0/23` negative controls（负向对照）变为 usable（可用） | wider rollout（更大范围推广）**暂缓** |
| `#30e` | table plausibility hardening（表格合理性加固） | audit-only（仅审计） | `18/18` manual-WRONG（人工标错）表格目标 strict wrong（严格审计下错误）；harness（试跑框架）产物已清理 | 无 sample apply（样本应用） |
| `#30f` | insurer（保险）low-n semantic hardening（小样本语义加固） | audit-only（仅审计） | `8/8` insurer 负向目标 non-usable（不可用）；`10/10` 正向对照保持 | 无 sample apply（样本应用） |
| `#30g` | subtype/tag review（子类型/标签复核） | diagnosis-only（仅诊断） | 复核 `000402` / `600816` / `600318`；无 YAML 变更 | **暂缓** |

## 按类别变更说明

### audit-only（仅审计）修复

- `#30a`：broker（券商）专用 `not_found_missed`（应该找到但没有找到）PDF 门控，减少 false recall hints（误召回提示）。
- `#30b`：收紧 ratio（比率）语义、table（表格）语义，改善 `major_subsidiaries`（主要子公司字段）处理。
- `#30e`：收紧 `loan_structure`（贷款结构）、`deposit_structure`（存款结构）、`regional_distribution`（地区分布）、`revenue_by_region`（分地区收入）、`revenue_by_segment`（分业务收入）的金融 table plausibility（表格合理性）。
- `#30f`：为 `combined_ratio`（综合成本率）、`claims_expense`（赔付支出）、`investment_income`（投资收益）、`solvency_ratio`（偿付能力）等增加 insurer-only（仅保险）语义防护。

### extraction helpers（抽取辅助）

- `#30c`：bank-only（仅银行）ratio extraction helper（比率抽取辅助），针对定向 ratio recall failures（比率召回失败）。
- `#30d`：broker-only（仅券商）辅助：分部收入抽取、投行附注深度回退、两融余额抽取。

### diagnosis-only（仅诊断）子类型复核

- `#30g`：只读 subtype/tag review（子类型/标签复核）：
  - `000402` 金融街：可能不是 broker（券商）；可能根本不是 financial（金融）
  - `600816` 建元信托：trust-like（信托类），不是 bank（银行）
  - `600318` 新力金融：多元金融控股，不是 bank（银行）
- `#30g` **未**变更 YAML 或 schema tags（标签）。

## 验证汇总

| 步骤 | 验证结果 |
|---|---|
| `#30a` | broker（券商）`not_found_missed`（应该找到但没有找到）减少；冻结 joined agreement（合并一致率）`202/325 -> 226/325` |
| `#30b` | joined agreement（合并一致率）`226/325 -> 233/325` |
| `#30c` | `6/6` bank-ratio `MISSED`（漏抽）恢复；`0/11` WRONG（错误）对照变为 usable（可用）；wider rollout（更大范围推广）**暂缓** |
| `#30d` | `4/4` broker `MISSED`（漏抽）恢复；`0/23` negative controls（负向对照）usable（可用）；wider rollout（更大范围推广）**暂缓** |
| `#30e` | `18/18` manual-WRONG（人工标错）表格目标 strict wrong（严格审计下错误）；harness（试跑框架）清理后 `0/26` 对照新降级 |
| `#30f` | `8/8` insurer（保险）负向 non-usable（不可用）；`10/10` 正向对照保持 |
| `#30g` | 仅 subtype（子类型）诊断；无 YAML 变更 |

## 指标注意事项

`#30` 以冻结的 `#29` manual calibration（人工校准）样本作为 validation anchor（验证锚点）。

因此 **agreement（一致率）可能在 extraction（抽取）改善时反而下降**：

- 若某行人工标为 `MISSED`（漏抽）
- 而新 extraction（抽取）正确恢复为 `usable`（可用）
- 冻结的人工 vs 自动 agreement（一致率）会下降（人工列仍为 `MISSED`（漏抽））

`#30c`、`#30d` 的 sample apply（样本应用）中曾出现此情况。应读作 **frozen-label metric caveat（冻结标签指标注意事项）**，**不**应自动视为 regression（回归）。

## 暂缓工作路由至后续 issue

| Issue | 主题 | 路由工作 |
|---|---|---|
| `#31` | Financial under-tagging scan（金融漏标扫描） | under-tagging scan（漏标扫描）；`000402` / `600816` / `600318` 受控 retagging（重打标签） |
| `#32` | Revenue + rnd residual fixes（收入与研发残留修复） | residual revenue/rnd wrong cells（残留 wrong（错误）单元格）与 scoped fixes（小范围修复） |
| `#33` | Multiyear expansion decision（多年份扩展决策） | 2025 / 2023 / 2022 范围、`run_name`（运行名称）与扩展口径 |

若后续批准 subtype retagging（子类型重打标签），应跟踪在 **`#31`** 或其子任务下。

## 关单口径

`#30` **可以关单**，作为 **financial follow-up tranche（金融 follow-up（跟进）批次）**，明确口径如下：

- audit hardening（审计加固）已交付
- 低风险的 targeted extraction helpers（定向抽取辅助）已交付并验证
- subtype/tag caveats（子类型/标签注意事项）已诊断但**未**自动变更
- wider financial rollout（更大范围金融推广）仍**暂缓**

## 可提交（safe-to-commit）列表

- `outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md`
- `CURRENT_STATUS.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `docs/financial_company_schema.md`
- `docs/evaluation_method.md`
- `outputs/generalization/full_market_2024/stage3_quality_followup_summary.md`（仅交叉链接）

## 勿提交（do-not-commit）列表

- 任何 `company_profile.json`（公司档案 JSON）
- 任何 `eval_results.json`
- `financial_audit_sample.csv`
- `financial_audit_population.csv`
- `financial_audit_summary.md`
- 任何 YAML tag changes（标签变更）
- PDFs / `.cache`
- `outputs/db/*.db`

## 相关产物

- [financial_audit_fix_30a_summary.md](financial_audit_fix_30a_summary.md)
- [financial_audit_fix_30b_summary.md](financial_audit_fix_30b_summary.md)
- [financial_audit_fix_30c_apply_summary.md](financial_audit_fix_30c_apply_summary.md)
- [financial_audit_fix_30d_apply_summary.md](financial_audit_fix_30d_apply_summary.md)
- [financial_audit_fix_30e_dryrun_summary.md](financial_audit_fix_30e_dryrun_summary.md)
- [financial_audit_fix_30f_dryrun_summary.md](financial_audit_fix_30f_dryrun_summary.md)
- [financial_subtype_review_30g.md](financial_subtype_review_30g.md)

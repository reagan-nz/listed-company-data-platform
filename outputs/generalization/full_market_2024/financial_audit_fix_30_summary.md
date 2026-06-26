# 金融严格质量审计修复 #30 汇总

_生成日期：2026-06-25 | 文档汇总 #30a–#30g_

**术语说明：** strict audit = 严格质量审计；scoped apply = 小范围写回；dry-run = 只读诊断；headline = 核心指标。

---

## 范围与边界

本文档汇总 **#30 金融跟进系列**：

- `#30a` broker `not_found_missed` 审计收紧
- `#30b` 比率/表格审计校准 + `major_subsidiaries` 门控
- `#30c` 银行比率抽取辅助
- `#30d` 券商收入/两融召回
- `#30e` 金融表格合理性审计加固
- `#30f` 保险小样本审计加固
- `#30g` 子类型/标签仅诊断

**边界 / 不得声称：**

- **无**全量金融推广
- **无**全量 CNINFO 重下
- **无** SQLite 导入
- **无** YAML 标签变更
- **无**非金融 `9.43/11` 核心指标变更
- 金融抽取**尚未**完全签核
- 金融指标仍**单独**于非金融核心指标

---

## #30a–#30g 变更记录

| 步骤 | 主题 | 类型 | 主要结果 | 推广状态 |
|---|---|---|---|---|
| `#30a` | broker `not_found_missed` 收紧 | 仅审计 | 减少 broker 过度召回；冻结一致率 `202/325 -> 226/325` | 已提交代码 |
| `#30b` | 比率/表格校准 + `major_subsidiaries` 门控 | 仅审计 | 合并一致率 `226/325 -> 233/325` | 已提交代码 |
| `#30c` | 银行比率辅助 | 抽取 + 定向样本写回 | `6/6` bank-ratio `MISSED` 恢复；`0/11` WRONG 对照变为 usable | 更大范围推广**暂缓** |
| `#30d` | 券商收入/两融召回 | 抽取 + 定向样本写回 | `4/4` 已确认 broker `MISSED` 恢复；`0/23` 负向对照变为 usable | 更大范围推广**暂缓** |
| `#30e` | 表格合理性加固 | 仅审计 | `18/18` 人工标错表格目标 strict wrong；试跑框架产物已清理 | 无样本写回 |
| `#30f` | 保险小样本语义加固 | 仅审计 | `8/8` 保险负向目标 non-usable；`10/10` 正向对照保持 | 无样本写回 |
| `#30g` | 子类型/标签复核 | 仅诊断 | 复核 `000402` / `600816` / `600318`；无 YAML 变更 | **暂缓** |

---

## 按类别变更说明

### 仅审计修复

- `#30a`：broker 专用 `not_found_missed` PDF 门控，减少误召回提示。
- `#30b`：收紧比率语义、表格语义，改善 `major_subsidiaries` 处理。
- `#30e`：收紧 `loan_structure`、`deposit_structure`、`regional_distribution`、`revenue_by_region`、`revenue_by_segment` 的金融表格合理性。
- `#30f`：为 `combined_ratio`、`claims_expense`、`investment_income`、`solvency_ratio` 等增加仅保险语义防护。

### 抽取辅助

- `#30c`：仅银行比率抽取辅助，针对定向比率召回失败。
- `#30d`：仅券商辅助：分部收入抽取、投行附注深度回退、两融余额抽取。

### 仅诊断子类型复核

- `#30g`：只读子类型/标签复核：
  - `000402` 金融街：可能不是 broker；可能根本不是 financial
  - `600816` 建元信托：信托类，不是 bank
  - `600318` 新力金融：多元金融控股，不是 bank
- `#30g` **未**变更 YAML 或 schema 标签。

---

## 验证汇总

| 步骤 | 验证结果 |
|---|---|
| `#30a` | broker `not_found_missed` 减少；冻结合并一致率 `202/325 -> 226/325` |
| `#30b` | 合并一致率 `226/325 -> 233/325` |
| `#30c` | `6/6` bank-ratio `MISSED` 恢复；`0/11` WRONG 对照变为 usable；更大范围推广**暂缓** |
| `#30d` | `4/4` broker `MISSED` 恢复；`0/23` 负向对照 usable；更大范围推广**暂缓** |
| `#30e` | `18/18` 人工标错表格目标 strict wrong；试跑框架清理后 `0/26` 对照新降级 |
| `#30f` | `8/8` 保险负向 non-usable；`10/10` 正向对照保持 |
| `#30g` | 仅子类型诊断；无 YAML 变更 |

---

## 指标注意事项

`#30` 以冻结的 `#29` 人工校准样本作为验证锚点。

因此 **一致率可能在抽取改善时反而下降**：

- 若某行人工标为 `MISSED`
- 而新抽取正确恢复为 `usable`
- 冻结的人工 vs 自动一致率会下降（人工列仍为 `MISSED`）

`#30c`、`#30d` 的小范围写回中曾出现此情况。应读作**冻结标签指标注意事项**，**不**应自动视为回归。

---

## 暂缓工作路由至后续 issue

| Issue | 主题 | 路由工作 |
|---|---|---|
| `#31` | 金融漏标扫描 | 漏标扫描；`000402` / `600816` / `600318` 受控重打标签 |
| `#32` | 收入与研发残留修复 | 残留 wrong 字段单元格与小范围修复 |
| `#33` | 多年份扩展决策 | 2025 / 2023 / 2022 范围、`run_name` 与扩展口径 |

若后续批准子类型重打标签，应跟踪在 **`#31`** 或其子任务下。

---

## 关单口径

`#30` **可以关单**，作为 **金融跟进批次**，明确口径如下：

- 审计加固已交付
- 低风险的定向抽取辅助已交付并验证
- 子类型/标签注意事项已诊断但**未**自动变更
- 更大范围金融推广仍**暂缓**

---

## 可提交列表

- `outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md`
- `CURRENT_STATUS.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `docs/financial_company_schema.md`
- `docs/evaluation_method.md`
- `outputs/generalization/full_market_2024/stage3_quality_followup_summary.md`（仅交叉链接）

---

## 勿提交列表

- 任何 `company_profile.json`
- 任何 `eval_results.json`
- `financial_audit_sample.csv`
- `financial_audit_population.csv`
- `financial_audit_summary.md`
- 任何 YAML 标签变更
- PDFs / `.cache`
- `outputs/db/*.db`

---

## 相关产物

- [financial_audit_fix_30a_summary.md](financial_audit_fix_30a_summary.md)
- [financial_audit_fix_30b_summary.md](financial_audit_fix_30b_summary.md)
- [financial_audit_fix_30c_apply_summary.md](financial_audit_fix_30c_apply_summary.md)
- [financial_audit_fix_30d_apply_summary.md](financial_audit_fix_30d_apply_summary.md)
- [financial_audit_fix_30e_dryrun_summary.md](financial_audit_fix_30e_dryrun_summary.md)
- [financial_audit_fix_30f_dryrun_summary.md](financial_audit_fix_30f_dryrun_summary.md)
- [financial_subtype_review_30g.md](financial_subtype_review_30g.md)

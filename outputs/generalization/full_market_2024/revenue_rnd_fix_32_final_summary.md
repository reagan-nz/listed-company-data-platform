# 收入 + 研发 residual（残留问题）修复 #32 — 最终关单汇总

_生成日期：2026-06-26 | Issue #32 当前范围已关闭_

## 关单决定

**#32 当前范围已关闭**，包括：只读 residual inventory（残留盘点）、scoped P0 R&D fix（小范围 P0 研发修复，已验证 apply（应用））、revenue strict wrong（收入严格审计下错误）dry-run（只读诊断）分类。剩余 revenue extraction（收入抽取）工作与更广 R&D partial（研发部分可用）**明确暂缓**至未来 scoped pilot（小范围试点）。**Non-fin（非金融）strict usable（严格审计下可用）headline（核心指标/对外口径）仍为 9.43/11**（#26 后参考值；#32 未更新）。

---

## 1. 范围与边界

| #32 范围内 | 范围外（暂缓） |
|---|---|
| #25/#26 后 revenue + R&D residuals（残留）盘点 | Full-market revenue/R&D refresh（全市场收入/研发刷新） |
| Scoped P0 R&D apply（小范围 P0 研发应用）（104 家公司） | Full population R&D partial fix（全人口研发 partial（部分可用）修复，~255） |
| Revenue strict wrong（收入严格审计下错误）dry-run（只读诊断）分类（57 cells（字段单元格）） | Revenue production apply（收入生产应用） |
| 文档 + harness（试跑框架）产物 | CNINFO 重下、SQLite（轻量数据库）import（导入） |
| Post-apply local verification（应用后本地验证）（#32c-R5） | Global `strict_audit_summary.md` rerun（全局 strict audit（严格质量审计）重跑） |

**Financial cohort（金融公司分组）**：单独 sub-schema（字段体系）headline（核心指标/对外口径）；8 个 revenue wrong（收入错误）cells（字段单元格）暂缓至 #31 tagging review（标签复核）。

---

## 2. #32 完成内容

| 轨道 | 交付物 | 结果 |
|---|---|---|
| **Inventory（盘点）** | `revenue_rnd_residual_inventory_32.md`、`revenue_rnd_residual_candidates_32.csv`（513 行） | Residuals（残留）已分类；P0/P1/P2 分层已文档化 |
| **#32c R&D（研发）** | R2–R5 harnesses（试跑框架）+ production helper（生产辅助）+ scoped apply（小范围应用）+ verification（验证） | 32/104 P0 strict（严格审计）改善；0 apply errors（应用错误）；verify PASS（通过） |
| **#32b Revenue（收入）** | `revenue_residual_fix_32b_dryrun.py` + summary + details CSV | 57/57 wrong（错误）cells（字段单元格）已分类；17 harness（试跑框架）改善；0 control regressions（对照回归） |

---

## 3. 盘点结果（#32 基线）

| 池 | 数量 | 说明 |
|---|---:|---|
| Revenue strict wrong（收入严格审计下错误） | **57** field-cells（字段单元格）/ **48** issuers（发行人） | region（分地区）38 + segment（分业务）19 |
| Revenue partial（收入部分可用）（仅子池） | CSV 中 **186** | 全量 ~753 partial（部分可用）**未**全量枚举 |
| R&D partial（研发部分可用） | **255** | 在 CSV 中 |
| R&D suspicious not_found（研发可疑未找到） | **15** | snippet（片段）中有表格证据 |
| Non-fin headline（非金融核心指标/对外口径）（参考） | **9.43/11** | #32 全程不变 |

---

## 4. #32c R&D（研发）— 实施与应用

| 阶段 | 关键结果 |
|---|---|
| **R2** | 生产路径加入 guarded `extract_rnd_situation_table_numeric()` + `merge_rnd_investment_with_guard()` |
| **R3** | Dry-run（只读试跑）104 P0 targets（目标公司）：32 strict（严格审计）改善，0 regressions（回归） |
| **R4** | Apply（应用）：104 targets（目标公司），**32 updated（更新）**，0 errors（错误），14 not_found→found（未找到→找到），0 found→not_found（找到→未找到） |
| **R5** | Post-apply verify（应用后验证）**PASS（通过）**：104/104 status（状态）一致；0 regressions（回归）；002415 usable（可用）；000333 partial（部分可用） |

**Scoped 池 post-apply strict（严格审计）分布：** usable（可用）=32，partial（部分可用）=71，not_found_unverified（未找到且未确认）=1（600238）。

强制恢复 → usable（可用）：600011、600020、688081、600029、600115、600844。

---

## 5. #32b Revenue（收入）— dry-run（只读诊断）分类

| 指标 | 数值 |
|---|---:|
| 评估行数 | **57/57** |
| 实验 harness（试跑框架）改善 | **17** |
| Control revenue regressions（对照收入回归） | **0** |
| Production apply（生产应用） | **暂缓** |

### 根因分布

| 根因 | Cells（字段单元格） |
|---|---:|
| Tier3 stitched, still empty（第三层拼接后仍空） | 20 |
| Sales-mode bleed（销售模式串扰） | 12 |
| Financial-like（金融控股类，暂缓 #31） | 8 |
| Layout / data-row heuristic（版式/数据行启发式） | 6 |
| Customer table as region（客户表误作地区表） | 6 |
| Empty / no stitch（空表/未拼接） | 5 |

**Harness（试跑框架）实验：** Tier4 N+2..N+4 → 16 usable/partial（可用/部分可用）；wrong-table ranking（错表排序）→ 17 usable/partial（可用/部分可用）。生产移植需人工签核与 scoped pilot（小范围试点）。

---

## 6. 为何 headline（核心指标/对外口径）9.43/11 不变

1. **#32c scoped apply（小范围定向应用）或 #32b dry-run（只读诊断）后未重跑 full strict audit（全量严格质量审计）。**
2. **Scoped apply（小范围定向应用）≠ population metric（全人口指标）** — 32 家 R&D profile（公司档案）更新不会重算 5,621 × 11 非金融 cells（字段单元格）。
3. **Revenue production fix（收入生产修复）未应用** — headline（核心指标/对外口径）目的下，57 个 strict wrong（严格审计下错误）cells（字段单元格）仍在已存 profile（公司档案）中。
4. **有意政策** — headline（核心指标/对外口径）仅在 scheduled full strict audit（计划全量 strict audit（严格质量审计））后更新，非每个 scoped tranche（小范围批次）。

参考 headline（核心指标/对外口径）来源：`run_name`（运行名称）=`full_market_2024_revenue_refresh` / [strict_audit_summary.md](strict_audit_summary.md)（#32 前）。

---

## 7. 暂缓的 revenue（收入）工作

| 事项 | 优先级 | 说明 |
|---|---|---|
| Tier4 multipage continuation（第四层多页续表）（N+2..N+4） | P0 pilot（试点） | BSE 去重后 ~12 issuers（发行人）；harness（试跑框架）信号 16 cells（字段单元格） |
| Wrong-table ranking（错表排序） | P1 pilot（试点） | 客户/供应商表 vs 地区/业务表判别 |
| Financial-like disclosures（金融控股类披露） | P2 暂缓 | 601066、601668、601611、601216 → #31 |
| Full revenue partial methodology（收入 partial（部分可用）全量方法论） | P2 | ~753 partial（部分可用）人口未全量枚举 |
| Sales-mode bleed trim（销售模式串扰修剪） | P1 | 12 cells（字段单元格）；部分 code 与 Tier4 重叠 |

---

## 8. 暂缓的 R&D（研发）工作

| 事项 | 说明 |
|---|---|
| 72/104 P0 池仍 partial（部分可用） | 多数为利润表「研发费用」误捕获 |
| 000333 cumulative narrative（累计叙述） | 设计上保持 partial（部分可用）；不强制 usable（可用） |
| 301221 | 不在 104-code apply pool（应用池）中（P2 inventory（盘点）） |
| ~255 full-population R&D partial（全人口研发部分可用） | 仅 32/104 scoped P0 改善 |
| R&D P1 unit-scale / audit-rejects-合计 | inventory（盘点）中 96 cells（字段单元格） |

---

## 9. 不得声称（anti-claims）

| 声称 | 是否允许 |
|---|---|
| #32 当前范围已关闭 | **是** |
| 全市场 revenue/R&D 已修复 | **否** |
| #32 更新了 non-fin（非金融）9.43/11 headline（核心指标/对外口径） | **否** |
| Full manual validation（全量人工验证） | **否** |
| #32 触发 CNINFO / SQLite rerun（重跑） | **否** |
| 金融指标混入 non-fin headline（非金融核心指标/对外口径） | **否** |
| Scoped apply（小范围定向应用）= 新全人口 strict（严格审计）分数 | **否** |

---

## 10. 产物索引

| 产物 | 轨道 |
|---|---|
| [revenue_rnd_residual_inventory_32.md](revenue_rnd_residual_inventory_32.md) | Inventory（盘点） |
| [revenue_rnd_residual_candidates_32.csv](revenue_rnd_residual_candidates_32.csv) | Inventory（盘点） |
| [rnd_residual_fix_32c_r2_summary.md](rnd_residual_fix_32c_r2_summary.md) | R&D（研发） |
| [rnd_residual_fix_32c_apply_summary.md](rnd_residual_fix_32c_apply_summary.md) | R&D apply（研发应用） |
| [rnd_residual_fix_32c_post_apply_verify.md](rnd_residual_fix_32c_post_apply_verify.md) | R&D verify（研发验证） |
| [revenue_residual_fix_32b_dryrun_summary.md](revenue_residual_fix_32b_dryrun_summary.md) | Revenue dry-run（收入只读诊断） |
| **本文件** | Closure（关单） |

---

## 11. 可提交（safe-to-commit）

- `outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md`（本文件）
- 上述全部 #32 inventory（盘点）、harness（试跑框架）与 summary markdown
- `lab/revenue_residual_fix_32b_dryrun.py`、`lab/rnd_residual_fix_32c_*.py`、`lab/extract_annual_report.py`（R&D helper（研发辅助），若已提交）
- 文档同步：`CURRENT_STATUS.md`、`CHANGELOG.md`、`ROADMAP.md`、`docs/evaluation_method.md`

## 12. 勿提交（do-not-commit）

- #32c apply（应用）产生的本地 `company_profile.json`（公司档案 JSON）/ `eval_results.json` 变更
- `rnd_refresh_changes_32c_apply.csv`、`.bak.rnd_refresh_*` 备份
- `strict_audit_summary.md`（headline（核心指标/对外口径）未变）
- Refresh CSVs、apply logs（应用日志）、YAML changes（标签变更）

---

## GitHub #32 closing comment（关单评论，中文）

```
#32 revenue + R&D residual — 当前范围已关闭

已完成：
1. 盘点：revenue_rnd_residual_inventory_32.md + candidates_32.csv（513 行）
   - 收入 strict wrong（严格审计下错误）57（region（分地区）38 + segment（分业务）19）
   - 研发 partial（部分可用）255 + 可疑 not_found（未找到）15
2. #32c R&D scoped P0：
   - 生产 guarded situation-table helper（带防护研发情况表辅助）
   - apply（应用）104 家 / 32 更新 / 0 errors（错误）/ 14 not_found→found（未找到→找到）
   - 后验 PASS（通过）（104/104 一致，0 回归；002415 usable（可用）；000333 partial（部分可用））
3. #32b 收入 dry-run（只读诊断）：
   - 57/57 strict-wrong（严格审计下错误）已分类；harness（试跑框架）实验改善 17；control（对照）回归 0
   - 生产 apply（应用）暂缓；建议后续 scoped Tier4 + wrong-table pilot（小范围试点）

Headline（核心指标/对外口径）：non-fin strict usable（非金融严格审计下可用）9.43/11 **未更新**（无全局 strict audit（严格质量审计）重跑；scoped apply（小范围定向应用）≠ 全人口指标）。

Defer（暂缓）：
- 收入 Tier4 / wrong-table ranking（错表排序）生产试点
- 金融控股类 8 cell → #31
- 研发 72/104 partial（部分可用）、000333/301221、全人口 partial（部分可用）
- #33 多年份（单独决策）

未做：CNINFO、SQLite、全市场 refresh（刷新）、全量人工验证。

产物：revenue_rnd_fix_32_final_summary.md
Do-not-commit（勿提交）：profile/eval apply（应用）产物、refresh CSV（除非明确批准）
```

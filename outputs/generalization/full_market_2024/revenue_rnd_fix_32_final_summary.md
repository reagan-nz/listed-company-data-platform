# 收入 + 研发残留修复 #32 — 最终关单汇总

_生成日期：2026-06-26 | Issue #32 当前范围已关闭_

**术语说明：** strict audit = 严格质量审计；scoped apply = 小范围写回；dry-run = 只读诊断；headline = 核心指标；Financial cohort = 金融公司分组。

---

## 关单决定

**#32 当前范围已关闭**，包括：只读残留盘点、小范围 P0 研发修复（已验证写回）、收入 strict wrong 只读诊断分类。剩余收入抽取工作与更广 R&D partial **明确暂缓**至未来小范围试点。**非金融 strict usable 核心指标仍为 9.43/11**（#26 后参考值；#32 未更新）。

---

## 1. 范围与边界

| #32 范围内 | 范围外（暂缓） |
|---|---|
| #25/#26 后 revenue + R&D 残留盘点 | 全市场收入/研发刷新 |
| 小范围 P0 研发写回（104 家公司） | 全人口研发 partial 修复（约 255） |
| 收入 strict wrong 只读诊断分类（57 字段单元格） | 收入生产写回 |
| 文档 + 试跑框架产物 | CNINFO 重下、SQLite 导入 |
| 应用后本地验证（#32c-R5） | 全局 `strict_audit_summary.md` 重跑 |

**金融公司分组**：单独子 schema 核心指标；8 个 revenue wrong 字段单元格暂缓至 #31 标签复核。

---

## 2. #32 完成内容

| 轨道 | 交付物 | 结果 |
|---|---|---|
| **盘点** | `revenue_rnd_residual_inventory_32.md`、`revenue_rnd_residual_candidates_32.csv`（513 行） | 残留已分类；P0/P1/P2 分层已文档化 |
| **#32c R&D** | R2–R5 试跑框架 + 生产辅助 + 小范围写回 + 验证 | 32/104 P0 strict 改善；0 写回错误；验证通过 |
| **#32b Revenue** | `revenue_residual_fix_32b_dryrun.py` + summary + details CSV | 57/57 wrong 字段单元格已分类；17 试跑框架改善；0 对照回归 |

---

## 3. 盘点结果（#32 基线）

| 池 | 数量 | 说明 |
|---|---:|---|
| 收入 strict wrong | **57** 字段单元格 / **48** 发行人 | region 38 + segment 19 |
| 收入 partial（仅子池） | CSV 中 **186** | 全量约 753 partial **未**全量枚举 |
| R&D partial | **255** | 在 CSV 中 |
| R&D 可疑 not_found | **15** | snippet 中有表格证据 |
| 非金融核心指标（参考） | **9.43/11** | #32 全程不变 |

---

## 4. #32c R&D — 实施与写回

| 阶段 | 关键结果 |
|---|---|
| **R2** | 生产路径加入 guarded `extract_rnd_situation_table_numeric()` + `merge_rnd_investment_with_guard()` |
| **R3** | 只读试跑 104 P0 目标：32 strict 改善，0 回归 |
| **R4** | 写回：104 目标，**32 updated**，0 errors，14 not_found→found，0 found→not_found |
| **R5** | 应用后验证**通过**：104/104 status 一致；0 回归；002415 usable；000333 partial |

**小范围池应用后 strict 分布：** usable=32，partial=71，not_found_unverified=1（600238）。

强制恢复 → usable：600011、600020、688081、600029、600115、600844。

---

## 5. #32b Revenue — 只读诊断分类

| 指标 | 数值 |
|---|---:|
| 评估行数 | **57/57** |
| 实验试跑框架改善 | **17** |
| 对照收入回归 | **0** |
| 生产写回 | **暂缓** |

### 根因分布

| 根因 | 字段单元格 |
|---|---:|
| Tier3 拼接后仍空 | 20 |
| 销售模式串扰 | 12 |
| 金融控股类（暂缓 #31） | 8 |
| 版式/数据行启发式 | 6 |
| 客户表误作地区表 | 6 |
| 空表/未拼接 | 5 |

**试跑框架实验：** Tier4 N+2..N+4 → 16 usable/partial；错表排序 → 17 usable/partial。生产移植需人工确认与小范围试点。

---

## 6. 为何核心指标 9.43/11 不变

1. **#32c 小范围写回或 #32b 只读诊断后未重跑全量严格质量审计。**
2. **小范围写回 ≠ 全人口指标** — 32 家 R&D profile 更新不会重算 5,621 × 11 非金融字段单元格。
3. **收入生产修复未应用** — 核心指标目的下，57 个 strict wrong 字段单元格仍在已存 profile 中。
4. **有意政策** — 核心指标仅在计划全量严格质量审计后更新，非每个小范围批次。

参考核心指标来源：`run_name`=`full_market_2024_revenue_refresh` / [strict_audit_summary.md](strict_audit_summary.md)（#32 前）。

---

## 7. 暂缓的收入工作

| 事项 | 优先级 | 说明 |
|---|---|---|
| Tier4 多页续表（N+2..N+4） | P0 试点 | 北交所去重后约 12 发行人；试跑框架信号 16 字段单元格 |
| 错表排序 | P1 试点 | 客户/供应商表 vs 地区/业务表判别 |
| 金融控股类披露 | P2 暂缓 | 601066、601668、601611、601216 → #31 |
| 收入 partial 全量方法论 | P2 | 约 753 partial 人口未全量枚举 |
| 销售模式串扰修剪 | P1 | 12 字段单元格；部分 code 与 Tier4 重叠 |

---

## 8. 暂缓的 R&D 工作

| 事项 | 说明 |
|---|---|
| 72/104 P0 池仍 partial | 多数为利润表「研发费用」误捕获 |
| 000333 累计叙述 | 设计上保持 partial；不强制 usable |
| 301221 | 不在 104-code 写回池中（P2 盘点） |
| 约 255 全人口 R&D partial | 仅 32/104 小范围 P0 改善 |
| R&D P1 单位尺度 / audit-rejects-合计 | 盘点中 96 字段单元格 |

---

## 9. 不得声称

| 声称 | 是否允许 |
|---|---|
| #32 当前范围已关闭 | **是** |
| 全市场 revenue/R&D 已修复 | **否** |
| #32 更新了非金融 9.43/11 核心指标 | **否** |
| 全量人工验证 | **否** |
| #32 触发 CNINFO / SQLite 重跑 | **否** |
| 金融指标混入非金融核心指标 | **否** |
| 小范围写回 = 新全人口 strict 分数 | **否** |

---

## 10. 产物索引

| 产物 | 轨道 |
|---|---|
| [revenue_rnd_residual_inventory_32.md](revenue_rnd_residual_inventory_32.md) | 盘点 |
| [revenue_rnd_residual_candidates_32.csv](revenue_rnd_residual_candidates_32.csv) | 盘点 |
| [rnd_residual_fix_32c_r2_summary.md](rnd_residual_fix_32c_r2_summary.md) | R&D |
| [rnd_residual_fix_32c_apply_summary.md](rnd_residual_fix_32c_apply_summary.md) | R&D 写回 |
| [rnd_residual_fix_32c_post_apply_verify.md](rnd_residual_fix_32c_post_apply_verify.md) | R&D 验证 |
| [revenue_residual_fix_32b_dryrun_summary.md](revenue_residual_fix_32b_dryrun_summary.md) | 收入只读诊断 |
| **本文件** | 关单 |

---

## 11. 可提交

- `outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md`（本文件）
- 上述全部 #32 盘点、试跑框架与 summary markdown
- `lab/revenue_residual_fix_32b_dryrun.py`、`lab/rnd_residual_fix_32c_*.py`、`lab/extract_annual_report.py`（R&D 辅助，若已提交）
- 文档同步：`CURRENT_STATUS.md`、`CHANGELOG.md`、`ROADMAP.md`、`docs/evaluation_method.md`

## 12. 勿提交

- #32c 写回产生的本地 `company_profile.json` / `eval_results.json` 变更
- `rnd_refresh_changes_32c_apply.csv`、`.bak.rnd_refresh_*` 备份
- `strict_audit_summary.md`（核心指标未变）
- 刷新 CSV、写回日志、YAML 变更

---

## GitHub #32 关单评论（中文）

```
#32 revenue + R&D residual — 当前范围已关闭

已完成：
1. 盘点：revenue_rnd_residual_inventory_32.md + candidates_32.csv（513 行）
   - 收入 strict wrong 57（region 38 + segment 19）
   - 研发 partial 255 + 可疑 not_found 15
2. #32c R&D 小范围 P0：
   - 生产 guarded situation-table 辅助
   - 写回 104 家 / 32 更新 / 0 errors / 14 not_found→found
   - 后验通过（104/104 一致，0 回归；002415 usable；000333 partial）
3. #32b 收入只读诊断：
   - 57/57 strict-wrong 已分类；试跑框架实验改善 17；对照回归 0
   - 生产写回暂缓；建议后续小范围 Tier4 + 错表试点

核心指标：非金融 strict usable 9.43/11 **未更新**（无全局严格质量审计重跑；小范围写回 ≠ 全人口指标）。

暂缓：
- 收入 Tier4 / 错表排序生产试点
- 金融控股类 8 字段 → #31
- 研发 72/104 partial、000333/301221、全人口 partial
- #33 多年份（单独决策）

未做：CNINFO、SQLite、全市场刷新、全量人工验证。

产物：revenue_rnd_fix_32_final_summary.md
勿提交：profile/eval 写回产物、refresh CSV（除非明确批准）
```

# CNINFO C 类 — Snapshot Exclusion Universe 一致性审计

_生成时间：2026-07-14 · Task **C-GEN-20260714-07** · CNINFO **0**_

> **offline only** · **no production snapshot mutate** · **no commit/push** · **no live**

---

## 1. 任务范围

对 C-06 progression 包产出的 **19 行**排除清单（`cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv`）与三条来源 ledger 做行级一致性核验：

| 来源 ledger | 路径 | 期望行数 |
|-------------|------|----------|
| partial7 | `cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` | 7 |
| empty-dividend3 | `cninfo_c_class_empty_dividend_offline_matrix_20260714.csv` | 3 |
| holdout9 | `cninfo_c_class_phase35_holdout_closed_with_caveat_ledger.csv` | 9 |

**核验维度：** `company_code` · `case_id`（partial7/empty-dividend）· `company_name` · `ledger_status` · `audit_status` / holdout category · `promotion_allowed_now` · 反向覆盖（来源行是否均在排除清单中）。

---

## 2. 汇总

| 指标 | 值 |
|------|-----|
| 排除清单行数 | **19** |
| partial7 子集 | 7（EXC-P01–P07） |
| empty-dividend3 子集 | 3（EXC-E01–E03） |
| holdout9 子集 | 9（EXC-H01–H09） |
| 行级 MATCH | **19 / 19** |
| 行级 MISMATCH | **0** |
| 来源 orphan（未纳入排除清单） | **0** |
| 双轨登记（设计预期） | `000003` 同时出现在 partial7（CE1E061）与 holdout9（EXC-H01） |
| CNINFO 调用 | **0** |
| Production snapshot mutate | **未执行** |

---

## 3. 行级结果

### 3.1 Partial7（7/7 MATCH）

| exclusion_id | company_code | case_id | ledger | audit | promotion | 结果 |
|--------------|--------------|---------|--------|-------|-----------|------|
| EXC-P01 | 600001 | CE1E002 | partial | partial | no | MATCH |
| EXC-P02 | 600005 | CE1E003 | partial | partial | no | MATCH |
| EXC-P03 | 600068 | CE1E034 | partial | partial | no | MATCH |
| EXC-P04 | 000003 | CE1E061 | partial | partial | no | MATCH |
| EXC-P05 | 000015 | CE1E067 | partial | partial | no | MATCH |
| EXC-P06 | 000022 | CE1E070 | partial | partial | no | MATCH |
| EXC-P07 | 000024 | CE1E071 | partial | partial | no | MATCH |

与 partial7 QA 矩阵一致：`caveat_type=delisted_or_merged_partial_normalized` · `requires_snapshot=false` · `requires_live=false`。

### 3.2 Empty-Dividend3（3/3 MATCH）

| exclusion_id | company_code | case_id | ledger | audit | promotion | 结果 |
|--------------|--------------|---------|--------|-------|-----------|------|
| EXC-E01 | 688031 | CE1E176 | complete | needs_review | no | MATCH |
| EXC-E02 | 688062 | CE1E188 | complete | needs_review | no | MATCH |
| EXC-E03 | 688071 | CE1E193 | complete | needs_review | no | MATCH |

与 empty-dividend 矩阵一致：`caveat_type=empty_but_valid_dividend_normalized_zero_byte` · ledger complete / audit needs_review 双层分歧合法登记。

### 3.3 Holdout9（9/9 MATCH）

| exclusion_id | company_code | ledger_status | audit_status | promotion | 结果 |
|--------------|--------------|---------------|--------------|-----------|------|
| EXC-H01 | 000003 | closed_with_caveat | hold_for_review | no | MATCH |
| EXC-H02 | 000578 | closed_with_caveat | hold_for_review | no | MATCH |
| EXC-H03 | 000666 | closed_with_caveat | hold_for_review | no | MATCH |
| EXC-H04 | 000689 | closed_with_caveat | hold_for_review | no | MATCH |
| EXC-H05 | 000861 | closed_with_caveat | hold_for_review | no | MATCH |
| EXC-H06 | 000961 | closed_with_caveat | hold_for_review | no | MATCH |
| EXC-H07 | 002280 | closed_with_caveat | hold_for_review | no | MATCH |
| EXC-H08 | 301212 | closed_with_caveat_still_partial | C35R016 | no | MATCH |
| EXC-H09 | 600220 | closed_with_caveat | hold_for_review | no | MATCH |

与 holdout closed-with-caveat ledger 一致：`final_disposition` · `holdout_category` · `promotion_allowed_now=no` 全部对齐。

---

## 4. 控制面措辞建议（prep vs execute）

| 文档 | `approved_for_snapshot_rebuild` | `execute_production_snapshot_rebuild` |
|------|--------------------------------|---------------------------------------|
| `PROJECT_CONTROL.md`（审计前 C-track） | `false` | 未显式分列 |
| C-06 progression 包（`cninfo_c_class_snapshot_progression_package_20260714.md`） | `true`（**preparation path only** · AQ-C-SNAP） | `false` |

**解读：** 两文档并非事实矛盾，而是**准备路径**与**生产执行**未分层表述。C-06 在 AQ-C-SNAP 下将 progression 准备工件（排除清单 · mock 计划 · validation 包）登记为 `approved_for_snapshot_rebuild=true`，同时显式保持 `execute_production_snapshot_rebuild=false` 与全 cohort `rebuild_candidate=no`。`PROJECT_CONTROL` 仍用单一 `false` 易读成「禁止一切 snapshot 相关工作」，与 progression 包语义不对齐。

**建议（已落实于 `PROJECT_CONTROL.md` C-track `current_gate` 行）：** 分列 `approved_for_snapshot_rebuild=true`（preparation path only）与 `execute_production_snapshot_rebuild=false`；**不**将 execute 翻转为 true · **不**膨胀 production_ready。

---

## 5. 红线确认

| 项 | 状态 |
|----|------|
| CNINFO 调用 | **0** |
| Production snapshot 根 mutate | **未执行** |
| commit / push | **无** |
| verified / production_ready 膨胀 | **无** |

---

## 6. Gate

```
task_id = C-GEN-20260714-07
exclusion_rows = 19
row_level_match = 19/19
reverse_coverage_orphans = 0
overall_gate = PASS_OFFLINE
```

**不是 verified** · **不是 production_ready** · **不是 execute_production_snapshot_rebuild**

---

## 7. 伴生产物

| 文件 | 说明 |
|------|------|
| [cninfo_c_class_snapshot_exclusion_consistency_matrix_20260714.csv](cninfo_c_class_snapshot_exclusion_consistency_matrix_20260714.csv) | 19 行一致性矩阵（排除侧 vs 来源侧字段对照） |

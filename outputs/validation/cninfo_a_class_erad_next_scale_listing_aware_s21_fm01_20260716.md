# A-FM-01 — Build listing-aware S21 + wire runner + AD2E1551–1600 dry-run/live

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-01_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **CNINFO live（本 turn）：** **104**（main 101 + isolated retry 3）· dry-run → bounded live · **未 mutate S1–S20 live 主根** · **无 commit/push**  
> **Prior：** A-FM-20/21 S20 AD2E1501–1550 first-pass 44/50（6×605* SSL `not_found`）→ isolated retry 6/6 → combined 50/50 `PASS_WITH_CAVEAT`

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-01** |
| track | A |
| executor | a-class-executor |
| controller_execution_allowed | false |
| 目标 | listing-aware builder 生成 S21（AD2E1551–1600）→ phase2 接线独立新根 → dry-run → bounded live full50 → 若 not_found 则孤立 retry |
| 保护 | **禁止** mutate S1–S20 live 主根 |

## 2. S20 SSL caveat（FM21 引用）

S20 首轮 6×`not_found`（AD2E1540–1545 / 605*）分类为：

```text
prior_class   = ssl_transport_eof_with_orgid_already_resolved
not_cause     = listing_date_after_period | orgid_missing | empty_matching_window
likely_cause  = transient_ssl_transport (cninfo_request_count=0 on S20 main live)
```

A-FM-21 孤立 retry 根 `.../s20/retry_not_found_1540_1545/` 已 6/6 found（CNINFO=12）。**S21 本包不得把同类 SSL 静默吞掉；单案 not_found 须诚实分类。**

## 3. Runner / builder rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21`
2. 禁止写入封闭 S1 / listing-aware S2–S20 live 根
3. case_id：**AD2E1551–AD2E1600** · cohort=`next_scale_listing_aware`
4. CNINFO request cap：**120**/run（同 S2–S20）
5. listing_period lint 使用 A 轨 coverage overlay（`cninfo_a_class_basic_profile_coverage_overlay_fm06`）
6. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S20**
7. **prefix_concentration**：本片同一 3 位前缀最多 **25**

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E1551–1600） |
| prefix counts | 600=25 · 605=4 · 688=21（max=25） |
| reject ledger | **1459**（a_exclude=1550 等） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** · CNINFO=**0** |
| live first-pass | 50 executed · **49/50** acceptable · not_found=**1** |
| not_found case | AD2E1555（600616 金枫酒业） |
| not_found class | `matching_v2_empty_window_with_orgid_resolved`（orgid=`gssh0600616` · cninfo=3 · records=12 · last_err=ok；**非** FM21 SSLEof） |
| isolated retry | `.../s21/retry_not_found_1555/` · dry-run 1/1 · live **仍 not_found** · CNINFO=**3** · **未写主 live** |
| combined S21+retry | **49/50** acceptable（无 recovery） |
| CNINFO calls（本 turn） | **104**（main 101 + retry 3；cap ≤ 120/run） |
| orgid_fallback | hits=**0** · misses=**0** |
| network_timeout | **0** |
| execution gate（main / combined） | `PASS_WITH_CAVEAT`（阈值 ≥45/50） |
| S1–S20 live 主根 mutated | **no**（mtime 全量校验） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `cninfo_a_class_listing_aware_cohort_builder.py --slice s21` | size=50 · CNINFO=0 | ~2.3s |
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 24/24 OK | ~0.05s |
| `test_cninfo_a_class_erad_listing_aware_s21_runner.py` | 5/5 OK | ~0.02s |
| `test_cninfo_a_class_erad_listing_aware_s20_runner.py` | 5/5 OK | ~0.02s |
| dry-run listing-aware S21 | planned_ok 50/50 · CNINFO=0 | ~0.7s |
| **live listing-aware S21（full50）** | 49/50 PASS_WITH_CAVEAT · CNINFO=101 | **~417s** |
| dry-run + live isolated retry AD2E1555 | still not_found · CNINFO=3 | ~21s |

## 6. Files

### Created
- `lab/test_cninfo_a_class_erad_listing_aware_s21_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_plus50_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_reject_ledger_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21/retry_not_found_1555/`（孤立 retry 子根）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_not_found_retry_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_not_found_precheck_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_recovery_ledger_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_combined_live_report_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_combined_live_quality_report_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_20260716.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S21 slice · overlay + prefix cap · exclude S2–S20）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S21 模式接线 · 隔离根 · 禁止写 S1–S20 live）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S21 case_id_start 单测）

### Not touched（保护）
- 封闭 S1 **live** 主报告
- listing-aware S2–S20 **live** 主报告（mtime 校验通过）
- B/C/D · commit/push

## 7. Allow-list（ready_for_commit）

Track-A only（排除 console log · 排除 gitignored `raw_metadata/` · 排除 B/C/D）：

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s21_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_plus50_universe_20260716.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_reject_ledger_20260716.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21/`（整根；`raw_metadata/` 按 `.gitignore` 排除；`reports/*console*` 不入 allow-list）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_not_found_retry_universe_20260716.csv`
9. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_not_found_precheck_20260716.csv`
10. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_recovery_ledger_20260716.csv`
11. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_combined_live_report_20260716.csv`
12. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_combined_live_quality_report_20260716.csv`
13. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s21_fm01_20260716.md`

## 8. Gate

```text
a_class_fm01_listing_aware_s21_gate = PASS_WITH_CAVEAT
a_class_fm01_s21_not_found_retry_gate = FAIL_REVIEW_REQUIRED   # AD2E1555 仍 not_found
a_class_fm01_combined_s21_plus_retry_gate = PASS_WITH_CAVEAT  # 49/50 combined
cninfo_calls = 104
s1_s20_live_main_roots_mutated = no
ready_for_commit = yes
commit = not_done
push = not_done
```

## 9. Next

```text
Controller：审阅 S21 49/50 PASS_WITH_CAVEAT + AD2E1555 matching_v2 空窗（非 SSL）→ track-A-only commit；
下一候选 A：S22 listing-aware +50（AD2E1601–1650）同构扩片；
可选：针对 600616 做匹配窗口/报告类型专项调查（勿静默改 period）；
勿 mutate S1–S21 live 主根；无 B/C/D；无 push。
```

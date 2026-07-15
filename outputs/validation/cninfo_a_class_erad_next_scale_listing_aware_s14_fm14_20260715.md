# A-FM-14 — Build listing-aware S14 + wire runner + AD2E1201–1250 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-14_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **CNINFO live（本 turn）：** **101** · dry-run → bounded live · **未 mutate 封闭 S1–S13 live 根** · **无 commit/push**  
> **Prior：** A-FM-13 S13 AD2E1151–1200 live 50/50 `PASS_WITH_CAVEAT`（CNINFO=107）

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** build+wire S14 · **3** bounded live proof |
| 选择 | listing-aware builder 生成 S14（AD2E1201–1250）→ phase2 接线独立新根 → dry-run → bounded live full50 |
| 为何不是 S13 not_found retry | standing_scope 优先 metadata scale；S14 未 blocked |
| 为何不是 IDLE | S13 已封闭；prefix_concentration + overlay 分母可复用 |
| Prior | A-FM-13 S13 live PASS_WITH_CAVEAT；A-FM-06 overlay 863→1726 |

## 2. Runner / builder rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14`
2. 禁止写入封闭 S1 / listing-aware S2–S13 live 根
3. case_id：**AD2E1201–AD2E1250** · cohort=`next_scale_listing_aware`
4. CNINFO request cap：**120**/run（同 S2–S13）
5. listing_period lint 使用 A 轨 coverage overlay（`cninfo_a_class_basic_profile_coverage_overlay_fm06`）
6. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S13**
7. **prefix_concentration**：本片同一 3 位前缀最多 **25**

## 3. Files

### Created
- `lab/test_cninfo_a_class_erad_listing_aware_s14_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14_fm14_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S14 slice · overlay + prefix cap · exclude S2–S13）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S14 模式接线 · 隔离根 · overlay listing lint · 禁止写 S1–S13 live）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S14 case_id_start 单测）

### Reused（未改）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（FM06）

### Not touched（保护）
- 封闭 S1 **live**（mtime 仍为 **14:41**）
- listing-aware S2–S13 **live**（mtime 分别为 17:11 / 17:29 / 17:48 / 18:16 / 20:26 / 20:50 / 21:26 / 21:41 / 21:56 / 22:11 / 22:29 / 22:46）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E1201–1250） |
| prefix counts | 300=25 · 301=9 · 302=1 · 600=15（max=25） |
| reject ledger | **895**（a_cumulative_exclude=788 · prefix_concentration_exclude=43 · st_exclude=38 · listing_period_gate=26） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live | 50 executed · **49/50** acceptable · not_found=**1**（AD2E1236 / 600000） |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（本 turn） | **101**（cap ≤ 120；builder/dry-run=0） |
| orgid_fallback | hits=**4**（AD2E1232/301603 · AD2E1236/600000 · AD2E1237/600004 · AD2E1238/600006） · misses=**0** |
| network_timeout | **0** |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50；本片 49/50） |
| closed S1–S13 live roots mutated | **no**（mtime 校验） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `cninfo_a_class_listing_aware_cohort_builder.py --slice s14` | size=50 · CNINFO=0 | ~3.85s |
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 17/17 OK | ~0.18s |
| `test_cninfo_a_class_erad_listing_aware_s14_runner.py` | 5/5 OK | ~0.42s |
| `test_cninfo_a_class_erad_listing_aware_s13_runner.py` | 5/5 OK | ~0.21s |
| dry-run listing-aware S14 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.38s |
| **live listing-aware S14（full50）** | 49/50 PASS_WITH_CAVEAT · CNINFO=101 | **~521.0s** |

## 6. Allow-list（ready_for_commit）

Track-A only（排除 console log · 排除 gitignored `raw_metadata/` · 排除 B/C/D 与无关 dirty）：

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s14_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14/`（整根；`raw_metadata/` 按 `.gitignore` 排除；`reports/dryrun_fm14_console_20260715.log` / `reports/live_fm14_console_20260715.log` 不入 allow-list）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s14_fm14_20260715.md`

## 7. Gate

```text
a_class_fm14_listing_aware_s14_gate = PASS_WITH_CAVEAT
a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice2_s1_execution_gate = PASS_WITH_CAVEAT
cninfo_calls = 101
ready_for_commit = yes
commit = not_done
push = not_done
```

## 8. Next

```text
Controller：审阅 allow-list → track-A-only commit（无 push）；
下一片：listing-aware S15（AD2E1251–1300 · 独立新根）或 coverage overlay 扩分母；
可选：AD2E1236（600000）not_found 孤立探针（勿 mutate S14 live 主根除非独立 retry 根）；
勿 reopen S8/S12/S14 not_found 除非下一片 blocked；勿 mutate S1–S14 live 根。
```

# A-FM-20 — Build listing-aware S20 + wire runner + AD2E1501–1550 dry-run/live

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-20_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **CNINFO live（本 turn）：** **87** · dry-run → bounded live · **未 mutate 封闭 S1–S19 live 根** · **无 commit/push**  
> **Prior：** A-FM-19 S19 AD2E1451–1500 live 50/50 `PASS_WITH_CAVEAT`（CNINFO=99）

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** build+wire S20 · **3** bounded live proof |
| 选择 | listing-aware builder 生成 S20（AD2E1501–1550）→ phase2 接线独立新根 → dry-run → bounded live full50 |
| 为何不是 IDLE | S19 已封闭；prefix_concentration + overlay 分母可复用 |
| Prior | A-FM-19 S19 live PASS_WITH_CAVEAT；A-FM-06 overlay 863→1726 |

## 2. Runner / builder rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20`
2. 禁止写入封闭 S1 / listing-aware S2–S19 live 根
3. case_id：**AD2E1501–AD2E1550** · cohort=`next_scale_listing_aware`
4. CNINFO request cap：**120**/run（同 S2–S19）
5. listing_period lint 使用 A 轨 coverage overlay（`cninfo_a_class_basic_profile_coverage_overlay_fm06`）
6. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S19**
7. **prefix_concentration**：本片同一 3 位前缀最多 **25**

## 3. Files

### Created
- `lab/test_cninfo_a_class_erad_listing_aware_s20_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_plus50_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_reject_ledger_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm20_20260716.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S20 slice · overlay + prefix cap · exclude S2–S19）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S20 模式接线 · 隔离根 · overlay listing lint · 禁止写 S1–S19 live）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S20 case_id_start 单测）

### Reused（未改）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（FM06）

### Not touched（保护）
- 封闭 S1 **live**（mtime 校验通过）
- listing-aware S2–S19 **live**（mtime 校验通过 · 本 turn 未变）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E1501–1550） |
| prefix counts | 600=25 · 603=11 · 605=14（max=25） |
| reject ledger | **1429**（a_cumulative_exclude=1265 · prefix_concentration_exclude=80 · st_exclude=54 · listing_period_gate=30） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live | 50 executed · **44/50** acceptable · not_found=**6** |
| not_found cases | AD2E1540(605133) · AD2E1541(605151) · AD2E1542(605222) · AD2E1543(605296) · AD2E1544(605305) · AD2E1545(605333) |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（本 turn） | **87**（cap ≤ 120；builder/dry-run=0；orgid_fallback hits=7） |
| orgid_fallback | hits=**7** · misses=**0** |
| network_timeout | **0** |
| execution gate | `FAIL_REVIEW_REQUIRED`（阈值 ≥45/50；本片 44/50） |
| closed S1–S19 live roots mutated | **no**（mtime 校验） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `cninfo_a_class_listing_aware_cohort_builder.py --slice s20` | size=50 · CNINFO=0 | ~1.59s |
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 23/23 OK | ~0.16s |
| `test_cninfo_a_class_erad_listing_aware_s20_runner.py` | 5/5 OK | ~0.23s |
| `test_cninfo_a_class_erad_listing_aware_s19_runner.py` | 5/5 OK | ~0.64s |
| dry-run listing-aware S20 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.23s |
| **live listing-aware S20（full50）** | 44/50 FAIL_REVIEW_REQUIRED · CNINFO=87 | **~249.0s** |

## 6. Allow-list（ready_for_commit）

Track-A only（排除 console log · 排除 gitignored `raw_metadata/` · 排除 B/C/D 与无关 dirty）：

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s20_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_plus50_universe_20260716.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_reject_ledger_20260716.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20/`（整根；`raw_metadata/` 按 `.gitignore` 排除；`reports/dryrun_fm20_console_20260716.log` / `reports/live_fm20_console_20260716.log` 不入 allow-list）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm20_20260716.md`

## 7. Gate

```text
a_class_fm20_listing_aware_s20_gate = FAIL_REVIEW_REQUIRED
a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice2_s1_execution_gate = FAIL_REVIEW_REQUIRED
cninfo_calls = 87
ready_for_commit = no
commit = not_done
push = not_done
```

## 8. Next

```text
Controller：审阅 6× not_found（均为 605* · AD2E1540–1545）→ 可选独立 orgid/匹配 retry 根（勿 mutate S20 live 主根除非明确批准）或接受 FAIL 后仍 track-A-only commit wiring；
阈值差 1（44 vs ≥45）· 下一片勿在未解 not_found 前盲扩 S21；
勿 mutate S1–S20 live 根；无 B/C/D；无 push。
```

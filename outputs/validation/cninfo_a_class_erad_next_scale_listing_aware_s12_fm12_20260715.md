# A-FM-12 — Build listing-aware S12 + wire runner + AD2E1101–1150 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-12_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **CNINFO live（本 turn）：** **110** · dry-run → bounded live · **未 mutate 封闭 S1–S11 live 根** · **无 commit/push**  
> **Prior：** A-FM-11 S11 AD2E1051–1100 live 50/50 `PASS_WITH_CAVEAT`（CNINFO=110）

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** build+wire S12 · **3** bounded live proof |
| 选择 | listing-aware builder 生成 S12（AD2E1101–1150）→ phase2 接线独立新根 → dry-run → bounded live full50 |
| 为何不是 S8 not_found retry | S8 已过阈值；standing_scope 优先 metadata scale；S12 未 blocked |
| 为何不是 IDLE | S11 已封闭；prefix_concentration + overlay 分母可复用 |
| Prior | A-FM-11 S11 live PASS_WITH_CAVEAT；A-FM-06 overlay 863→1726 |

## 2. Runner / builder rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12`
2. 禁止写入封闭 S1 / listing-aware S2–S11 live 根
3. case_id：**AD2E1101–AD2E1150** · cohort=`next_scale_listing_aware`
4. CNINFO request cap：**120**/run（同 S2–S11）
5. listing_period lint 使用 A 轨 coverage overlay（`cninfo_a_class_basic_profile_coverage_overlay_fm06`）
6. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S11**
7. **prefix_concentration**：本片同一 3 位前缀最多 **25**

## 3. Files

### Created
- `lab/test_cninfo_a_class_erad_listing_aware_s12_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12_fm12_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S12 slice · overlay + prefix cap · exclude S2–S11）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S12 模式接线 · 隔离根 · overlay listing lint · 禁止写 S1–S11 live）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S12 case_id_start 单测）

### Reused（未改）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（FM06）

### Not touched（保护）
- 封闭 S1 **live**（mtime 仍为 **14:41**）
- listing-aware S2–S11 **live**（mtime 分别为 17:11 / 17:29 / 17:48 / 18:16 / 20:26 / 20:50 / 21:26 / 21:41 / 21:56 / 22:11）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E1101–1150） |
| prefix counts | 300=25 · 301=25（max=25） |
| reject ledger | **798**（a_cumulative_exclude=657 · prefix_concentration_exclude=93 · st_exclude=38 · listing_period_gate=10） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live | 50 executed · **49/50** acceptable · failed/not_found=**1**（AD2E1148 / 301267） |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（本 turn） | **110**（cap ≤ 120；builder/dry-run=0） |
| orgid_fallback | hits=**0** · misses=**0** |
| network_timeout | **0** |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50；本片 49/50） |
| closed S1–S11 live roots mutated | **no**（mtime 校验） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `cninfo_a_class_listing_aware_cohort_builder.py --slice s12` | size=50 · CNINFO=0 | ~4.97s |
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 15/15 OK | ~0.16s |
| `test_cninfo_a_class_erad_listing_aware_s12_runner.py` | 5/5 OK | ~0.29s |
| `test_cninfo_a_class_erad_listing_aware_s11_runner.py` | 5/5 OK | ~0.23s |
| dry-run listing-aware S12 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.29s |
| **live listing-aware S12（full50）** | 49/50 PASS_WITH_CAVEAT · CNINFO=110 | **~641.1s** |

## 6. Allow-list（ready_for_commit）

Track-A only（排除 console log · 排除 gitignored `raw_metadata/` · 排除 B/C/D 与无关 dirty）：

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s12_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12/`（整根；`raw_metadata/` 按 `.gitignore` 排除；`reports/live_fm12_console_20260715.log` 不入 allow-list）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s12_fm12_20260715.md`

## 7. Gate

```text
a_class_fm12_listing_aware_s12_gate = PASS_WITH_CAVEAT
a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice2_s1_execution_gate = PASS_WITH_CAVEAT
cninfo_calls = 110
ready_for_commit = yes
commit = not_done
push = not_done
```

## 8. Next

```text
Controller：审阅 allow-list → track-A-only commit（无 push）；
下一片：listing-aware S13（AD2E1151–1200 · 独立新根）或 coverage overlay 扩分母；
可选：AD2E1148（301267）not_found 孤立探针（勿 mutate S12 live 主根除非独立 retry 根）；
勿 reopen S8 not_found 除非下一片 blocked；勿 mutate S1–S12 live 根。
```

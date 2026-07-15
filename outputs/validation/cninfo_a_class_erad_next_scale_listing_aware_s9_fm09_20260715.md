# A-FM-09 — Build listing-aware S9 + wire runner + AD2E951–1000 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-09_

> **standing_scope：** full-market periodic / metadata scale  
> **CNINFO live（本 turn）：** **109** · dry-run → bounded live · **未 mutate 封闭 S1–S8 live 根** · **无 commit/push**  
> **Prior：** A-FM-08 S8 AD2E901–950 live 46/50 `PASS_WITH_CAVEAT`（CNINFO=105；4 not_found 未开 isolated retry）

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** build+wire S9 · **3** bounded live proof |
| 选择 | listing-aware builder 生成 S9（AD2E951–1000）→ phase2 接线独立新根 → dry-run → bounded live full50 |
| 为何不是 S8 not_found retry | S8 已过阈值（≥45）；4 个 `not_found` 为结构空结果而非 timeout；standing_scope 优先 metadata scale |
| 为何不是 IDLE | S8 已封闭；prefix_concentration + overlay 分母可复用 |
| Prior | A-FM-08 S8 live PASS_WITH_CAVEAT；A-FM-06 overlay 863→1726 |

## 2. Runner / builder rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9`
2. 禁止写入封闭 S1 / listing-aware S2–S8 live 根
3. case_id：**AD2E951–AD2E1000** · cohort=`next_scale_listing_aware`
4. CNINFO request cap：**120**/run（同 S2–S8）
5. listing_period lint 使用 A 轨 coverage overlay（`cninfo_a_class_basic_profile_coverage_overlay_fm06`）
6. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S8**
7. **prefix_concentration**：本片同一 3 位前缀最多 **25**
8. case_id 模式扩展：`^AD2E\d{3,4}$`（支持 AD2E1000）

## 3. Files

### Created
- `lab/test_cninfo_a_class_erad_listing_aware_s9_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9_fm09_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S9 slice · overlay + prefix cap · exclude S2–S8）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S9 模式接线 · 隔离根 · overlay listing lint · AD2E1000 模式 · 禁止写 S1–S8 live）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S9 case_id_start 单测）

### Reused（未改）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（FM06）

### Not touched（保护）
- 封闭 S1 **live**（mtime 仍为 **14:41**）
- listing-aware S2–S8 **live**（mtime 分别为 17:11 / 17:29 / 17:48 / 18:16 / 20:26 / 20:50 / 21:26）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E951–1000） |
| prefix counts | 000=25 · 002=25（max=25） |
| reject ledger | **301**（a_cumulative_exclude=261 · st_exclude=19 · prefix_concentration_exclude=12 · listing_period_gate=9） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live | 50 executed · **50/50** acceptable · failed/not_found=**0** |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（本 turn） | **109**（cap ≤ 120；builder/dry-run=0） |
| orgid_fallback | hits=**1** · misses=**0** |
| network_timeout | **0** |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50；本片 50/50） |
| closed S1–S8 live roots mutated | **no**（mtime 校验） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `cninfo_a_class_listing_aware_cohort_builder.py --slice s9` | size=50 · CNINFO=0 | ~3.32s |
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 12/12 OK | ~0.16s |
| `test_cninfo_a_class_erad_listing_aware_s9_runner.py` | 5/5 OK | ~0.29s |
| `test_cninfo_a_class_erad_listing_aware_s8_runner.py` | 5/5 OK | ~0.23s |
| dry-run listing-aware S9 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.27s |
| **live listing-aware S9（full50）** | 50/50 PASS_WITH_CAVEAT · CNINFO=109 | **~546.2s** |

## 6. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s9_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9/`（整根；`raw_metadata/` 按 `.gitignore` 排除）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s9_fm09_20260715.md`

**Exclude：** 封闭 S1–S8 live 根；其他 track 脏文件（B/C/D 未请求改动）；未请求的 commit/push。

## 7. capability_gain

```text
capability_gain = true
- listing-aware S9 (AD2E951–1000) built offline with prefix_concentration + FM06 overlay
- wired into phase2 runner under isolated output root
- case_id pattern extended to AD2E\d{3,4} for AD2E1000
- closed prior live roots S1–S8 write-forbidden (mtime verified untouched)
- S9 listing_period lint uses FM06 coverage overlay
- live proof: 50/50 acceptable first-pass (CNINFO=109; threshold >=45 → PASS_WITH_CAVEAT)
- S8 four not_found left for optional later isolated retry (not in this package)
```

## 8. Gate

```text
a_class_fm09_listing_aware_s9_gate = PASS_WITH_CAVEAT
cninfo_calls = 109
live = yes
ready_for_commit = yes
push = no
```

## 9. Next hint

```text
next_hint = 可选对 S8 AD2E918/929/931/938 做 isolated not_found retry（独立根）；
            或继续 listing-aware builder 取 AD2E1001+（独立新根）；
            保持 prefix_concentration + overlay 分母；
            勿 mutate S1–S9 live 根；commit 仅 allow-list；勿 push。
```

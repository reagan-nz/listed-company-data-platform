# A-FM-10 — Build listing-aware S10 + wire runner + AD2E1001–1050 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-10_

> **standing_scope：** full-market periodic / metadata scale  
> **CNINFO live（本 turn）：** **108** · dry-run → bounded live · **未 mutate 封闭 S1–S9 live 根** · **无 commit/push**  
> **Prior：** A-FM-09 S9 AD2E951–1000 live 50/50 `PASS_WITH_CAVEAT`（CNINFO=109）

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** build+wire S10 · **3** bounded live proof |
| 选择 | listing-aware builder 生成 S10（AD2E1001–1050）→ phase2 接线独立新根 → dry-run → bounded live full50 |
| 为何不是 S8 not_found retry | S8 已过阈值（≥45）；4 个 `not_found` 为结构空结果而非 timeout；standing_scope 优先 metadata scale |
| 为何不是 IDLE | S9 已封闭；prefix_concentration + overlay 分母可复用 |
| Prior | A-FM-09 S9 live PASS_WITH_CAVEAT；A-FM-06 overlay 863→1726 |

## 2. Runner / builder rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10`
2. 禁止写入封闭 S1 / listing-aware S2–S9 live 根
3. case_id：**AD2E1001–AD2E1050** · cohort=`next_scale_listing_aware`
4. CNINFO request cap：**120**/run（同 S2–S9）
5. listing_period lint 使用 A 轨 coverage overlay（`cninfo_a_class_basic_profile_coverage_overlay_fm06`）
6. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S9**
7. **prefix_concentration**：本片同一 3 位前缀最多 **25**

## 3. Files

### Created
- `lab/test_cninfo_a_class_erad_listing_aware_s10_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10_fm10_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S10 slice · overlay + prefix cap · exclude S2–S9）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S10 模式接线 · 隔离根 · overlay listing lint · 禁止写 S1–S9 live）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S10 case_id_start 单测）

### Reused（未改）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（FM06）

### Not touched（保护）
- 封闭 S1 **live**（mtime 仍为 **14:41**）
- listing-aware S2–S9 **live**（mtime 分别为 17:11 / 17:29 / 17:48 / 18:16 / 20:26 / 20:50 / 21:26 / 21:41）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E1001–1050） |
| prefix counts | 000=12 · 002=25 · 003=6 · 300=7（max=25） |
| reject ledger | **421**（a_cumulative_exclude=363 · st_exclude=27 · prefix_concentration_exclude=22 · listing_period_gate=9） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live | 50 executed · **50/50** acceptable · failed/not_found=**0** |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（本 turn） | **108**（cap ≤ 120；builder/dry-run=0） |
| orgid_fallback | hits=**1** · misses=**0** |
| network_timeout | **0** |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50；本片 50/50） |
| closed S1–S9 live roots mutated | **no**（mtime 校验） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `cninfo_a_class_listing_aware_cohort_builder.py --slice s10` | size=50 · CNINFO=0 | ~4.66s |
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 13/13 OK | ~0.05s |
| `test_cninfo_a_class_erad_listing_aware_s10_runner.py` | 5/5 OK | ~0.02s |
| `test_cninfo_a_class_erad_listing_aware_s9_runner.py` | 5/5 OK | ~0.03s |
| dry-run listing-aware S10 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.34s |
| **live listing-aware S10（full50）** | 50/50 PASS_WITH_CAVEAT · CNINFO=108 | **~613.6s** |

## 6. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s10_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10/`（整根；`raw_metadata/` 按 `.gitignore` 排除）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s10_fm10_20260715.md`

**Exclude：** 封闭 S1–S9 live 根；其他 track 脏文件（B/C/D 未请求改动）；未请求的 commit/push。

## 7. capability_gain

```text
capability_gain = true
- listing-aware S10 (AD2E1001–1050) built offline with prefix_concentration + FM06 overlay
- wired into phase2 runner under isolated output root
- closed prior live roots S1–S9 write-forbidden (mtime verified untouched)
- S10 listing_period lint uses FM06 coverage overlay
- live proof: 50/50 acceptable first-pass (CNINFO=108; threshold >=45 → PASS_WITH_CAVEAT)
- S8 four not_found left for optional later isolated retry (not in this package)
```

## 8. Gate

```text
a_class_fm10_listing_aware_s10_gate = PASS_WITH_CAVEAT
cninfo_calls = 108
live = yes
ready_for_commit = yes
push = no
```

## 9. Next hint

```text
next_hint = 可选对 S8 AD2E918/929/931/938 做 isolated not_found retry（独立根）；
            或继续 listing-aware builder 取 AD2E1051+（独立新根）；
            保持 prefix_concentration + overlay 分母；
            勿 mutate S1–S10 live 根；commit 仅 allow-list；勿 push。
```

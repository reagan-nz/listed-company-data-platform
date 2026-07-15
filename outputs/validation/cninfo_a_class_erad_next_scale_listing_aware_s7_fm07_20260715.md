# A-FM-07 — Wire listing-aware S7 into phase2 runner + AD2E851–900 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-07_

> **standing_scope：** full-market periodic / metadata scale  
> **CNINFO live（本 turn）：** **105** · dry-run → bounded live · **未 mutate 封闭 S1–S6 live 根** · **无 commit/push**  
> **Prior：** A-FM-06 `8af1962` profile overlay 863→1726 + prefix_concentration + S7 universe offline `PASS_OFFLINE`

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** wire S7 runner · **3** bounded live proof |
| 选择 | phase2 runner 接线 listing-aware S7（独立新根）→ dry-run → bounded live full50 |
| 为何不是 IDLE / 非 profile hardening | S7 universe 已由 FM06 落盘；wiring 未阻塞；standing_scope 覆盖 metadata scale |
| Prior | A-FM-06 S7 AD2E851–900 offline；A-FM-05 S6 live 50/50 CNINFO=111 |

## 2. Runner rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7`
2. 禁止写入封闭 S1 / listing-aware S2–S6 live 根
3. case_id：**AD2E851–AD2E900** · cohort=`next_scale_listing_aware`
4. CNINFO request cap：**120**/run（同 S2–S6）
5. listing_period lint 使用 A 轨 coverage overlay（`cninfo_a_class_basic_profile_coverage_overlay_fm06`）
6. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S6**

## 3. Files

### Created
- `lab/test_cninfo_a_class_erad_listing_aware_s7_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_fm07_20260715.md`（本报告）

### Modified
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S7 模式接线 · 隔离根 · overlay listing lint · 禁止写 S1–S6 live）

### Reused（未改）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_plus50_universe_20260715.csv`（FM06）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_reject_ledger_20260715.csv`（FM06）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（FM06）

### Not touched（保护）
- 封闭 S1 **live**（mtime 仍为 **14:41**）
- listing-aware S2–S6 **live**（mtime 分别为 17:11 / 17:29 / 17:48 / 18:16 / 20:26）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E851–900） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live | 50 executed · **50/50** acceptable · retrieval=found · quality=pass |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（本 turn） | **105**（cap ≤ 120） |
| orgid_fallback | hits=**4** · misses=**0** |
| network_timeout | **0**（无需 isolation retry） |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50） |
| closed S1–S6 live roots mutated | **no**（mtime 校验） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `test_cninfo_a_class_erad_listing_aware_s7_runner.py` | 5/5 OK | ~0.03s |
| `test_cninfo_a_class_erad_listing_aware_s6_runner.py` | 5/5 OK | ~0.02s |
| dry-run listing-aware S7 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.28s |
| **live listing-aware S7（full50）** | 50/50 PASS_WITH_CAVEAT · CNINFO=105 | **~382.1s** |

## 6. Allow-list（ready_for_commit）

1. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
2. `lab/test_cninfo_a_class_erad_listing_aware_s7_runner.py`
3. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7/`（整根；`raw_metadata/` 按 `.gitignore` 排除）
4. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_fm07_20260715.md`

**Exclude：** 封闭 S1–S6 live 根；其他 track 脏文件（B/C/D 未请求改动）；未请求的 commit/push。  
**Note：** S7 universe / reject ledger / overlay 已在 FM06 commit；本包不重复纳入 unless dirty。

## 7. capability_gain

```text
capability_gain = true
- listing-aware S7 (AD2E851–900) wired into phase2 runner under isolated output root
- closed prior live roots S1–S6 write-forbidden (mtime verified untouched)
- S7 listing_period lint uses FM06 coverage overlay (codes absent from C harvest default)
- live proof: 50/50 acceptable first-pass (CNINFO=105; no timeout retry needed)
- prefix-diversified S7 cohort avoided S6-style mono-prefix timeout window
```

## 8. Gate

```text
a_class_fm07_listing_aware_s7_gate = PASS_WITH_CAVEAT
cninfo_calls = 105
live = yes
ready_for_commit = yes
push = no
```

## 9. Next hint

```text
next_hint = 继续 listing-aware builder 取 AD2E901+（独立新根）；
            保持 prefix_concentration + overlay 分母；
            勿 mutate S1–S7 live 根；commit 仅 allow-list；勿 push。
```

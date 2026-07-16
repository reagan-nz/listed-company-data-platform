# A-FM-03 — R19 excellence ladder：S23 listing-aware ~200（AD2E1651–1850）

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-03 · R19 excellence-gated scale_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **CNINFO live（本包）：** **438** · dry-run → bounded live full200 · **未 mutate S1–S22 live 主根** · **无 commit/push**  
> **Prior：** A-FM-02 S22 combined **48/50 = 96%** EXCELLENT → ladder 升至 ~200（禁止继续无尽 +50）

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-03** |
| track | A |
| R19 ladder | ~50（S22 EXCELLENT）→ **~200（本包）** → ~1000（下一候选） |
| 目标 | 新孤立根 S23 · AD2E1651–1850 · builder+runner · dry-run · bounded live |
| 保护 | **禁止** mutate S1–S22 live 主根 |

## 2. Builder / runner rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23`
2. case_id：**AD2E1651–AD2E1850** · size=**200** · cohort=`next_scale_listing_aware`
3. CNINFO request cap：**480**/run
4. prefix_concentration：**100**（~200 尺度）
5. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S22**
6. profile overlay：扩展 latent 纳入 `phase3_batch_500_001`（仅 A overlay symlink · **未写** C harvest 根）
7. dry-run cap 修复：listing-aware 使用模式 cap，避免默认 slice2=240 误杀 planned=400

## 3. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **200**（AD2E1651–1850） |
| prefix counts | 000=40 · 001=12 · 002=86 · 003=4 · 300=58（max≤100） |
| reject ledger | **712** |
| dry-run planned_ok | **200/200** · planned_requests=**400** · CNINFO=**0** |
| dry-run gate | runner_extension `READY_FOR_APPROVAL`（技术可跑；非 governance PASS） |
| live | **200/200** found/pass · not_found=**0** |
| CNINFO calls | **438**（cap ≤ 480） |
| orgid_fallback | hits=**0** · misses=**0** |
| network_timeout | **0** |
| execution gate | `PASS_WITH_CAVEAT` |
| **excellence** | **YES**（100% ≥ 95% · 无残差失败 · 无需 retry） |
| S1–S22 live 主根 mutated | **no**（mtime vs `_tmp_s23_prior_live_mtime_snap.json`） |
| wall live | **~917s** |

## 4. Tests

| 步骤 | 结果 |
|------|------|
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | **26/26 OK**（含 S23 case_id_start） |
| `test_cninfo_a_class_erad_listing_aware_s23_runner.py` | **5/5 OK** |
| `test_cninfo_a_class_erad_listing_aware_s22_runner.py` | **5/5 OK**（回归） |

## 5. Files

### Created / modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S23 ~200）
- `lab/cninfo_a_class_profile_coverage.py`（latent + phase3_batch_500_001）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（S23 模式 · cap=480 · dry-run 模式 cap 修复）
- `lab/test_cninfo_a_class_erad_listing_aware_s23_runner.py`
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S23 单测）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23_plus200_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23_reject_ledger_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23/`（独立根 · dry-run + live）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（symlink 并集扩大 · CNINFO=0）
- `outputs/validation/_tmp_s23_prior_live_mtime_snap.json`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23_fm03_20260716.md`（本报告）

### Not touched（保护）
- S1–S22 **live** 主报告
- B/C/D · commit/push

## 6. Allow-list（ready_for_commit）

Track-A only（排除 console log · 排除 gitignored `raw_metadata/` · 排除 B/C/D · 排除 `_tmp_*`）：

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/cninfo_a_class_profile_coverage.py`
3. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
4. `lab/test_cninfo_a_class_erad_listing_aware_s23_runner.py`
5. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23_plus200_universe_20260716.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23_reject_ledger_20260716.csv`
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23/`（排除 `raw_metadata/` · `*console*`）
9. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s23_fm03_20260716.md`
10. （可选同 commit）S22 FM02 allow-list 见 `..._s22_fm02_20260716.md` §8 — **建议 Controller 分两个 track-A commit：S22 收口 / S23 ladder**

## 7. Gate

```text
a_class_fm03_listing_aware_s23_dryrun_gate = READY_FOR_APPROVAL   # runner extension；CNINFO=0
a_class_fm03_listing_aware_s23_live_gate = PASS_WITH_CAVEAT       # 200/200
a_class_fm03_excellence = YES                                     # 100% >= 95%
cninfo_calls = 438
s1_s22_live_main_roots_mutated = no
ready_for_commit = yes
commit = not_done
push = not_done
```

## 8. Next ladder step

```text
S23 EXCELLENT → 下一档 = listing-aware ~1000 新孤立根（勿再无尽 +50 / 勿重复 +200）
先决：profile overlay / listing_date 分母需再扩大（当前 overlay≈2213；a_exclude 将达 1850）
勿 mutate S1–S23 live 主根；无 B/C/D；无 push
```

# A-FM-05 — R19：分母扩容尝试 + S24 诚实残差 live（≈371）

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-05 · R19 excellence-gated scale_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **本包：** overlay rebuild **CNINFO=0** · 分母**无增量** · S24 **诚实残差 371** dry-run→bounded live · **未**声称 1000 · **未 mutate S1–S23 live 主根** · **无 commit/push** · 无 B/C/D  
> **Prior：** A-FM-04 S24~1000 `DENOMINATOR_BLOCKED`（residual 371 << 1000）

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-05** |
| track | A |
| #1 | 扩 `listing_date` / `company_basic_profile` 分母（offline · overlay CNINFO=0） |
| #2 | 诚实 max residual listing-aware live（新孤立根；excellence≥95%） |
| 保护 | 禁止 mutate S1–S23；禁止伪造 1000；无 commit/push |

## 2. Result

| 项 | 值 |
|----|-----|
| **PASS/FAIL** | **PASS_WITH_CAVEAT**（残差 live；**非** S24~1000） |
| size | **371**（AD2E1851–2221 · **诚实残差**；**不是** 1000） |
| accuracy / excellence | **371/371 = 100%** ≥ 95% · **YES** |
| CNINFO | overlay/rebuild **0** · dry-run **0** · live **754**（cap≤960） · **合计 754** |
| live executed | **yes** |
| S1–S23 live 主根 mutated | **no**（mtime snap 校验） |
| claimed_1000 | **no** |

## 3. Task #1 — denominator expansion（offline · CNINFO=0）

### Probe

| 指标 | 值 |
|------|-----|
| overlay union（refresh 后） | **2213**（无增量） |
| overlay with listing_date | **2207** |
| canon / latent-only | **863** / **1350** |
| A cumulative exclude（含 S23） | **1850** |
| max selectable residual | **371**（与 A-FM-04 一致） |
| S24~1000 shortfall | **629** |
| latent dirs | phase35 / phase35_resume / phase2_smoke_200 / fuller_slice1_200 / phase3_batch_500_001 **均已在 overlay** |
| raw∉overlay | **38**（mapper 全失败 · usable listing_date=**0**） |
| full_market_2024 缺 profile | **3911**（无离线 listing_date 源可补） |

**诚实进度：** 离线并集已耗尽；本轮 **未能** 把残差抬到 ≥1000。扩分母下一步仍需 C-class（或显式授权 A）对缺口码补 `company_basic_profile`（含 F006D），落盘后 A 仅 symlink overlay。

禁止项遵守：未伪造 listing_date；未用 establishment_date 冒充；未放宽 listing_period_gate；未写 C harvest 根。

## 4. Task #2 — S24 residual371 live

### Builder / runner rules（本包冻结）

1. 独立输出根：`outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24`
2. case_id：**AD2E1851–AD2E2221** · size=**371** · cohort=`next_scale_listing_aware`
3. CNINFO request cap：**960**/run
4. prefix_concentration：**371**（残差全量；不因前缀门丢可选码）
5. A cumulative exclude：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S23**
6. 命名：`residual371` · **禁止** 把本包表述为 S24~1000

### Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **371** |
| reject ledger | **1833** |
| dry-run planned_ok | **371/371** · planned_requests=**742** · CNINFO=**0** |
| dry-run gate | runner_extension `READY_FOR_APPROVAL`（技术可跑；非 governance PASS） |
| live | **371/371** found/pass · not_found=**0** |
| CNINFO calls | **754**（cap ≤ 960） |
| orgid_fallback | hits=**0** · misses=**0** |
| network_timeout | **0** |
| execution gate | `PASS_WITH_CAVEAT` |
| **excellence** | **YES**（100% ≥ 95% · 无残差失败 · 无需 retry） |
| S1–S23 live 主根 mutated | **no** |
| wall live | **~1684s**（~28.1 min） |

## 5. Tests

| 步骤 | 结果 |
|------|------|
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | **27/27 OK**（含 S24 case_id_start） |
| `test_cninfo_a_class_erad_listing_aware_s24_runner.py` | **5/5 OK** |
| `test_cninfo_a_class_erad_listing_aware_s23_runner.py` | **5/5 OK**（回归） |

## 6. Files

### Created / modified

- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S24 residual371）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（S24 模式 · cap=960）
- `lab/test_cninfo_a_class_erad_listing_aware_s24_runner.py`
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S24 单测）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_residual371_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_reject_ledger_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24/`（独立根 · dry-run + live）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（symlink refresh · 仍 2213 · CNINFO=0）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_matrix_fm06_20260715.csv`
- `outputs/validation/cninfo_a_class_basic_profile_coverage_fm06_20260715.md`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_fm05_20260716.md`（本报告）

### Not touched（保护）

- S1–S23 **live** 主报告与输出根
- B/C/D · commit/push

### Exclude from commit

- `outputs/validation/_tmp_*`
- `**/raw_metadata/`
- `*console*`

## 7. Allow-list（ready_for_commit）

Track-A only：

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s24_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_residual371_universe_20260716.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_reject_ledger_20260716.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24/`（排除 `raw_metadata/` · `*console*`）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_fm05_20260716.md`
9. （可选）overlay matrix + summary（refresh 无增量）

**建议 commit message：**

```text
feat(a-class): S24 residual371 listing-aware live after denominator stall

Offline overlay stays at 2213; honest residual AD2E1851-2221 runs 371/371
(excellence 100%, CNINFO=754). Does not claim S24~1000; S1-S23 untouched.
```

## 8. Gate

```text
a_class_fm05_denominator_expansion = NO_GROWTH   # still 2213 / residual 371
a_class_fm05_listing_aware_s24_dryrun_gate = READY_FOR_APPROVAL
a_class_fm05_listing_aware_s24_live_gate = PASS_WITH_CAVEAT   # 371/371
a_class_fm05_excellence = YES                                 # 100% >= 95%
a_class_fm05_size_claim = residual_371_not_1000
cninfo_calls = 754
s1_s23_live_main_roots_mutated = no
ready_for_commit = yes
commit = not_done
push = not_done
```

## 9. Issues requiring Controller

**Decision question：** listing-aware 可跑残差已耗尽（本包 371/371）；全市场下一档 ~1000 仍被 profile 分母挡住。是否派 C-class 补 basic_profile？

**Options（最多 2）：**

1. **Preferred — C-class profile harvest 扩分母**（再谈 ~1000）  
   对 full_market 缺口码补 `company_basic_profile`（含 listing_date）；A 仅 overlay symlink（CNINFO=0）。

2. **Close listing-aware residual ladder**  
   承认 overlay 内 listing-aware 残差已清；下一 A 包改其它 standing 任务，勿再伪扩 1000。

**Controller recommendation：** 选 **1** 若仍要 excellence@1000；否则选 **2** 收口残差 ladder。

## 10. Next recommendation（A-class）

```text
residual_listing_aware = EXHAUSTED (371/371 this package)
blocked_for_1000 = profile/listing_date denominator (shortfall 629)
next = C-class（或显式授权）basic_profile harvest → A overlay rebuild (CNINFO=0)
      → only then S25/~1000 listing-aware
do_not = claim 1000; mutate S1–S24 live roots; endless +50; B/C/D; push
```

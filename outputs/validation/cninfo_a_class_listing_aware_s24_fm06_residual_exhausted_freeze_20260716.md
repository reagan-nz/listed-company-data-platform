# A-FM-06 — R19：S24 residual 耗尽冻结 + overlay 离线再探（CNINFO=0）

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-06 · R19 excellence-gated scale_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **本包：** OFFLINE ONLY · **CNINFO=0** · **no live** · 冻结 S24 诚实残差陈述 · overlay 再探 · Controller 包（C profile 前置条件）  
> **禁止：** 声称 ~1000 · mutate S1–S24 live 主根 · B/C/D 改写 · commit/push · 伪造 1000 cohort  
> **Prior：** A-FM-05 committed — S24 residual371 LIVE 371/371 excellence YES；overlay union 2213

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-06** |
| track | A |
| mode | **OFFLINE ONLY** |
| #1 | Freeze attestation：S24 residual exhausted；`size_claim=residual_371_not_1000` |
| #2 | Offline overlay rebuild probe（仅既有 profile∪listing_date 源） |
| #3 | Controller packet：C-class `basic_profile` harvest 须交付什么，A 才能 reopen listing-aware ~1000 |
| #4 | 可选：最小离线 test hardening（无 live / 无 CNINFO） |

## 2. Result

| 项 | 值 |
|----|-----|
| **PASS/FAIL** | **PASS_OFFLINE** |
| CNINFO | **0** |
| live executed | **no** |
| claimed_1000 | **no** |
| S1–S24 live 主根 mutated | **no**（attestation sha256 冻结） |
| size_claim | **residual_371_not_1000**（保持） |
| residual_listing_aware_scale | **EXHAUSTED**（诚实 max 371 已由 S24 跑完） |
| residual_literal_zero | **no** — post-S24 **micro residual = 2**（见下；**不是** scale cohort） |

## 3. Freeze attestation（#1）

### Locked claims

```text
a_class_fm05_size_claim          = residual_371_not_1000   # unchanged
a_class_fm05_excellence          = YES                     # 371/371 historical
a_class_s24_live_size            = 371                     # AD2E1851–2221
a_class_residual_scale_ladder    = EXHAUSTED               # no honest ~1000 from current denominator
a_class_fm06_cninfo_calls        = 0
a_class_fm06_live_executed       = no
s1_s24_live_main_roots_mutated   = no
```

### Attestation file

- `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_freeze_attestation_20260716.csv`

覆盖：S2–S24 live_summary / S24 live 报告与 universe / 既有 overlay matrix 摘要 / cumulative exclude universe 的 sha256。本包**只读冻结**，未改写这些权威 live 根。

### Micro residual（诚实，勿夸大）

S24 在 case 窗 `AD2E1851+` 上的诚实可选上限为 **371**（已 live）。Exclude 含 S24 后，换到 `AD2E2222+` 的 expected_period 窗，仍有 **2** 码可通过 listing_period_gate：

| code | name | listing_date | 说明 |
|------|------|--------------|------|
| 301617 | 博苑新材 | 2024-12-11 | period-window 微残差 |
| 688721 | 龙图光罩 | 2024-08-06 | period-window 微残差 |

台账：`outputs/validation/cninfo_a_class_listing_aware_s24_fm06_micro_residual2_20260716.csv`

**冻结规则：** micro residual=2 **不得**表述为可 reopen ~1000；**不得**单独开 S25 live；scale ladder 仍视为 **EXHAUSTED**。

## 4. Offline overlay rebuild probe（#2）

| 指标 | 值 |
|------|-----|
| 源 | canon ∪ latent（`lab/cninfo_a_class_profile_coverage.py` DEFAULT_*） |
| overlay refresh | **yes**（仅 A 轨 symlink 目录；**未**写 C harvest；**未**碰 S1–S24 live） |
| overlay union | **2213**（无增量） |
| with listing_date | **2207** |
| canon / latent-only | **863** / **1350** |
| post-S24 selectable residual | **2**（micro） |
| residual ≥ 1000? | **NO**（shortfall **998** vs gate） |
| CNINFO | **0** |

探针 JSON：`outputs/validation/cninfo_a_class_listing_aware_s24_fm06_overlay_residual_probe_20260716.json`

**结论：** 既有 profile∪listing_date 离线并集已耗尽；union 仍 2213；**不能**诚实声称 residual≈1000。

## 5. Controller packet（#3）

完整包见：

`outputs/validation/cninfo_a_class_listing_aware_reopen_1000_c_profile_controller_packet_fm06_20260716.md`

缺口码表（full_market − overlay）：

`outputs/validation/cninfo_a_class_listing_aware_fm06_missing_profile_vs_full_market_20260716.csv`  
（**3911** 行 · 只读候选；A 不 harvest）

**Gate（A reopen listing-aware ~1000 之前必须满足）：**

```text
after C harvest lands + A overlay symlink rebuild (CNINFO=0):
  selectable_residual_post_exclude_S24 >= 1000
else:
  DENOMINATOR_BLOCKED — do not open S25/~1000 live
```

## 6. Optional hardening（#4）

- `lab/test_cninfo_a_class_listing_aware_s24_fm06_freeze.py` — 离线断言：CNINFO=0 探针字段、union=2213、residual∈{0,1,2} 微残差、size_claim 冻结、禁止声称 1000。

## 7. Files

### Created（本包）

- `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_freeze_attestation_20260716.csv`
- `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_overlay_residual_probe_20260716.json`
- `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_micro_residual2_20260716.csv`
- `outputs/validation/cninfo_a_class_listing_aware_fm06_missing_profile_vs_full_market_20260716.csv`
- `outputs/validation/cninfo_a_class_listing_aware_reopen_1000_c_profile_controller_packet_fm06_20260716.md`
- `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_residual_exhausted_freeze_20260716.md`（本报告）
- `lab/test_cninfo_a_class_listing_aware_s24_fm06_freeze.py`

### Touched（非 live）

- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/` — symlink refresh only（union 仍 2213）

### Not touched（保护）

- S1–S24 **live** 主报告与输出根内容
- B/C/D harvest / runners
- commit / push

### Exclude from commit

- `outputs/validation/_tmp_*`
- `**/raw_metadata/`
- `*console*`

## 8. Allow-list（ready_for_commit · Controller 决策）

Track-A only：

1. `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_freeze_attestation_20260716.csv`
2. `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_overlay_residual_probe_20260716.json`
3. `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_micro_residual2_20260716.csv`
4. `outputs/validation/cninfo_a_class_listing_aware_fm06_missing_profile_vs_full_market_20260716.csv`
5. `outputs/validation/cninfo_a_class_listing_aware_reopen_1000_c_profile_controller_packet_fm06_20260716.md`
6. `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_residual_exhausted_freeze_20260716.md`
7. `lab/test_cninfo_a_class_listing_aware_s24_fm06_freeze.py`

**建议 commit message：**

```text
docs(a-class): freeze S24 residual-exhausted after overlay stall

Offline probe keeps overlay union at 2213; post-S24 micro residual=2
(not ~1000). Locks size_claim=residual_371_not_1000; CNINFO=0; no live.
```

## 9. Gate

```text
a_class_fm06_gate = PASS_OFFLINE
a_class_fm06_size_claim = residual_371_not_1000
a_class_fm06_overlay_union = 2213
a_class_fm06_residual_post_s24 = 2   # micro; scale EXHAUSTED
a_class_fm06_reopen_1000 = BLOCKED_until_C_profile_residual_ge_1000
cninfo_calls = 0
live_executed = no
s1_s24_live_main_roots_mutated = no
ready_for_commit = yes
commit = not_done
push = not_done
```

## 10. Next recommendation（A-class）

```text
preferred = WAIT for C-class basic_profile harvest (see controller packet)
            → A overlay rebuild CNINFO=0 → residual>=1000 gate → only then S25/~1000
alternate_A_offline_axis = non-listing-aware standing metadata task
                           OR close listing-aware scale ladder documentation-only
do_not = claim 1000; live micro-2 as S25; mutate S1–S24; CNINFO; B/C/D; push
```

# A-FM-01 — Listing-aware next cohort builder + AD2E601–650 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-01_

> **standing_scope：** full-market company information / static metadata  
> **CNINFO live：** bounded · **未 mutate 封闭 S1 live 根** · **无 commit/push**

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** next cohort/slice + **3** generalization（listing_period_gate 复用） |
| 选择 | 自动 listing-aware cohort builder → 生成 AD2E601–650（+50）→ dry-run → bounded live |
| 为何不是 IDLE | standing authorization：下一 cohort/slice **不是** new scope；S1 封闭不构成拒绝理由 |
| 为何不是 O3 +8 微片 | 889 余量 listing_ok 仅 2；全市场 profile 覆盖下 A-disjoint 可达 ≥50 |

## 2. Cohort rules（本包冻结）

1. 源：`company_basic_profile` ∩ `eval_companies_full_market_2024.yaml`
2. 排除 A cumulative：scale-200 ∪ slice1 ∪ slice2 S1
3. ST-EXCLUDE · 非 BSE
4. 分配 `expected_period` 后硬跑 `listing_period_gate`（不通过则跳过；**不**静默改 period）
5. B 轨 overlap：**允许**（跨轨不同维度：A 周期报告元数据 vs B 披露事件）
6. case_id：**AD2E601–AD2E650** · cohort=`next_scale_listing_aware`

## 3. Files

### Created
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
- `lab/test_cninfo_a_class_erad_listing_aware_s2_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2/`（独立输出根）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2_fm01_20260715.md`（本报告）

### Modified
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S2 模式接线 · 隔离根 · A-only overlap lint）

### Not touched（保护）
- 封闭 S1 **live** report / quality / raw_metadata（mtime 仍为 14:41）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E601–650） |
| reject ledger rows | 36（构建扫描中拒绝；含 A 占用/ST/listing_gap 等） |
| profile candidates after prefilter | 53 |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live executed | **50** |
| live acceptable | **50/50**（retrieval=found · quality=pass） |
| CNINFO calls | **110**（cap ≤ 120） |
| orgId offline fallback hits/misses | 0 / 0 |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50） |
| closed S1 live root mutated | **no** |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 4/4 OK | ~0.01s |
| builder generate +50 | OK | ~1.06s |
| `test_cninfo_a_class_erad_listing_aware_s2_runner.py` | 5/5 OK | ~0.02s |
| `test_cninfo_a_class_erad_next_scale_slice2_runner.py` | 23/23 OK | ~2.67s |
| `test_cninfo_a_class_listing_period_gate.py` | 8/8 OK | ~0.01s |
| `test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py` | 23/23 OK | ~0.31s |
| dry-run listing-aware S2 | READY_FOR_APPROVAL | ~0.16s |
| **live listing-aware S2** | **50/50 PASS_WITH_CAVEAT** | **~352.3s** |

## 6. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s2_runner.py`
4. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2/`（整根）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2_fm01_20260715.md`

**Exclude：** 封闭 S1 live 根；其他 track 脏文件；未请求的 commit/push。

## 7. capability_gain

```text
capability_gain = true
- first listing_period_gate-driven automatic A cohort build (beyond S1 lint-only wire)
- AD2E601–650 next-scale path under isolated output root
- A-cumulative-disjoint full-market continuation with B-overlap-allowed policy explicit
- live proof: 50/50 acceptable metadata retrieval (CNINFO=110)
```

## 8. Gate

```text
a_class_fm01_listing_aware_s2_gate = PASS_WITH_CAVEAT
cninfo_calls = 110
live = yes
ready_for_commit = yes
push = no
```

## 9. Next hint

```text
next_hint = 继续 listing-aware builder 取 AD2E651+（仍受 profile 覆盖瓶颈）；
            或扩展 basic_profile 分母后再放大片；勿 mutate S1 live 根。
```

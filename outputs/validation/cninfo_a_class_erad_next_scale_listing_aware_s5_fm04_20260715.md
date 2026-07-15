# A-FM-04 — Listing-aware S5 cohort builder + AD2E751–800 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-04_

> **standing_scope：** full-market periodic / metadata scale  
> **CNINFO live（本 turn）：** **110** · dry-run → bounded live · **未 mutate 封闭 S1 / S2 / S3 / S4 live 根** · **无 commit/push**

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** next cohort/slice（S5）+ **3** generalization（listing_period_gate 复用） |
| 选择 | listing-aware cohort builder `--slice s5` → 生成 AD2E751–800（+50）→ dry-run → bounded live（独立新根） |
| 为何不是 IDLE | standing authorization：下一 cohort/slice **不是** new scope；S1–S4 封闭不构成拒绝理由 |
| Prior failure | 前次 A-FM-04 `resource_exhausted` 无交付物；本 turn 完整重试 |

## 2. Cohort rules（本包冻结）

1. 源：`company_basic_profile` ∩ `eval_companies_full_market_2024.yaml`
2. 排除 A cumulative：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2（AD2E601–650）∪ S3（AD2E651–700）∪ **S4（AD2E701–750）**
3. ST-EXCLUDE · 非 BSE
4. 分配 `expected_period` 后硬跑 `listing_period_gate`（不通过则跳过；**不**静默改 period）
5. B 轨 overlap：**允许**（跨轨不同维度：A 周期报告元数据 vs B 披露事件）
6. case_id：**AD2E751–AD2E800** · cohort=`next_scale_listing_aware`

## 3. Files

### Created / evidence on disk
- `lab/test_cninfo_a_class_erad_listing_aware_s5_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5_fm04_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S5 slice · A exclude 含 S2+S3+S4）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S5 用例）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S5 模式接线 · 隔离根 · 禁止写 S1/S2/S3/S4 live）

### Not touched（保护）
- 封闭 S1 **live** report / quality（mtime 仍为 **14:41**）
- listing-aware S2 **live** report / quality（mtime 仍为 **17:11**）
- listing-aware S3 **live** report / quality（mtime 仍为 **17:29**）
- listing-aware S4 **live** report / quality（mtime 仍为 **17:48**）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E751–800） |
| reject ledger rows | **345**（a_cumulative_exclude=320 · st_exclude=20 · listing_period_gate=5） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100**（每案 topSearch+hisAnnouncement） |
| live executed | **50** |
| live acceptable | **50/50**（retrieval=found · quality=pass） |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls | **110**（cap ≤ 120） |
| orgId offline fallback hits/misses | 0 / 0 |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50） |
| closed S1/S2/S3/S4 live roots mutated | **no** |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 7/7 OK | ~0.09s |
| `test_cninfo_a_class_erad_listing_aware_s5_runner.py` | 5/5 OK | ~0.23s |
| `test_cninfo_a_class_erad_listing_aware_s4_runner.py` | 5/5 OK | ~0.13s |
| `test_cninfo_a_class_erad_listing_aware_s3_runner.py` | 5/5 OK | ~0.13s |
| `test_cninfo_a_class_listing_period_gate.py` | 8/8 OK | ~0.05s |
| dry-run listing-aware S5 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.17s |
| **live listing-aware S5** | **50/50 PASS_WITH_CAVEAT** | **~342.8s**（`live_fm04_console_20260715.log`） |

## 6. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s5_runner.py`
4. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5/`（整根；`raw_metadata/` 按 `.gitignore` 排除）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s5_fm04_20260715.md`

**Exclude：** 封闭 S1–S4 live 根；其他 track 脏文件（B/C/D 未请求改动）；未请求的 commit/push。

## 7. capability_gain

```text
capability_gain = true
- listing_period_gate-driven automatic A cohort build extended to S5 (AD2E751–800)
- A-cumulative exclude now includes listing-aware S2+S3+S4; isolated S5 output root
- live proof: 50/50 acceptable metadata retrieval (CNINFO=110, cap=120)
- closed prior live roots S1–S4 untouched (mtime verified)
```

## 8. Gate

```text
a_class_fm04_listing_aware_s5_gate = PASS_WITH_CAVEAT
cninfo_calls = 110
live = yes
ready_for_commit = yes
push = no
```

## 9. Next hint

```text
next_hint = 继续 listing-aware builder 取 AD2E801+（profile 覆盖接近瓶颈：本片 profile_candidates≈55）；
            或扩展 basic_profile 分母后再放大片；勿 mutate S1–S5 live 根；
            commit 仅 allow-list；勿 push。
```

# A-FM-03 — Listing-aware S4 cohort builder + AD2E701–750 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-03_

> **standing_scope：** full-market periodic / metadata scale  
> **CNINFO live（本 turn）：** **0** · 复用已落盘 live 证据 · **未 mutate 封闭 S1 / S2 / S3 live 根** · **无 commit/push**

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** next cohort/slice（S4）+ **3** generalization（listing_period_gate 复用） |
| 选择 | listing-aware cohort builder `--slice s4` → 生成 AD2E701–750（+50）→ dry-run → bounded live（已完成于磁盘）→ 本包仅收口报告/测试/allow-list |
| 为何不是 IDLE | standing authorization：下一 cohort/slice **不是** new scope；S1/S2/S3 封闭不构成拒绝理由 |
| 为何不是重跑 live | Prior A-FM-03 已 live 完成 50/50 · CNINFO=109 · `PASS_WITH_CAVEAT`；本 turn 仅 package（PING timeout 后收口），禁止再调 CNINFO |

## 2. Cohort rules（本包冻结）

1. 源：`company_basic_profile` ∩ `eval_companies_full_market_2024.yaml`
2. 排除 A cumulative：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2（AD2E601–650）∪ **listing-aware S3（AD2E651–700）**
3. ST-EXCLUDE · 非 BSE
4. 分配 `expected_period` 后硬跑 `listing_period_gate`（不通过则跳过；**不**静默改 period）
5. B 轨 overlap：**允许**（跨轨不同维度：A 周期报告元数据 vs B 披露事件）
6. case_id：**AD2E701–AD2E750** · cohort=`next_scale_listing_aware`

## 3. Files

### Created / evidence on disk
- `lab/test_cninfo_a_class_erad_listing_aware_s4_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4_fm03_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S4 slice · A exclude 含 S2+S3）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S4 用例）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S4 模式接线 · 隔离根 · 禁止写 S1/S2/S3 live）

### Not touched（保护）
- 封闭 S1 **live** report / quality（mtime 仍为 **14:41**）
- listing-aware S2 **live** report / quality（mtime 仍为 **17:11**）
- listing-aware S3 **live** report / quality（mtime 仍为 **17:29**）
- B/C/D 生产根 · commit/push

## 4. Verified metrics（on-disk evidence · 本 turn 未 live）

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E701–750） |
| reject ledger rows | **294**（a_cumulative_exclude=269 · st_exclude=20 · listing_period_gate=5） |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100**（每案 topSearch+hisAnnouncement） |
| live executed | **50** |
| live acceptable | **50/50**（retrieval=found · quality=pass） |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（prior live） | **109**（cap ≤ 240；console 确认） |
| CNINFO calls（本 turn） | **0** |
| orgId offline fallback hits/misses | 0 / 0 |
| execution gate | `PASS_WITH_CAVEAT`（阈值 ≥45/50） |
| closed S1 live root mutated | **no** |
| closed S2 live root mutated | **no** |
| closed S3 live root mutated | **no** |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 6/6 OK | ~0.13s |
| `test_cninfo_a_class_erad_listing_aware_s4_runner.py` | 5/5 OK | ~0.20s |
| `test_cninfo_a_class_erad_listing_aware_s3_runner.py` | 5/5 OK | ~0.11s |
| `test_cninfo_a_class_erad_listing_aware_s2_runner.py` | 5/5 OK | ~0.26s |
| `test_cninfo_a_class_listing_period_gate.py` | 8/8 OK | ~0.08s |
| `test_cninfo_a_class_erad_next_scale_slice2_runner.py` | 23/23 OK | ~2.76s |
| `test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py` | 23/23 OK | ~0.42s |
| dry-run listing-aware S4（已落盘） | READY_FOR_APPROVAL · planned_ok 50/50 | （先前；本 turn 未重跑） |
| **live listing-aware S4（已落盘）** | **50/50 PASS_WITH_CAVEAT** | **~363.1s**（`live_fm03_console_20260715.log`） |

## 6. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s4_runner.py`
4. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4/`（整根；`raw_metadata/` 按 `.gitignore` 排除）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s4_fm03_20260715.md`

**Exclude：** 封闭 S1 live 根；listing-aware S2/S3 live 根；其他 track 脏文件（如 B/C/D 未请求改动）；未请求的 commit/push。

## 7. capability_gain

```text
capability_gain = true
- listing_period_gate-driven automatic A cohort build extended to S4 (AD2E701–750)
- A-cumulative exclude now includes listing-aware S2+S3; isolated S4 output root
- live proof on disk: 50/50 acceptable metadata retrieval (CNINFO=109)
- package-only closure after PING timeout: report + tests + allow-list without re-live
```

## 8. Gate

```text
a_class_fm03_listing_aware_s4_gate = PASS_WITH_CAVEAT
cninfo_calls_prior_live = 109
cninfo_calls_this_turn = 0
live = yes (on-disk evidence; not re-run)
ready_for_commit = yes
push = no
```

## 9. Next hint

```text
next_hint = 继续 listing-aware builder 取 AD2E751+（仍受 profile 覆盖瓶颈）；
            或扩展 basic_profile 分母后再放大片；勿 mutate S1/S2/S3 live 根；
            commit 仅 allow-list；勿 push。
```

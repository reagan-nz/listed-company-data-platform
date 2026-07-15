# A-FM-05 — Listing-aware S6 cohort builder + AD2E801–850 dry-run/live

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-05_

> **standing_scope：** full-market periodic / metadata scale  
> **CNINFO live（本 turn）：** **111** · dry-run → bounded live + timeout isolated retry · **未 mutate 封闭 S1 / S2 / S3 / S4 / S5 live 根** · **无 commit/push**  
> **相对 `4d35d75`：** 该 commit 将 gate 叙事冻结为 FAIL_REVIEW_REQUIRED（32/50）；但盘上权威 live CSV/summary 已为 merged **50/50**。本报告以盘上权威证据为准，**纠正**为 `PASS_WITH_CAVEAT`。

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** next cohort/slice（S6）+ **3** generalization（listing_period_gate 复用） |
| 选择 | listing-aware cohort builder `--slice s6` → 生成 AD2E801–850（+50）→ dry-run → bounded live（独立新根）→ 18×network_timeout 隔离重试合并 |
| 为何不是 IDLE / 非 basic_profile 扩展 | probe：exclude 至 S5 后仍有 eligible_pre_gate≈212 · max_passable≈192；**分母未阻塞**；优先 AD2E801+ |
| Prior | A-FM-04 `fd316a9` S5 AD2E751–800 live 50/50 CNINFO=110 |

## 2. Cohort rules（本包冻结）

1. 源：`company_basic_profile` ∩ `eval_companies_full_market_2024.yaml`
2. 排除 A cumulative：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2–**S5**
3. ST-EXCLUDE · 非 BSE
4. 分配 `expected_period` 后硬跑 `listing_period_gate`（不通过则跳过；**不**静默改 period）
5. B 轨 overlap：**允许**（跨轨不同维度）
6. case_id：**AD2E801–AD2E850** · cohort=`next_scale_listing_aware`

## 3. Files

### Created / evidence on disk
- `lab/test_cninfo_a_class_erad_listing_aware_s6_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6/`（独立输出根 · dry-run + live + retry 子根 + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_fm05_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S6 slice · A exclude 含 S2+S3+S4+S5）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S6 用例）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S6 模式接线 · 隔离根 · 禁止写 S1–S5 live）

### Not touched（保护）
- 封闭 S1 **live** report / quality（mtime 仍为 **14:41**）
- listing-aware S2 **live**（mtime **17:11**）
- listing-aware S3 **live**（mtime **17:29**）
- listing-aware S4 **live**（mtime **17:48**）
- listing-aware S5 **live**（mtime **18:16**）
- B/C/D 生产根 · commit/push

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E801–850） |
| reject ledger rows | **396**（a_cumulative_exclude=370 · st_exclude=20 · listing_period_gate=6） |
| profile_candidates（builder scan-to-fill） | **56** |
| dry-run planned_ok | **50/50** |
| dry-run planned_requests | **100** |
| live first-pass | 50 executed · **32/50** acceptable · 18×`network_timeout` · CNINFO=**71** · gate=`FAIL_REVIEW_REQUIRED` |
| retry AD2E801–810 | **10/10** · CNINFO=**22** |
| retry AD2E819–826 | **8/8** · CNINFO=**18** |
| **merged live** | **50/50** acceptable（retrieval=found · quality=pass） |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（本 turn 合计） | **111**（71+22+18 · cap ≤ 120/run） |
| execution gate（merged） | `PASS_WITH_CAVEAT`（阈值 ≥45/50） |
| closed S1–S5 live roots mutated | **no** |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 8/8 OK | ~0.02s |
| `test_cninfo_a_class_erad_listing_aware_s6_runner.py` | 5/5 OK | ~0.01s |
| `test_cninfo_a_class_erad_listing_aware_s5_runner.py` | 5/5 OK | ~0.03s |
| `test_cninfo_a_class_listing_period_gate.py` | 8/8 OK | ~0.01s |
| dry-run listing-aware S6 | READY_FOR_APPROVAL · planned_ok 50/50 | ~0.36s |
| **live listing-aware S6（full50）** | 32/50 FAIL_REVIEW_REQUIRED | **~879.4s** |
| **retry 801–810** | 10/10 PASS_WITH_CAVEAT | **~52.9s** |
| **retry 819–826** | 8/8 PASS_WITH_CAVEAT | **~58.2s** |
| merge offline | 50/50 PASS_WITH_CAVEAT | ~0.5s |

## 6. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s6_runner.py`
4. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6/`（整根含 retry 子根与 merged reports；`raw_metadata/` 按 `.gitignore` 排除）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_fm05_20260715.md`

**Exclude：** 封闭 S1–S5 live 根；其他 track 脏文件（B/C/D 未请求改动）；未请求的 commit/push。

## 7. capability_gain

```text
capability_gain = true
- listing_period_gate-driven automatic A cohort build extended to S6 (AD2E801–850)
- A-cumulative exclude now includes listing-aware S2–S5; isolated S6 output root
- live proof: 50/50 acceptable after timeout isolated retry merge (CNINFO=111)
- closed prior live roots S1–S5 untouched (mtime verified)
- confirmed profile denominator not yet blocking (eligible_pre_gate≈212 post-S5)
```

## 8. Gate

```text
a_class_fm05_listing_aware_s6_gate = PASS_WITH_CAVEAT
cninfo_calls = 111
live = yes
ready_for_commit = yes
push = no
```

## 9. Next hint

```text
next_hint = 继续 listing-aware builder 取 AD2E851+（独立新根）；
            profile 分母仍充足（post-S6 eligible 仍百级）；
            勿 mutate S1–S6 live 根；commit 仅 allow-list；勿 push。
```

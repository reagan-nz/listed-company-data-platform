# A-FM-05 — Listing-aware S6 cohort builder + AD2E801–850 dry-run/live（package-only）

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-05_

> **standing_scope：** full-market periodic / metadata scale  
> **本 turn：** **package-only** · **CNINFO = 0** · **不**重跑 live · **不** inflate gate  
> **先验 live（已在盘）：** acceptable **32/50** · failed/needs_review **18** · CNINFO=**71** · gate **`FAIL_REVIEW_REQUIRED`**（阈值 ≥45/50）  
> **未 mutate 封闭 S1 / S2 / S3 / S4 / S5 live 根** · **无 commit/push** · **无 B/C/D**

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** next cohort/slice（S6）+ **3** generalization（listing_period_gate 复用） |
| 本 turn 动作 | 盘上 live 已完成但 agent stalled → **仅打包**诚实报告 + 复测 + allow-list |
| 为何不是 IDLE | standing authorization：下一 cohort/slice **不是** new scope；S1–S5 封闭不构成拒绝理由 |
| Prior live | 已落盘于 `…/listing_aware_s6/`；本 turn **禁止**再调 CNINFO |

## 2. Cohort rules（本包冻结）

1. 源：`company_basic_profile` ∩ `eval_companies_full_market_2024.yaml`
2. 排除 A cumulative：scale-200 ∪ slice1 ∪ slice2 S1 ∪ listing-aware S2（AD2E601–650）∪ S3（AD2E651–700）∪ S4（AD2E701–750）∪ **S5（AD2E751–800）**
3. ST-EXCLUDE · 非 BSE
4. 分配 `expected_period` 后硬跑 `listing_period_gate`（不通过则跳过；**不**静默改 period）
5. B 轨 overlap：**允许**（跨轨不同维度）
6. case_id：**AD2E801–AD2E850** · cohort=`next_scale_listing_aware`

## 3. Files

### Created / evidence on disk
- `lab/test_cninfo_a_class_erad_listing_aware_s6_runner.py`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6/`（独立输出根 · dry-run + live + raw_metadata×50）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_fm05_20260715.md`（本报告）

### Modified（本包相关）
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S6 slice · A exclude 含 S2+S3+S4+S5）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（S6 用例）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（listing-aware S6 模式接线 · 隔离根 · 禁止写 S1–S5 live）

### Not touched（保护 · mtime 核验）
- 封闭 S1 **live** summary：mtime **14:41**
- listing-aware S2 **live** summary：mtime **17:11**
- listing-aware S3 **live** summary：mtime **17:29**
- listing-aware S4 **live** summary：mtime **17:48**
- listing-aware S5 **live** summary：mtime **18:16**
- B/C/D 生产根 · commit/push

### Explicitly excluded from allow-list
- 无关脏文件：slice1 / scale-200 / slice2_s1 dryrun 漂移、D-class dryrun 摘要、C-track `_mock_*` 临时根
- `retry_timeout_801_810/`：不完整旁路 retry 痕迹（**未**并入权威 gate；**不**用于 inflate）

## 4. Verified metrics（权威 = 全量 50 案 live 报告）

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E801–850） |
| reject ledger rows | **396**（a_cumulative_exclude=370 · st_exclude=20 · listing_period_gate=6） |
| builder profile_candidates（S6 构建） | **56**（a_exclude=800） |
| dry-run planned_ok | **50/50**（CSV；planned_requests=**100**） |
| live executed | **50** |
| live acceptable | **32/50**（retrieval=found · quality=pass） |
| live failed / needs_review | **18/50**（全部 `network_timeout` · notes 含 orgId fallback hit） |
| raw_metadata JSON | **50**（gitignored under `**/raw_metadata/`） |
| CNINFO calls（先验 live） | **71**（cap ≤ 120；console `cninfo_calls=71`） |
| CNINFO calls（本 turn） | **0** |
| orgId offline fallback hits/misses | **18** / **0** |
| execution gate | **`FAIL_REVIEW_REQUIRED`**（阈值 ≥45/50 → PASS_WITH_CAVEAT；**未达标**） |
| closed S1–S5 live roots mutated | **no** |

### Failure ledger（18 · 诚实记录 · 不重分类为 PASS）

`AD2E801–810` · `AD2E819–826`：`retrieval_status=not_found` · `quality_status=needs_review` · `last_err=network_timeout`。

> 旁路目录 `retry_timeout_801_810/` 与 `live_fm05_retry_801_810_console.log` 显示对 801+ 的**不完整** retry 曾出现 found/pass，但**未**写回权威 `*_live_report.csv` / summary。本包 **拒绝**用其抬升 32/50 或改写 gate。

## 5. Tests / wall times（本 turn · CNINFO=0）

| 步骤 | 结果 | wall |
|------|------|------|
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 8/8 OK | ~0.14s |
| `test_cninfo_a_class_erad_listing_aware_s6_runner.py` | 5/5 OK | ~0.23s |
| `test_cninfo_a_class_erad_listing_aware_s5_runner.py` | 5/5 OK | ~0.18s |
| `test_cninfo_a_class_erad_listing_aware_s4_runner.py` | 5/5 OK | ~0.19s |
| `test_cninfo_a_class_listing_period_gate.py` | 8/8 OK | ~0.07s |
| dry-run listing-aware S6（先验） | planned_ok 50/50 · READY_FOR_APPROVAL | 盘上已有 |
| **live listing-aware S6（先验 · 不重跑）** | **32/50 FAIL_REVIEW_REQUIRED** | **~879.4s**（`live_fm05_console_20260715.log`） |

## 6. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s6_runner.py`
4. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_plus50_universe_20260715.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_reject_ledger_20260715.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6/`（整根；`raw_metadata/` 与旁路 `retry_timeout_801_810/` 按 `.gitignore` / 审阅排除策略处理）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6_fm05_20260715.md`

**Exclude：** 封闭 S1–S5 live 根；其他 track 脏文件（B/C/D / `_mock_*`）；slice1/scale-200/D-class dryrun 漂移；未请求的 commit/push。

## 7. capability_gain

```text
capability_gain = true (builder/runner 扩展成立；live 未达阈值)
- listing_period_gate-driven automatic A cohort build extended to S6 (AD2E801–850)
- A-cumulative exclude now includes listing-aware S2+S3+S4+S5; isolated S6 output root
- live evidence on disk: 32/50 acceptable metadata (CNINFO=71 prior); gate FAIL_REVIEW_REQUIRED
- package-only closure after agent stall: report + tests + allow-list without re-live
- closed prior live roots S1–S5 untouched (mtime verified)
```

## 8. Gate

```text
a_class_fm05_listing_aware_s6_gate = FAIL_REVIEW_REQUIRED
cninfo_calls_prior_live = 71
cninfo_calls_this_turn = 0
live = yes (on-disk evidence; not re-run)
acceptable = 32/50
threshold = >=45/50
ready_for_commit = yes
push = no
```

**不是 PASS** · **不是 PASS_WITH_CAVEAT** · **不是 verified** · **不是 production_ready**

## 9. Next hint

```text
next_hint = 优先做 profile 覆盖 / cohort 过滤改进（收紧超时敏感窗、过滤不稳定板/代码段、
            或扩展 basic_profile 分母后再取 AD2E851+）；
            勿用旁路 retry 或假 PASS 抬升本包 gate；
            勿 mutate S1–S6 live 根；commit 仅 allow-list；勿 push；
            若需补救 18 案 timeout，须独立批准的 bounded retry（非本 package turn）。
```

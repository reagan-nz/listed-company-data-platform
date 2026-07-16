# A-FM-07 — ALTERNATE A OFFLINE AXIS：A erad protected-root freeze

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-07 · R19_

> **standing_scope：** A-class metadata QA（**非** listing-aware S25/~1000）  
> **本包：** OFFLINE ONLY · **CNINFO=0** · **no live** · ladder CLOSED 结案 + protected-root 冻结  
> **禁止：** live micro-2 · 声称 ~1000 · mutate S2–S24 live 主根 · B/C/D · commit/push · PDF/OCR/DB/MinIO/RAG

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-07** |
| track | A |
| mode | **OFFLINE ONLY** |
| #1 | 正式关闭 listing-aware scale ladder（短结案注；引用 FM06） |
| #2 | 选定 **一条** 非 S25/~1000 离线轴：`a_erad_protected_root_freeze` |
| #3 | 测试通过 · fail_count=0 · KEEP no live |
| #4 | 无 commit/push |

## 2. Result

| 项 | 值 |
|----|-----|
| **PASS/FAIL** | **PASS_OFFLINE** |
| CNINFO | **0** |
| live executed | **no** |
| listing_aware_scale_ladder_gate | **CLOSED** |
| claimed_1000 | **no** |
| S2–S24 live 主根 mutated | **no**（FM06 交叉校验 0 drift） |
| alternate_axis | **a_erad_protected_root_freeze** |
| protected_root_count | **30**（不含 MOCK 行） |
| anchor_frozen_ok | **31/31** |
| fm06_match_count | **26**（FM06 已登记路径全部 MATCH） |

## 3. Ladder closure（#1）

短结案注：

`outputs/validation/cninfo_a_class_listing_aware_scale_ladder_fm07_closed_20260716.md`

锁定：

```text
listing_aware_scale_ladder_gate = CLOSED
size_claim = residual_371_not_1000
overlay_union = 2213
micro_residual_post_s24 = 2
reopen_1000 = BLOCKED_until_C_basic_profile
```

## 4. Alternate offline axis（#2）

**选择：** protected-root freeze for A erad outputs（**不是** cohort builder / S25 / ~1000）。

动机：ladder 已 CLOSED；在等待 C `basic_profile` 期间，用最小隔离工件把 S2–S24 live 主根与 Phase2 基线登记为 `read_only_no_mutate` / `read_only_baseline_no_overwrite`，并对照 FM06 attestation 做零漂移交叉校验。

### 隔离目录

`outputs/validation/_a_fm07_erad_protected_root_freeze/`

| 文件 | 作用 |
|------|------|
| `protected_roots.csv` | 站立保护根登记 |
| `freeze_attestation.csv` | 锚点 sha256 + FM06 交叉 |
| `protected_root_existence.csv` | 目录/文件存在性 |
| `fm07_attestation_probe.json` | 离线探针摘要 |

### Dated validation copies

- `outputs/validation/cninfo_a_class_erad_protected_output_roots_fm07_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_protected_root_freeze_attestation_fm07_20260716.csv`
- `outputs/validation/cninfo_a_class_fm07_attestation_probe_20260716.json`

### Registry 要点

- **A-ROOT-S2 … A-ROOT-S24**：listing-aware live 主根 · `read_only_no_mutate`
- **A-ROOT-SCALE200 / SLICE1**：早期 erad live 根 · `read_only_no_mutate`
- **A-ROOT-PHASE2-***：Phase2 expansion/retry 基线 · `read_only_baseline_no_overwrite`
- **A-ROOT-FM06-FREEZE**：FM06 attestation · `read_only_no_overwrite`
- **无** `listing_aware_s1/` 目录（命名从 S2 起；不伪造 S1）

### FM06 交叉校验

对 FM06 freeze CSV 中已登记且本包复算的路径：**全部 MATCH · drift=0**。证明本包未改写 S2–S24 live 主报告内容。

## 5. Tests（#3）

- `lab/test_cninfo_a_class_fm07_erad_protected_root_freeze.py`
- 回归：`lab/test_cninfo_a_class_listing_aware_s24_fm06_freeze.py`

期望：`fail_count=0` · CNINFO=0 · 无 live。

## 6. Files

### Created（本包）

- `outputs/validation/cninfo_a_class_listing_aware_scale_ladder_fm07_closed_20260716.md`
- `outputs/validation/cninfo_a_class_fm07_erad_protected_root_freeze_20260716.md`（本报告）
- `outputs/validation/cninfo_a_class_erad_protected_output_roots_fm07_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_protected_root_freeze_attestation_fm07_20260716.csv`
- `outputs/validation/cninfo_a_class_fm07_attestation_probe_20260716.json`
- `outputs/validation/_a_fm07_erad_protected_root_freeze/`（隔离工件）
- `lab/test_cninfo_a_class_fm07_erad_protected_root_freeze.py`

### Not touched（保护）

- S2–S24 **live** 主根内容
- B/C/D
- commit / push
- CNINFO / PDF / OCR / DB / MinIO / RAG

## 7. Allow-list（ready_for_commit · Controller 决策）

Track-A only：

1. `outputs/validation/cninfo_a_class_listing_aware_scale_ladder_fm07_closed_20260716.md`
2. `outputs/validation/cninfo_a_class_fm07_erad_protected_root_freeze_20260716.md`
3. `outputs/validation/cninfo_a_class_erad_protected_output_roots_fm07_20260716.csv`
4. `outputs/validation/cninfo_a_class_erad_protected_root_freeze_attestation_fm07_20260716.csv`
5. `outputs/validation/cninfo_a_class_fm07_attestation_probe_20260716.json`
6. `outputs/validation/_a_fm07_erad_protected_root_freeze/`
7. `lab/test_cninfo_a_class_fm07_erad_protected_root_freeze.py`

**建议 commit message：**

```text
docs(a-class): close listing-aware ladder; freeze A erad protected roots

Offline A-FM-07: gate CLOSED after FM06; register S2–S24/phase2 roots
as read-only; CNINFO=0; no live; reopen_1000 still wait-for-C.
```

## 8. Gate

```text
a_class_fm07_gate = PASS_OFFLINE
listing_aware_scale_ladder_gate = CLOSED
a_class_fm07_alternate_axis = a_erad_protected_root_freeze
a_class_fm07_cninfo_calls = 0
a_class_fm07_live_executed = no
s2_s24_live_main_roots_mutated = no
reopen_1000 = BLOCKED_until_C_basic_profile
ready_for_commit = yes
commit = not_done
push = not_done
```

## 9. Next recommendation（A-class）

```text
preferred = WAIT for C-class basic_profile harvest
            → A overlay rebuild CNINFO=0 → residual>=1000 gate
            → only then reopen listing-aware ~1000 / S25
alternate_A_offline = phase2 dry-path re-attestation OR cohort-builder
                      regression pack（仍禁止 S25/~1000 live）
do_not = claim 1000; live micro-2; mutate S2–S24; CNINFO; B/C/D; push
```

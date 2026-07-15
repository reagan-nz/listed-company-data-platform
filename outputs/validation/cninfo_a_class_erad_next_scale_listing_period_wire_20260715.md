# A-R16-03 — Wire listing_period_gate into next-scale lint / builder path

_生成时间：2026-07-15_

> **offline only** · **CNINFO = 0** · **无 live** · **无 commit/push** · **未 mutate 封闭 S1 live 根**

## 1. Objective

将 `lab/cninfo_a_class_listing_period_gate.py` 接入 A-class next-scale slice2 **lint / future cohort builder** 路径，使未来 cohort 在 `expected_period` 早于 `listing_date` 或 `listing_date` 为空时 **reject**；封闭 S1 已知三案 **flag only**。

## 2. Wiring

| 入口 | 行为 |
|------|------|
| `lint_erad_next_scale_slice2_overlap` | 末尾调用 L-D6；非 grandfather 案 blocking |
| `lint_erad_next_scale_slice2_listing_period` | 返回 `(blocking, flags)` |
| `filter_erad_next_scale_slice2_cases_by_listing_period` | **未来 builder 硬拒**（无 grandfather） |
| `process_erad_next_scale_slice2_dry_run` | 行级 `listing_period_flag=` 标注冻结三案 |

Grandfather（仅 dry-run / overlap 不阻断）：`AD2E578` / `AD2E590` / `AD2E598`（A-R16-02 已证 listing_gap/unlisted）。

## 3. Verified metrics

| 指标 | 值 |
|------|-----|
| 冻结 S1 universe | 100 |
| listing_ok | 97 |
| L-D6 grandfather flags | 3 |
| L-D6 blocking（含 grandfather） | 0 |
| builder filter rejected | 3 |
| builder filter kept | 97 |
| CNINFO calls | **0** |

## 4. Tests / wall times

| 测试 | 结果 | wall |
|------|------|------|
| `lab/test_cninfo_a_class_listing_period_gate.py` | 8/8 OK | ~0.14s |
| `lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py` | 23/23 OK | ~3.52s |
| `lab/test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py` | 23/23 OK | ~0.40s |
| `lab/test_cninfo_a_class_orgid_fallback_hook.py` | 10/10 OK | ~6.92s |

## 5. Gate

```text
a_class_erad_next_scale_listing_period_wire_gate = PASS_OFFLINE
cninfo_calls = 0
live = no
ready_for_commit = yes
```

## 6. Allow-list for commit（A-R16-03 only）

1. `lab/cninfo_a_class_listing_period_gate.py`
2. `lab/test_cninfo_a_class_listing_period_gate.py`
3. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
4. `lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py`
5. `lab/test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_period_wire_20260715.md`（本文件）

**Exclude：** 封闭 S1 live 根与其 dryrun 产物；C/D/其他 track；未请求的 commit/push。

## 7. Next

```text
next_hint = 下一 slice/cohort 选码时调用
            filter_erad_next_scale_slice2_cases_by_listing_period
            （或 gate.filter_codes_passing_listing_period）
```

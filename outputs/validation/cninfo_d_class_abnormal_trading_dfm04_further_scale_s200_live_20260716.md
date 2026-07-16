# CNINFO D 类 abnormal_trading — D-FM-04 / R19 Further-Scale S200 Bounded Live

_生成时间：2026-07-16 · D-FM-04 · R19 continuous async · excellence-gated scale_

> **性质：** abnormal_trading further-scale ~200 · dry-run CNINFO=0 → bounded live CNINFO=2（按日共享）· universe cite CNINFO=2 · **execution_gate = PASS_WITH_CAVEAT** · **excellence = YES** · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **ladder：** ~5–10 → ~50（D-FM-03 EXCELLENT）→ **~200（本包 EXCELLENT）** → 推荐下一步 ~1000

---

## Task Card

| 项 | 值 |
|----|-----|
| task_id | **D-FM-04** |
| track / executor | D / d-class-executor |
| standing_scope | shareholder / capital / abnormal_trading further-scale S200 |
| cohort | **DAT301–DAT500（200）** |
| compose | primary denser-day `2026-07-02` 全量可用 **156** + adjacent `2026-07-01` 增量 **39** + empty **5** |
| shared probes | 按日各 1 · page=1 · rows=300 · live CNINFO=**2** |
| universe cite | primary+adjacent marketList · CNINFO=**2** |
| ESS H3/H4 | **未触碰**（paused） |
| DLC006R | **未 reopen** |
| A/B/C | **未触碰** |
| S50 / next_slice | **未 mutate**（见 freeze attestation） |

---

## Excellence Gate

| 指标 | 阈值 | 实测 | 判定 |
|------|------|------|------|
| acceptable rate | ≥ 95% | **100.00%（200/200）** | PASS |
| failed / http_error | = 0 | **0** | PASS |
| caveats documented | required | multi_day_compose_not_full_market · detail_nested_deferred | PASS |
| **excellence** | all of above | **YES** | **scale-up authorized** |

---

## Gates

```text
d_class_abnormal_trading_further_scale_s200_dryrun_gate = PASS_OFFLINE
d_class_abnormal_trading_further_scale_s200_execution_gate = PASS_WITH_CAVEAT
d_class_abnormal_trading_further_scale_s200_live_executed = true
d_class_abnormal_trading_further_scale_s200_live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
acceptable = 200/200
acceptable_rate = 100.00%
found = 195
empty_but_valid = 5
failed_or_http_error = 0
cninfo_universe_cite = 2
cninfo_dryrun = 0
cninfo_live = 2
cninfo_package_total = 4
controller_execution_allowed = false
```

**强制语义：** `PASS_WITH_CAVEAT` ≠ bare PASS ≠ verified ≠ production_ready。

---

## Results

### Universe cite（CNINFO=2）

| 项 | 值 |
|----|-----|
| primary denser-day | `2026-07-02` · marketList total **170** · unique after exclusions **156** · selected **156** |
| adjacent day | `2026-07-01` · marketList total **124** · adjacent-only available **76** · selected **39** |
| empty controls | **5**（000895 / 601988 / 600519 / 000858 / 601318 · cite-verified absent） |

### Dry-run（CNINFO=0）

| 项 | 值 |
|----|-----|
| planned_ok | **200/200** |
| planned_shared_days | **2** |
| isolated root | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200/` |

### Bounded live（CNINFO=2）

| 项 | 值 |
|----|-----|
| acceptable | **200/200** |
| found | **195**（DAT301–DAT495） |
| empty_but_valid | **5**（DAT496–DAT500） |
| failed / http_error | **0** |
| PDF/OCR/DB/MinIO/RAG | **no** |

Primary caveat：`multi_day_compose_not_full_market` — primary+adjacent 拼合子集 ≠ 全市场；本包证明 ~200 规模 found-path + empty-control 稳定性。

---

## Freeze Attestation（未 mutate）

```text
AT further_scale S50 live_report sha256 = 88d77c2b60bb28535a2d073009a0f734056ad995a0deb1b1f99d27300225253c
AT further_scale S50 live_summary sha256 = 2d5a2858495dd517996edd55cef2160b328b14694ff999b0f2aa225ba14ee918
AT further_scale S50 lock sha256 = 98cd6393f5fd242d49a0c8a7a1bf3baf0512d97404aa157d001f5deb593bcfe7
AT next-slice dryrun_report sha256 = 51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497
ESH next-slice lock sha256 = 4213de37e19d1d6bd920a9b2efd24495338a27eeb17f2602a8159fbb4b6d2fd1
ESH next-slice live_report sha256 = dc16b591b117a9411c0ec458a1ff3cdb4d850417fcf87d5de851c5c73af23e25
SC next dryrun_report sha256 = 5abc61e4f7ea6014af7e50847aefc7e46f4e39e3ba10e394fd56e683b19a08a5
EP next dryrun_report sha256 = 054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e
RSU next dryrun_report sha256 = 87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c
```

---

## Deliverables

| 项 | 路径 |
|----|------|
| runner | `lab/run_cninfo_d_class_abnormal_trading_further_scale_s200.py` |
| tests | `lab/test_cninfo_d_class_abnormal_trading_further_scale_s200_runner.py` |
| universe lock | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_universe_lock_20260716.csv` |
| marketList cite | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_marketlist_cite_20260716.json` |
| isolated root | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200/` |
| dry-run / live / quality reports | `.../reports/` |
| evidence（本文件） | `outputs/validation/cninfo_d_class_abnormal_trading_dfm04_further_scale_s200_live_20260716.md` |
| freeze attestation | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_freeze_attestation_20260716.csv` |
| next step | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_next_step_recommendation_20260716.md` |
| command draft | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_command_draft_20260716.md` |

---

## Tests

| 测试 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_abnormal_trading_further_scale_s200_runner.py` | **PASS** |
| `lab/test_cninfo_d_class_abnormal_trading_further_scale_runner.py` | **回归 PASS**（S50 未破坏） |

---

## Explicit Non-Claims

- **不是** verified / production_ready / bare PASS
- **不是** ESS H3/H4 / DLC006R reopen
- **不是** A/B/C 变更
- **无** commit / push / git add（executor）
- 未 mutate S50 further_scale / next_slice 冻结根

---

## Commit Boundary（Controller）

```text
ready_for_commit = true
allow_list =
  lab/run_cninfo_d_class_abnormal_trading_further_scale_s200.py
  lab/test_cninfo_d_class_abnormal_trading_further_scale_s200_runner.py
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200/
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_universe_lock_20260716.csv
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_marketlist_cite_20260716.json
  outputs/validation/cninfo_d_class_abnormal_trading_dfm04_further_scale_s200_live_20260716.md
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_freeze_attestation_20260716.csv
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_next_step_recommendation_20260716.md
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_command_draft_20260716.md
exclude = A/B/C · S50 further_scale frozen root · next_slice · ESH/SC/EP/RSU/FIA · ESS · console logs
```

Suggested message:

```text
feat(d-class): AT further-scale ~200 multi-day live (DAT301-500)

Compose denser-day 2026-07-02 full usable codes with adjacent 2026-07-01
increments plus empty controls on isolated s200 root; dry-run CNINFO=0
then dual shared-probe live CNINFO=2 with excellence PASS_WITH_CAVEAT
(200/200 acceptable).
```

---

## Next D Candidate

```text
next_d_candidate = abnormal_trading_further_scale_s1000_bounded_live
scale_ladder = 5-10(done) → 50(done D-FM-03 EXCELLENT) → 200(done D-FM-04 EXCELLENT) → 1000(next)
ess_h3_h4 = paused_pending_devtools
dlc006r = closed
```

Excellence note：本包 200/200 · failed/http_error=0 · caveats documented → **推荐 ladder 下一步 ~1000**（新孤立根；仍勿 inflate 若非 excellent）。

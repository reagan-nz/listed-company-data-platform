# CNINFO D 类 abnormal_trading — D-FM-03 / R19 Further-Scale ~50 Bounded Live

_生成时间：2026-07-16 · D-FM-03 · R19 continuous async · course-corrected from tiny DAT101–105_

> **性质：** abnormal_trading further-scale ~50 · dry-run CNINFO=0 → bounded live CNINFO=1 · universe cite CNINFO=1 · **execution_gate = PASS_WITH_CAVEAT** · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **prefer taken：** AT denser-day further-scale ~50（isolated root）— 快于 ESH further-scale；supersedes tiny next-slice DAT101–105 作为本包主交付

---

## Task Card

| 项 | 值 |
|----|-----|
| task_id | **D-FM-03**（R19 · controller course correction） |
| track / executor | D / d-class-executor |
| standing_scope | shareholder / capital / abnormal_trading further-scale |
| cohort | **DAT201–DAT250（50）** |
| shared probe | sdate=edate=`2026-07-02` · page=1 · **rows=200** · CNINFO=**1**（live） |
| universe cite | denser-day marketList snapshot · CNINFO=**1** |
| ESS H3/H4 | **未触碰**（paused） |
| DLC006R | **未 reopen** |
| A/B/C | **未触碰** |

---

## Prefer Decision

| 选项 | 取舍 |
|------|------|
| AT further-scale ~50（denser-day marketList lock） | **primary — 执行** |
| ESH further-scale ~50 | deferred（AT denser-day 有现成 170 截面，更快到 found-path） |
| 继续 DAT101–105 micro-live 作为主包 | **拒绝**（controller course correction） |

---

## Gates

```text
d_class_abnormal_trading_further_scale_s4_dryrun_gate = PASS_OFFLINE
d_class_abnormal_trading_further_scale_execution_gate = PASS_WITH_CAVEAT
d_class_abnormal_trading_further_scale_live_executed = true
d_class_abnormal_trading_further_scale_live_authority = R19_STANDING_SCOPE_BOUNDED
acceptable = 50/50
found = 48
empty_but_valid = 2
cninfo_universe_cite = 1
cninfo_dryrun = 0
cninfo_live = 1
cninfo_package_total = 2
controller_execution_allowed = false
```

**强制语义：** `PASS_WITH_CAVEAT` ≠ bare PASS ≠ verified ≠ production_ready。  
常量文案 `live_gate=NOT_APPROVED` 可仍出现于 summary 模板；**本回合已在 R19 standing 授权下执行 bounded live**。

---

## Results

### Universe cite（CNINFO=1）

| 项 | 值 |
|----|-----|
| denser-day | `2026-07-02` |
| marketList total | **170** |
| selected found-path | **48**（排除 forbidden / DAT101–105 代码） |
| empty controls | **2**（000895 / 601988 · 先验 next-slice live 证明不在截面） |

### Dry-run（CNINFO=0）

| 项 | 值 |
|----|-----|
| planned_ok | **50/50** |
| planned_shared | **1** |
| isolated root | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale/` |

### Bounded live（CNINFO=1）

| 项 | 值 |
|----|-----|
| acceptable | **50/50** |
| found | **48**（DAT201–DAT248） |
| empty_but_valid | **2**（DAT249–DAT250） |
| failed / http_error | **0** |
| PDF/OCR/DB/MinIO/RAG | **no** |

Primary caveat：`denser_day_marketlist_not_full_market` — 截面 170 行 ≠ 全市场；本包只证明 denser-day 子集 found-path + empty-control。

---

## Freeze Attestation（未 mutate）

```text
AT next-slice lock sha256 = 4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6
AT next-slice dryrun_report sha256 = 51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497
AT next-slice dryrun_summary sha256 = 7fae1ccaacf31cbb254e51fc4b5a139554f40185eacd29ed692b1ce9320bb624
ESH next-slice lock sha256 = 4213de37e19d1d6bd920a9b2efd24495338a27eeb17f2602a8159fbb4b6d2fd1
ESH next-slice live_report sha256 = dc16b591b117a9411c0ec458a1ff3cdb4d850417fcf87d5de851c5c73af23e25
SC next dryrun_report sha256 = 5abc61e4f7ea6014af7e50847aefc7e46f4e39e3ba10e394fd56e683b19a08a5
EP next dryrun_report sha256 = 054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e
RSU next dryrun_report sha256 = 87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c
FIA next dryrun_report sha256 = 3f858f92e62f65b8c2bd51b84842561c6fbada39f93715b00a3f0234ff0c85f4
```

---

## Deliverables

| 项 | 路径 |
|----|------|
| runner | `lab/run_cninfo_d_class_abnormal_trading_further_scale.py` |
| tests | `lab/test_cninfo_d_class_abnormal_trading_further_scale_runner.py` |
| universe lock | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_universe_lock_20260716.csv` |
| marketList cite | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_marketlist_cite_20260716.json` |
| isolated root | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale/` |
| dry-run / live / quality reports | `.../reports/` |
| evidence（本文件） | `outputs/validation/cninfo_d_class_abnormal_trading_dfm03_further_scale_s50_live_20260716.md` |
| freeze attestation | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_freeze_attestation_20260716.csv` |
| next step | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_next_step_recommendation_20260716.md` |
| command draft | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_command_draft_20260716.md` |

---

## Tests

| 测试 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_abnormal_trading_further_scale_runner.py` | **PASS** |
| `lab/test_cninfo_d_class_abnormal_trading_next_slice_fixtures.py` | **回归 PASS** |

---

## Explicit Non-Claims

- **不是** verified / production_ready / bare PASS
- **不是** ESS H3/H4 / DLC006R reopen
- **不是** A/B/C 变更
- **无** commit / push / git add（executor）
- 先验 DAT101–105 tiny live 保留于 next-slice 根，**不是**本包主交付

---

## Commit Boundary（Controller）

```text
ready_for_commit = true
allow_list =
  lab/run_cninfo_d_class_abnormal_trading_further_scale.py
  lab/test_cninfo_d_class_abnormal_trading_further_scale_runner.py
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale/
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_universe_lock_20260716.csv
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_marketlist_cite_20260716.json
  outputs/validation/cninfo_d_class_abnormal_trading_dfm03_further_scale_s50_live_20260716.md
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_freeze_attestation_20260716.csv
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_next_step_recommendation_20260716.md
  outputs/validation/cninfo_d_class_abnormal_trading_further_scale_command_draft_20260716.md
  # optional prior micro-live artifacts on next-slice root if Controller chooses to include:
  # outputs/validation/cninfo_d_class_abnormal_trading_next_slice/reports/*live*
  # outputs/validation/cninfo_d_class_abnormal_trading_next_slice/live_snapshots/
exclude = A/B/C · ESH/SC/EP/RSU/FIA frozen roots · ESS · console logs
```

Suggested message:

```text
feat(d-class): AT further-scale ~50 denser-day live (DAT201-250)

Lock 48 found-path + 2 empty-control companies from 2026-07-02
marketList cite; isolated further-scale root; dry-run CNINFO=0 then
shared-probe live CNINFO=1 with PASS_WITH_CAVEAT (50/50 acceptable).
```

---

## Next D Candidate

```text
next_d_candidate = abnormal_trading_further_scale_s200_bounded_live
  OR at_further_scale_post_live_offline_closure
secondary = shareholder_data_next_slice_bounded_live OR esh_further_scale_s50
ess_h3_h4 = paused_pending_devtools
dlc006r = closed
```

Scale ladder note：本包 ~50 稳定（50/50 · found=48）→ **推荐下一步 ~200**（仍可用 denser-day 全量 170 + 邻近日 / 或跨日拼合至 ~200，isolated new root）。

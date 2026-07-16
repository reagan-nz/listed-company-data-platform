# CNINFO D 类 executive_shareholding — D-FM-06 / R19 Further-Scale S50 Bounded Live

_生成时间：2026-07-16 · D-FM-06 · R19 continuous async · excellence-gated scale_

> **性质：** executive_shareholding further-scale ~50 · dry-run CNINFO=0 → bounded live CNINFO=1（共享 denser-mode）· universe cite CNINFO=1 · **execution_gate = PASS_WITH_CAVEAT** · **excellence = YES** · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**

---

## Task Card

| 项 | 值 |
|----|-----|
| task_id | **D-FM-06** |
| track / executor | D / d-class-executor |
| standing_scope | shareholder / capital / executive_shareholding further-scale S50 |
| prefer | component switch after AT 50→200→1000 EXCELLENT |
| worktree | `listed_company_data_collector-worktrees/d-class` |
| branch | `agent/d-class`（synced to main @ `959bb00` D-FM-05） |
| ESS H3/H4 | **未触碰** |
| DLC006R | **未 reopen** |
| A/B/C | **未触碰** |

---

## Excellence Gate

| 指标 | 阈值 | 实测 | 结果 |
|------|------|------|------|
| size | ~50 | **50**（DES201–DES250） | OK |
| acceptable rate | ≥95% | **100.00%**（50/50） | YES |
| fail | 0 | **0** | YES |
| http_error / blocked | 0 | **0** | YES |
| **excellence** | all of above | **YES** | **next recommend ~200** |

```text
d_class_executive_shareholding_further_scale_dryrun_gate = PASS_OFFLINE
d_class_executive_shareholding_further_scale_execution_gate = PASS_WITH_CAVEAT
d_class_executive_shareholding_further_scale_live_executed = true
d_class_executive_shareholding_further_scale_live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**强制语义：** `PASS_WITH_CAVEAT` ≠ bare PASS ≠ verified ≠ production_ready。

---

## Deliverables

| 项 | 路径 / 说明 |
|----|-------------|
| runner | `lab/run_cninfo_d_class_executive_shareholding_further_scale.py` |
| tests | `lab/test_cninfo_d_class_executive_shareholding_further_scale_runner.py` |
| universe lock | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_universe_lock_20260716.csv` |
| leader/detail cite | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_leader_detail_cite_20260716.json` |
| isolated root | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale/` |
| dry-run report | `.../reports/d_class_executive_shareholding_further_scale_dryrun_report.csv` |
| dry-run summary | `.../reports/d_class_executive_shareholding_further_scale_dryrun_summary.md` |
| live report | `.../reports/d_class_executive_shareholding_further_scale_live_report.csv` |
| quality report | `.../reports/d_class_executive_shareholding_further_scale_quality_report.csv` |
| live summary | `.../reports/d_class_executive_shareholding_further_scale_live_summary.md` |
| evidence（本文件） | `outputs/validation/cninfo_d_class_executive_shareholding_dfm06_further_scale_s50_live_20260716.md` |
| freeze attestation | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_freeze_attestation_20260716.csv` |
| next step | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_next_step_recommendation_20260716.md` |
| command draft | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_command_draft_20260716.md` |

---

## Universe Lock（cite CNINFO=1）

| 指标 | 值 |
|------|-----|
| cases | **50**（DES201–DES248 found · DES249–250 empty control） |
| endpoint | `https://www.cninfo.com.cn/data20/leader/detail` |
| shared query | timeMark=**threeMonth** · varyType=**b** |
| cite total | **2123** |
| unique codes after exclusions | ≥48（selected 48） |
| empty controls | 000895 / 601988（D-FM-01 next-slice live 已证空） |
| excluded prior | DES001–005 / DES101–105 company codes · 688671 · 301259 |
| universe sha256 | `8ca94115a7ae180cb382687b46d864bedcbe28343eb0efe2cb2cd552dd97f068` |

---

## S4 Dry-run Result（CNINFO=0）

| 指标 | 值 |
|------|-----|
| cases | **50** |
| planned_ok | **50/50** |
| planned_shared_cninfo_requests | **1** |
| CNINFO calls | **0** |

---

## Bounded Live Result（CNINFO=1）

| 指标 | 值 |
|------|-----|
| cases | **50** |
| acceptable | **50/50**（100%） |
| found | **48** |
| empty_but_valid | **2**（DES249/DES250） |
| fail / http | **0 / 0** |
| shared CNINFO requests | **1** |
| execution_gate | **PASS_WITH_CAVEAT** |
| excellence | **YES** |
| PDF/OCR/DB/MinIO/RAG | **no** |

Caveat：denser-mode threeMonth+b 截面密度 ≠ 全市场高管持股变动覆盖；仅 leader/detail 元数据路径；禁 oneMonth+b sole found 锚。

---

## Tests

| 测试 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_executive_shareholding_further_scale_runner.py` | **7/7 PASS** |

---

## Freeze Attestation（DES101–105 未 mutate）

```text
esh_next_lock   = 4213de37e19d1d6bd920a9b2efd24495338a27eeb17f2602a8159fbb4b6d2fd1
esh_next_live   = dc16b591b117a9411c0ec458a1ff3cdb4d850417fcf87d5de851c5c73af23e25
esh_first_lock  = d42aaaf71f427fefe96f03700ff33e333686965355149ff2ad63311f7ac283c8
esh_first_dry   = cd8f25c24aebc75bc18ec5bb887eb4c0664ec7a579fcbc6d10c221f40a3b6092
sc_next_dry     = 5abc61e4f7ea6014af7e50847aefc7e46f4e39e3ba10e394fd56e683b19a08a5
ep_next_dry     = 054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e
rsu_next_dry    = 87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c
```

---

## Explicit Non-Claims

- **不是** verified / production_ready / bare PASS
- **未** mutate ESH next-slice DES101–105 冻结根
- **未** reopen DLC006R · **未**探 ESS H3/H4
- **未**触碰 A/B/C
- **未** commit / push

---

## Commit Boundary（Controller only · 本 executor 不 commit）

```text
include =
  lab/run_cninfo_d_class_executive_shareholding_further_scale.py
  lab/test_cninfo_d_class_executive_shareholding_further_scale_runner.py
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale/
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_universe_lock_20260716.csv
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_leader_detail_cite_20260716.json
  outputs/validation/cninfo_d_class_executive_shareholding_dfm06_further_scale_s50_live_20260716.md
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_freeze_attestation_20260716.csv
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_next_step_recommendation_20260716.md
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_command_draft_20260716.md
exclude = A/B/C · ESH next-slice DES101–105 frozen · first-slice · AT/SC/EP/RSU/FIA · ESS · DLC006R · console logs
```

Suggested message:

```text
feat(d-class): ESH further-scale ~50 denser-mode live (DES201-250)

Isolated further-scale root with threeMonth+b shared probe; dry-run CNINFO=0;
live CNINFO=1 with excellence PASS_WITH_CAVEAT (50/50 acceptable).
```

---

## Next Ladder Step

```text
preferred = executive_shareholding_further_scale_s200
scale_ladder = 5(next-slice done) → 50(D-FM-06 EXCELLENT) → 200(next) → 1000(if excellent)
alternate_if_blocked = harden_@50_or_SC_EP_RSU_FIA_further_scale_~50
```

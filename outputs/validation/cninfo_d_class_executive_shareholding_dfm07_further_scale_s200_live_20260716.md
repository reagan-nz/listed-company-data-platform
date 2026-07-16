# CNINFO D 类 executive_shareholding — D-FM-07 / R19 Further-Scale S200 Bounded Live

_生成时间：2026-07-16 · D-FM-07 · R19 continuous async · excellence-gated scale_

> **性质：** executive_shareholding further-scale ~200 · dry-run CNINFO=0 → bounded live CNINFO=1（共享 denser-mode）· universe cite CNINFO=1 · **execution_gate = PASS_WITH_CAVEAT** · **excellence = YES** · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**

---

## Task Card

| 项 | 值 |
|----|-----|
| task_id | **D-FM-07** |
| track / executor | D / d-class-executor |
| standing_scope | shareholder / capital / executive_shareholding further-scale S200 |
| prefer | excellence-gated ladder after D-FM-06 S50 EXCELLENT |
| worktree | `listed_company_data_collector-worktrees/d-class` |
| branch | `agent/d-class`（synced to main @ `7bc5486` D-FM-06） |
| ESS H3/H4 | **未触碰** |
| DLC006R | **未 reopen** |
| A/B/C | **未触碰** |
| AT>1000 | **未发明** |

---

## Excellence Gate

| 指标 | 阈值 | 实测 | 结果 |
|------|------|------|------|
| size | ~200 | **200**（DES251–DES450） | OK |
| acceptable rate | ≥95% | **100.00%**（200/200） | YES |
| fail | 0 | **0** | YES |
| http_error / blocked | 0 | **0** | YES |
| **excellence** | all of above | **YES** | **next recommend ~1000** |

```text
d_class_executive_shareholding_further_scale_s200_dryrun_gate = PASS_OFFLINE
d_class_executive_shareholding_further_scale_s200_execution_gate = PASS_WITH_CAVEAT
d_class_executive_shareholding_further_scale_s200_live_executed = true
d_class_executive_shareholding_further_scale_s200_live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**强制语义：** `PASS_WITH_CAVEAT` ≠ bare PASS ≠ verified ≠ production_ready。

---

## Deliverables

| 项 | 路径 / 说明 |
|----|-------------|
| runner | `lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py` |
| tests | `lab/test_cninfo_d_class_executive_shareholding_further_scale_s200_runner.py` |
| universe lock | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_universe_lock_20260716.csv` |
| leader/detail cite | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_leader_detail_cite_20260716.json` |
| isolated root | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200/` |
| dry-run report | `.../reports/d_class_executive_shareholding_further_scale_s200_dryrun_report.csv` |
| dry-run summary | `.../reports/d_class_executive_shareholding_further_scale_s200_dryrun_summary.md` |
| live report | `.../reports/d_class_executive_shareholding_further_scale_s200_live_report.csv` |
| quality report | `.../reports/d_class_executive_shareholding_further_scale_s200_quality_report.csv` |
| live summary | `.../reports/d_class_executive_shareholding_further_scale_s200_live_summary.md` |
| evidence（本文件） | `outputs/validation/cninfo_d_class_executive_shareholding_dfm07_further_scale_s200_live_20260716.md` |
| freeze attestation | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_freeze_attestation_20260716.csv` |
| next step | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_next_step_recommendation_20260716.md` |
| command draft | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_command_draft_20260716.md` |

---

## Universe Lock（cite CNINFO=1）

| 指标 | 值 |
|------|-----|
| cases | **200**（DES251–DES448 found · DES449–450 empty control） |
| endpoint | `https://www.cninfo.com.cn/data20/leader/detail` |
| shared query | timeMark=**threeMonth** · varyType=**b** |
| cite total | **2123** |
| selected found | **198**（排除 S50 DES201–250 found 码与 prior-slice 码） |
| empty controls | 000895 / 601988（D-FM-01 next-slice live 已证空） |
| excluded prior | DES001–005 / DES101–105 / DES201–250 found company codes · 688671 · 301259 |
| universe sha256 | `19808c3cf455aef1c37b49cb5d6e6598bc6fcd34cced6194c8e02f26858ce25d` |

---

## S4 Dry-run Result（CNINFO=0）

| 指标 | 值 |
|------|-----|
| cases | **200** |
| planned_ok | **200/200** |
| planned_shared_cninfo_requests | **1** |
| CNINFO calls | **0** |

---

## Bounded Live Result（CNINFO=1）

| 指标 | 值 |
|------|-----|
| cases | **200** |
| acceptable | **200/200**（100%） |
| found | **198** |
| empty_but_valid | **2**（DES449/DES450） |
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
| `lab/test_cninfo_d_class_executive_shareholding_further_scale_s200_runner.py` | **6/6 PASS** |

---

## Freeze Attestation（DES201–250 / DES101–105 未 mutate）

```text
esh_s50_lock    = 8ca94115a7ae180cb382687b46d864bedcbe28343eb0efe2cb2cd552dd97f068
esh_s50_live    = 1d32b6f324948417b2726e0dd5bd637db1ce01e30e0fe29ae983cd3c4ab73d06
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
- **未** mutate ESH further-scale S50 DES201–250 冻结根
- **未** mutate ESH next-slice DES101–105 冻结根
- **未** reopen DLC006R · **未**探 ESS H3/H4
- **未**触碰 A/B/C · **未**发明 AT>1000
- **未** commit / push

---

## Commit Boundary（Controller only · 本 executor 不 commit）

```text
include =
  lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py
  lab/test_cninfo_d_class_executive_shareholding_further_scale_s200_runner.py
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200/
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_universe_lock_20260716.csv
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_leader_detail_cite_20260716.json
  outputs/validation/cninfo_d_class_executive_shareholding_dfm07_further_scale_s200_live_20260716.md
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_freeze_attestation_20260716.csv
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_next_step_recommendation_20260716.md
  outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_command_draft_20260716.md
exclude = A/B/C · ESH S50 DES201–250 frozen · ESH next-slice DES101–105 frozen · first-slice · AT/SC/EP/RSU/FIA · ESS · DLC006R · console logs
```

Suggested message:

```text
feat(d-class): ESH further-scale ~200 denser-mode live (DES251-450)

Isolated S200 root with threeMonth+b shared probe; dry-run CNINFO=0;
live CNINFO=1 with excellence PASS_WITH_CAVEAT (200/200 acceptable).
```

---

## Next Ladder Step

```text
preferred = executive_shareholding_further_scale_s1000
scale_ladder = 5(next-slice done) → 50(D-FM-06 EXCELLENT) → 200(D-FM-07 EXCELLENT) → 1000(next)
alternate_if_blocked = harden_@200_or_SC_EP_RSU_FIA_further_scale_~50
```

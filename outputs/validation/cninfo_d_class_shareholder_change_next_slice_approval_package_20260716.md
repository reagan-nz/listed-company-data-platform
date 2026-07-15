# CNINFO D 类 shareholder_change Next-Slice — Approval Package

_生成时间：2026-07-16 · D-FM-50_

> **性质：** Era D 离线 next-slice approval package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **任务 ID：** D-FM-50
>
> **Standing auth：** shareholder / capital / FIA / AT / SD / EP / RSU / SC · **Level-2 phrase NOT required** · **不** IDLE
>
> **Prior：** D-FM-49 denser-mode sketch DSC101–105 · `type=desc` · `anchor_tdate=2026-07-03` · priority2 rows=16 · planning_gate=`READY_FOR_APPROVAL` · SC first-slice + RSU/EP/FIA/AT/SD roots **frozen**

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | shareholder / capital / FIA / AT / SD / EP / RSU / SC |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--shareholder-change-next-slice` 未实现） |
| next-slice live | **NOT APPROVED**（须另批 + approve flag） |
| CNINFO calls (this package) | **0** |
| SC first-slice universe / live / dry-run | **未 mutate** |
| RSU first/next lock / dry-run | **未 mutate** |
| EP first/next lock / dry-run | **未 mutate** |
| FIA first/next/further-scale lock / dry-run | **未 mutate** |
| AT/SD first/next lock / dry-run | **未 mutate** |
| ESS H3/H4 | **未探**（禁止） |
| DLC006R | **未重开** |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `shareholder_change` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event` |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail`（拼写 **shareholeder** 不修正） |
| query mode | **type_desc_tdate_daily** · type=**desc** · tdate=**2026-07-03** |
| universe | **5** rows · **DSC101–DSC105**（locked） |
| denser-mode cite | D-FM-49 · priority2 type=desc rows=16 · **禁** `type=inc`+`2026-07-03` sole found 锚 |
| request model | prefer **1 shared probe** · total cap **≤ 5** · per-case ≤ 1 |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/shareholder_change_desc/sample_raw.json` · `fixtures/d_class/phase1/DC005.json`（结构 only） |
| Tier-1 fixtures | **9** files under `fixtures/d_class/shareholder_change_next_slice/` |
| live found-path DSC101–105 | **NOT_PROVEN**（cite ≠ company-level found） |

---

## 3. Gate Status

```text
d_class_shareholder_change_next_slice_planning_gate = READY_FOR_APPROVAL
d_class_shareholder_change_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_change_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_shareholder_change_next_slice_live_gate = NOT_APPROVED
d_class_shareholder_change_next_slice_runner_gate = NOT_APPROVED
d_class_shareholder_change_next_slice_execution_gate = NOT_APPLICABLE
shareholder_change_component_approved = standing_scope
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DSC101–DSC105）

**正式锁定：** [cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv](cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_shareholder_change_next_slice_universe_draft_sketch_20260716.csv](cninfo_d_class_shareholder_change_next_slice_universe_draft_sketch_20260716.csv)

| case_id | company_code | market | query_type | anchor_tdate | expected_behavior |
|---------|--------------|--------|------------|--------------|-------------------|
| DSC101 | 000550 | szse_main | desc | 2026-07-03 | captured_normal_or_empty_but_valid |
| DSC102 | 000895 | szse_main | desc | 2026-07-03 | captured_normal_or_empty_but_valid |
| DSC103 | 600000 | sse_main | desc | 2026-07-03 | captured_normal_or_empty_but_valid |
| DSC104 | 002415 | szse_main | desc | 2026-07-03 | captured_normal_or_empty_but_valid |
| DSC105 | 601988 | sse_main | desc | 2026-07-03 | empty_but_valid |

**Closed-root freeze（未触碰）：**

```text
sc_first_slice_universe_lock_sha256 = 49e6ece0c0a5c5ecce32328e4e1fe990b48d7d46d3cc1f32da1c8d2245a3c402
sc_first_slice_live_report_sha256 = 5d73c24e40d028976da4054983649ee2a3e2a9ad2b3edf12babe893cfc779e1f
sc_first_slice_dryrun_report_sha256 = e37e9fbe485bf63b9c4d41cf1170aec558100f51c9ac69654bf09f7eb1213e44
rsu_next_slice_universe_lock_sha256 = 13254f44f344c0f2976dfbde6fe75e363f91283a6eec1a5ae02d29f3831f193f
rsu_next_slice_dryrun_report_sha256 = 87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c
rsu_first_slice_universe_draft_sha256 = 81a792f43962849778d53af97b4d67c64d53b1cd15d8428ff6d0a74931c84ec9
ep_next_slice_universe_lock_sha256 = 1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384
ep_next_slice_dryrun_report_sha256 = 054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e
ep_first_slice_universe_draft_sha256 = 5fb4fa005236a162ef3bcc5322fe3b7134b36cbe7727fb0273724d0638dc8e10
fia_further_scale_lock_sha256 = 398494f1cf6a6cf00637b82d6e3f5c38ae21671a4b47324fd1ee2262df92e9f1
fia_first_slice_universe_lock_sha256 = 49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c
fia_next_slice_universe_lock_sha256 = c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515
at_first_slice_universe_lock_sha256 = d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2
at_next_slice_universe_lock_sha256 = 4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6
sd_first_slice_universe_lock_sha256 = 06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5
sd_next_slice_universe_lock_sha256 = c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f
at_next_dryrun_report_sha256 = 51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497
sd_next_dryrun_report_sha256 = 2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362
```

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen** · **no type=inc+2026-07-03 sole found anchor** · **no sole needs_review** · **no first-slice DSC001–005 mutate**

---

## 5. Fixtures

| case_id | files | 覆盖 |
|---------|-------|------|
| DSC101 | `DSC101_found.json` · `DSC101_empty.json` | mixed found/empty · structure cite |
| DSC102 | `DSC102_found.json` · `DSC102_empty.json` | mixed found/empty |
| DSC103 | `DSC103_found.json` · `DSC103_empty.json` | mixed found/empty |
| DSC104 | `DSC104_found.json` · `DSC104_empty.json` | mixed found/empty |
| DSC105 | `DSC105_empty_but_valid_synthetic.json` | empty control |

结构 cite Tier-0 sample_raw / DC005（只读）· fixture 仍标 `synthetic=true` · `cninfo_called=false` · 全案 `type=desc` · `tdate=2026-07-03`。

---

## 6. Artifacts

| 项 | 路径 |
|----|------|
| planning（prior） | [plans/cninfo_d_class_shareholder_change_next_slice_planning_20260716.md](../../plans/cninfo_d_class_shareholder_change_next_slice_planning_20260716.md) |
| universe lock | [cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv](cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv) |
| VR | [cninfo_d_class_shareholder_change_next_slice_validation_rules_20260716.md](cninfo_d_class_shareholder_change_next_slice_validation_rules_20260716.md) |
| command draft | [cninfo_d_class_shareholder_change_next_slice_command_draft_20260716.md](cninfo_d_class_shareholder_change_next_slice_command_draft_20260716.md) |
| checklist | [cninfo_d_class_shareholder_change_next_slice_offline_prep_checklist_20260716.csv](cninfo_d_class_shareholder_change_next_slice_offline_prep_checklist_20260716.csv) |
| fixtures | `fixtures/d_class/shareholder_change_next_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_shareholder_change_next_slice_fixtures.py` |
| evidence | [cninfo_d_class_shareholder_change_dfm50_next_slice_approval_package_20260716.md](cninfo_d_class_shareholder_change_dfm50_next_slice_approval_package_20260716.md) |

---

## 7. Red Lines

No CNINFO · No live · No runner implement · No SC first-slice mutate · No RSU/EP/FIA/AT/SD mutate · No ESS H3/H4 · No DLC006R reopen · No type=inc+2026-07-03 sole found · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE · No console logs in allow-list

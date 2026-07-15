# CNINFO D 类 equity_pledge Next-Slice — Approval Package

_生成时间：2026-07-15 · D-FM-42_

> **性质：** Era D 离线 next-slice approval package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **任务 ID：** D-FM-42
>
> **Standing auth：** shareholder / capital / FIA / AT / SD · **Level-2 phrase NOT required** · **不** IDLE
>
> **Prior：** D-FM-41 denser-day sketch DEP101–105 · `anchor_tdate=2026-07-02` · planning_gate=`READY_FOR_APPROVAL` · first-slice EP + FIA/AT/SD roots **frozen**

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | shareholder / capital / FIA / AT / SD |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--equity-pledge-next-slice` 未实现） |
| next-slice live | **NOT APPROVED**（须另批 + approve flag） |
| CNINFO calls (this package) | **0** |
| EP first-slice universe / live / dry-run | **未 mutate** |
| FIA first/next/further-scale lock / dry-run | **未 mutate** |
| AT/SD first/next lock / dry-run | **未 mutate** |
| ESS H3/H4 | **未探**（禁止） |
| DLC006R | **未重开** |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `equity_pledge` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event` |
| endpoint | `https://www.cninfo.com.cn/data20/equityPledge/list` |
| query mode | **tdate_daily** · tdate=**2026-07-02** |
| universe | **5** rows · **DEP101–DEP105**（locked） |
| denser-day cite | D-FM-41 · priority-2 rows=68 · **禁** `2026-07-03` sole found 锚 |
| request model | prefer **1 shared probe** · total cap **≤ 5** · per-case ≤ 1 |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/equity_pledge/sample_raw.json` |
| Tier-1 fixtures | **9** files under `fixtures/d_class/equity_pledge_next_slice/` |
| live found-path DEP101–105 | **NOT_PROVEN**（cite ≠ company-level found） |

---

## 3. Gate Status

```text
d_class_equity_pledge_next_slice_planning_gate = READY_FOR_APPROVAL
d_class_equity_pledge_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_equity_pledge_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_equity_pledge_next_slice_live_gate = NOT_APPROVED
d_class_equity_pledge_next_slice_runner_gate = NOT_APPROVED
d_class_equity_pledge_next_slice_execution_gate = NOT_APPLICABLE
equity_pledge_component_approved = standing_scope
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DEP101–DEP105）

**正式锁定：** [cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv](cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_equity_pledge_next_slice_universe_draft_sketch_20260715.csv](cninfo_d_class_equity_pledge_next_slice_universe_draft_sketch_20260715.csv)

| case_id | company_code | market | anchor_tdate | expected_behavior |
|---------|--------------|--------|--------------|-------------------|
| DEP101 | 000001 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DEP102 | 000895 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DEP103 | 600000 | sse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DEP104 | 002415 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DEP105 | 601988 | sse_main | 2026-07-02 | empty_but_valid |

**Closed-root freeze（未触碰）：**

```text
ep_first_slice_universe_draft_sha256 = 5fb4fa005236a162ef3bcc5322fe3b7134b36cbe7727fb0273724d0638dc8e10
ep_first_slice_live_report_sha256 = 435b53bc9cc5360a0dc8843b81431bbc108b37a71fc80527d501bf420fc12387
ep_first_slice_dryrun_report_sha256 = a035f8ef6102946bb2b4406f59f17cff20aff810de9c1fb59cab82c7d43084bc
fia_further_scale_lock_sha256 = 398494f1cf6a6cf00637b82d6e3f5c38ae21671a4b47324fd1ee2262df92e9f1
fia_first_slice_universe_lock_sha256 = 49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c
fia_next_slice_universe_lock_sha256 = c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515
at_first_slice_universe_lock_sha256 = d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2
at_next_slice_universe_lock_sha256 = 4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6
sd_first_slice_universe_lock_sha256 = 06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5
sd_next_slice_universe_lock_sha256 = c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f
```

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen** · **no 2026-07-03 sole found anchor** · **no sole needs_review** · **no first-slice DEP001–005 mutate**

---

## 5. Fixtures

| case_id | files | 覆盖 |
|---------|-------|------|
| DEP101 | `DEP101_found.json` · `DEP101_empty.json` | mixed found/empty · sample_raw cite |
| DEP102 | `DEP102_found.json` · `DEP102_empty.json` | mixed found/empty |
| DEP103 | `DEP103_found.json` · `DEP103_empty.json` | mixed found/empty |
| DEP104 | `DEP104_found.json` · `DEP104_empty.json` | mixed found/empty |
| DEP105 | `DEP105_empty_but_valid_synthetic.json` | empty control |

结构 cite Tier-0 `sample_raw.json`（只读）· fixture 仍标 `synthetic=true` · `cninfo_called=false` · 全案 `tdate=2026-07-02`。

---

## 6. Artifacts

| 项 | 路径 |
|----|------|
| planning（prior） | [plans/cninfo_d_class_equity_pledge_next_slice_planning_20260715.md](../../plans/cninfo_d_class_equity_pledge_next_slice_planning_20260715.md) |
| universe lock | [cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv](cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv) |
| VR | [cninfo_d_class_equity_pledge_next_slice_validation_rules_20260715.md](cninfo_d_class_equity_pledge_next_slice_validation_rules_20260715.md) |
| command draft | [cninfo_d_class_equity_pledge_next_slice_command_draft_20260715.md](cninfo_d_class_equity_pledge_next_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_equity_pledge_next_slice_offline_prep_checklist_20260715.csv](cninfo_d_class_equity_pledge_next_slice_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/equity_pledge_next_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_equity_pledge_next_slice_fixtures.py` |
| evidence | [cninfo_d_class_equity_pledge_dfm42_next_slice_approval_package_20260715.md](cninfo_d_class_equity_pledge_dfm42_next_slice_approval_package_20260715.md) |

---

## 7. Red Lines

No CNINFO · No live · No runner implement · No EP first-slice mutate · No FIA/AT/SD mutate · No ESS H3/H4 · No DLC006R reopen · No 2026-07-03 sole found · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE · No console logs in allow-list

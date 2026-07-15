# CNINFO D 类 restricted_shares_unlock（ES / 限售解禁）Next-Slice — Approval Package

_生成时间：2026-07-15 · D-FM-46_

> **性质：** Era D 离线 next-slice approval package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **任务 ID：** D-FM-46
>
> **Standing auth：** shareholder / capital / FIA / AT / SD · **Level-2 phrase NOT required** · **不** IDLE
>
> **Prior：** D-FM-45 denser-day sketch DRU101–105 · `anchor_tdate=2026-07-03` · planning_gate=`READY_FOR_APPROVAL` · RSU first-slice + EP/FIA/AT/SD roots **frozen**
>
> **命名：** ES = **限售解禁 / equity structure** = `restricted_shares_unlock`（**不是** executive_shareholding）

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | shareholder / capital / FIA / AT / SD |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--restricted-shares-unlock-next-slice` 未实现） |
| next-slice live | **NOT APPROVED**（须另批 + approve flag） |
| CNINFO calls (this package) | **0** |
| RSU first-slice universe / live | **未 mutate** |
| EP first/next lock / dry-run | **未 mutate** |
| FIA first/next/further-scale lock / dry-run | **未 mutate** |
| AT/SD first/next lock / dry-run | **未 mutate** |
| shareholder_change | **deferred**（本包不规划） |
| ESS H3/H4 | **未探**（禁止） |
| DLC006R | **未重开** |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `restricted_shares_unlock` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event` |
| endpoint | `https://www.cninfo.com.cn/data20/liftBan/detail` |
| query mode | **tdate_daily** · tdate=**2026-07-03** |
| universe | **5** rows · **DRU101–DRU105**（locked） |
| denser-day cite | D-FM-45 · multidate rows=9 · **禁** `2026-06-08` sole found 锚 |
| request model | prefer **1 shared probe** · total cap **≤ 5** · per-case ≤ 1 |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/restricted_shares_unlock/sample_raw.json`（结构 only） |
| Tier-1 fixtures | **9** files under `fixtures/d_class/restricted_shares_unlock_next_slice/` |
| live found-path DRU101–105 | **NOT_PROVEN**（cite ≠ company-level found） |

---

## 3. Gate Status

```text
d_class_restricted_shares_unlock_next_slice_planning_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_restricted_shares_unlock_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_restricted_shares_unlock_next_slice_live_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_runner_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_execution_gate = NOT_APPLICABLE
restricted_shares_unlock_component_approved = standing_scope
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DRU101–DRU105）

**正式锁定：** [cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv](cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_restricted_shares_unlock_next_slice_universe_draft_sketch_20260715.csv](cninfo_d_class_restricted_shares_unlock_next_slice_universe_draft_sketch_20260715.csv)

| case_id | company_code | market | anchor_tdate | expected_behavior |
|---------|--------------|--------|--------------|-------------------|
| DRU101 | 300992 | chinext | 2026-07-03 | captured_normal_or_empty_but_valid |
| DRU102 | 000895 | szse_main | 2026-07-03 | captured_normal_or_empty_but_valid |
| DRU103 | 600000 | sse_main | 2026-07-03 | captured_normal_or_empty_but_valid |
| DRU104 | 002415 | szse_main | 2026-07-03 | captured_normal_or_empty_but_valid |
| DRU105 | 601988 | sse_main | 2026-07-03 | empty_but_valid |

**Closed-root freeze（未触碰）：**

```text
rsu_first_slice_universe_draft_sha256 = 81a792f43962849778d53af97b4d67c64d53b1cd15d8428ff6d0a74931c84ec9
rsu_first_slice_live_report_sha256 = 9a0de0186eb22dceb5be7357267438d9a9ebb94ffcaf996f5a81440407ab5c57
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
```

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen** · **no 2026-06-08 sole found anchor** · **no sole needs_review** · **no first-slice DRU001–005 mutate**

---

## 5. Fixtures

| case_id | files | 覆盖 |
|---------|-------|------|
| DRU101 | `DRU101_found.json` · `DRU101_empty.json` | mixed found/empty · sample_raw structure cite |
| DRU102 | `DRU102_found.json` · `DRU102_empty.json` | mixed found/empty |
| DRU103 | `DRU103_found.json` · `DRU103_empty.json` | mixed found/empty |
| DRU104 | `DRU104_found.json` · `DRU104_empty.json` | mixed found/empty |
| DRU105 | `DRU105_empty_but_valid_synthetic.json` | empty control |

结构 cite Tier-0 `sample_raw.json`（只读）· fixture 仍标 `synthetic=true` · `cninfo_called=false` · 全案 `tdate=2026-07-03`。

---

## 6. Artifacts

| 项 | 路径 |
|----|------|
| planning（prior） | [plans/cninfo_d_class_restricted_shares_unlock_next_slice_planning_20260715.md](../../plans/cninfo_d_class_restricted_shares_unlock_next_slice_planning_20260715.md) |
| universe lock | [cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv](cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv) |
| VR | [cninfo_d_class_restricted_shares_unlock_next_slice_validation_rules_20260715.md](cninfo_d_class_restricted_shares_unlock_next_slice_validation_rules_20260715.md) |
| command draft | [cninfo_d_class_restricted_shares_unlock_next_slice_command_draft_20260715.md](cninfo_d_class_restricted_shares_unlock_next_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_restricted_shares_unlock_next_slice_offline_prep_checklist_20260715.csv](cninfo_d_class_restricted_shares_unlock_next_slice_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/restricted_shares_unlock_next_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_fixtures.py` |
| evidence | [cninfo_d_class_restricted_shares_unlock_dfm46_next_slice_approval_package_20260715.md](cninfo_d_class_restricted_shares_unlock_dfm46_next_slice_approval_package_20260715.md) |

---

## 7. Red Lines

No CNINFO · No live · No runner implement · No RSU first-slice mutate · No EP/FIA/AT/SD mutate · No ESS H3/H4 · No DLC006R reopen · No 2026-06-08 sole found · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE · No console logs in allow-list · No shareholder_change reopen this package

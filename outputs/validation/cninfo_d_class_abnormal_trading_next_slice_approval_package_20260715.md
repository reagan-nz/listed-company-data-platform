# CNINFO D 类 abnormal_trading Next-Slice — Approval Package

_生成时间：2026-07-15 21:59:00 +0800_

> **性质：** Era D 离线 next-slice approval package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **任务 ID：** D-FM-30
>
> **Standing auth：** full-market shareholder / capital · **Level-2 phrase NOT required** · **不** IDLE
>
> **Prior：** D-FM-29 denser-day cite `2026-07-02` · `OFFLINE_PROVISIONAL_CITE_2026_07_02` · sketch DAT101–105 · first-slice AT/SD + FIA locks **frozen**

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | full-market shareholder / capital |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--abnormal-trading-next-slice` 未实现） |
| next-slice live | **NOT APPROVED**（须另批 + approve flag） |
| CNINFO calls (this package) | **0** |
| AT/SD first-slice lock / live roots | **未 mutate** |
| FIA first/next-slice lock / live roots | **未 mutate** |
| ESS H3/H4 | **未探**（禁止） |
| DLC006R | **未重开** |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `abnormal_trading` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event`（detail[] → `d_event_party_detail` deferred） |
| endpoint | `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData` |
| query mode | **single_day_paged** · sdate=edate=**2026-07-02** |
| universe | **5** rows · **DAT101–DAT105**（locked） |
| denser-day cite | D-FM-29 · observed_total_rows=173 · **禁** `2026-07-03` sole found 锚 |
| request model | prefer **1 shared probe** · total cap **≤ 5** · per-case ≤ 1 |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/abnormal_trading/sample_raw.json` |
| Tier-1 fixtures | **9** files under `fixtures/d_class/abnormal_trading_next_slice/` |
| live found-path DAT101–105 | **NOT_PROVEN**（cite ≠ company-level found） |

---

## 3. Gate Status

```text
d_class_abnormal_trading_dense_day_cite_gate = READY_FOR_APPROVAL
at_dense_day_status = OFFLINE_PROVISIONAL_CITE_2026_07_02
d_class_abnormal_trading_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_abnormal_trading_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_abnormal_trading_next_slice_live_gate = NOT_APPROVED
d_class_abnormal_trading_next_slice_runner_gate = NOT_APPROVED
d_class_abnormal_trading_next_slice_execution_gate = NOT_APPLICABLE
abnormal_trading_component_approved = standing_scope
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DAT101–DAT105）

**正式锁定：** [cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv](cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_abnormal_trading_next_slice_universe_draft_sketch_20260715.csv](cninfo_d_class_abnormal_trading_next_slice_universe_draft_sketch_20260715.csv)

| case_id | company_code | market | anchor_tdate | expected_behavior |
|---------|--------------|--------|--------------|-------------------|
| DAT101 | 000895 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DAT102 | 600000 | sse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DAT103 | 002415 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DAT104 | 000001 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid |
| DAT105 | 601988 | sse_main | 2026-07-02 | empty_but_valid |

**Closed-root freeze（未触碰）：**

```text
at_first_slice_universe_lock_sha256 = d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2
sd_first_slice_universe_lock_sha256 = 06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5
fia_next_slice_universe_lock_sha256 = c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515
fia_first_slice_universe_lock_sha256 = 49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c
```

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen** · **no 2026-07-03 sole found anchor** · **no sole needs_review**

---

## 5. Fixtures

| case_id | files | 覆盖 |
|---------|-------|------|
| DAT101 | `DAT101_found.json` · `DAT101_empty.json` | mixed found/empty |
| DAT102 | `DAT102_found.json` · `DAT102_empty.json` | mixed found/empty |
| DAT103 | `DAT103_found.json` · `DAT103_multi_type_found.json` | found + multi-type structure |
| DAT104 | `DAT104_found.json` · `DAT104_empty.json` | mixed found/empty |
| DAT105 | `DAT105_empty_but_valid_synthetic.json` | empty control |

结构 cite first-slice Tier-1（只读）· fixture 仍标 `synthetic=true` · `cninfo_called=false` · 全案 `sdate=edate=2026-07-02`。

---

## 6. Artifacts

| 项 | 路径 |
|----|------|
| denser-day cite（prior） | [plans/cninfo_d_class_abnormal_trading_dense_day_cite_20260715.md](../../plans/cninfo_d_class_abnormal_trading_dense_day_cite_20260715.md) |
| universe lock | [cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv](cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv) |
| VR | [cninfo_d_class_abnormal_trading_next_slice_validation_rules_20260715.md](cninfo_d_class_abnormal_trading_next_slice_validation_rules_20260715.md) |
| command draft | [cninfo_d_class_abnormal_trading_next_slice_command_draft_20260715.md](cninfo_d_class_abnormal_trading_next_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_abnormal_trading_next_slice_offline_prep_checklist_20260715.csv](cninfo_d_class_abnormal_trading_next_slice_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/abnormal_trading_next_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_abnormal_trading_next_slice_fixtures.py` |
| evidence | [cninfo_d_class_abnormal_trading_dfm30_next_slice_approval_package_20260715.md](cninfo_d_class_abnormal_trading_dfm30_next_slice_approval_package_20260715.md) |

---

## 7. Red Lines

No CNINFO · No live · No runner implement · No first-slice mutate · No FIA mutate · No ESS H3/H4 · No DLC006R reopen · No 2026-07-03 sole found · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE

# CNINFO D 类 shareholder_data Next-Slice — Approval Package

_生成时间：2026-07-15 22:20:00 +0800_

> **性质：** Era D 离线 next-slice approval package · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **任务 ID：** D-FM-32
>
> **Standing auth：** shareholder / capital / FIA / AT / SD · **Level-2 phrase NOT required** · **不** IDLE
>
> **Prior：** D-FM-28 AT/SD next-slice scale sketch · D-FM-31 AT next-slice runner+S4 offline committed · AT live 仍 `NOT_APPROVED` · first-slice AT/SD + FIA locks **frozen**

---

## 1. Standing Auth Record

| 项 | 值 |
|----|-----|
| standing_scope | shareholder / capital / FIA / AT / SD |
| level2_phrase_required | **false** |
| offline lock / VR / fixtures | **authorized** under standing D |
| S4 dry-run | **blocked_until_runner**（`--shareholder-data-next-slice` 未实现） |
| next-slice live | **NOT APPROVED**（须另批 + approve flag） |
| AT next-slice bounded live | **未翻转**（`controller_execution_allowed=false` · live_gate=`NOT_APPROVED` · 本包不 honest-flip） |
| CNINFO calls (this package) | **0** |
| AT/SD first-slice lock / live roots | **未 mutate** |
| AT next-slice lock / dry-run root | **未 mutate** |
| FIA first/next-slice lock / live roots | **未 mutate** |
| ESS H3/H4 | **未探**（禁止） |
| DLC006R | **未重开** |

---

## 2. Prefer Decision（D-FM-32）

| 选项 | 本任务取舍 |
|------|------------|
| AT next-slice bounded live | **跳过** — 不能诚实翻转 live approval（见 §1） |
| **SD next-slice approval package offline** | **primary — 执行** · CNINFO=0 |
| FIA further-scale offline | deferred |
| ESS H3/H4 blind probe | **禁止** |

**Live 不翻转理由（诚实边界）：**

1. 任务 YAML `controller_execution_allowed=false`
2. AT next-slice `live_gate=NOT_APPROVED` · approve flag 未显式批
3. STANDING_SCOPE_AUTHORIZED ≠ live_approved
4. DAT101–105 company-level found-path 仍 `NOT_PROVEN`（cite ≠ live）
5. 用户红线：未经明确批准不得 live / 调用 CNINFO

---

## 3. Executive Summary

| 项 | 值 |
|----|-----|
| component | `shareholder_data` |
| source_layer | `company_metric_periodic` |
| target_logical_table | `d_company_metric_periodic` |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/data` |
| query mode | **rdate_report_period** · multi-rdate next-slice |
| universe | **5** rows · **DSD101–DSD105**（locked） |
| rdate set | `20260331`（proven cite）+ `20251231`（unproven_mixed） |
| request model | prefer **2 shared probes** · total cap **≤ 5** · per-case ≤ 1 |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| Tier-0 cite | `fixtures/d_class/shareholder_data/sample_raw.json` |
| Tier-1 fixtures | **8** files under `fixtures/d_class/shareholder_data_next_slice/` |
| live found-path DSD104/105 `20251231` | **NOT_PROVEN** |

---

## 4. Gate Status

```text
d_class_shareholder_data_next_slice_scale_planning_gate = READY_FOR_APPROVAL
d_class_shareholder_data_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_data_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_shareholder_data_next_slice_live_gate = NOT_APPROVED
d_class_shareholder_data_next_slice_runner_gate = NOT_APPROVED
d_class_shareholder_data_next_slice_execution_gate = NOT_APPLICABLE
shareholder_data_component_approved = standing_scope
at_next_slice_live_gate = NOT_APPROVED
```

**强制语义：** STANDING_SCOPE_AUTHORIZED ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 5. Universe Lock（DSD101–DSD105）

**正式锁定：** [cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv](cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv)

**来源草案（只读 · 不修改）：** [cninfo_d_class_shareholder_data_next_slice_universe_draft_sketch_20260715.csv](cninfo_d_class_shareholder_data_next_slice_universe_draft_sketch_20260715.csv)

| case_id | company_code | market | anchor_rdate | expected_behavior |
|---------|--------------|--------|--------------|-------------------|
| DSD101 | 000001 | szse_main | 20260331 | captured_normal |
| DSD102 | 000895 | szse_main | 20260331 | captured_normal_or_empty_but_valid |
| DSD103 | 600519 | sse_main | 20260331 | captured_normal_or_empty_but_valid |
| DSD104 | 002415 | szse_main | 20251231 | captured_normal_or_empty_but_valid |
| DSD105 | 000004 | szse_main | 20251231 | empty_but_valid |

**Closed-root freeze（未触碰）：**

```text
at_first_slice_universe_lock_sha256 = d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2
at_next_slice_universe_lock_sha256 = 4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6
sd_first_slice_universe_lock_sha256 = 06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5
fia_next_slice_universe_lock_sha256 = c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515
fia_first_slice_universe_lock_sha256 = 49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c
```

**Permanent exclusions：** 688671 · 301259 · **no DLC006R reopen** · **no first-slice mutate** · **no claim 20251231 live-proven**

---

## 6. Fixtures

| case_id | files | 覆盖 |
|---------|-------|------|
| DSD101 | `DSD101_found.json` | captured_normal · rdate=20260331 |
| DSD102 | `DSD102_found.json` · `DSD102_empty.json` | mixed · 20260331 |
| DSD103 | `DSD103_found.json` · `DSD103_empty.json` | mixed · 600519 diversify |
| DSD104 | `DSD104_found.json` · `DSD104_empty.json` | mixed · 20251231 unproven |
| DSD105 | `DSD105_empty_but_valid_synthetic.json` | empty control · 20251231 |

结构 cite first-slice Tier-1（只读）· fixture 仍标 `synthetic=true` · `cninfo_called=false` · `multi_rdate_slice=true`。

---

## 7. Artifacts

| 项 | 路径 |
|----|------|
| universe lock | [cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv](cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv) |
| VR | [cninfo_d_class_shareholder_data_next_slice_validation_rules_20260715.md](cninfo_d_class_shareholder_data_next_slice_validation_rules_20260715.md) |
| command draft | [cninfo_d_class_shareholder_data_next_slice_command_draft_20260715.md](cninfo_d_class_shareholder_data_next_slice_command_draft_20260715.md) |
| checklist | [cninfo_d_class_shareholder_data_next_slice_offline_prep_checklist_20260715.csv](cninfo_d_class_shareholder_data_next_slice_offline_prep_checklist_20260715.csv) |
| fixtures | `fixtures/d_class/shareholder_data_next_slice/` |
| fixture VR test | `lab/test_cninfo_d_class_shareholder_data_next_slice_fixtures.py` |
| evidence | [cninfo_d_class_shareholder_data_dfm32_next_slice_approval_package_20260715.md](cninfo_d_class_shareholder_data_dfm32_next_slice_approval_package_20260715.md) |

---

## 8. Red Lines

No CNINFO · No live · No runner implement · No first-slice mutate · No AT next-slice mutate · No FIA mutate · No ESS H3/H4 · No DLC006R reopen · No claim 20251231 live-proven · No verified · No commit · No push · No A/B/C touch · No Level-2 IDLE · No honest-flip AT live without controller_execution_allowed

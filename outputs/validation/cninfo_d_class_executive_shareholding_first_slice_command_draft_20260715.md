# CNINFO D 类 executive_shareholding First-Slice — Command Draft

_生成时间：2026-07-15_

> **状态：NOT APPROVED · DO NOT RUN** — 仅为未来命令形状草案 · **本任务未执行任何命令**
>
> **任务 ID：** D-R16-01
>
> **Gate：** `READY_FOR_APPROVAL` · `component_approved=false` · **NOT verified** · **NOT production_ready**

---

## 1. Purpose

在用户显式批准 **component** 以及后续 **first-slice runner / live** 后，对 **DES001–DES005** 执行 `executive_shareholding` 第一切片 metadata validation，验证 `leader/detail` 结构化行捕获与 `empty_but_valid` / `needs_review` 语义。

**本草案仅为未来命令形状** · **runner 未实现** · **dry-run / live 均未执行** · **CNINFO calls = 0**

---

## 2. Prerequisites

- [ ] human **component** approval：**I approve D-class executive_shareholding as the next Era D component.** — **NOT received** · `component_approved=false`
- [x] planning package（Run 15）ready · gate `READY_FOR_APPROVAL`
- [x] [universe lock](cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv) — **5 rows locked**
- [x] [approval package](cninfo_d_class_executive_shareholding_first_slice_approval_package_20260715.md) prepared
- [x] [validation rules](cninfo_d_class_executive_shareholding_validation_rules_20260715.md) VR-001–VR-042 promoted
- [x] [sample prep](cninfo_d_class_executive_shareholding_sample_prep_20260715.md) Tier-0=DC006/DLC007 only
- [ ] runner first-slice mode extension — **NOT implemented** · **FORBIDDEN this round**
- [ ] Tier-1 synthetic fixtures — **optional · S3 gated**
- [ ] human first-slice **live** approval phrase — **NOT received**
- [ ] human first-slice **runner** approval — **NOT received**

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_executive_shareholding_first_slice/
```

**禁止写入：**

- `cninfo_d_class_shareholder_change_first_slice/`
- `cninfo_d_class_known_event_replacement_validation/`
- `cninfo_d_class_known_event_targeted_probe/`
- `cninfo_d_class_margin_trading_first_slice/`
- `cninfo_d_class_disclosure_schedule_first_slice/`
- `cninfo_d_class_block_trade_first_slice/`
- `cninfo_d_class_restricted_shares_unlock_first_slice/`
- `cninfo_d_class_equity_pledge_first_slice/`
- `cninfo_d_class_tiny_live_validation/`（v1）
- `cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 4. Universe（locked）

```text
outputs/validation/cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv
```

| case_id | company_code | time_mark | vary_type | expected_behavior |
|---------|--------------|-----------|-----------|-------------------|
| DES001 | 002415 | oneMonth | b | captured_normal_or_needs_review |
| DES002 | 000895 | oneMonth | b | captured_normal_or_empty_but_valid |
| DES003 | 600000 | oneMonth | b | captured_normal_or_empty_but_valid |
| DES004 | 000550 | oneMonth | b | captured_normal_or_empty_but_valid |
| DES005 | 601988 | oneMonth | b | empty_but_valid |

**excluded primary cases：** 688671 · 301259（永久排除 · VR-004/VR-040）

**total request cap ≤ 20** · planned **~5**（单 timeMark+varyType / 案）

---

## 5. Approval Flags（规划 · 未实现）

```text
--executive-shareholding-first-slice
--approve-d-class-executive-shareholding-first-slice
```

**参照 prior slice 模式（shareholder_change `--shareholder-change-first-slice`）。** 当前 `lab/run_cninfo_d_class_tiny_live_validation.py` **不含** 上述 flag · **本轮禁止实现**。

---

## 6. Dry-Run Command（未来 · NOT APPROVED · DO NOT RUN）

**前置：** S4 runner extension approval · Tier-1 fixtures（可选） · component approved

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --executive-shareholding-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_first_slice/
```

**预期结果（未来）：** 5/5 planned_ok · planned ~5 · CNINFO **0**

**输出：**

- `reports/d_class_executive_shareholding_first_slice_dryrun_report.csv`
- `reports/d_class_executive_shareholding_first_slice_dryrun_summary.md`
- `planned_snapshots/{case_id}_executive_shareholding.json`（若实现）

---

## 7. Live Command（未来 · NOT APPROVED · DO NOT RUN）

**前置：** S5 explicit live approval · dry-run PASS · runner 已实现 · component approved

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --executive-shareholding-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_first_slice/ \
  --approve-d-class-executive-shareholding-first-slice
```

**CNINFO cap：** total **≤ 20** · planned **~5**

**Future acceptance threshold：** ≥3/5 acceptable → `PASS_WITH_CAVEAT` · **不是 bare PASS**

**预期输出：**

- `reports/d_class_executive_shareholding_first_slice_live_report.csv`
- `reports/d_class_executive_shareholding_first_slice_quality_report.csv`
- `reports/d_class_executive_shareholding_first_slice_live_outcome_ledger.csv`
- `live_snapshots/{case_id}_executive_shareholding.json`

---

## 8. Endpoint & Request Shape（规划）

| 项 | 值 |
|----|-----|
| endpoint | `POST https://www.cninfo.com.cn/data20/leader/detail` |
| params_location | query |
| `timeMark` | `oneMonth` |
| `varyType` | `b` |
| records_path | `data.records` |
| company filter | `SECCODE` == universe `company_code` |
| sleep | 0.6s between requests（默认 · 未来 live 规划值） |

---

## 9. Red Lines

- no DLC003R / DLC006R rerun · no 301259 / 688671 primary
- no shareholder_change / known-event / margin_trading / disclosure_schedule / block_trade / restricted_shares_unlock / equity_pledge reopen or expansion
- no disclosure→captured_normal
- no PDF download / parse / OCR / extraction
- no DB / MinIO / RAG writes
- no verified / production_ready / testing_stable_sample claim
- no threeMonth / oneYear / varyType=s in first-slice（VR-008）
- **no runner implement this round**
- **no CNINFO live this round**

---

## 10. Offline VR Harness（CNINFO=0 · 未来）

组件批准后、live 前，可对照 Tier-0（DC006/DLC007）与 Tier-1 synthetic fixtures 离线运行 VR-001–VR-042（见 [validation_rules](cninfo_d_class_executive_shareholding_validation_rules_20260715.md)）。**本草案不执行。**

---

## 11. Safety Zeros（this draft）

| 项 | 值 |
|----|-----|
| CNINFO calls | **0** |
| dry-run executed | **no** |
| live executed | **no** |
| runner invoked | **no** |
| runner implemented | **no** |
| commit / push | **no** |
| component_approved | **false** |

---

## 12. Summary Block

```text
task_id = D-R16-01
phase = executive_shareholding_first_slice_command_draft_20260715
status = NOT_APPROVED_DO_NOT_RUN
universe = universe_lock_20260715.csv
output_root = cninfo_d_class_executive_shareholding_first_slice/
flags = --executive-shareholding-first-slice (not implemented)
current_gate = READY_FOR_APPROVAL
component_approved = false
cninfo_calls = 0
next_gated_steps = human_component_approve / S3 fixtures / S4 dry-run / S5 live
```

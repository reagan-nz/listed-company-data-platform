# CNINFO D 类 shareholder_change First-Slice — Command Draft

_生成时间：2026-07-14_

> **状态：NOT APPROVED · DO NOT RUN** — 仅为未来命令形状草案 · **本任务未执行任何命令**
>
> **任务 ID：** D-GEN-20260714-06

---

## 1. Purpose

在用户显式批准 **first-slice runner / live** 后，对 **DSC001–DSC005** 执行 `shareholder_change` 第一切片 metadata validation，验证 `shareholeder/detail` 结构化行捕获与 `empty_but_valid` / `needs_review` 语义。

**本草案仅为未来命令形状** · **runner 未实现** · **dry-run / live 均未执行** · **CNINFO calls = 0**

---

## 2. Prerequisites

- [x] human **component** approval：**I approve D-class shareholder_change as the next Era D component.**（2026-07-14 · AQ-D-SC）
- [x] `d_class_shareholder_change_next_component_planning_gate = COMPONENT_APPROVED`
- [x] [first-slice plan draft](../plans/cninfo_d_class_shareholder_change_first_slice_plan_draft.md) prepared
- [x] [universe lock](cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv) — **5 rows locked**
- [x] [approval package](cninfo_d_class_shareholder_change_first_slice_approval_package_20260714.md) prepared
- [x] [validation rules](cninfo_d_class_shareholder_change_validation_rules_20260714.md) VR-001–VR-042 cross-ref
- [x] [sample prep](cninfo_d_class_shareholder_change_sample_prep_20260714.md) Tier-0/1/2 规格
- [ ] runner first-slice mode extension — **NOT implemented**
- [ ] Tier-1 synthetic fixtures — **optional · S3 gated**
- [ ] human first-slice **live** approval phrase — **NOT received**
- [ ] human first-slice **runner** approval — **NOT received**

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_shareholder_change_first_slice/
```

**禁止写入：**

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
outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv
```

| case_id | company_code | anchor_tdate | query_type | expected_behavior |
|---------|--------------|--------------|------------|-------------------|
| DSC001 | 000550 | 2026-07-03 | inc | captured_normal_or_empty_but_valid |
| DSC002 | 000895 | 2026-07-03 | inc | captured_normal_or_empty_but_valid |
| DSC003 | 600000 | 2026-07-03 | inc | captured_normal_or_empty_but_valid |
| DSC004 | 002415 | 2026-07-03 | inc | captured_normal_or_needs_review |
| DSC005 | 601988 | 2026-07-03 | inc | empty_but_valid |

**excluded primary cases：** 688671 · 301259（永久排除 · VR-004/VR-040）

**total request cap ≤ 20** · planned **~5**（单 type+tdate / 案）

---

## 5. Approval Flags（规划 · 未实现）

```text
--shareholder-change-first-slice
--approve-d-class-shareholder-change-first-slice
```

**参照 prior slice 模式（equity_pledge `--equity-pledge-first-slice`）。** 当前 `lab/run_cninfo_d_class_tiny_live_validation.py` **不含** 上述 flag。

---

## 6. Dry-Run Command（未来 · NOT APPROVED · DO NOT RUN）

**前置：** S4 runner extension approval · Tier-1 fixtures（可选）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --shareholder-change-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_first_slice/
```

**预期结果（未来）：** 5/5 planned_ok · planned ~5 · CNINFO **0**

**输出：**

- `reports/d_class_shareholder_change_first_slice_dryrun_report.csv`
- `reports/d_class_shareholder_change_first_slice_dryrun_summary.md`
- `planned_snapshots/{case_id}_shareholder_change.json`（若实现）

---

## 7. Live Command（未来 · NOT APPROVED · DO NOT RUN）

**前置：** S5 explicit live approval · dry-run PASS · runner 已实现

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --shareholder-change-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_first_slice/ \
  --approve-d-class-shareholder-change-first-slice
```

**CNINFO cap：** total **≤ 20** · planned **~5**

**Future acceptance threshold：** ≥3/5 acceptable → `PASS_WITH_CAVEAT` · **不是 bare PASS**

**预期输出：**

- `reports/d_class_shareholder_change_first_slice_live_report.csv`
- `reports/d_class_shareholder_change_first_slice_quality_report.csv`
- `reports/d_class_shareholder_change_first_slice_live_outcome_ledger.csv`
- `live_snapshots/{case_id}_shareholder_change.json`

---

## 8. Endpoint & Request Shape（规划）

| 项 | 值 |
|----|-----|
| endpoint | `POST https://www.cninfo.com.cn/data20/shareholeder/detail` |
| params_location | query |
| `type` | `inc` |
| `tdate` | `2026-07-03` |
| records_path | `data.records` |
| company filter | `SECCODE` == universe `company_code` |
| sleep | 0.6s between requests（默认） |

---

## 9. Red Lines

- no DLC003R / DLC006R rerun
- no known-event / margin_trading / disclosure_schedule / block_trade / restricted_shares_unlock / equity_pledge reopen or expansion
- no disclosure→captured_normal
- no PDF download / parse / OCR / extraction
- no DB / MinIO / RAG writes
- no verified / production_ready / testing_stable_sample claim
- no `type=desc` / decrease mode in first-slice（VR-008）
- **688671** · **301259** permanently excluded from primary universe

---

## 10. Offline VR Harness（CNINFO=0 · 未来）

组件批准后、live 前，可对照 Tier-1 synthetic fixtures 离线运行 VR-001–VR-042（见 [validation_rules](cninfo_d_class_shareholder_change_validation_rules_20260714.md) 第 7 节）。**本草案不执行。**

---

## 11. Safety Zeros（this draft）

| 项 | 值 |
|----|-----|
| CNINFO calls | **0** |
| dry-run executed | **no** |
| live executed | **no** |
| runner invoked | **no** |
| commit / push | **no** |

---

## 12. Summary Block

```text
task_id = D-GEN-20260714-06
phase = shareholder_change_first_slice_command_draft_20260714
status = NOT_APPROVED_DO_NOT_RUN
universe = universe_lock_20260714.csv
output_root = cninfo_d_class_shareholder_change_first_slice/
flags = --shareholder-change-first-slice (not implemented)
cninfo_calls = 0
next_gated_steps = S3 fixtures / S4 dry-run / S5 live
```

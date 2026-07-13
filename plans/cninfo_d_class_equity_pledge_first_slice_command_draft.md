# CNINFO D 类 equity_pledge First-Slice — Command Draft

_生成时间：2026-07-10_

> **状态：APPROVED_FOR_THIS_LIVE_ONLY** — dry-run **已执行** · live-path **已实现** · isolated live **已执行** · **NOT verified** · **NOT production_ready**

---

## 1. Purpose

在用户显式批准后，对 **DEP001–DEP005** 执行 `equity_pledge` 第一切片 metadata validation，验证 `equityPledge/list` 结构化行捕获与 `empty_but_valid` / `needs_review` 语义。

**本草案仅为未来命令形状** · **live-path 已离线实现（mock）** · **real live 未执行**

---

## 2. Prerequisites

- [x] human component approval：**I approve D-class equity_pledge as the next Era D component.**
- [x] `d_class_equity_pledge_next_component_planning_gate = PASS_WITH_CAVEAT`
- [x] [first-slice plan](cninfo_d_class_equity_pledge_first_slice_plan.md) prepared
- [x] [universe draft](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv) — **5 rows**
- [x] [approval checklist](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_approval_checklist.md) prepared
- [x] runner first-slice mode extension implemented → [extension summary](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_runner_extension_summary.md)
- [x] dry-run **5/5 planned_ok** · planned **5** · CNINFO **0**
- [x] tests **20/20 PASS**
- [x] live-path offline implementation → [live-path summary](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_path_summary.md) · tests **22/22** · mock only
- [x] isolated live executed → [live execution summary](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_execution_summary.md) · CNINFO **5** · acceptable **4/5**
- [x] `d_class_equity_pledge_first_slice_approval_gate` human-approved for **this live only**

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_equity_pledge_first_slice/
```

**禁止写入：**

- `cninfo_d_class_known_event_replacement_validation/`
- `cninfo_d_class_known_event_targeted_probe/`
- `cninfo_d_class_margin_trading_first_slice/`
- `cninfo_d_class_disclosure_schedule_first_slice/`
- `cninfo_d_class_block_trade_first_slice/`
- `cninfo_d_class_restricted_shares_unlock_first_slice/`
- `cninfo_d_class_tiny_live_validation/`（v1）
- `cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv
```

| case_id | company_code | anchor_tdate | expected_behavior |
|---------|--------------|--------------|-------------------|
| DEP001 | 688981 | 2026-07-03 | empty_but_valid（DLC005-style control） |
| DEP002 | 000895 | 2026-07-03 | captured_normal_or_empty_but_valid |
| DEP003 | 600000 | 2026-07-03 | captured_normal_or_empty_but_valid |
| DEP004 | 002415 | 2026-07-03 | captured_normal_or_needs_review |
| DEP005 | 601988 | 2026-07-03 | captured_normal_or_empty_but_valid |

**excluded primary cases：** 688671 · 301259

**total request cap ≤ 20** · planned **~5**（单 tdate / 案）

---

## 5. Approval Flags（规划 · 未实现）

```text
--equity-pledge-first-slice
--approve-d-class-equity-pledge-first-slice
```

---

## 6. Dry-Run Command（已完成 · CNINFO 0）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --equity-pledge-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_equity_pledge_first_slice/
```

结果：**5/5 planned_ok** · planned **5** · CNINFO **0**

---

## 7. Live Command（已执行 · 2026-07-10）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --equity-pledge-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_equity_pledge_first_slice/ \
  --approve-d-class-equity-pledge-first-slice
```

**Result：** acceptable **4/5** · CNINFO **5** · execution gate **`PASS_WITH_CAVEAT`**

详见 [live execution summary](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_execution_summary.md)

**Future acceptance threshold：** ≥3/5 acceptable → `PASS_WITH_CAVEAT`

---

## 8. Red Lines

- no DLC003R / DLC006R rerun
- no known-event / margin_trading / disclosure_schedule / block_trade / restricted_shares_unlock reopen or expansion
- no disclosure→captured_normal
- no PDF / OCR / extraction
- no DB / MinIO / RAG
- no verified / production_ready / testing_stable_sample
- no sole `captured_normal_candidate` on sparse anchor（RSU / block_trade lesson）

---

## 9. Gate

```text
d_class_equity_pledge_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_equity_pledge_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_equity_pledge_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_first_slice_execution_gate = PASS_WITH_CAVEAT
d_class_equity_pledge_next_component_planning_gate = PASS_WITH_CAVEAT
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
approved_for_runner = false
```

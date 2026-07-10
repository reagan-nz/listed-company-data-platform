# CNINFO D 类 block_trade First-Slice — Command Draft

_生成时间：2026-07-10_

> **状态：APPROVED_FOR_THIS_LIVE_ONLY** — isolated live **已执行** · **NOT verified** · **NOT production_ready**

---

## 1. Purpose

在用户显式批准后，对 **DBT001–DBT005** 执行 `block_trade` 第一切片 metadata validation，验证 `ints/statistics` 结构化行捕获与 `empty_but_valid` / `needs_review` 语义。

**本草案 dry-run 已执行** · **isolated live 已执行**（2026-07-10 · CNINFO **5** · acceptable **4/5**）

---

## 2. Prerequisites

- [x] `d_class_erad_next_component_planning_gate = READY_FOR_APPROVAL`
- [x] [first-slice plan](cninfo_d_class_block_trade_first_slice_plan.md) prepared
- [x] [universe draft](../outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv) — **5 rows**
- [x] [approval checklist](../outputs/validation/cninfo_d_class_block_trade_first_slice_approval_checklist.md) prepared
- [x] runner first-slice mode extension implemented → [extension summary](../outputs/validation/cninfo_d_class_block_trade_first_slice_runner_extension_summary.md)
- [x] dry-run **5/5 planned_ok** · planned **5** · CNINFO **0**
- [x] tests **19/19 PASS**（runner）
- [x] live-path offline implementation → [live-path summary](../outputs/validation/cninfo_d_class_block_trade_first_slice_live_path_summary.md)
- [x] live-path tests **18/18 PASS**（mock CNINFO only）
- [x] `d_class_block_trade_first_slice_approval_gate` human-approved for isolated live（**已批准** · 2026-07-10）
- [x] isolated live executed → [isolated live summary](../outputs/validation/cninfo_d_class_block_trade_first_slice_isolated_live_validation_summary.md)

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_block_trade_first_slice/
```

**禁止写入：**

- `cninfo_d_class_known_event_replacement_validation/`
- `cninfo_d_class_known_event_targeted_probe/`
- `cninfo_d_class_margin_trading_first_slice/`
- `cninfo_d_class_disclosure_schedule_first_slice/`
- `cninfo_d_class_tiny_live_validation/`（v1）
- `cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv
```

| case_id | company_code | anchor_tdate | expected_behavior |
|---------|--------------|--------------|-------------------|
| DBT001 | 601988 | 2026-07-03 | empty_but_valid（DLC002-style control） |
| DBT002 | 000895 | 2026-07-03 | captured_normal_candidate |
| DBT003 | 600000 | 2026-07-03 | captured_normal_or_empty_but_valid |
| DBT004 | 002415 | 2026-07-03 | captured_normal_or_empty_but_valid |
| DBT005 | 688981 | 2026-07-03 | captured_normal_or_empty_but_valid |

**excluded primary cases：** 688671 · 301259

**total request cap ≤ 20** · planned **~5**

---

## 5. Approval Flags（已实现 · live guard only）

```text
--block-trade-first-slice
--approve-d-class-block-trade-first-slice
```

---

## 6. Dry-Run Command（已完成 · CNINFO 0）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --block-trade-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_block_trade_first_slice/
```

结果：**5/5 planned_ok** · planned **5** · CNINFO **0**

---

## 7. Live Command（已执行 · 2026-07-10）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --block-trade-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_block_trade_first_slice/ \
  --approve-d-class-block-trade-first-slice
```

**结果：** CNINFO **5** · acceptable **4/5** · execution gate **`PASS_WITH_CAVEAT`** · caveat **DBT002 expectation_mismatch**（sparse-day empty）

**Future acceptance threshold：** ≥3/5 acceptable → `PASS_WITH_CAVEAT`

---

## 8. Red Lines

- no DLC003R / DLC006R rerun
- no known-event / margin_trading / disclosure_schedule reopen or expansion
- no disclosure→captured_normal
- no PDF / OCR / extraction
- no DB / MinIO / RAG
- no verified / production_ready / testing_stable_sample

---

## 9. Gate

```text
d_class_block_trade_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_block_trade_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_block_trade_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_block_trade_first_slice_execution_gate = PASS_WITH_CAVEAT
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
```

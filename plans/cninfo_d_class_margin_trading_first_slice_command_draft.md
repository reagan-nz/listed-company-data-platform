# CNINFO D 类 margin_trading First-Slice — Command Draft

_生成时间：2026-07-10_

> **状态：NOT APPROVED** — 未来 live 命令草案 only · **Do not execute**

---

## 1. Purpose

在用户显式批准后，对 **DMT001–DMT005** 执行 `margin_trading` 第一切片 metadata validation，验证 `company_metric_daily` 结构化行捕获与 empty_but_valid / needs_review 语义。

**本草案不执行** · **live 路径已离线实现**（dry-run + approval guard + live path **已实现** · **NOT APPROVED**）

---

## 2. Prerequisites

- [x] `d_class_next_component_planning_gate = READY_FOR_HUMAN_DECISION`
- [x] [first-slice plan](cninfo_d_class_margin_trading_first_slice_plan.md) prepared
- [x] [universe draft](../outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv) — **5 rows**
- [x] [approval checklist](../outputs/validation/cninfo_d_class_margin_trading_first_slice_approval_checklist.md) prepared
- [x] runner first-slice mode extension implemented → [extension summary](../outputs/validation/cninfo_d_class_margin_trading_first_slice_runner_extension_summary.md)
- [x] dry-run **5/5 planned_ok** · planned **20** · CNINFO **0**
- [x] tests **21/21 PASS**（runner）+ **19/19 PASS**（live-path · mock only）= **40/40 PASS**
- [x] live path implementation offline complete → [live-path summary](../outputs/validation/cninfo_d_class_margin_trading_first_slice_live_path_summary.md)
- [x] `d_class_margin_trading_first_slice_live_path_gate = READY_FOR_APPROVAL`
- [ ] `d_class_margin_trading_first_slice_approval_gate` human-approved for live（**未批准**）

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_margin_trading_first_slice/
```

**禁止写入：**

- `cninfo_d_class_known_event_replacement_validation/`
- `cninfo_d_class_known_event_targeted_probe/`
- `cninfo_d_class_tiny_live_validation/`（v1）
- `cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv
```

| case_id | company_code | anchor_tdate |
|---------|--------------|--------------|
| DMT001 | 000895 | 2026-07-08 |
| DMT002 | 600000 | 2026-07-08 |
| DMT003 | 601988 | 2026-07-08 |
| DMT004 | 002415 | 2026-07-08 |
| DMT005 | 688981 | 2026-07-08 |

**excluded primary cases：** 688671 · 301259

**total request cap ≤ 20**

---

## 5. Approval Flags（已实现）

```text
--margin-trading-first-slice
--approve-d-class-margin-trading-first-slice
```

---

## 6. Dry-Run Command（已完成 · CNINFO 0）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --margin-trading-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_margin_trading_first_slice/
```

结果：**5/5 planned_ok** · planned **20** · CNINFO **0**

---

## 7. Future Live Command（NOT APPROVED · DO NOT RUN）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --margin-trading-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_margin_trading_first_slice/ \
  --approve-d-class-margin-trading-first-slice
```

**禁止执行** — live path **已实现但未批准** · approval guard 仍将在无批准时拒绝真实 CNINFO

**Future acceptance threshold：** ≥3/5 acceptable → `PASS_WITH_CAVEAT`（**本任务不评估**）

---

## 8. Red Lines

- no DLC003R / DLC006R rerun
- no known-event replacement reopen
- no disclosure→captured_normal
- no PDF / OCR / extraction
- no DB / MinIO / RAG
- no verified / production_ready / testing_stable_sample

---

## 9. Gate

```text
d_class_margin_trading_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_margin_trading_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_margin_trading_first_slice_live_path_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
approved_for_live = false
```

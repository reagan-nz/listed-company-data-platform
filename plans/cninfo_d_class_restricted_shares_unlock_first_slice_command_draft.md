# CNINFO D 类 restricted_shares_unlock First-Slice — Command Draft

_生成时间：2026-07-10_

> **状态：NOT APPROVED** — dry-run **已执行** · live-path **已实现**（mock tests **22/22**）· **DO NOT RUN real live**

---

## 1. Purpose

在用户显式批准后，对 **DRU001–DRU005** 执行 `restricted_shares_unlock` 第一切片 metadata validation，验证 `liftBan/detail` 结构化行捕获与 `empty_but_valid` / `needs_review` 语义。

**本草案 dry-run 已执行** · **live-path 已离线实现**（mock tests only · **NOT APPROVED for real live**）

---

## 2. Prerequisites

- [x] human component approval：**I approve D-class restricted_shares_unlock as the next Era D component.**
- [x] `d_class_erad_next_component_planning_refresh_gate = PASS_WITH_CAVEAT`
- [x] [first-slice plan](cninfo_d_class_restricted_shares_unlock_first_slice_plan.md) prepared
- [x] [universe draft](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv) — **5 rows**
- [x] [approval checklist](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_approval_checklist.md) prepared
- [x] runner first-slice mode extension implemented → [extension summary](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_runner_extension_summary.md)
- [x] dry-run **5/5 planned_ok** · planned **20** · CNINFO **0**
- [x] tests **20/20 PASS**（runner）
- [x] live-path offline implementation → [live-path summary](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_live_path_summary.md) · tests **22/22 PASS**（mock only）
- [ ] `d_class_restricted_shares_unlock_first_slice_approval_gate` human-approved for **real** live → **未批准**

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/
```

**禁止写入：**

- `cninfo_d_class_known_event_replacement_validation/`
- `cninfo_d_class_known_event_targeted_probe/`
- `cninfo_d_class_margin_trading_first_slice/`
- `cninfo_d_class_disclosure_schedule_first_slice/`
- `cninfo_d_class_block_trade_first_slice/`
- `cninfo_d_class_tiny_live_validation/`（v1）
- `cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv
```

| case_id | company_code | anchor_tdate | expected_behavior |
|---------|--------------|--------------|-------------------|
| DRU001 | 300009 | 2026-06-08 | empty_but_valid（DLC003-style control） |
| DRU002 | 000895 | 2026-06-08 | captured_normal_or_empty_but_valid |
| DRU003 | 600000 | 2026-06-08 | captured_normal_or_empty_but_valid |
| DRU004 | 002415 | 2026-06-08 | captured_normal_or_needs_review |
| DRU005 | 688981 | 2026-06-08 | captured_normal_or_empty_but_valid |

**excluded primary cases：** 688671 · 301259

**total request cap ≤ 20** · planned **~5–20**（multi-probe）

---

## 5. Approval Flags（规划 · 未实现）

```text
--restricted-shares-unlock-first-slice
--approve-d-class-restricted-shares-unlock-first-slice
```

---

## 6. Dry-Run Command（已完成 · CNINFO 0）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --restricted-shares-unlock-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/
```

结果：**5/5 planned_ok** · planned **20** · CNINFO **0**

---

## 7. Live Command（未来 · 显式 live 批准后 · path 已实现 · 未执行）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --restricted-shares-unlock-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/ \
  --approve-d-class-restricted-shares-unlock-first-slice
```

**Future acceptance threshold：** ≥3/5 acceptable → `PASS_WITH_CAVEAT`

**当前状态：** **DO NOT RUN** — **NOT APPROVED for real live** · requires phrase:

> I approve D-class restricted_shares_unlock first-slice live validation.

---

## 8. Red Lines

- no DLC003R / DLC006R rerun
- no known-event / margin_trading / disclosure_schedule / block_trade reopen or expansion
- no disclosure→captured_normal
- no PDF / OCR / extraction
- no DB / MinIO / RAG
- no verified / production_ready / testing_stable_sample
- no sole `captured_normal_candidate` on sparse anchor（block_trade lesson）

---

## 9. Gate

```text
d_class_restricted_shares_unlock_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_erad_next_component_planning_refresh_gate = PASS_WITH_CAVEAT
approval_status = NOT_APPROVED
approved_for_live = false
approved_for_runner = false
```

# CNINFO D 类 margin_trading First-Slice — Live Path Summary

_生成时间：2026-07-10_

> **approval_status = NOT_APPROVED** · **approved_for_live = false** · **Do not execute live**

---

## 1. Scope

离线实现 `margin_trading` 第一切片 live path，供未来人工批准后执行 **DMT001–DMT005** 五案 universe。**本任务未执行 live** · **CNINFO calls = 0**。

---

## 2. Implemented Live Path

| 项 | 内容 |
|----|------|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| entry | `run_margin_trading_first_slice()` → `execute_margin_trading_first_slice_live()` |
| probe plan | `build_margin_trading_first_slice_live_probe_plan()` |
| per-case execution | `execute_v2_bounded_probe_case()`（metadata / structured-table only） |
| live report | `write_margin_trading_first_slice_live_report()` |
| quality report | `write_margin_trading_first_slice_quality_report()` |
| live summary | `write_margin_trading_first_slice_live_summary()` |
| execution gate | `compute_margin_trading_first_slice_execution_gate()`（≥3/5 acceptable → `PASS_WITH_CAVEAT`） |
| live-path gate | **`d_class_margin_trading_first_slice_live_path_gate = READY_FOR_APPROVAL`** |

---

## 3. Approval Guard（仍必需）

Live 在 **任何 CNINFO 调用之前** 拒绝，若：

- 缺少 `--approve-d-class-margin-trading-first-slice`
- approval flag 错误
- universe size ≠ **5**
- case_id 不在 **DMT001–DMT005**
- company_code **688671** 或 **301259** 出现
- output root 非 `outputs/validation/cninfo_d_class_margin_trading_first_slice/`

**approval_status = NOT_APPROVED** · **approved_for_live = false**

---

## 4. Universe & Component Constraints

- universe：`outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv`（**5** 行）
- case_id：**DMT001–DMT005**
- component：**margin_trading** only
- endpoint：`margin_trading/detailList`
- anchor_tdate：**2026-07-08**
- excluded primary cases：**688671** · **301259**

| case_id | company_code |
|---------|--------------|
| DMT001 | 000895 |
| DMT002 | 600000 |
| DMT003 | 601988 |
| DMT004 | 002415 |
| DMT005 | 688981 |

---

## 5. Output Isolation & Write-Blocks

**仅允许写入：**

```text
outputs/validation/cninfo_d_class_margin_trading_first_slice/
```

**写入阻断：**

- `cninfo_d_class_known_event_replacement_validation/`
- `cninfo_d_class_known_event_targeted_probe/`
- `cninfo_d_class_tiny_live_validation/`（v1）
- `cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 6. Request Cap

- per-case ≤ **4**
- total ≤ **20**
- `validate_margin_trading_first_slice_request_caps()` 在 planning / guards 中强制执行

---

## 7. Safety Confirmations

| 约束 | 状态 |
|------|------|
| PDF download | **blocked** |
| PDF parse | **blocked** |
| OCR | **blocked** |
| extraction | **blocked** |
| DB | **blocked** |
| MinIO | **blocked** |
| RAG | **blocked** |
| verified | **blocked** |
| production_ready | **blocked** |
| testing_stable_sample | **blocked** |
| disclosure→captured_normal | **blocked** |
| DLC003R rerun | **no** |
| DLC006R rerun | **no** |
| known-event track reopen | **no** |

**known-event track remains closed** · `d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT`

---

## 8. Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_margin_trading_first_slice_runner.py` | **21/21 PASS** |
| `lab/test_cninfo_d_class_margin_trading_first_slice_live_path.py` | **19/19 PASS**（mock CNINFO · 不执行真实 live） |
| **合计** | **40/40 PASS** |

Live-path 测试覆盖：approval guard · universe size · case_id · component · 688671/301259 排除 · output isolation · write-blocks · request cap · PDF/OCR/extraction/DB/MinIO/RAG 阻断 · verified/production_ready 阻断 · captured_normal upgrade 阻断 · dry-run 5/5 CNINFO 0。

---

## 9. Dry-Run Reconfirm（本任务）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --margin-trading-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_margin_trading_first_slice/
```

结果：**5/5 planned_ok** · planned **20** · **CNINFO = 0**

---

## 10. Future Live Command（NOT APPROVED · DO NOT RUN）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --margin-trading-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_margin_trading_first_slice/ \
  --approve-d-class-margin-trading-first-slice
```

**Future acceptance threshold：** ≥3/5 acceptable → `PASS_WITH_CAVEAT`（**本任务不评估**）

---

## 11. Gate Status

```text
d_class_margin_trading_first_slice_live_path_gate = READY_FOR_APPROVAL
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Prior gates unchanged：

- `d_class_margin_trading_first_slice_runner_extension_gate = READY_FOR_APPROVAL`
- `d_class_margin_trading_first_slice_approval_gate = READY_FOR_APPROVAL`
- `d_class_next_component_planning_gate = READY_FOR_HUMAN_DECISION`
- `d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT`

---

## 12. Task Safety Confirmations

- **CNINFO calls = 0**（本任务）
- **no live executed**
- **no first-slice live report created**（仅 dry-run 产物保留）
- **688671 / 301259 still excluded**
- **known-event track remains closed**

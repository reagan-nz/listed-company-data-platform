# CNINFO D 类 block_trade First-Slice — Isolated Live Validation Summary

_生成时间：2026-07-10_

> **性质：** isolated live validation · human-approved · **NOT verified** · **NOT production_ready**

---

## 1. Approval

Human approval phrase received:

> **I approve D-class block_trade first-slice live validation.**

```text
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
```

---

## 2. Command Executed

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --block-trade-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_block_trade_first_slice/ \
  --approve-d-class-block-trade-first-slice
```

**exit code：** **0**

---

## 3. Result

| 项 | 值 |
|----|-----|
| universe | DBT001–DBT005（**5**） |
| component | **block_trade** only |
| anchor_tdate | **2026-07-03** |
| CNINFO requests | **5**（cap ≤ **20**） |
| acceptable | **4/5** |
| execution gate | **`PASS_WITH_CAVEAT`** |
| excluded codes | **688671** · **301259** not in universe |

| case_id | company | expected_behavior | retrieval_status | acceptable | failure_type |
|---------|---------|-------------------|------------------|------------|--------------|
| DBT001 | 601988 | empty_but_valid | empty_but_valid | yes | — |
| DBT002 | 000895 | captured_normal_candidate | empty_but_valid | **no** | expectation_mismatch |
| DBT003 | 600000 | captured_normal_or_empty_but_valid | empty_but_valid | yes | — |
| DBT004 | 002415 | captured_normal_or_empty_but_valid | empty_but_valid | yes | — |
| DBT005 | 688981 | captured_normal_or_empty_but_valid | empty_but_valid | yes | — |

**retrieval_status 汇总：** empty_but_valid **×5** · found **0** · http_error **0**

---

## 4. Caveat（DBT002）

DBT002（000895 双汇发展）标注为 `captured_normal_candidate`，但 anchor `tdate=2026-07-03` 当日公司级过滤后 **0 行** → `empty_but_valid`。

- 符合 quality policy 的合法空结果
- 与 `captured_normal_candidate` 期望不一致 → `expectation_mismatch`
- 不影响 execution gate（**4/5 ≥ 3/5** → `PASS_WITH_CAVEAT`）
- 全 universe 当日均为 sparse-day empty；无 `found` 样本本回合

---

## 5. Artifacts

| artifact | path |
|----------|------|
| live report | [d_class_block_trade_first_slice_live_report.csv](cninfo_d_class_block_trade_first_slice/reports/d_class_block_trade_first_slice_live_report.csv) |
| quality report | [d_class_block_trade_first_slice_quality_report.csv](cninfo_d_class_block_trade_first_slice/reports/d_class_block_trade_first_slice_quality_report.csv) |
| live summary | [d_class_block_trade_first_slice_live_summary.md](cninfo_d_class_block_trade_first_slice/reports/d_class_block_trade_first_slice_live_summary.md) |
| live snapshots | `cninfo_d_class_block_trade_first_slice/live_snapshots/DBT00{1-5}_block_trade.json` |

---

## 6. Safety Confirmations

- [x] output root isolated → `outputs/validation/cninfo_d_class_block_trade_first_slice/`
- [x] no known-event / margin_trading / disclosure_schedule root mutation
- [x] no A/B/C live root mutation
- [x] no PDF / OCR / extraction / DB / MinIO / RAG
- [x] no verified / production_ready / bare PASS
- [x] closed tracks remain **closed**
- [x] no commit · no push

---

## 7. Gates

```text
d_class_block_trade_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_block_trade_first_slice_execution_gate = PASS_WITH_CAVEAT
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
```

**NOT bare PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 8. Next Step

**block_trade first-slice closure review**（offline · CNINFO **0** · **无 commit**）

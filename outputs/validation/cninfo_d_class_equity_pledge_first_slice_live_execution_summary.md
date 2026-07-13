# CNINFO D 类 equity_pledge First-Slice — Isolated Live Execution Summary

_生成时间：2026-07-10_

> **性质：** isolated live validation · human-approved · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**

---

## 1. Approval

Human approval phrase received:

> **I approve D-class equity_pledge first-slice live validation.**

```text
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
```

---

## 2. Command Executed

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --equity-pledge-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_equity_pledge_first_slice/ \
  --approve-d-class-equity-pledge-first-slice
```

**exit code：** **0**

---

## 3. Result

| 项 | 值 |
|----|-----|
| universe | DEP001–DEP005（**5**） |
| component | **equity_pledge** only |
| anchor_tdate | **2026-07-03** |
| endpoint | `https://www.cninfo.com.cn/data20/equityPledge/list` |
| CNINFO requests | **5**（cap ≤ **20** · **1/case**） |
| acceptable | **4/5** |
| executed | **5/5** |
| execution gate | **`PASS_WITH_CAVEAT`** |
| excluded codes | **688671** · **301259** not in universe |

### Per-case outcomes

| case_id | company | expected_behavior | retrieval_status | acceptable | outcome | failure_type |
|---------|---------|-------------------|------------------|------------|---------|--------------|
| DEP001 | 688981 中芯国际 | empty_but_valid | empty_but_valid | yes | empty_but_valid | — |
| DEP002 | 000895 双汇发展 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid | — |
| DEP003 | 600000 浦发银行 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid | — |
| DEP004 | 002415 海康威视 | captured_normal_or_needs_review | empty_but_valid | **no** | empty_but_valid | expectation_mismatch |
| DEP005 | 601988 中国银行 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid | — |

**outcome mix：** empty_but_valid **×5** · found **0** · needs_review **0** · fail **0**

**retrieval_status 汇总：** empty_but_valid **×5** · http_error **0**

---

## 4. Caveat（DEP004）

DEP004（002415 海康威视）标注为 `captured_normal_or_needs_review`，但 anchor `tdate=2026-07-03` 当日公司级过滤后 **0 行** → `empty_but_valid`。

- 符合 quality policy 的合法空结果（**未**升级为 found / captured_normal）
- 与 `captured_normal_or_needs_review` 期望不一致 → `expectation_mismatch`
- 不影响 execution gate（**4/5 ≥ 3/5** → `PASS_WITH_CAVEAT`）
- 全 universe 当日均为 sparse-day empty；无 `found` 样本本回合

---

## 5. Artifacts

| artifact | path |
|----------|------|
| live report | [d_class_equity_pledge_first_slice_live_report.csv](cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_live_report.csv) |
| quality report | [d_class_equity_pledge_first_slice_quality_report.csv](cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_quality_report.csv) |
| live summary | [d_class_equity_pledge_first_slice_live_summary.md](cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_live_summary.md) |
| outcome ledger | [cninfo_d_class_equity_pledge_first_slice_live_outcome_ledger.csv](cninfo_d_class_equity_pledge_first_slice_live_outcome_ledger.csv) |
| live snapshots | `cninfo_d_class_equity_pledge_first_slice/live_snapshots/DEP00{1-5}_equity_pledge.json` |

---

## 6. Safety Confirmations

- [x] output root isolated → `outputs/validation/cninfo_d_class_equity_pledge_first_slice/`
- [x] no known-event / margin_trading / disclosure_schedule / block_trade / RSU root mutation
- [x] no A/B/C live root mutation
- [x] no PDF / OCR / extraction / DB / MinIO / RAG
- [x] no verified / production_ready / bare PASS
- [x] closed tracks remain **closed**
- [x] no commit · no push

---

## 7. Gates

```text
d_class_equity_pledge_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_first_slice_execution_gate = PASS_WITH_CAVEAT
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
```

**NOT bare PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 8. Next Step

**equity_pledge first-slice closure / commit-boundary package**（offline · CNINFO **0** · **无 commit**）

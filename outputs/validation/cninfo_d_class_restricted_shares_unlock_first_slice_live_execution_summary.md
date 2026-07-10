# CNINFO D 类 restricted_shares_unlock First-Slice — Isolated Live Execution Summary

_生成时间：2026-07-10_

> **性质：** isolated live validation · human-approved · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**

---

## 1. Approval

Human approval phrase received:

> **I approve D-class restricted_shares_unlock first-slice live validation.**

```text
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
```

---

## 2. Command Executed

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --restricted-shares-unlock-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/ \
  --approve-d-class-restricted-shares-unlock-first-slice
```

**exit code：** **0**

---

## 3. Result

| 项 | 值 |
|----|-----|
| universe | DRU001–DRU005（**5**） |
| component | **restricted_shares_unlock** only |
| anchor_tdate | **2026-06-08** |
| endpoint | `liftBan/detail` |
| CNINFO requests | **15**（cap ≤ **20** · **3/case** · no early_stop） |
| acceptable | **5/5** |
| executed | **5/5** |
| execution gate | **`PASS_WITH_CAVEAT`** |
| excluded codes | **688671** · **301259** not in universe |

### Per-case outcomes

| case_id | company | expected_behavior | retrieval_status | acceptable | outcome |
|---------|---------|-------------------|------------------|------------|---------|
| DRU001 | 300009 安科生物 | empty_but_valid | empty_but_valid | yes | empty_but_valid |
| DRU002 | 000895 双汇发展 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid |
| DRU003 | 600000 浦发银行 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid |
| DRU004 | 002415 海康威视 | captured_normal_or_needs_review | empty_but_valid | yes | empty_but_valid |
| DRU005 | 688981 中芯国际 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid |

**outcome mix：** empty_but_valid **×5** · found **0** · needs_review **0** · fail **0**

**retrieval_status 汇总：** empty_but_valid **×5** · http_error **0**

---

## 4. Sparse-Day Note

Anchor `tdate=2026-06-08` 全宇宙 **5/5** 公司级零行（multi-probe 各 **3** 请求后耗尽 cap）。

- 全部 `empty_but_valid` 属 quality policy 合法结果
- expectation mix 已吸收 block_trade DBT002 教训（无 sole `captured_normal_candidate`）
- 本回合无 `found` 样本 · 不影响 gate（**5/5 ≥ 3/5** → `PASS_WITH_CAVEAT`）

---

## 5. Artifacts

| artifact | path |
|----------|------|
| live report | [d_class_restricted_shares_unlock_first_slice_live_report.csv](cninfo_d_class_restricted_shares_unlock_first_slice/reports/d_class_restricted_shares_unlock_first_slice_live_report.csv) |
| quality report | [d_class_restricted_shares_unlock_first_slice_quality_report.csv](cninfo_d_class_restricted_shares_unlock_first_slice/reports/d_class_restricted_shares_unlock_first_slice_quality_report.csv) |
| live summary | [d_class_restricted_shares_unlock_first_slice_live_summary.md](cninfo_d_class_restricted_shares_unlock_first_slice/reports/d_class_restricted_shares_unlock_first_slice_live_summary.md) |
| outcome ledger | [cninfo_d_class_restricted_shares_unlock_first_slice_per_case_outcome_ledger.csv](cninfo_d_class_restricted_shares_unlock_first_slice_per_case_outcome_ledger.csv) |
| live snapshots | `cninfo_d_class_restricted_shares_unlock_first_slice/live_snapshots/DRU00{1-5}_restricted_shares_unlock.json` |

---

## 6. Gates

```text
d_class_restricted_shares_unlock_first_slice_execution_gate = PASS_WITH_CAVEAT
d_class_restricted_shares_unlock_first_slice_live_path_gate = READY_FOR_APPROVAL
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
```

**NOT bare PASS** · **NOT verified** · **NOT production_ready**

---

## 7. Safety Confirmations

| 项 | 本回合 |
|----|--------|
| commit / push | **no** |
| PDF / DB / MinIO / RAG | **no** |
| closed tracks mutated | **no** |
| block_trade verified claim | **no**（`403472d` · NOT verified · NOT pushed） |

---

## 8. Next Step

**restricted_shares_unlock first-slice closure / commit-boundary package**（offline · CNINFO **0**）

# CNINFO D 类 restricted_shares_unlock First-Slice Live-Path Summary

_生成时间：2026-07-10_

> **性质：** live-path offline implementation + mock tests only · **CNINFO calls = 0**（本任务）· **NOT APPROVED for live**

---

## Implementation

| 项 | 值 |
|----|-----|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| live function | `execute_restricted_shares_unlock_first_slice_live()` |
| mode flag | `--restricted-shares-unlock-first-slice` |
| approval flag | `--approve-d-class-restricted-shares-unlock-first-slice` |
| tests | `lab/test_cninfo_d_class_restricted_shares_unlock_first_slice_live_path.py`（**22/22 PASS**） |
| runner tests | `lab/test_cninfo_d_class_restricted_shares_unlock_first_slice_runner.py`（**20/20 PASS**） |
| stub removed | **yes**（`restricted_shares_unlock_first_slice_live_not_implemented` replaced） |

---

## Live-Path Semantics

| 项 | 值 |
|----|-----|
| endpoint | `liftBan/detail` |
| layer | `company_event`（metadata / structured-table only） |
| multi-probe | anchor + ±1 day · **≤4/case** · **≤20 total** |
| early_stop | per-case on company-level hit |
| allowed outcomes | `found` · `empty_but_valid` · `needs_review` |
| execution threshold | **≥3/5 acceptable → PASS_WITH_CAVEAT** |

---

## Mock Verification（本任务）

| 项 | 值 |
|----|-----|
| real CNINFO | **0** |
| mock parent | `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/_mock_live_tests/` |
| production live report | **not written**（mock isolated subdirs only） |

---

## Dry-Run Reconfirm

| 指标 | 值 |
|------|-----|
| planned_ok | **5/5** |
| planned_request_count_total | **20** |
| CNINFO calls | **0** |

---

## Gates

```text
d_class_restricted_shares_unlock_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_first_slice_approval_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
approved_for_live = false
```

**NOT PASS live** · **NOT verified** · **NOT production_ready**

---

## Next Step

Human approve isolated live with exact phrase:

> **I approve D-class restricted_shares_unlock first-slice live validation.**

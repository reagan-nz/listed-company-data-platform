# CNINFO D 类 restricted_shares_unlock First-Slice Runner Extension Summary

_生成时间：2026-07-10_

> **性质：** runner extension + dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**

---

## Implementation

| 项 | 值 |
|----|-----|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| mode flag | `--restricted-shares-unlock-first-slice` |
| approval flag | `--approve-d-class-restricted-shares-unlock-first-slice` |
| tests | `lab/test_cninfo_d_class_restricted_shares_unlock_first_slice_runner.py`（**20/20 PASS**） |
| live path | **implemented** → [live-path summary](cninfo_d_class_restricted_shares_unlock_first_slice_live_path_summary.md)（mock **22/22**） |

---

## Dry-Run Result

| 指标 | 值 |
|------|-----|
| planned_ok | **5/5** |
| planned_request_count_total | **20** |
| CNINFO calls | **0** |
| output root | `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/` |

| 产物 | 路径 |
|------|------|
| dry-run report | [d_class_restricted_shares_unlock_first_slice_dryrun_report.csv](cninfo_d_class_restricted_shares_unlock_first_slice/reports/d_class_restricted_shares_unlock_first_slice_dryrun_report.csv) |
| dry-run summary | [d_class_restricted_shares_unlock_first_slice_dryrun_summary.md](cninfo_d_class_restricted_shares_unlock_first_slice/reports/d_class_restricted_shares_unlock_first_slice_dryrun_summary.md) |

---

## Guards Enforced

- universe size = **5** · case_id **DRU001–DRU005** only
- component = **restricted_shares_unlock** · anchor_tdate = **2026-06-08**
- exclude **688671** · **301259**
- per-case request budget **≤ 4** · total cap **≤ 20**（planned **20**）
- write-block: v1/v2 tiny-live · known-event · margin_trading · disclosure_schedule · block_trade roots
- live without approval → reject before CNINFO
- live with approval → gated live path（**NOT APPROVED for real CNINFO in this task**）
- PDF/OCR/extraction/DB/MinIO/RAG/verified/production_ready blocked

---

## Gates

```text
d_class_restricted_shares_unlock_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_first_slice_approval_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
approved_for_live = false
```

**NOT PASS live** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Next Step

Human approve isolated live with exact phrase:

> **I approve D-class restricted_shares_unlock first-slice live validation.**

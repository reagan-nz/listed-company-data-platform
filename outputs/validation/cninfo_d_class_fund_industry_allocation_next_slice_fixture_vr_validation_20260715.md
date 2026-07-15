# CNINFO D 类 fund_industry_allocation — Next-Slice Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-24 · wall≈0.01s_

> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/fund_industry_allocation_next_slice/` |
| universe lock | `cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv` |
| fixtures | **8** |
| matrix rows | **13** |
| first-slice lock sha256 | `49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c` |
| CNINFO | **0** |

```text
d_class_fund_industry_allocation_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_fund_industry_allocation_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_next_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_next_slice_runner_gate = NOT_APPROVED
fund_industry_allocation_component_approved = standing_scope
first_slice_mutated = false
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_fund_industry_allocation_next_slice_fixtures.py`

```text
task_id = D-FM-24
phase = fund_industry_allocation_next_slice_approval_package_offline
```

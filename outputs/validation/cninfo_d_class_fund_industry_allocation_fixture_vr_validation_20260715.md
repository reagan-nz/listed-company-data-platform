# CNINFO D 类 fund_industry_allocation — Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-11 · wall≈0.00s_

> **性质：** Tier-1 fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/fund_industry_allocation_first_slice/` |
| universe lock | `cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv` |
| fixtures | **7** |
| matrix rows | **11** |
| CNINFO | **0** |

```text
d_class_fund_industry_allocation_fixture_vr_gate = PASS_OFFLINE
d_class_fund_industry_allocation_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_first_slice_runner_gate = NOT_APPROVED
fund_industry_allocation_component_approved = standing_scope
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_fund_industry_allocation_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_fund_industry_allocation_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_fund_industry_allocation_fixtures.py`

```text
task_id = D-FM-11
phase = fund_industry_allocation_first_slice_approval_package_offline
```

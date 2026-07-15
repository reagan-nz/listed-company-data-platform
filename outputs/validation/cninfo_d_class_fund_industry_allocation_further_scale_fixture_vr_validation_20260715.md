# CNINFO D 类 fund_industry_allocation — Further-Scale Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-38 · wall≈0.01s_

> **性质：** Tier-1 further-scale fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/fund_industry_allocation_further_scale/` |
| universe lock | `cninfo_d_class_fund_industry_allocation_further_scale_universe_lock_20260715.csv` |
| fixtures | **8** |
| matrix rows | **13** |
| first-slice lock sha256 | `49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c` |
| next-slice lock sha256 | `c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515` |
| CNINFO | **0** |

```text
d_class_fund_industry_allocation_further_scale_fixture_vr_gate = PASS_OFFLINE
d_class_fund_industry_allocation_further_scale_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_further_scale_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_further_scale_runner_gate = NOT_APPROVED
fund_industry_allocation_component_approved = standing_scope
controller_execution_allowed = false
fia_first_next_mutated = false
at_sd_dryrun_mutated = false
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_fund_industry_allocation_further_scale_fixtures.py`

```text
task_id = D-FM-38
phase = fund_industry_allocation_further_scale_approval_package_offline
```

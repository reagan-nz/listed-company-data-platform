# CNINFO D 类 shareholder_data — Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-07 · wall≈0.00s_

> **性质：** Tier-1 fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/shareholder_data_first_slice/` |
| universe lock | `cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv` |
| fixtures | **9** |
| matrix rows | **13** |
| CNINFO | **0** |

```text
d_class_shareholder_data_fixture_vr_gate = PASS_OFFLINE
d_class_shareholder_data_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED
d_class_shareholder_data_first_slice_runner_gate = NOT_APPROVED
shareholder_data_component_approved = standing_scope
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_shareholder_data_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_shareholder_data_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_shareholder_data_fixtures.py`

```text
task_id = D-FM-07
phase = shareholder_data_first_slice_approval_package_offline
```

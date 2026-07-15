# CNINFO D 类 shareholder_change — Next-Slice Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-50 · wall≈0.01s_

> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/shareholder_change_next_slice/` |
| universe lock | `cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv` |
| fixtures | **9** |
| matrix rows | **13** |
| query_type | `desc` |
| anchor_tdate | `2026-07-03` |
| SC next-slice lock sha256 | `5452bc546def60754182a0e5b38fb165d709a37e0a267113088732237b5508fb` |
| SC first-slice lock sha256 | `49e6ece0c0a5c5ecce32328e4e1fe990b48d7d46d3cc1f32da1c8d2245a3c402` |
| RSU next-slice lock sha256 | `13254f44f344c0f2976dfbde6fe75e363f91283a6eec1a5ae02d29f3831f193f` |
| EP next-slice lock sha256 | `1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384` |
| CNINFO | **0** |

```text
d_class_shareholder_change_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_shareholder_change_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_change_next_slice_live_gate = NOT_APPROVED
d_class_shareholder_change_next_slice_runner_gate = NOT_APPROVED
shareholder_change_component_approved = standing_scope
closed_roots_mutated = false
company_level_live_found_path_for_DSC101_105 = NOT_PROVEN
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_shareholder_change_next_slice_fixture_vr_matrix_20260716.csv`
- summary: `outputs/validation/cninfo_d_class_shareholder_change_next_slice_fixture_vr_validation_20260716.md`
- test: `lab/test_cninfo_d_class_shareholder_change_next_slice_fixtures.py`

```text
task_id = D-FM-50
phase = shareholder_change_next_slice_approval_package_offline
allow_list_excludes = console_logs
```

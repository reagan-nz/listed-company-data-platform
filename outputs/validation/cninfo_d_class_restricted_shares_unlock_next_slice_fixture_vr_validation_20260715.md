# CNINFO D 类 restricted_shares_unlock — Next-Slice Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-46 · wall≈0.01s_

> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/restricted_shares_unlock_next_slice/` |
| universe lock | `cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv` |
| fixtures | **9** |
| matrix rows | **13** |
| anchor_tdate | `2026-07-03` |
| RSU next-slice lock sha256 | `13254f44f344c0f2976dfbde6fe75e363f91283a6eec1a5ae02d29f3831f193f` |
| RSU first-slice universe sha256 | `81a792f43962849778d53af97b4d67c64d53b1cd15d8428ff6d0a74931c84ec9` |
| EP next-slice lock sha256 | `1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384` |
| CNINFO | **0** |

```text
d_class_restricted_shares_unlock_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_restricted_shares_unlock_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_restricted_shares_unlock_next_slice_live_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_runner_gate = NOT_APPROVED
restricted_shares_unlock_component_approved = standing_scope
closed_roots_mutated = false
company_level_live_found_path_for_DRU101_105 = NOT_PROVEN
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_fixtures.py`

```text
task_id = D-FM-46
phase = restricted_shares_unlock_next_slice_approval_package_offline
allow_list_excludes = console_logs
```

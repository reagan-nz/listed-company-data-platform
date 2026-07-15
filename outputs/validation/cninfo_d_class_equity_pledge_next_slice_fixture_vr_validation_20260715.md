# CNINFO D 类 equity_pledge — Next-Slice Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-42 · wall≈0.01s_

> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/equity_pledge_next_slice/` |
| universe lock | `cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv` |
| fixtures | **9** |
| matrix rows | **13** |
| anchor_tdate | `2026-07-02` |
| EP next-slice lock sha256 | `1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384` |
| EP first-slice universe sha256 | `5fb4fa005236a162ef3bcc5322fe3b7134b36cbe7727fb0273724d0638dc8e10` |
| FIA first-slice lock sha256 | `49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c` |
| FIA next-slice lock sha256 | `c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515` |
| CNINFO | **0** |

```text
d_class_equity_pledge_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_equity_pledge_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_equity_pledge_next_slice_live_gate = NOT_APPROVED
d_class_equity_pledge_next_slice_runner_gate = NOT_APPROVED
equity_pledge_component_approved = standing_scope
closed_roots_mutated = false
company_level_live_found_path_for_DEP101_105 = NOT_PROVEN
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_equity_pledge_next_slice_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_equity_pledge_next_slice_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_equity_pledge_next_slice_fixtures.py`

```text
task_id = D-FM-42
phase = equity_pledge_next_slice_approval_package_offline
allow_list_excludes = console_logs
```

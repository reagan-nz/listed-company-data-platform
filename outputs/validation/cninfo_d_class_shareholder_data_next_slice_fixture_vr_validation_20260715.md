# CNINFO D 类 shareholder_data — Next-Slice Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-32 · wall≈0.01s_

> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/shareholder_data_next_slice/` |
| universe lock | `cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv` |
| fixtures | **8** |
| matrix rows | **12** |
| rdate set | `20260331` + `20251231` |
| shared_probe_prefer | **2** |
| AT first-slice lock sha256 | `d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2` |
| AT next-slice lock sha256 | `4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6` |
| SD first-slice lock sha256 | `06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5` |
| FIA next-slice lock sha256 | `c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515` |
| FIA first-slice lock sha256 | `49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c` |
| CNINFO | **0** |

```text
d_class_shareholder_data_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_shareholder_data_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_data_next_slice_live_gate = NOT_APPROVED
d_class_shareholder_data_next_slice_runner_gate = NOT_APPROVED
shareholder_data_component_approved = standing_scope
closed_roots_mutated = false
at_next_slice_live_flipped = false
```

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_shareholder_data_next_slice_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_shareholder_data_next_slice_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_shareholder_data_next_slice_fixtures.py`

```text
task_id = D-FM-32
phase = shareholder_data_next_slice_approval_package_offline
```

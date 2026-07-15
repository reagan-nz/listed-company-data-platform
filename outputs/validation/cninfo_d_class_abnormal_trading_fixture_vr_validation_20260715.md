# CNINFO D 类 abnormal_trading — Tier-1 Fixture VR Validation（Offline）

_生成时间：D-FM-04 · wall≈0.00s_

> **性质：** Tier-1 fixture offline VR · **CNINFO = 0** · **不是 verified**

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/abnormal_trading_first_slice/` |
| universe lock | `cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv` |
| fixtures | **10** |
| matrix rows | **15** |
| CNINFO | **0** |

```text
d_class_abnormal_trading_fixture_vr_gate = PASS_OFFLINE
d_class_abnormal_trading_next_component_planning_gate = READY_FOR_APPROVAL
abnormal_trading_component_approved = standing_scope
```

## D-FM-04 增补

- `DAT003_market_list_filtered_empty.json` · VR-009/010
- `DAT004_multi_type_found.json` · VR-011 + VR-021/024

## Artifacts

- matrix: `outputs/validation/cninfo_d_class_abnormal_trading_fixture_vr_matrix_20260715.csv`
- summary: `outputs/validation/cninfo_d_class_abnormal_trading_fixture_vr_validation_20260715.md`
- test: `lab/test_cninfo_d_class_abnormal_trading_fixtures.py`

```text
task_id = D-FM-04
phase = abnormal_trading_tier1_fixture_edge_extension
```

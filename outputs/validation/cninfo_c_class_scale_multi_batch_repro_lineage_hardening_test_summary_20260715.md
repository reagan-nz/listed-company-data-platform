# C-FM-23 Scale Multi-Batch Repro Lineage Hardening — Test Summary

_offline · CNINFO=0_

| case | result |
|------|--------|
| `test_output_root_requires_mock_and_not_frozen` | **PASS** |
| `test_auth_index_write_still_forbidden` | **PASS** |
| `test_scale_specs_seven_tiers_coverage_3314` | **PASS** |
| `test_registry_repro_and_combined_dryrun_pass` | **PASS** |
| `test_multi_batch_dual_layer_and_lineage_hardening` | **PASS** |
| `test_frozen_isolation_blocks_mock24_allows_mock25` | **PASS** |
| `test_fingerprint_matrix_stable` | **PASS** |
| `test_full_scale_pass_isolated_mock` | **PASS** |
| `test_cli_execute_forbidden` | **PASS** |
| `test_cninfo_not_called` | **PASS** |

```
c_fm_23_scale_multi_batch_repro_lineage_hardening_test_gate = PASS_OFFLINE
cninfo_calls = 0
execute_production_snapshot_rebuild = false
ready_for_execute = false
decision_status = AWAITING_HUMAN_EXECUTE_DECISION
idle_not_required_while_awaiting = true
hold_recommendation = KEEP_EXECUTE_FALSE
seal_chain_extended = false
scale_tier_count = 7
company_coverage_sum = 3314
combined_dryrun_coverage = 1053
```

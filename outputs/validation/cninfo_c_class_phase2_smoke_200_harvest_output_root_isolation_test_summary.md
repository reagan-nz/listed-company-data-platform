# CNINFO C-Class Harvest Output-Root Isolation Test Summary

## Result: **8/8 PASS**

| case | description | result |
|------|-------------|--------|
| `case_1_raw_path` | case_1_raw_path | **PASS** |
| `case_2_normalized_path` | case_2_normalized_path | **PASS** |
| `case_3_quality_path` | case_3_quality_path | **PASS** |
| `case_4_run_status` | case_4_run_status | **PASS** |
| `case_5_default_paths` | case_5_default_paths | **PASS** |
| `case_6_no_approval` | case_6_no_approval | **PASS** |
| `case_7_approval_scope` | case_7_approval_scope | **PASS** |
| `case_8_dry_run` | case_8_dry_run | **PASS** |

## Cases

- case_1: `--output-root` routes raw path
- case_2: `--output-root` routes normalized path
- case_3: `--output-root` routes quality path
- case_4: `run_status.json` isolated under output-root
- case_5: omitting `--output-root` preserves old paths
- case_6: phase2 live without `--approve-phase2-smoke-harvest` fails safely
- case_7: phase2 approval separate from `--approve-full-harvest`
- case_8: dry-run does not require live approval flag

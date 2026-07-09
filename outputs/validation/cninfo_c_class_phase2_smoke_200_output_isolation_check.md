# CNINFO C-Class Phase 2 Smoke 200 Output Isolation Check

_生成时间：2026-07-08_

## Phase 2 isolated root

- root: `outputs/harvest/cninfo_c_class/phase2_smoke_200/`
- raw files: **1400** (expected **1400**)
- normalized files: **1928** (expected **1928**)
- quality files: **4**
- run_status: `present`

## Report path audit

- direct rows with phase2 raw path: **1200/1200**
- direct rows referencing legacy 863 raw path: **0**

## Legacy 863 root (read-only check)

- legacy raw files on disk: **6041**
- legacy normalized files on disk: **8630**
- legacy quality files on disk: **5**
- sample 863 artifact mtime (`000009.jsonl`): **2026-07-07 20:16**
- Phase 2 live run completed **2026-07-08 22:55**; sample mtime predates run

## Gate

**phase2_output_isolation_gate = PASS**

863 `outputs/harvest/cninfo_c_class/{raw,normalized,quality}/` were not written by this Phase 2 run.

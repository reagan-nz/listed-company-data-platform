# CNINFO C-Class Phase 3.5 Expanded Snapshot Build Command Draft

_生成时间：2026-07-10_

```
NOT APPROVED
Do not execute.
```

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

## Preconditions

- User has explicitly approved expanded snapshot build
- Planning gate `READY_FOR_APPROVAL` satisfied
- Builder extension gate `READY_FOR_APPROVAL` satisfied
- Universe = **491** (C35R016 excluded · 8 hold_for_review excluded)
- Merge manifest reviewed
- Dry-run **491/491 planned_ok** completed

## Dry-Run Command (completed offline)

```bash
python -u lab/build_cninfo_c_class_snapshot_batch.py \
  --dry-run \
  --sample-file lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase35_batch_500_001 \
  --resume-harvest-root outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume \
  --merge-manifest outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv \
  --output-root outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491
```

## Future Build Command (DO NOT RUN)

```bash
python -u lab/build_cninfo_c_class_snapshot_batch.py \
  --execute \
  --sample-file lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase35_batch_500_001 \
  --resume-harvest-root outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume \
  --merge-manifest outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv \
  --output-root outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491 \
  --approve-phase35-expanded-success-snapshot-build
```

```
NOT APPROVED
Do not execute.
```

## Forbidden

- Including C35R016 / 301212
- Including 8 hold_for_review companies
- Writing to original or resume harvest roots
- DB / MinIO / RAG
- Marking verified / production_ready

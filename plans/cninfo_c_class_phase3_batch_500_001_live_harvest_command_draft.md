# CNINFO C-Class Phase 3 Batch 500 Live Harvest Command Draft

_生成时间：2026-07-09_

> **NOT APPROVED YET** — 本文件仅为未来 live harvest 命令草稿，**不得执行**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

**Approval gate：** `phase3_batch_500_001_live_harvest_approval_gate = READY_FOR_APPROVAL`

**Live status：** `live_harvest_executed = false`

---

## Status

```
NOT APPROVED YET
```

---

## Command Draft (DO NOT RUN)

```bash
python -u lab/harvest_cninfo_c_class.py \
  --live \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_001.yaml \
  --output-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --approve-phase3-batch-500-harvest
```

---

## Preconditions

- User has explicitly approved Phase 3 batch 500 live harvest
- Dry-run gate **PASS**
- Dedicated approval flag **implemented** and **required**
- Output root **isolated** under `phase3_batch_500_001/`
- No snapshot build during harvest
- No modification to 863 main track or Phase 2 smoke outputs

---

## Forbidden Flags (Phase 3 live)

Do **not** use:

- `--approve-full-harvest` alone
- `--approve-phase2-smoke-harvest` alone

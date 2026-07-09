# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Build Command Draft

_生成时间：2026-07-09_

> **NOT APPROVED YET** — 本文件仅为未来 snapshot build 命令草稿，**不得执行**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

**Approval gate：** `phase3_batch_500_success_snapshot_build_approval_gate = READY_FOR_APPROVAL`

**Build status：** `snapshot_build_executed = false`

---

## Status

```
NOT APPROVED YET
```

---

## Prerequisites

| 项 | 要求 |
|----|------|
| universe | **491** identity-clean companies |
| excluded | **9** identity caveat（不得出现在 YAML） |
| dry-run | `phase3_success_subset_snapshot_dryrun_execution = PASS_WITH_CAVEAT` |
| runner flag | `--approve-phase3-success-snapshot-build` **已实现** |
| user approval | 显式批准 Phase 3 success-subset snapshot build |

---

## Command Draft (DO NOT RUN)

```bash
python lab/build_cninfo_c_class_snapshot_batch.py \
  --execute \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --output-dir outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success \
  --approve-phase3-success-snapshot-build
```

---

## Required Flags

| Flag | 说明 |
|------|------|
| `--execute` | 进入 build 模式（非 dry-run） |
| `--approve-phase3-success-snapshot-build` | Phase 3 **491** success-subset 专用批准 |

---

## Forbidden Flags (Phase 3 success-subset build)

Do **not** use alone or as substitute:

| Flag | 原因 |
|------|------|
| `--approve-full-snapshot-batch` | 仅适用于 863 `full/` batch |
| `--approve-phase2-smoke-188-snapshot` | 仅适用于 phase2 188 子集 |

使用错误 approval flag 时 runner **必须** fail safely。

---

## Expected Output

| 项 | 路径 |
|----|------|
| snapshot root | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/` |
| snapshot JSON | `{company_code}.json` × **491** |
| status CSV | `.../quality/company_snapshot_status.csv` |
| error CSV | `.../quality/company_snapshot_error.csv` |

---

## Isolation

| 禁止触碰 | 路径 |
|----------|------|
| 863 full snapshot | `outputs/snapshot/cninfo_c_class/full/` |
| phase2 snapshot | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` |
| harvest raw/normalized | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`（只读） |

---

## Red Lines

- **no CNINFO**
- **no harvest rerun**
- **no verified**
- **no DB / MinIO / RAG**

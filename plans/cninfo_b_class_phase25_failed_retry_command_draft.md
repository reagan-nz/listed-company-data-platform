# CNINFO B 类 Phase 2.5 Failed-case Isolated Retry — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 5-case isolated retry 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## 1. Scope

| 项 | 值 |
|----|-----|
| retry cases | **5** only |
| case IDs | B25E003 · B25E008 · B25E032 · B25E039 · B25E040 |
| successful cases | **45** — **must NOT rerun** |
| schema_impact | **none** |
| quality_impact | **retry_needed** |
| CNINFO calls（本回合） | **0** |

**允许：** metadata retrieval · announcement lineage · pdf URL lineage  
**禁止：** PDF download · PDF parse · OCR · section extraction · DB · MinIO · RAG · verified

---

## 2. Output Isolation

```text
outputs/validation/cninfo_b_class_phase25_failed_retry/
├── raw_metadata/
├── quality/
└── reports/
    ├── b_class_phase25_failed_retry_dryrun_report.csv
    ├── b_class_phase25_failed_retry_dryrun_summary.md
    ├── b_class_phase25_failed_retry_report.csv      (future live)
    └── b_class_phase25_failed_retry_summary.md      (future live)
```

**禁止写入：**

- `outputs/validation/cninfo_b_class_phase25_expansion/`（Phase 2.5 主 batch · 只读）
- Phase 1 tiny live · TLC002 retry · Phase 2 expansion · C-class harvest

---

## 3. Universe

```text
outputs/validation/cninfo_b_class_phase25_failed_retry_universe.csv
```

---

## 4. Approval Flag

```text
--approve-b-class-phase25-failed-retry
```

| Flag | 行为 |
|------|------|
| `--approve-b-class-phase25-failed-retry` | **必须**（retry live） |
| `--approve-b-class-phase25-expansion` | **拒绝**（wrong flag for retry） |
| `--retry-failed-only` | **必须**（retry 模式） |

---

## 5. Command Draft（NOT APPROVED）

### Dry-run（本回合已执行）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --retry-failed-only \
  --dry-run \
  --universe-csv outputs/validation/cninfo_b_class_phase25_failed_retry_universe.csv \
  --output-root outputs/validation/cninfo_b_class_phase25_failed_retry/
```

### Live retry（未来 · NOT APPROVED）

```bash
# NOT APPROVED — 须用户显式批准后方可执行

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --retry-failed-only \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_phase25_failed_retry_universe.csv \
  --output-root outputs/validation/cninfo_b_class_phase25_failed_retry/ \
  --approve-b-class-phase25-failed-retry
```

---

## 6. Expected Outcomes（批准后）

| 成功 | 失败（可接受） |
|------|----------------|
| `retrieval_status=found` | `network_error`（再次记录，不自动循环） |
| `quality_status=pass` 或 `needs_review` | `needs_review` |
| `lineage_status=discovered` | `needs_review` |

**永不：** `verified` · PDF 落盘 · 45 成功 case rerun

---

## 7. Gate

```text
b_class_phase25_failed_retry_planning_gate = READY_FOR_APPROVAL
```

**NOT EXECUTED** · **NOT APPROVED**

---

## 8. Red Lines

- No CNINFO in this planning round
- No retry execution in this planning round
- No rerun of 45 successful cases
- No 100-company expansion
- No schema modification
- No PDF · No OCR · No extraction · No DB · No MinIO · No RAG · No verified

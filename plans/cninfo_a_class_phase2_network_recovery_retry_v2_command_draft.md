# CNINFO A 类 Phase 2 Network Recovery Retry v2 命令草稿

_生成时间：2026-07-09 · 更新：runner extension + dry-run 完成_

> **状态：NOT APPROVED**  
> **Do not execute live.**

---

## 配置

| 项 | 值 |
|----|-----|
| universe | `outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv` |
| output root | `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/` |
| approval flag | `--approve-a-class-phase2-network-recovery-retry-v2` |
| cases | **8** unresolved network failures only |
| successful 12 | **excluded** |

---

## Step 1 — Dry-run（已完成 · CNINFO=0）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --retry-failed-only \
  --dry-run \
  --universe-csv outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/
```

**结果：** 8/8 planned_ok · CNINFO requests = 0 · 无 PDF

**产物：**
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/reports/a_class_phase2_retry_v2_dryrun_report.csv`
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/reports/a_class_phase2_retry_v2_dryrun_summary.md`

---

## Step 2 — Live（须显式批准 · 网络恢复后 · NOT APPROVED）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --retry-failed-only \
  --live \
  --universe-csv outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/ \
  --approve-a-class-phase2-network-recovery-retry-v2
```

**Do not execute without human approval.**

---

## 禁止组合

- `--approve-a-class-phase2-metadata-expansion`
- `--approve-a-class-phase2-failed-retry`
- `--download-pdf` / `--parse-pdf`
- `--enable-ocr` / `--enable-extraction`
- `--write-db` / `--write-minio` / `--run-rag`
- `--mark-verified` / `--mark-production-ready`

---

## Runner 状态

- `--approve-a-class-phase2-network-recovery-retry-v2` — **已实现**
- `retry_v2/` output-root 校验 — **已实现**
- tests — **18/18 PASS**

**NOT APPROVED · Do not execute live.**

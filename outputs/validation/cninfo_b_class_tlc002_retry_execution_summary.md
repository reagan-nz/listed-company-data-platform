# TLC002 Isolated Retry — Execution Summary

_生成时间：2026-07-09_

> **性质：** TLC002 isolated live retry · **无 PDF 下载/解析** · **不是 verified**

---

## Pre-execution Verification

| 检查项 | 结果 |
|--------|------|
| output root | `cninfo_b_class_tlc002_retry/`（含 dry-run prep；live 覆盖写入） |
| tiny live baseline | **untouched**（report mtime 未变） |
| PDF disabled | **yes** |
| C-class Phase3 | **untouched** |

---

## Results

| 指标 | 值 |
|------|-----|
| company | **300009** 安科生物 |
| CNINFO requests | **2** |
| EP002 (topSearch) | **1** |
| EP001 (hisAnnouncement) | **1** |
| retrieval_status | **found** |
| quality_status | **pass** |
| lineage_status | **discovered** |
| failure recovered | **yes**（原 `network_error` → 现 `found`） |

### Announcement

| 字段 | 值 |
|------|------|
| announcement_id | 1223997045 |
| announcement_title | 关于第3期员工持股计划非交易过户完成的公告 |
| announcement_category | general_announcement |
| pdf_url | metadata only（**未下载**） |

---

## Gate

```text
b_class_tlc002_retry_execution_gate = PASS_WITH_CAVEAT
```

**Never：** verified · production_ready · full_b_class_support

`b_class_tiny_live_validation_execution_gate = PASS_WITH_CAVEAT`（保持）

---

## Outputs

- [tlc002_retry_report.csv](cninfo_b_class_tlc002_retry/reports/tlc002_retry_report.csv)
- [tlc002_retry_summary.md](cninfo_b_class_tlc002_retry/reports/tlc002_retry_summary.md)
- [TLC002_EP005.json](cninfo_b_class_tlc002_retry/raw_metadata/TLC002_EP005.json)

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- tiny live baseline: **read-only preserved**
- PDF files: **0**

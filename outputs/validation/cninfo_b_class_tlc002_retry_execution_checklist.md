# CNINFO B 类 TLC002 Isolated Retry — Execution Checklist

_生成时间：2026-07-09_

> **性质：** 未来 TLC002 isolated retry 执行清单；**本轮 runner 准备 only** · **retry 未执行**

**Runner：** [lab/run_cninfo_b_class_tlc002_retry.py](../../lab/run_cninfo_b_class_tlc002_retry.py)

---

## Before

- [ ] 仅 **TLC002** / **300009** 安科生物
- [ ] `--approve-b-class-tlc002-retry` 已显式提供
- [ ] **未**单独使用 `--approve-b-class-tiny-live-validation`
- [ ] 输出根 = `outputs/validation/cninfo_b_class_tlc002_retry/`
- [ ] **不写入** `outputs/validation/cninfo_b_class_tiny_live_validation/`
- [ ] `b_class_tiny_live_validation_execution_gate = PASS_WITH_CAVEAT`（**保持**）
- [ ] PDF download / parse **disabled**
- [ ] schema / registry / freeze artifacts **未修改**

---

## During

- [ ] 打印：`case_id` · `endpoint_id` · `company_code` · `retrieval_status` · `quality_status`
- [ ] 跟踪 CNINFO 请求（预期 ≤2：EP002 + EP001）
- [ ] 仅允许 EP001 · EP002 · EP004 · EP005
- [ ] 禁止 EP006 · EP007
- [ ] rate limit ≥0.6s · 无 burst

---

## After

- [ ] `reports/tlc002_retry_report.csv` 在隔离根
- [ ] `reports/tlc002_retry_summary.md` 在隔离根
- [ ] `raw_metadata/TLC002_EP005.json` · `quality/TLC002.json`
- [ ] lineage：`found` → `discovered`；失败 → `needs_review`（不伪造）
- [ ] **无 verified** · **无 PDF 落盘**
- [ ] tiny live baseline **未覆盖**
- [ ] C-class **`SNAPSHOT_GENERATED_QA_REVIEW`** 不变

---

## Gate

```text
b_class_tlc002_retry_runner_gate = READY_FOR_APPROVAL
```

执行 retry 前须用户显式批准 `--approve-b-class-tlc002-retry`。

---

## Red Lines

- No CNINFO during runner-prep round
- No retry execution until approved
- No PDF · No parser · No DB · No MinIO · No RAG · No verified

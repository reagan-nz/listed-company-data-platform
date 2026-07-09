# CNINFO B 类 TLC002 Isolated Retry Checklist

_生成时间：2026-07-09_

> **性质：** 未来 isolated retry 执行前检查清单；**本轮不执行 retry**。  
> **重试计划：** [cninfo_b_class_tlc002_isolated_retry_plan.md](../../plans/cninfo_b_class_tlc002_isolated_retry_plan.md)

---

## Before Execution

- [ ] 仅 **TLC002**（300009 安科生物）— 无其他 universe case
- [ ] 输出根 = `outputs/validation/cninfo_b_class_tlc002_retry/` only
- [ ] **不复用** `outputs/validation/cninfo_b_class_tiny_live_validation/` 原 live 产物
- [ ] `PDF_DOWNLOAD_ENABLED = false`
- [ ] `PDF_PARSE_ENABLED = false`
- [ ] `--approve-b-class-tlc002-retry` **已显式提供**
- [ ] 未单独使用 `--approve-b-class-tiny-live-validation`（除非与 TLC002 flag **同时**显式组合批准）
- [ ] C-class Phase 3 harvest 无冲突并发
- [ ] `b_class_tiny_live_validation_execution_gate = PASS_WITH_CAVEAT`（**保持，不升级**）
- [ ] schema freeze v1 / endpoint catalog **未修改**

---

## During Execution

- [ ] 跟踪 **CNINFO request count**（预期 ≤2：EP002 + EP001）
- [ ] 跟踪 **endpoint_id** 命中（EP002 · EP001 · EP005 scope only）
- [ ] 记录 **error_type**（`network_error` · `empty_response` · `not_found` 等）
- [ ] rate limit：sleep ≥0.6s · 无 burst · HTTP 429 停止无 retry storm
- [ ] 实时打印：`case_id` · `endpoint_id` · `company_code` · `retrieval_status` · success/failure

---

## After Execution

- [ ] `reports/tlc002_retry_report.csv` 写入隔离根
- [ ] `reports/tlc002_retry_summary.md` 写入隔离根
- [ ] **lineage 校验**：`found` 时 `lineage_status=discovered`；失败时 `needs_review`（不伪造 discovered）
- [ ] **quality_status 校验**：不得标 `verified`；missing pdf_url 允许 `needs_review`
- [ ] **无 verified 升级** · **无 testing_stable_sample 升级**
- [ ] **无 PDF 文件**落盘
- [ ] 原 tiny live 报告 **未覆盖修改**
- [ ] C-class status 保持 **`SNAPSHOT_GENERATED_QA_REVIEW`**

---

## Gate Reference

```text
b_class_tlc002_isolated_retry_gate = READY_FOR_APPROVAL
```

执行前须用户显式批准 `--approve-b-class-tlc002-retry`。

---

## Red Lines

- No CNINFO in this checklist round
- No retry execution in this checklist round
- No PDF · No DB · No MinIO · No RAG · No verified

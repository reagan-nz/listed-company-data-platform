# CNINFO B 类 Phase 1 Tiny Live Metadata Validation — 最终批准检查清单

_生成时间：2026-07-09_

> **性质：** 未来 tiny live metadata 执行前的最终批准包；**本轮不执行 live** · **NOT APPROVED**。  
> **前置批准计划：** [cninfo_b_class_phase1_live_validation_approval_plan.md](../../plans/cninfo_b_class_phase1_live_validation_approval_plan.md)  
> **离线 benchmark：** [execution summary](cninfo_b_class_phase1_ready_case_benchmark_execution_summary.md)（**5/5 PASS**）

---

## Preconditions

以下项须 **PASS** 后方可申请 live execution：

| # | 条件 | 要求 | 当前状态 |
|---|------|------|----------|
| 1 | freeze v1 implementation | `b_class_phase1_freeze_v1_implementation_gate = PASS_OFFLINE` | **PASS** |
| 2 | ready-case benchmark execution | `b_class_ready_case_benchmark_execution_gate = PASS_OFFLINE` · RC001–RC005 全 PASS | **PASS** |
| 3 | endpoint catalog review | EP001/EP002/EP004/EP005 `phase1_in_scope`；EP003 removed；EP006/EP007 deferred | **PASS（离线审阅）** |
| 4 | output isolation | 产物仅写入 `outputs/validation/cninfo_b_class_tiny_live_validation/` | **已定义** |

### 额外并行安全（执行前再确认）

- [ ] C-class Phase 3 live harvest **未在并发运行**
- [ ] `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` **未被读写**
- [ ] C-class status 保持 **`SNAPSHOT_GENERATED_QA_REVIEW`**
- [ ] 用户已显式批准 tiny live metadata（见 [approval summary](cninfo_b_class_phase1_tiny_live_validation_approval_summary.md)）

---

## Live Scope

### Only（允许）

- metadata retrieval（公告列表 API 响应 metadata）
- announcement lineage（`announcement_id` · `announcement_time` · `announcement_date` · `announcement_title`）
- pdf URL lineage（`adjunctUrl` → `adjunct_url` / `pdf_url` 登记；**不下载**）
- quality status（`pass` · `needs_review` · `caveat`；**不写 verified**）

### In-scope endpoints / sources

| ID | name | 用途 |
|----|------|------|
| EP001 | hisAnnouncement/query | 主公告列表检索 |
| EP002 | topSearch/query | orgId 发现辅助（非文档列表） |
| EP004 | cninfo_periodic_report_pdf | 定期报告 metadata |
| EP005 | cninfo_general_announcement_pdf | 非定期公告 metadata |

### Exclude（禁止）

- PDF download
- PDF parsing
- OCR
- text extraction
- RAG / embeddings / vector index
- DB / MinIO
- verified / testing_stable_sample 升级
- production registry 状态更新
- C-class harvest 输出修改
- BSE legacy universe

---

## Tiny Universe 检查

- [ ] [tiny universe CSV](cninfo_b_class_phase1_tiny_live_validation_universe.csv) 已审阅（**5** 家 · 全 `low` risk）
- [ ] 无退市 / ST / manual review 样本
- [ ] 无 BSE legacy 代码
- [ ] 尚未创建 universe YAML（未来回合）

---

## 执行前技术检查

- [ ] [command draft](../../plans/cninfo_b_class_phase1_tiny_live_validation_command_draft.md) 已审阅
- [ ] `--approve-phase1-tiny-live-metadata` 批准 flag 已实现（**未来回合**）
- [ ] `--output-root outputs/validation/cninfo_b_class_tiny_live_validation/` 隔离已确认
- [ ] rate limit：`sleep_seconds >= 0.6` · 并发 = 1
- [ ] resume：读/写 isolation root 内 `run_status.csv`（或等价 marker）
- [ ] failure handling：HTTP 429 / network_error → 停止并记录，无 retry storm

---

## Post-run 检查（未来 live 回合）

- [ ] `live_report.csv` + `live_summary.md` 写入 isolation root only
- [ ] 无 PDF 文件落盘
- [ ] endpoint `live_validation_status` 仅在报告中更新（**不**改 production registry）
- [ ] gate **仍不是** PASS / verified / live approved
- [ ] C-class Phase 3 输出根未被触碰

---

## Gate Reference

```text
b_class_phase1_tiny_live_validation_gate = READY_FOR_APPROVAL
```

**不设为 PASS** — tiny live metadata validation **未执行**。

---

## Red Lines

- No CNINFO in this approval-preparation round
- No live execution in this round
- No harvest · No PDF download · No PDF parse
- No DB · No MinIO · No RAG
- No verified · No testing_stable_sample upgrade
- No C-class phase3 output touch

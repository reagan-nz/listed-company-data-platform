# CNINFO A 类 Phase 1 Tiny Live Metadata Validation — 批准检查清单

_生成时间：2026-07-09_

> **性质：** 未来 tiny live metadata 执行前的批准包；**本轮不执行 live** · **NOT APPROVED**。  
> **前置：** [ready-case benchmark summary](cninfo_a_class_phase1_ready_case_benchmark_summary.md)（**5/5 PASS** · gate **`READY_FOR_REVIEW`**）  
> **输入：** [field catalog](cninfo_a_class_phase1_freeze_v1_field_catalog.csv) · [registry draft](../../config/cninfo_a_class_source_registry_draft.yaml) · [ready-case fixtures](../../fixtures/a_class/phase1/ready_cases/)

---

## Preconditions

以下项须 **PASS / 已审阅** 后方可申请 live execution：

| # | 条件 | 要求 | 当前状态 |
|---|------|------|----------|
| 1 | freeze v1 implementation | `a_class_phase1_freeze_v1_implementation_gate = PASS_OFFLINE` | **PASS** |
| 2 | ready-case benchmark | `a_class_ready_case_benchmark_gate = READY_FOR_REVIEW` · AC001–AC005 全 PASS | **PASS（离线审阅）** |
| 3 | no PDF download | Phase1 tiny live **仅 metadata**；禁止 PDF 落盘 | **已定义** |
| 4 | no PDF parsing | 禁止 parser / OCR / section / table extraction | **已定义** |
| 5 | output isolation | 产物仅写入 `outputs/validation/cninfo_a_class_tiny_live_metadata/` | **已定义** |
| 6 | explicit user approval | 用户须显式批准 tiny live metadata（见 [approval summary](cninfo_a_class_phase1_tiny_live_metadata_approval_summary.md)） | **待批准** |

### 额外并行安全（执行前再确认）

- [ ] C-class Phase 3 live harvest **未在并发运行**
- [ ] `outputs/harvest/cninfo_c_class/` **未被读写**
- [ ] C-class status 保持 **`SNAPSHOT_GENERATED_QA_REVIEW`**
- [ ] B-class / D-class 既有输出 **未被修改**
- [ ] 用户已显式批准 `--approve-a-class-tiny-live-metadata`

---

## Live Scope

### Only（允许 — metadata validation only）

| 对象 | 允许字段 / 行为 |
|------|----------------|
| `report_document` | metadata 检索与 freeze v1 required 字段校验 |
| `report_period_snapshot` | company × year × report_type 链接与 coverage 视图 |
| `document_lineage` | metadata 谱系；`storage_status=not_attempted` |
| pdf_url / adjunct_url lineage | `adjunctUrl` → `pdf_url` / `adjunct_url` **登记**；**不下载** |
| quality_status | `pass` · `caveat` · `needs_review` · `blocked`；**不写 verified** |

### In-scope sources（registry draft · phase1_in_scope）

| source_id | source_name | report_type |
|-----------|-------------|-------------|
| cninfo_a_class_periodic_report_annual | A类年报 metadata | `annual_report` |
| cninfo_a_class_periodic_report_semi_annual | A类半年报 metadata | `semi_annual_report` |
| cninfo_a_class_periodic_report_quarterly | A类季报 metadata | `quarterly_report_q1` / `quarterly_report_q3` |

### In-scope endpoints（设计引用）

| endpoint | 用途 |
|----------|------|
| `hisAnnouncement/query` | 主公告列表 metadata 检索 |
| `topSearch/query` | orgId 发现辅助（非文档列表） |

### Explicitly exclude（禁止）

- PDF download
- PDF parsing
- OCR
- section extraction
- table extraction
- embeddings
- RAG / vector index
- DB / MinIO / MongoDB
- verified / testing_stable_sample 升级
- production registry 状态更新
- C-class / B-class / D-class 输出修改
- BSE legacy universe
- manual review identity 样本

---

## Ready-case Benchmark 对照

| case_id | 场景 | benchmark 结论 |
|---------|------|----------------|
| AC001 | valid periodic report metadata | PASS |
| AC002 | valid announcement lineage | PASS |
| AC003 | missing pdf_url / quality downgrade | PASS |
| AC004 | duplicate document_id | PASS |
| AC005 | unknown report_type enum | PASS |

---

## Tiny Universe 检查

- [ ] [tiny universe CSV](cninfo_a_class_phase1_tiny_live_metadata_universe.csv) 已审阅（**5** 家 · 全 `low` risk）
- [ ] 无退市 / ST / *ST / manual review 样本
- [ ] 无 BSE legacy 代码
- [ ] 含 annual report case（**≥1**）
- [ ] semi-annual / quarterly 仅使用 registry `phase1_in_scope` source
- [ ] 尚未创建 universe YAML（未来回合）

---

## 执行前技术检查

- [ ] [command draft](../../plans/cninfo_a_class_phase1_tiny_live_metadata_command_draft.md) 已审阅
- [ ] `--approve-a-class-tiny-live-metadata` 批准 flag 已实现（**未来回合**）
- [ ] `--output-root outputs/validation/cninfo_a_class_tiny_live_metadata/` 隔离已确认
- [ ] `DOWNLOAD_PDF = False` / `--no-pdf-download` 常量或 flag 已实现（**未来回合**）
- [ ] `PARSE_PDF = False` / `--no-parser` 常量或 flag 已实现（**未来回合**）
- [ ] rate limit：`sleep_seconds >= 0.6` · 并发 = 1
- [ ] resume：读/写 isolation root 内 `run_status.csv`（或等价 marker）
- [ ] failure handling：HTTP 429 / network_error → 停止并记录，无 retry storm

---

## Post-run 检查（未来 live 回合）

- [ ] `live_report.csv` + `live_summary.md` 写入 isolation root only
- [ ] 无 PDF 文件落盘
- [ ] `document_lineage.storage_status` 保持 `not_attempted`
- [ ] source `live_validation_status` 仅在报告中更新（**不**改 production registry）
- [ ] gate **仍不是** PASS / verified / live_ready
- [ ] C-class / B-class / D-class 输出根未被触碰

---

## Gate Reference

```text
a_class_phase1_tiny_live_metadata_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** — tiny live metadata validation **未执行**。

---

## Red Lines

- No CNINFO in this approval-preparation round
- No live execution in this round
- No PDF download · No PDF parsing · No OCR · No extraction
- No DB · No MinIO · No RAG
- No verified · No testing_stable_sample upgrade
- No C-class / B-class / D-class output touch

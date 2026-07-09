# CNINFO B 类 Phase 1 Live Validation Approval Plan

_最后更新：2026-07-09_

> **性质：** 批准规划 only；**不执行 live**；**不**将 gate 改为 PASS。  
> **前置：** [freeze v1 implementation summary](../outputs/validation/cninfo_b_class_phase1_freeze_v1_implementation_summary.md) · [ready-case benchmark summary](../outputs/validation/cninfo_b_class_phase1_ready_case_benchmark_summary.md)

---

## Scope

未来 live validation **仅测试**：

- metadata retrieval（公告列表 API 响应 metadata）
- `announcement_id` lineage
- `announcement_time` / `announcement_date`
- `announcement_category`（含 unknown/review_later 路径）
- `pdf_url` lineage（`adjunctUrl` → `pdf_url` 登记）

### Exclude

- PDF download
- PDF parsing / OCR
- embeddings / vector index
- RAG pipeline
- DB / MinIO
- verified / testing_stable_sample upgrade
- C-class harvest 输出修改

### In-scope endpoints / sources

| ID | name |
|----|------|
| EP001 | hisAnnouncement/query |
| EP002 | topSearch/query（orgId helper only） |
| EP004 | cninfo_periodic_report_pdf |
| EP005 | cninfo_general_announcement_pdf |

**不在 Phase 1 live 范围：** EP003（removed）· EP006/EP007（deferred Phase 2）

---

## Preconditions

全部满足后才可申请 live execution：

| # | 条件 | 当前状态 |
|---|------|----------|
| 1 | `b_class_phase1_freeze_v1_implementation_gate = PASS_OFFLINE` | **满足** |
| 2 | ready-case benchmark reviewed | **READY_FOR_REVIEW**（待人工） |
| 3 | endpoint live status approved | **未批准**（全部 `not_run`） |
| 4 | rate limit policy defined | **草案**（registry `sleep_seconds: 0.6`） |
| 5 | output isolation defined | **已定义**（见下文） |

---

## Live Output Isolation

未来 live validation 产物**仅**写入：

```text
outputs/validation/cninfo_b_class_live_validation/
```

建议子路径：

```text
outputs/validation/cninfo_b_class_live_validation/
  phase1_tiny_sample/
    live_report.csv
    live_summary.md
    raw_metadata_snapshots/
```

**禁止：**

- 写入 `outputs/harvest/`
- 写入 `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`
- 修改 C-class raw/normalized/snapshot
- 下载 PDF 到 harvest 目录

---

## Rate Limit Policy（草案）

| 项 | 值 |
|----|-----|
| 请求间隔 | ≥ 0.6s（与 registry defaults 一致） |
| 并发 | 1（无并行 CNINFO 请求） |
| 超时 | 10s |
| 最大 case 数（首次 tiny live） | ≤ 5（对齐 RC001–RC005 或 ready 子集） |
| 与 C-class 并发 | **禁止**同时跑 C-class Phase 3 live harvest |

---

## Approval Workflow

1. 人工 review [ready-case benchmark summary](../outputs/validation/cninfo_b_class_phase1_ready_case_benchmark_summary.md)
2. 人工 review [live validation checklist](../outputs/validation/cninfo_b_class_phase1_live_validation_checklist.md)
3. 用户显式批准 tiny live metadata sample
4. 执行 isolated live runner（**未来回合** · 本 plan 不实现）
5. 产出 live_report.csv + live_summary.md 至 isolation root
6. **仍不写 verified**

---

## Approval Gate

```text
b_class_phase1_live_validation_gate = READY_FOR_APPROVAL
```

**不设为 PASS** — live validation **未执行**。

---

## Red Lines

- No CNINFO in this planning round
- No live execution in this planning round
- No PDF download / parse
- No DB / MinIO / RAG
- No verified
- No testing_stable_sample upgrade

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- C-class Phase 3 live output root: **untouched**

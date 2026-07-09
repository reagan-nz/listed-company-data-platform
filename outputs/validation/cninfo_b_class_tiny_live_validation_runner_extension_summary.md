# CNINFO B 类 Tiny Live Validation Runner 扩展摘要

_生成时间：2026-07-09_

> **性质：** runner 能力已准备；**无 CNINFO** · **无 live 执行** · **NOT APPROVED for live**

---

## Runner

| 项 | 路径 |
|----|------|
| runner | [lab/run_cninfo_b_class_tiny_live_validation.py](../../lab/run_cninfo_b_class_tiny_live_validation.py) |
| tests | [lab/test_cninfo_b_class_tiny_live_validation_runner.py](../../lab/test_cninfo_b_class_tiny_live_validation_runner.py) |
| universe | [cninfo_b_class_phase1_tiny_live_validation_universe.csv](cninfo_b_class_phase1_tiny_live_validation_universe.csv) |

---

## Test Result

| 指标 | 值 |
|------|-----|
| tests_run | **11** |
| passed | **11** |
| failed | **0** |
| CNINFO calls | **0** |

覆盖：dry-run 无网络 · 输出隔离 · approval flag 阻断 · endpoint 白名单 · PDF 下载/解析禁用。

---

## Allowed Endpoints

| ID | name |
|----|------|
| EP001 | hisAnnouncement/query |
| EP002 | topSearch/query |
| EP004 | cninfo_periodic_report_pdf |
| EP005 | cninfo_general_announcement_pdf |

---

## Blocked Operations

| 类别 | 状态 |
|------|------|
| EP003 | removed · 拒绝 |
| EP006 / EP007 | deferred Phase 2 · 拒绝 |
| `--approve-full-harvest` | 拒绝 |
| `--approve-phase2-smoke-harvest` | 拒绝 |
| `--approve-phase3-batch-500-harvest` | 拒绝 |
| PDF download | **disabled**（`PDF_DOWNLOAD_ENABLED=False`） |
| PDF parsing | **disabled**（`PDF_PARSE_ENABLED=False`） |
| DB / MinIO / RAG | **未实现** |
| verified / testing_stable_sample | **禁止** |

---

## Output Root

```text
outputs/validation/cninfo_b_class_tiny_live_validation/
├── raw_metadata/
├── quality/
└── reports/
    ├── cninfo_b_class_tiny_live_validation_report.csv
    └── run_summary.md
```

索引报告（同步写入）：

`outputs/validation/cninfo_b_class_tiny_live_validation_report.csv`

**无 PDF 文件。**

---

## Dry-run Result

| 指标 | 值 |
|------|-----|
| mode | dry_run（default） |
| cases | **5**（TLC001–TLC005） |
| retrieval_status | `dry_run_planned` |
| CNINFO calls | **0** |

---

## Live Status

| 项 | 状态 |
|----|------|
| `--live` | 须 `--approve-b-class-tiny-live-validation` |
| live CNINFO execution | **NOT EXECUTED**（runner-prep 回合仍 `live_not_executed_runner_prepared`） |
| 用户显式批准 | **待批准** |

---

## Gate

```text
b_class_tiny_live_runner_gate = READY_FOR_APPROVAL
```

**不是 PASS** · **不是 live approved**

（`b_class_phase1_tiny_live_validation_gate = READY_FOR_APPROVAL` 保持）

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`: **untouched**
- CNINFO calls（本回合）: **0**

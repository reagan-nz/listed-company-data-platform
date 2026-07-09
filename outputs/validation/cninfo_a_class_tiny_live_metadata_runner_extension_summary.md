# CNINFO A 类 Tiny Live Metadata Runner 扩展摘要

_生成时间：2026-07-09_

> **性质：** runner 已离线准备；dry-run 完成；**无 CNINFO** · **无 live 执行** · **NOT APPROVED for live**

---

## Runner

| 项 | 路径 |
|----|------|
| runner | [lab/run_cninfo_a_class_tiny_live_metadata_validation.py](../../lab/run_cninfo_a_class_tiny_live_metadata_validation.py) |
| tests | [lab/test_cninfo_a_class_tiny_live_metadata_validation_runner.py](../../lab/test_cninfo_a_class_tiny_live_metadata_validation_runner.py) |
| universe | [cninfo_a_class_phase1_tiny_live_metadata_universe.csv](cninfo_a_class_phase1_tiny_live_metadata_universe.csv) |

---

## Test Result

| 指标 | 值 |
|------|-----|
| tests_run | **9** |
| passed | **9** |
| failed | **0** |
| CNINFO calls | **0** |

覆盖：dry-run 无网络 · approval flag 阻断 · 错误批准 flag 拒绝 · 输出隔离 · universe size=5 · PDF 下载/解析禁用 · dry-run 报告生成 · B/C/D 输出未触碰。

---

## Approval Flag

```text
--approve-a-class-tiny-live-metadata
```

**live 模式须显式传入；dry-run 默认不需要。**

---

## Output Root

```text
outputs/validation/cninfo_a_class_tiny_live_metadata/
├── planned/
└── reports/
    ├── a_class_tiny_live_metadata_dryrun_report.csv
    └── a_class_tiny_live_metadata_dryrun_summary.md
```

**无 PDF 文件。**

---

## Dry-run Result

| 指标 | 值 |
|------|-----|
| mode | dry_run |
| universe size | **5** |
| planned_ok | **5** |
| universe_issues | **0** |
| CNINFO calls | **0** |

| case_id | company | report_type | dryrun_status |
|---------|---------|-------------|---------------|
| ALM001 | 600000 浦发银行 | annual_report | planned_ok |
| ALM002 | 300001 特锐德 | semi_annual_report | planned_ok |
| ALM003 | 688001 华熙生物 | quarterly_report_q1 | planned_ok |
| ALM004 | 000858 五粮液 | quarterly_report_q3 | planned_ok |
| ALM005 | 600519 贵州茅台 | annual_report | planned_ok |

---

## Safety Checks

| 检查 | 状态 |
|------|------|
| default mode = dry-run | **yes** |
| live requires `--approve-a-class-tiny-live-metadata` | **enforced** |
| wrong approval flags rejected | **yes** |
| output root isolation | **enforced** |
| universe size = 5 | **enforced** |
| non-ALM case rejected | **enforced** |
| PDF download | **permanently disabled** |
| PDF parse / OCR / extraction | **permanently disabled** |
| verified / testing_stable_sample | **禁止** |
| DB / MinIO / RAG | **未实现** |

### Rejected approval flags

- `--approve-full-harvest`
- `--approve-phase2-smoke-harvest`
- `--approve-phase3-batch-500-harvest`
- `--approve-b-class-tiny-live-validation`
- `--approve-phase1-tiny-live-metadata`
- `--download-pdf`
- `--enable-parser`

---

## Allowed Metadata Only

- report_document metadata
- report_period_snapshot linkage
- document_lineage metadata
- pdf_url / adjunct_url lineage（登记 only）
- quality_status · lineage_status

---

## Gate

```text
a_class_tiny_live_metadata_runner_gate = READY_FOR_APPROVAL
```

**不是 PASS** · **不是 live_ready** · **不是 verified**

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- B-class outputs: **unchanged**
- D-class outputs: **unchanged**
- CNINFO calls（本回合）: **0**

---

## Pending

| 项 | 状态 |
|----|------|
| explicit user approval for live | **待批准** |
| live metadata CNINFO path | **reserved · 未执行** |
| `a_class_phase1_tiny_live_metadata_gate` | **`READY_FOR_APPROVAL`**（不变） |
